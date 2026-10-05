import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LSP_PATH = ROOT / "vscode-kisite" / "server" / "kisite_lsp.py"
SPEC = importlib.util.spec_from_file_location("kisite_lsp", LSP_PATH)
assert SPEC is not None and SPEC.loader is not None
kisite_lsp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kisite_lsp)


class LanguageServerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = kisite_lsp.Analyzer(ROOT)

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

    def test_parser_error_becomes_diagnostic(self):
        analysis = self.analyzer.analyze("Palusta Tuni { Takute kas 1.")
        self.assertIsNotNone(analysis.diagnostic)
        self.assertEqual(analysis.diagnostic["severity"], 1)
        self.assertEqual(analysis.diagnostic["source"], "Kisite")

    def test_definition_and_references_use_symbol_tokens(self):
        source = "Sonome kas value tas 3.\nTakute kas value.\nTakute kas value + 1.\n"
        uri = (ROOT / "tmp_lsp_test.kis").as_uri()
        server = kisite_lsp.KisiteLanguageServer(self.analyzer)
        server.documents[uri] = source
        server.analyses[uri] = self.analyzer.analyze(source)

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

    def test_rename_returns_workspace_edit(self):
        source = "Sonome kas value tas 3.\nTakute kas value.\n"
        uri = (ROOT / "tmp_lsp_rename.kis").as_uri()
        server = kisite_lsp.KisiteLanguageServer(self.analyzer)
        server.documents[uri] = source
        server.analyses[uri] = self.analyzer.analyze(source)

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
        uri = (ROOT / "tmp_lsp_signature.kis").as_uri()
        server = kisite_lsp.KisiteLanguageServer(self.analyzer)
        server.documents[uri] = source
        server.analyses[uri] = self.analyzer.analyze(source)
        line = source.splitlines()[2]

        help_result = server.signature_help({
            "textDocument": {"uri": uri},
            "position": {"line": 2, "character": len(line)},
        })
        self.assertIsNotNone(help_result)
        self.assertEqual(help_result["activeParameter"], 1)
        self.assertIn("x kasta y", help_result["signatures"][0]["label"])


if __name__ == "__main__":
    unittest.main()
