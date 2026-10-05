import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
LSP_PATH = ROOT / "vscode-kisite" / "server" / "kisite_lsp.py"
SPEC = importlib.util.spec_from_file_location("kisite_lsp", LSP_PATH)
assert SPEC is not None and SPEC.loader is not None
kisite_lsp = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = kisite_lsp
SPEC.loader.exec_module(kisite_lsp)


class LanguageServerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = kisite_lsp.Analyzer(ROOT)

    def make_server(self, source, name="tmp_lsp_test.kis"):
        uri = (ROOT / name).as_uri()
        server = kisite_lsp.KisiteLanguageServer(self.analyzer)
        server.documents[uri] = source
        server.analyses[uri] = self.analyzer.analyze(source)
        server.workspace_texts[uri] = source
        server.workspace_analyses[uri] = server.analyses[uri]
        return server, uri

    def test_nested_calls_parse_and_collect_function_signature(self):
        source = """
Kalivisku musope kas func vis x kasta y {
    Jasepe kas x + y.
}
Polike kas raw vos stdin.
Takute kas Kisite kas func vis Kisite kas minika vis raw kasta Kisite kas minika vis raw.
"""
        analysis = self.analyzer.analyze(source)
        self.assertIsNone(analysis.diagnostic)
        self.assertEqual(analysis.functions["func"].parameters, ("x", "y"))
        self.assertIn("raw", analysis.symbols)

    def test_japanese_identifier_is_indexed(self):
        source = "Sonome kas 合計 tas 1.\nTakute kas 合計.\n"
        analysis = self.analyzer.analyze(source)
        self.assertIsNone(analysis.diagnostic)
        self.assertIn("合計", analysis.symbols)

    def test_parser_error_becomes_diagnostic_with_raw_message(self):
        analysis = self.analyzer.analyze("Palusta Tuni { Takute kas 1.")
        self.assertIsNotNone(analysis.diagnostic)
        self.assertEqual(analysis.diagnostic["severity"], 1)
        self.assertEqual(analysis.diagnostic["source"], "Kisite")
        self.assertIn("rawMessage", analysis.diagnostic["data"])

    def test_definition_and_references_use_symbol_tokens(self):
        source = "Sonome kas value tas 3.\nTakute kas value.\nTakute kas value + 1.\n"
        server, uri = self.make_server(source)

        definition = server.definition({
            "textDocument": {"uri": uri},
            "position": {"line": 1, "character": 12},
        })
        self.assertIsNotNone(definition)
        self.assertEqual(definition["range"]["start"]["line"], 0)

        references = server.references({
            "textDocument": {"uri": uri},
            "position": {"line": 1, "character": 12},
        })
        self.assertEqual(len(references), 3)

    def test_scope_aware_definition_rename_and_highlight_do_not_cross_functions(self):
        source = """Kalivisku musope kas first vis x {
    Takute kas x.
}
Kalivisku musope kas second vis x {
    Takute kas x.
}
"""
        server, uri = self.make_server(source, "tmp_lsp_scope.kis")

        first_def = server.definition({
            "textDocument": {"uri": uri},
            "position": {"line": 1, "character": 15},
        })
        second_def = server.definition({
            "textDocument": {"uri": uri},
            "position": {"line": 4, "character": 15},
        })
        self.assertEqual(first_def["range"]["start"]["line"], 0)
        self.assertEqual(second_def["range"]["start"]["line"], 3)

        edit = server.rename({
            "textDocument": {"uri": uri},
            "position": {"line": 1, "character": 15},
            "newName": "left",
        })
        self.assertEqual(len(edit["changes"][uri]), 2)
        self.assertTrue(all(item["range"]["start"]["line"] <= 1 for item in edit["changes"][uri]))

        highlights = server.document_highlight({
            "textDocument": {"uri": uri},
            "position": {"line": 1, "character": 15},
        })
        self.assertEqual(len(highlights), 2)
        self.assertTrue(all(item["range"]["start"]["line"] <= 1 for item in highlights))

    def test_completion_only_exposes_current_function_locals(self):
        source = """Kalivisku musope kas first vis a {
    Sonome kas local_first tas a.
    Takute kas local_first.
}
Kalivisku musope kas second vis b {
    Sonome kas local_second tas b.
    Takute kas local_second.
}
"""
        server, uri = self.make_server(source, "tmp_lsp_completion_scope.kis")
        items = server.completion({
            "textDocument": {"uri": uri},
            "position": {"line": 2, "character": 10},
        })
        labels = {item["label"] for item in items}
        self.assertIn("a", labels)
        self.assertIn("local_first", labels)
        self.assertNotIn("b", labels)
        self.assertNotIn("local_second", labels)

    def test_rename_returns_workspace_edit(self):
        source = "Sonome kas value tas 3.\nTakute kas value.\n"
        server, uri = self.make_server(source, "tmp_lsp_rename.kis")
        edit = server.rename({
            "textDocument": {"uri": uri},
            "position": {"line": 1, "character": 12},
            "newName": "answer",
        })
        self.assertIsNotNone(edit)
        self.assertEqual(len(edit["changes"][uri]), 2)
        self.assertTrue(all(item["newText"] == "answer" for item in edit["changes"][uri]))

    def test_signature_help_for_user_function(self):
        source = """
Kalivisku musope kas add vis x kasta y { Jasepe kas x + y. }
Takute kas Kisite kas add vis 1 kasta 
"""
        server, uri = self.make_server(source, "tmp_lsp_signature.kis")
        line = source.splitlines()[2]
        help_result = server.signature_help({
            "textDocument": {"uri": uri},
            "position": {"line": 2, "character": len(line)},
        })
        self.assertIsNotNone(help_result)
        self.assertEqual(help_result["activeParameter"], 1)
        self.assertIn("x kasta y", help_result["signatures"][0]["label"])

    def test_semantic_tokens_include_functions_parameters_variables_and_builtins(self):
        source = """Kalivisku musope kas add vis x kasta y {
    Sonome kas total tas x + y.
    Jasepe kas total.
}
Takute kas Kisite kas minika vis "3".
Takute kas Kisite kas add vis 1 kasta 2.
"""
        server, uri = self.make_server(source, "tmp_lsp_semantic.kis")
        data = server.semantic_tokens({"textDocument": {"uri": uri}})["data"]
        self.assertTrue(data)
        token_types = data[3::5]
        self.assertIn(kisite_lsp.SEMANTIC_TOKEN_TYPES.index("function"), token_types)
        self.assertIn(kisite_lsp.SEMANTIC_TOKEN_TYPES.index("parameter"), token_types)
        self.assertIn(kisite_lsp.SEMANTIC_TOKEN_TYPES.index("variable"), token_types)

        modifiers = data[4::5]
        default_library_bit = 1 << kisite_lsp.SEMANTIC_TOKEN_MODIFIERS.index("defaultLibrary")
        self.assertTrue(any(value & default_library_bit for value in modifiers))

    def test_workspace_symbols_searches_multiple_files(self):
        server = kisite_lsp.KisiteLanguageServer(self.analyzer)
        uri_a = (ROOT / "alpha.kis").as_uri()
        uri_b = (ROOT / "beta.kis").as_uri()
        text_a = "Kalivisku musope kas Alpha { Jasepe kas 1. }\n"
        text_b = "Sonome kas BetaValue tas 2.\n"
        server.workspace_texts = {uri_a: text_a, uri_b: text_b}
        server.workspace_analyses = {
            uri_a: self.analyzer.analyze(text_a),
            uri_b: self.analyzer.analyze(text_b),
        }

        alpha = server.workspace_symbols({"query": "alpha"})
        beta = server.workspace_symbols({"query": "beta"})
        self.assertEqual(alpha[0]["name"], "Alpha")
        self.assertEqual(beta[0]["name"], "BetaValue")
        self.assertNotEqual(alpha[0]["location"]["uri"], beta[0]["location"]["uri"])

    def test_folding_ranges_cover_blocks_and_comment_runs(self):
        source = """# one
# two
Kalivisku musope kas f vis x {
    Palusta x > 0 {
        Takute kas x.
    }
}
"""
        server, uri = self.make_server(source, "tmp_lsp_folding.kis")
        ranges = server.folding_ranges({"textDocument": {"uri": uri}})
        self.assertTrue(any(item.get("kind") == "comment" for item in ranges))
        regions = [item for item in ranges if item.get("kind") == "region"]
        self.assertGreaterEqual(len(regions), 2)

    def test_inlay_hints_show_parameter_names_for_simple_calls(self):
        source = """Kalivisku musope kas add vis x kasta y { Jasepe kas x + y. }
Takute kas Kisite kas add vis 1 kasta 2.
"""
        server, uri = self.make_server(source, "tmp_lsp_inlay.kis")
        hints = server.inlay_hints({
            "textDocument": {"uri": uri},
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 1, "character": 100},
            },
        })
        labels = [hint["label"] for hint in hints]
        self.assertIn("x: ", labels)
        self.assertIn("y: ", labels)

    def test_code_action_adds_missing_block_brace(self):
        source = "Palusta Tuni {\n    Takute kas 1.\n"
        server, uri = self.make_server(source, "tmp_lsp_action.kis")
        diagnostic = server.analyses[uri].diagnostic
        actions = server.code_actions({
            "textDocument": {"uri": uri},
            "range": diagnostic["range"],
            "context": {"diagnostics": [diagnostic]},
        })
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["kind"], "quickfix")
        edit = actions[0]["edit"]["changes"][uri][0]
        self.assertIn("}", edit["newText"])

    def test_document_symbols_nest_function_locals(self):
        source = """Kalivisku musope kas f vis x {
    Sonome kas y tas x.
    Jasepe kas y.
}
Sonome kas global_value tas 3.
"""
        server, uri = self.make_server(source, "tmp_lsp_symbols.kis")
        symbols = server.document_symbols({"textDocument": {"uri": uri}})
        function = next(item for item in symbols if item["name"] == "f")
        children = {item["name"] for item in function["children"]}
        self.assertIn("x", children)
        self.assertIn("y", children)
        self.assertIn("global_value", {item["name"] for item in symbols})


if __name__ == "__main__":
    unittest.main()
