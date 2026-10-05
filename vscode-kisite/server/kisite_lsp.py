from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlparse


KEYWORDS = [
    "Takute", "Sonome", "Kemese", "Polike", "Pilike", "Putike",
    "Kinise", "Kinate", "Kisite", "Kalivisku", "musope", "Jasepe",
    "Palusta", "Japalusta", "kas", "tas", "pas", "sis", "vis", "vos",
    "kasta", "vista", "kix", "kate", "stdin", "Tuni", "Jatuni",
]

BUILTIN_SIGNATURES: dict[str, tuple[str, ...]] = {
    "minika": ("value",),
    "kipala": ("collection",),
    "pilika": ("start", "stop?", "step?"),
    "paline": ("collection",),
    "japonavi": ("values...",),
    "ponavi": ("values...",),
    "sum": ("collection",),
    "abs": ("value",),
    "fill": ("size", "value"),
    "reverse": ("collection",),
    "resize": ("collection", "size", "fill?"),
    "truncate": ("collection", "size"),
    "combinations": ("collection", "r"),
    "gcd": ("a", "b", "values..."),
    "lcm": ("a", "b", "values..."),
    "set": ("collection",),
    "array": ("collection",),
    "readint": (),
    "readints": ("count",),
    "modint": ("value", "modulus"),
    "modpow": ("base", "exponent", "modulus"),
    "modinv": ("value", "modulus"),
    "convolution": ("left", "right", "modulus?"),
    "flush": (),
    "pi": (),
    "sin": ("x",),
    "cos": ("x",),
    "tan": ("x",),
    "sqrt": ("x",),
    "atan2": ("y", "x"),
    "hypot": ("x", "y"),
    "floor": ("x",),
    "ceil": ("x",),
    "heapify": ("array",),
    "heappush": ("heap", "value"),
    "heappop": ("heap",),
    "heappeek": ("heap",),
    "bisectleft": ("array", "value"),
    "bisectright": ("array", "value"),
}

BUILTIN_DOCS_EN = {
    "minika": "Convert a value to a Kisite number.",
    "kipala": "Return the length of a collection.",
    "pilika": "Create a range-like sequence.",
    "paline": "Return a sorted array.",
    "japonavi": "Return the minimum value.",
    "ponavi": "Return the maximum value.",
    "readint": "Read one integer from standard input.",
    "readints": "Read multiple integers from standard input.",
    "convolution": "Compute a convolution.",
    "flush": "Flush interactive output.",
    "heappush": "Push a value onto a heap.",
    "heappop": "Pop the minimum value from a heap.",
    "heappeek": "Read the minimum value without removing it.",
    "bisectleft": "Return the left insertion position in a sorted array.",
    "bisectright": "Return the right insertion position in a sorted array.",
}

BUILTIN_DOCS_JA = {
    "minika": "値を Kisite の数値へ変換します。",
    "kipala": "コレクションの長さを返します。",
    "pilika": "範囲状の列を作成します。",
    "paline": "ソート済み配列を返します。",
    "japonavi": "最小値を返します。",
    "ponavi": "最大値を返します。",
    "readint": "標準入力から整数を1つ読み取ります。",
    "readints": "標準入力から複数の整数を読み取ります。",
    "convolution": "畳み込みを計算します。",
    "flush": "対話出力をフラッシュします。",
    "heappush": "ヒープへ値を追加します。",
    "heappop": "ヒープから最小値を取り出します。",
    "heappeek": "ヒープの最小値を取り出さずに確認します。",
    "bisectleft": "ソート済み配列で左側の挿入位置を返します。",
    "bisectright": "ソート済み配列で右側の挿入位置を返します。",
}

SEMANTIC_TOKEN_TYPES = ["keyword", "function", "variable", "parameter", "type"]
SEMANTIC_TOKEN_MODIFIERS = ["declaration", "definition", "readonly", "defaultLibrary"]

GLOBAL_SCOPE = "<global>"


@dataclass
class Symbol:
    name: str
    kind: str
    token: Any
    parameters: tuple[str, ...] = ()
    scope: str = GLOBAL_SCOPE
    symbol_id: str = ""


@dataclass
class Occurrence:
    name: str
    token: Any
    token_index: int
    scope: str
    symbol_id: str
    kind: str
    role: str = "read"


@dataclass
class FunctionScope:
    name: str
    scope_id: str
    name_index: int
    open_index: int
    close_index: int
    parameters: tuple[str, ...]


@dataclass
class Analysis:
    tokens: list[Any]
    symbols: dict[str, Symbol]
    functions: dict[str, Symbol]
    diagnostic: dict[str, Any] | None
    scoped_symbols: dict[tuple[str, str], Symbol] = field(default_factory=dict)
    occurrences: list[Occurrence] = field(default_factory=list)
    occurrence_by_index: dict[int, Occurrence] = field(default_factory=dict)
    function_scopes: list[FunctionScope] = field(default_factory=list)


def uri_to_path(uri: str) -> Path:
    parsed = urlparse(uri)
    raw = unquote(parsed.path)
    if parsed.scheme == "file" and re.match(r"^/[A-Za-z]:/", raw):
        raw = raw[1:]
    return Path(raw)


def path_to_uri(path: Path) -> str:
    return path.resolve().as_uri()


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def py_index_from_utf16(text: str, units: int) -> int:
    used = 0
    for index, ch in enumerate(text):
        width = 2 if ord(ch) > 0xFFFF else 1
        if used + width > units:
            return index
        used += width
    return len(text)


def token_range(token: Any, lines: list[str]) -> dict[str, Any]:
    line_index = max(0, token.line - 1)
    line = lines[line_index] if line_index < len(lines) else ""
    start_cp = max(0, token.column - 1)
    text = str(token.value) if token.value is not None else ""
    start = utf16_length(line[:start_cp])
    end = start + utf16_length(text)
    return {
        "start": {"line": line_index, "character": start},
        "end": {"line": line_index, "character": max(start + 1, end)},
    }


def position_key(position: dict[str, int]) -> tuple[int, int]:
    return position["line"], position["character"]


def localize_parser_message(message: str, japanese: bool) -> str:
    if not japanese:
        return message
    replacements = [
        (r"^expected (.+), got (.+)$", r"\1 が必要ですが、\2 でした"),
        (r"^'(.+)' is reserved and cannot be a variable name$", r"「\1」は予約語のため変数名に使えません"),
        (r"^'(.+)' is reserved and cannot be a function name$", r"「\1」は予約語のため関数名に使えません"),
        (r"^unexpected character (.+)$", r"予期しない文字です: \1"),
        (r"^unsupported type '(.+)'$", r"未対応の型です: \1"),
    ]
    for pattern, replacement in replacements:
        if re.match(pattern, message):
            return re.sub(pattern, replacement, message)
    return {
        "unterminated string": "文字列が閉じられていません",
        "unterminated block": "ブロックが閉じられていません",
        "japalusta must follow a palusta block": "Japalusta は Palusta ブロックの直後に置く必要があります",
    }.get(message, message)


class Analyzer:
    def __init__(self, kisite_root: Path, japanese: bool = False) -> None:
        root = str(kisite_root)
        if root not in sys.path:
            sys.path.insert(0, root)
        import kisite  # noqa: F401 - installs parser/runtime extensions
        import kisite_parser
        import kisite_syntax

        self.parser_module = kisite_parser
        self.syntax_module = kisite_syntax
        self.japanese = japanese
        self.reserved = {str(word).lower() for word in kisite_syntax.RESERVED_WORDS}
        self.builtins = {str(word).lower() for word in kisite_syntax.BUILTIN_FUNCTIONS}
        self.types = {str(word).lower() for word in kisite_syntax.TYPE_NAMES}
        self.keyword_set = {word.lower() for word in KEYWORDS}

    def analyze(self, text: str) -> Analysis:
        tokens: list[Any] = []
        diagnostic = None
        try:
            tokens = self.syntax_module.tokenize(text)
            self.parser_module.Parser(tokens).parse()
        except Exception as exc:
            if not tokens:
                try:
                    tokens = self.syntax_module.tokenize(text)
                except Exception:
                    tokens = []
            diagnostic = self._diagnostic_from_error(str(exc), text)

        return self._build_analysis(tokens, diagnostic)

    def _diagnostic_from_error(self, message: str, text: str) -> dict[str, Any]:
        match = re.match(r"^(\d+):(\d+):\s*(.*)$", message, re.S)
        lines = text.splitlines() or [""]
        if match:
            line_index = max(0, int(match.group(1)) - 1)
            cp_col = max(0, int(match.group(2)) - 1)
            raw_body = match.group(3).strip()
            body = localize_parser_message(raw_body, self.japanese)
        else:
            line_index = 0
            cp_col = 0
            raw_body = message
            body = localize_parser_message(message, self.japanese)
        line_index = min(line_index, len(lines) - 1)
        line = lines[line_index]
        cp_col = min(cp_col, len(line))
        character = utf16_length(line[:cp_col])
        return {
            "range": {
                "start": {"line": line_index, "character": character},
                "end": {"line": line_index, "character": character + 1},
            },
            "severity": 1,
            "source": "Kisite",
            "message": body,
            "data": {"rawMessage": raw_body},
        }

    def _build_analysis(self, tokens: list[Any], diagnostic: dict[str, Any] | None) -> Analysis:
        symbols: dict[str, Symbol] = {}
        functions: dict[str, Symbol] = {}
        scoped_symbols: dict[tuple[str, str], Symbol] = {}
        occurrences: list[Occurrence] = []
        occurrence_by_index: dict[int, Occurrence] = {}
        n = len(tokens)

        def word(index: int, value: str | None = None) -> bool:
            if not 0 <= index < n or tokens[index].kind != "WORD":
                return False
            return value is None or str(tokens[index].value).lower() == value

        function_scopes: list[FunctionScope] = []
        i = 0
        while i + 3 < n:
            if not (word(i, "kalivisku") and word(i + 1, "musope") and word(i + 2, "kas") and word(i + 3)):
                i += 1
                continue

            name_index = i + 3
            name = str(tokens[name_index].value)
            j = name_index + 1
            params: list[str] = []
            if word(j, "vis"):
                j += 1
                while j < n and tokens[j].kind != "LBRACE":
                    if word(j) and str(tokens[j].value).lower() != "kasta":
                        params.append(str(tokens[j].value))
                    j += 1
            while j < n and tokens[j].kind != "LBRACE":
                j += 1
            if j >= n:
                i += 1
                continue

            depth = 0
            close_index = n - 1
            k = j
            while k < n:
                if tokens[k].kind == "LBRACE":
                    depth += 1
                elif tokens[k].kind == "RBRACE":
                    depth -= 1
                    if depth == 0:
                        close_index = k
                        break
                k += 1

            scope_id = f"fn:{name}@{tokens[name_index].line}:{tokens[name_index].column}"
            function_scopes.append(FunctionScope(name, scope_id, name_index, j, close_index, tuple(params)))
            i = max(i + 1, close_index + 1)

        def scope_for_index(index: int) -> str:
            containing = [scope for scope in function_scopes if scope.open_index < index < scope.close_index]
            if not containing:
                return GLOBAL_SCOPE
            containing.sort(key=lambda scope: scope.close_index - scope.open_index)
            return containing[0].scope_id

        declaration_indices: set[int] = set()

        for scope in function_scopes:
            token = tokens[scope.name_index]
            symbol_id = f"function:{scope.name}"
            symbol = Symbol(scope.name, "function", token, scope.parameters, GLOBAL_SCOPE, symbol_id)
            functions[scope.name] = symbol
            symbols.setdefault(scope.name, symbol)
            scoped_symbols[(GLOBAL_SCOPE, scope.name)] = symbol
            declaration_indices.add(scope.name_index)

            occurrence = Occurrence(scope.name, token, scope.name_index, GLOBAL_SCOPE, symbol_id, "function", "definition")
            occurrences.append(occurrence)
            occurrence_by_index[scope.name_index] = occurrence

            start = scope.name_index + 1
            end = scope.open_index
            if start < n and word(start, "vis"):
                index = start + 1
                while index < end:
                    if word(index) and str(tokens[index].value).lower() != "kasta":
                        name = str(tokens[index].value)
                        symbol_id = f"{scope.scope_id}:parameter:{name}"
                        param_symbol = Symbol(name, "parameter", tokens[index], (), scope.scope_id, symbol_id)
                        scoped_symbols[(scope.scope_id, name)] = param_symbol
                        symbols.setdefault(name, param_symbol)
                        declaration_indices.add(index)
                        occ = Occurrence(name, tokens[index], index, scope.scope_id, symbol_id, "parameter", "definition")
                        occurrences.append(occ)
                        occurrence_by_index[index] = occ
                    index += 1

        def declare(index: int, scope_id: str, kind: str = "variable") -> None:
            if not word(index):
                return
            name = str(tokens[index].value)
            lowered = name.lower()
            if lowered in self.reserved or lowered in self.builtins:
                return
            symbol_id = f"{scope_id}:{kind}:{name}"
            symbol = Symbol(name, kind, tokens[index], (), scope_id, symbol_id)
            scoped_symbols.setdefault((scope_id, name), symbol)
            symbols.setdefault(name, scoped_symbols[(scope_id, name)])
            declaration_indices.add(index)
            actual = scoped_symbols[(scope_id, name)]
            occ = Occurrence(name, tokens[index], index, scope_id, actual.symbol_id, actual.kind, "definition")
            occurrences.append(occ)
            occurrence_by_index[index] = occ

        i = 0
        while i < n:
            scope_id = scope_for_index(i)
            if word(i, "sonome") and word(i + 1, "kas"):
                j = i + 2
                while j < n and not word(j, "tas") and not word(j, "sis"):
                    if word(j) and str(tokens[j].value).lower() != "kasta":
                        declare(j, scope_id)
                    j += 1
            elif word(i, "polike") and word(i + 1, "kas"):
                j = i + 2
                while j < n and not word(j, "vos"):
                    if word(j) and str(tokens[j].value).lower() != "kasta":
                        declare(j, scope_id)
                    j += 1
            elif word(i, "pilike") and word(i + 1, "kas"):
                j = i + 2
                while j < n and not word(j, "pas"):
                    if word(j) and str(tokens[j].value).lower() != "kasta":
                        declare(j, scope_id)
                    j += 1
            i += 1

        i = 0
        while i < n:
            token = tokens[i]
            if token.kind != "WORD" or i in declaration_indices:
                i += 1
                continue

            name = str(token.value)
            lowered = name.lower()
            scope_id = scope_for_index(i)

            if i >= 2 and word(i - 2, "kisite") and word(i - 1, "kas"):
                if lowered in self.builtins:
                    symbol_id = f"builtin:{lowered}"
                    occ = Occurrence(name, token, i, scope_id, symbol_id, "builtin", "read")
                    occurrences.append(occ)
                    occurrence_by_index[i] = occ
                elif name in functions:
                    symbol = functions[name]
                    occ = Occurrence(name, token, i, scope_id, symbol.symbol_id, "function", "read")
                    occurrences.append(occ)
                    occurrence_by_index[i] = occ
                i += 1
                continue

            if lowered in self.keyword_set or lowered in self.types or lowered in self.builtins:
                i += 1
                continue

            symbol = scoped_symbols.get((scope_id, name))
            if symbol is None and scope_id == GLOBAL_SCOPE:
                symbol = scoped_symbols.get((GLOBAL_SCOPE, name))
            if symbol is not None:
                occ = Occurrence(name, token, i, scope_id, symbol.symbol_id, symbol.kind, "read")
                occurrences.append(occ)
                occurrence_by_index[i] = occ
            i += 1

        return Analysis(
            tokens=tokens,
            symbols=symbols,
            functions=functions,
            diagnostic=diagnostic,
            scoped_symbols=scoped_symbols,
            occurrences=occurrences,
            occurrence_by_index=occurrence_by_index,
            function_scopes=function_scopes,
        )


class KisiteLanguageServer:
    def __init__(self, analyzer: Analyzer) -> None:
        self.analyzer = analyzer
        self.documents: dict[str, str] = {}
        self.analyses: dict[str, Analysis] = {}
        self.workspace_texts: dict[str, str] = {}
        self.workspace_analyses: dict[str, Analysis] = {}
        self.workspace_roots: list[Path] = []
        self.running = True
        self.shutdown_requested = False
        self.diagnostics_enabled = True

    def send(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
        sys.stdout.buffer.write(body)
        sys.stdout.buffer.flush()

    def respond(self, request_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
        if error is not None:
            payload["error"] = error
        else:
            payload["result"] = result
        self.send(payload)

    def notify(self, method: str, params: Any) -> None:
        self.send({"jsonrpc": "2.0", "method": method, "params": params})

    def read_message(self) -> dict[str, Any] | None:
        headers: dict[str, str] = {}
        while True:
            line = sys.stdin.buffer.readline()
            if not line:
                return None
            if line in (b"\r\n", b"\n"):
                break
            key, _, value = line.decode("ascii", errors="replace").partition(":")
            headers[key.strip().lower()] = value.strip()
        length = int(headers.get("content-length", "0"))
        if length <= 0:
            return None
        data = sys.stdin.buffer.read(length)
        return json.loads(data.decode("utf-8"))

    def run(self) -> None:
        while self.running:
            message = self.read_message()
            if message is None:
                break
            try:
                self.handle(message)
            except Exception as exc:
                if "id" in message:
                    self.respond(message["id"], error={"code": -32603, "message": str(exc)})

    def handle(self, message: dict[str, Any]) -> None:
        method = message.get("method")
        params = message.get("params") or {}
        request_id = message.get("id")

        if method == "initialize":
            locale = str(params.get("locale") or "").lower()
            if locale.startswith("ja"):
                self.analyzer.japanese = True
            self._set_workspace_roots(params)
            self.respond(request_id, {
                "capabilities": {
                    "textDocumentSync": {"openClose": True, "change": 1, "save": True},
                    "completionProvider": {"triggerCharacters": [" "]},
                    "hoverProvider": True,
                    "definitionProvider": True,
                    "referencesProvider": True,
                    "renameProvider": {"prepareProvider": True},
                    "signatureHelpProvider": {"triggerCharacters": [" "]},
                    "documentSymbolProvider": True,
                    "workspaceSymbolProvider": True,
                    "documentHighlightProvider": True,
                    "semanticTokensProvider": {
                        "legend": {
                            "tokenTypes": SEMANTIC_TOKEN_TYPES,
                            "tokenModifiers": SEMANTIC_TOKEN_MODIFIERS,
                        },
                        "full": True,
                    },
                    "codeActionProvider": True,
                    "foldingRangeProvider": True,
                    "inlayHintProvider": True,
                },
                "serverInfo": {"name": "Kisite Language Server", "version": "0.2.0"},
            })
            return
        if method == "initialized":
            self._index_workspace()
            return
        if method == "shutdown":
            self.shutdown_requested = True
            self.respond(request_id, None)
            return
        if method == "exit":
            self.running = False
            return

        if method == "workspace/didChangeConfiguration":
            self._apply_configuration(params.get("settings"))
            self._republish_all_diagnostics()
            return
        if method == "workspace/didChangeWatchedFiles":
            self._handle_watched_files(params.get("changes") or [])
            return

        if method == "textDocument/didOpen":
            doc = params["textDocument"]
            self._set_document(doc["uri"], doc["text"])
            return
        if method == "textDocument/didChange":
            uri = params["textDocument"]["uri"]
            changes = params.get("contentChanges") or []
            if changes:
                self._set_document(uri, changes[-1]["text"])
            return
        if method == "textDocument/didSave":
            uri = params["textDocument"]["uri"]
            if uri in self.documents:
                self.workspace_texts[uri] = self.documents[uri]
                self.workspace_analyses[uri] = self.analyses[uri]
            return
        if method == "textDocument/didClose":
            uri = params["textDocument"]["uri"]
            self.documents.pop(uri, None)
            self.analyses.pop(uri, None)
            self.notify("textDocument/publishDiagnostics", {"uri": uri, "diagnostics": []})
            self._reload_workspace_uri(uri)
            return

        handlers = {
            "textDocument/completion": self.completion,
            "textDocument/hover": self.hover,
            "textDocument/definition": self.definition,
            "textDocument/references": self.references,
            "textDocument/prepareRename": self.prepare_rename,
            "textDocument/rename": self.rename,
            "textDocument/signatureHelp": self.signature_help,
            "textDocument/documentSymbol": self.document_symbols,
            "workspace/symbol": self.workspace_symbols,
            "textDocument/documentHighlight": self.document_highlight,
            "textDocument/semanticTokens/full": self.semantic_tokens,
            "textDocument/codeAction": self.code_actions,
            "textDocument/foldingRange": self.folding_ranges,
            "textDocument/inlayHint": self.inlay_hints,
        }
        if method in handlers:
            self.respond(request_id, handlers[method](params))
        elif request_id is not None:
            self.respond(request_id, None)

    def _set_workspace_roots(self, params: dict[str, Any]) -> None:
        roots: list[Path] = []
        for item in params.get("workspaceFolders") or []:
            try:
                roots.append(uri_to_path(item["uri"]).resolve())
            except Exception:
                pass
        root_uri = params.get("rootUri")
        if root_uri and not roots:
            try:
                roots.append(uri_to_path(root_uri).resolve())
            except Exception:
                pass
        self.workspace_roots = roots

    def _index_workspace(self) -> None:
        seen: set[str] = set()
        skip_parts = {".git", "node_modules", ".venv", "__pycache__"}
        count = 0
        for root in self.workspace_roots:
            if not root.exists():
                continue
            try:
                paths = root.rglob("*.kis")
            except OSError:
                continue
            for path in paths:
                if any(part in skip_parts for part in path.parts):
                    continue
                uri = path_to_uri(path)
                if uri in seen:
                    continue
                seen.add(uri)
                self._reload_workspace_uri(uri)
                count += 1
                if count >= 5000:
                    return

    def _reload_workspace_uri(self, uri: str) -> None:
        if uri in self.documents:
            self.workspace_texts[uri] = self.documents[uri]
            self.workspace_analyses[uri] = self.analyses[uri]
            return
        path = uri_to_path(uri)
        if not path.exists() or path.suffix.lower() != ".kis":
            self.workspace_texts.pop(uri, None)
            self.workspace_analyses.pop(uri, None)
            return
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return
        self.workspace_texts[uri] = text
        self.workspace_analyses[uri] = self.analyzer.analyze(text)

    def _handle_watched_files(self, changes: list[dict[str, Any]]) -> None:
        for change in changes:
            uri = str(change.get("uri") or "")
            if not uri:
                continue
            if int(change.get("type") or 0) == 3:
                self.workspace_texts.pop(uri, None)
                self.workspace_analyses.pop(uri, None)
            else:
                self._reload_workspace_uri(uri)

    def _apply_configuration(self, settings: Any) -> None:
        if not isinstance(settings, dict):
            return
        kisite = settings.get("kisite", settings)
        if not isinstance(kisite, dict):
            return
        diagnostics = kisite.get("diagnostics")
        if isinstance(diagnostics, dict) and "enabled" in diagnostics:
            self.diagnostics_enabled = bool(diagnostics["enabled"])

    def _republish_all_diagnostics(self) -> None:
        for uri, analysis in self.analyses.items():
            self._publish_diagnostics(uri, analysis)

    def _publish_diagnostics(self, uri: str, analysis: Analysis) -> None:
        diagnostics = []
        if self.diagnostics_enabled and analysis.diagnostic is not None:
            diagnostics = [analysis.diagnostic]
        self.notify("textDocument/publishDiagnostics", {"uri": uri, "diagnostics": diagnostics})

    def _set_document(self, uri: str, text: str) -> None:
        self.documents[uri] = text
        analysis = self.analyzer.analyze(text)
        self.analyses[uri] = analysis
        self.workspace_texts[uri] = text
        self.workspace_analyses[uri] = analysis
        self._publish_diagnostics(uri, analysis)

    def _analysis(self, uri: str) -> Analysis:
        if uri in self.analyses:
            return self.analyses[uri]
        if uri in self.workspace_analyses:
            return self.workspace_analyses[uri]
        text = self.documents.get(uri, self.workspace_texts.get(uri, ""))
        analysis = self.analyzer.analyze(text)
        self.workspace_analyses[uri] = analysis
        return analysis

    def _text(self, uri: str) -> str:
        return self.documents.get(uri, self.workspace_texts.get(uri, ""))

    def _lines(self, uri: str) -> list[str]:
        return self._text(uri).splitlines() or [""]

    def _token_index_at(self, uri: str, position: dict[str, int]) -> int | None:
        analysis = self._analysis(uri)
        lines = self._lines(uri)
        line_index = position["line"]
        if not 0 <= line_index < len(lines):
            return None
        cp_index = py_index_from_utf16(lines[line_index], position["character"])
        for index, token in enumerate(analysis.tokens):
            if token.kind != "WORD" or token.line - 1 != line_index:
                continue
            start = token.column - 1
            end = start + len(str(token.value))
            if start <= cp_index <= end:
                return index
        return None

    def _token_at(self, uri: str, position: dict[str, int]) -> Any | None:
        index = self._token_index_at(uri, position)
        return None if index is None else self._analysis(uri).tokens[index]

    def _occurrence_at(self, uri: str, position: dict[str, int]) -> Occurrence | None:
        index = self._token_index_at(uri, position)
        if index is None:
            return None
        return self._analysis(uri).occurrence_by_index.get(index)

    def _scope_at_position(self, uri: str, position: dict[str, int]) -> str:
        analysis = self._analysis(uri)
        lines = self._lines(uri)
        pos = position_key(position)
        containing: list[FunctionScope] = []
        for scope in analysis.function_scopes:
            start = token_range(analysis.tokens[scope.open_index], lines)["start"]
            end = token_range(analysis.tokens[scope.close_index], lines)["end"]
            if position_key(start) <= pos <= position_key(end):
                containing.append(scope)
        if not containing:
            return GLOBAL_SCOPE
        containing.sort(key=lambda scope: scope.close_index - scope.open_index)
        return containing[0].scope_id

    def _symbol_by_id(self, analysis: Analysis, symbol_id: str) -> Symbol | None:
        for symbol in analysis.scoped_symbols.values():
            if symbol.symbol_id == symbol_id:
                return symbol
        return None

    def _occurrences_for_symbol(self, uri: str, symbol_id: str) -> list[Occurrence]:
        return [occ for occ in self._analysis(uri).occurrences if occ.symbol_id == symbol_id]

    def completion(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        uri = params["textDocument"]["uri"]
        analysis = self._analysis(uri)
        scope_id = self._scope_at_position(uri, params.get("position") or {"line": 0, "character": 0})
        items: list[dict[str, Any]] = []
        seen: set[str] = set()

        for keyword in KEYWORDS:
            if keyword.lower() not in seen:
                items.append({
                    "label": keyword,
                    "kind": 14,
                    "detail": "Kisite キーワード" if self.analyzer.japanese else "Kisite keyword",
                })
                seen.add(keyword.lower())

        docs = BUILTIN_DOCS_JA if self.analyzer.japanese else BUILTIN_DOCS_EN
        for name in sorted(self.analyzer.builtins):
            params_text = " kasta ".join(BUILTIN_SIGNATURES.get(name, ()))
            label = f"{name} vis {params_text}" if params_text else name
            items.append({
                "label": name,
                "kind": 3,
                "detail": label,
                "documentation": {"kind": "markdown", "value": docs.get(name, "Kisite builtin")},
            })
            seen.add(name.lower())

        for symbol in analysis.functions.values():
            if symbol.name.lower() in seen:
                continue
            items.append({
                "label": symbol.name,
                "kind": 3,
                "detail": self._signature_label(symbol.name, symbol.parameters),
            })
            seen.add(symbol.name.lower())

        for (symbol_scope, name), symbol in analysis.scoped_symbols.items():
            if symbol.kind == "function" or symbol_scope != scope_id:
                continue
            if name.lower() in seen:
                continue
            items.append({
                "label": name,
                "kind": 6,
                "detail": "parameter" if symbol.kind == "parameter" else "variable",
            })
            seen.add(name.lower())
        return items

    def hover(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        token = self._token_at(uri, params["position"])
        if token is None:
            return None
        lines = self._lines(uri)
        name = str(token.value)
        lowered = name.lower()
        occurrence = self._occurrence_at(uri, params["position"])

        if lowered in self.analyzer.builtins:
            docs = BUILTIN_DOCS_JA if self.analyzer.japanese else BUILTIN_DOCS_EN
            signature = self._signature_label(lowered, BUILTIN_SIGNATURES.get(lowered, ()))
            value = f"```kisite\n{signature}\n```\n\n{docs.get(lowered, 'Kisite builtin')}"
        elif occurrence is not None:
            symbol = self._symbol_by_id(self._analysis(uri), occurrence.symbol_id)
            if symbol is None:
                return None
            if symbol.kind == "function":
                value = f"```kisite\n{self._signature_label(symbol.name, symbol.parameters)}\n```"
            else:
                labels = {
                    "parameter": "引数" if self.analyzer.japanese else "parameter",
                    "variable": "変数" if self.analyzer.japanese else "variable",
                }
                value = f"**{labels.get(symbol.kind, symbol.kind)}** `{symbol.name}`"
        else:
            return None

        return {
            "contents": {"kind": "markdown", "value": value},
            "range": token_range(token, lines),
        }

    def definition(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        occurrence = self._occurrence_at(uri, params["position"])
        if occurrence is None or occurrence.kind == "builtin":
            return None
        symbol = self._symbol_by_id(self._analysis(uri), occurrence.symbol_id)
        if symbol is None:
            return None
        return {"uri": uri, "range": token_range(symbol.token, self._lines(uri))}

    def references(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        uri = params["textDocument"]["uri"]
        occurrence = self._occurrence_at(uri, params["position"])
        if occurrence is None or occurrence.kind == "builtin":
            return []
        lines = self._lines(uri)
        return [
            {"uri": uri, "range": token_range(occ.token, lines)}
            for occ in self._occurrences_for_symbol(uri, occurrence.symbol_id)
        ]

    def prepare_rename(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        occurrence = self._occurrence_at(uri, params["position"])
        if occurrence is None or occurrence.kind == "builtin":
            return None
        name = occurrence.name
        if name.lower() in self.analyzer.reserved or name.lower() in self.analyzer.builtins:
            return None
        return {
            "range": token_range(occurrence.token, self._lines(uri)),
            "placeholder": name,
        }

    def rename(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        occurrence = self._occurrence_at(uri, params["position"])
        if occurrence is None or occurrence.kind == "builtin":
            return None
        new = str(params.get("newName") or "")
        if (
            not new
            or new.lower() in self.analyzer.reserved
            or new.lower() in self.analyzer.builtins
            or not (new[0].isalpha() or new[0] == "_")
            or any(not (ch.isalnum() or ch == "_") for ch in new)
        ):
            return None

        lines = self._lines(uri)
        edits = [
            {"range": token_range(occ.token, lines), "newText": new}
            for occ in self._occurrences_for_symbol(uri, occurrence.symbol_id)
        ]
        return {"changes": {uri: edits}}

    def document_highlight(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        uri = params["textDocument"]["uri"]
        occurrence = self._occurrence_at(uri, params["position"])
        if occurrence is None:
            return []
        lines = self._lines(uri)
        result = []
        for occ in self._occurrences_for_symbol(uri, occurrence.symbol_id):
            kind = 3 if occ.role == "definition" else 2
            result.append({"range": token_range(occ.token, lines), "kind": kind})
        return result

    def signature_help(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        position = params["position"]
        lines = self._lines(uri)
        if not 0 <= position["line"] < len(lines):
            return None
        cp_index = py_index_from_utf16(lines[position["line"]], position["character"])
        prefix_lines = lines[: position["line"]] + [lines[position["line"]][:cp_index]]
        prefix = "\n".join(prefix_lines)
        matches = list(re.finditer(r"(?iu)\bKisite\s+kas\s+([\w]+)\s+vis\s+", prefix))
        if not matches:
            return None
        match = matches[-1]
        name = match.group(1)
        tail = prefix[match.end():]
        active = len(re.findall(r"(?iu)\bkasta\b", tail))
        symbol = self._analysis(uri).functions.get(name)
        parameters = symbol.parameters if symbol is not None else BUILTIN_SIGNATURES.get(name.lower())
        if parameters is None:
            return None
        parameter_infos = [{"label": param} for param in parameters]
        active = min(active, max(0, len(parameter_infos) - 1))
        return {
            "signatures": [{
                "label": self._signature_label(name, parameters),
                "parameters": parameter_infos,
            }],
            "activeSignature": 0,
            "activeParameter": active,
        }

    def document_symbols(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        uri = params["textDocument"]["uri"]
        analysis = self._analysis(uri)
        lines = self._lines(uri)
        result: list[dict[str, Any]] = []

        children_by_scope: dict[str, list[dict[str, Any]]] = {}
        for symbol in analysis.scoped_symbols.values():
            if symbol.kind == "function":
                continue
            rng = token_range(symbol.token, lines)
            entry = {
                "name": symbol.name,
                "kind": 26 if symbol.kind == "parameter" else 13,
                "range": rng,
                "selectionRange": rng,
                "detail": symbol.kind,
            }
            children_by_scope.setdefault(symbol.scope, []).append(entry)

        for function in analysis.functions.values():
            scope = next((candidate for candidate in analysis.function_scopes if candidate.name == function.name), None)
            selection = token_range(function.token, lines)
            if scope is not None:
                start = token_range(analysis.tokens[scope.name_index], lines)["start"]
                end = token_range(analysis.tokens[scope.close_index], lines)["end"]
                full_range = {"start": start, "end": end}
                children = children_by_scope.get(scope.scope_id, [])
            else:
                full_range = selection
                children = []
            result.append({
                "name": function.name,
                "kind": 12,
                "range": full_range,
                "selectionRange": selection,
                "detail": self._signature_label(function.name, function.parameters),
                "children": children,
            })

        for symbol in analysis.scoped_symbols.values():
            if symbol.scope != GLOBAL_SCOPE or symbol.kind == "function":
                continue
            rng = token_range(symbol.token, lines)
            result.append({
                "name": symbol.name,
                "kind": 13,
                "range": rng,
                "selectionRange": rng,
                "detail": symbol.kind,
            })
        return result

    def workspace_symbols(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        query = str(params.get("query") or "").lower()
        result: list[dict[str, Any]] = []
        merged = dict(self.workspace_analyses)
        merged.update(self.analyses)
        for uri, analysis in merged.items():
            lines = self._text_for_indexed_uri(uri).splitlines() or [""]
            for symbol in analysis.scoped_symbols.values():
                if symbol.kind == "parameter":
                    continue
                if query and query not in symbol.name.lower():
                    continue
                result.append({
                    "name": symbol.name,
                    "kind": 12 if symbol.kind == "function" else 13,
                    "location": {"uri": uri, "range": token_range(symbol.token, lines)},
                    "containerName": "" if symbol.scope == GLOBAL_SCOPE else symbol.scope.split("@", 1)[0].removeprefix("fn:"),
                })
        return result[:500]

    def _text_for_indexed_uri(self, uri: str) -> str:
        return self.documents.get(uri, self.workspace_texts.get(uri, ""))

    def semantic_tokens(self, params: dict[str, Any]) -> dict[str, Any]:
        uri = params["textDocument"]["uri"]
        analysis = self._analysis(uri)
        lines = self._lines(uri)
        encoded: list[tuple[int, int, int, int, int]] = []
        occupied: set[int] = set()

        type_index = {name: index for index, name in enumerate(SEMANTIC_TOKEN_TYPES)}
        modifier_index = {name: index for index, name in enumerate(SEMANTIC_TOKEN_MODIFIERS)}

        def modifiers(*names: str) -> int:
            mask = 0
            for name in names:
                mask |= 1 << modifier_index[name]
            return mask

        for occ in analysis.occurrences:
            rng = token_range(occ.token, lines)
            start = rng["start"]
            length = max(1, rng["end"]["character"] - start["character"])
            if occ.kind in ("function", "builtin"):
                token_type = type_index["function"]
            elif occ.kind == "parameter":
                token_type = type_index["parameter"]
            else:
                token_type = type_index["variable"]
            mods = 0
            if occ.role == "definition":
                mods |= modifiers("declaration", "definition")
            if occ.kind == "builtin":
                mods |= modifiers("defaultLibrary")
            encoded.append((start["line"], start["character"], length, token_type, mods))
            occupied.add(occ.token_index)

        for index, token in enumerate(analysis.tokens):
            if token.kind != "WORD" or index in occupied:
                continue
            lowered = str(token.value).lower()
            rng = token_range(token, lines)
            start = rng["start"]
            length = max(1, rng["end"]["character"] - start["character"])
            previous = analysis.tokens[index - 1] if index > 0 else None
            if lowered in self.analyzer.types and previous is not None and previous.kind == "WORD" and str(previous.value).lower() == "sis":
                encoded.append((start["line"], start["character"], length, type_index["type"], 0))
            elif lowered in self.analyzer.keyword_set:
                encoded.append((start["line"], start["character"], length, type_index["keyword"], 0))

        encoded.sort(key=lambda item: (item[0], item[1]))
        data: list[int] = []
        prev_line = 0
        prev_char = 0
        for line, char, length, token_type, mods in encoded:
            delta_line = line - prev_line
            delta_char = char - prev_char if delta_line == 0 else char
            data.extend([delta_line, delta_char, length, token_type, mods])
            prev_line = line
            prev_char = char
        return {"data": data}

    def folding_ranges(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        uri = params["textDocument"]["uri"]
        analysis = self._analysis(uri)
        result: list[dict[str, Any]] = []
        stack: list[Any] = []
        for token in analysis.tokens:
            if token.kind == "LBRACE":
                stack.append(token)
            elif token.kind == "RBRACE" and stack:
                opening = stack.pop()
                start_line = opening.line - 1
                end_line = token.line - 1
                if end_line > start_line:
                    result.append({
                        "startLine": start_line,
                        "startCharacter": max(0, opening.column - 1),
                        "endLine": end_line,
                        "endCharacter": max(0, token.column),
                        "kind": "region",
                    })

        lines = self._lines(uri)
        comment_start: int | None = None
        for index, line in enumerate(lines + [""]):
            if index < len(lines) and line.lstrip().startswith("#"):
                if comment_start is None:
                    comment_start = index
            elif comment_start is not None:
                if index - comment_start >= 2:
                    result.append({
                        "startLine": comment_start,
                        "endLine": index - 1,
                        "kind": "comment",
                    })
                comment_start = None
        return result

    def inlay_hints(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        uri = params["textDocument"]["uri"]
        analysis = self._analysis(uri)
        lines = self._lines(uri)
        requested = params.get("range")
        result: list[dict[str, Any]] = []
        n = len(analysis.tokens)

        def word(index: int, value: str | None = None) -> bool:
            if not 0 <= index < n or analysis.tokens[index].kind != "WORD":
                return False
            return value is None or str(analysis.tokens[index].value).lower() == value

        i = 0
        while i + 3 < n:
            if not (word(i, "kisite") and word(i + 1, "kas") and word(i + 2) and word(i + 3, "vis")):
                i += 1
                continue
            name = str(analysis.tokens[i + 2].value)
            symbol = analysis.functions.get(name)
            parameters = symbol.parameters if symbol is not None else BUILTIN_SIGNATURES.get(name.lower())
            if not parameters:
                i += 1
                continue

            j = i + 4
            boundary = j
            nested = False
            while boundary < n and analysis.tokens[boundary].kind not in ("DOT", "RBRACE", "EOF"):
                if word(boundary, "kisite"):
                    nested = True
                    break
                boundary += 1
            if nested:
                i += 1
                continue

            arg_starts = [j]
            k = j
            while k < boundary:
                if word(k, "kasta") and k + 1 < boundary:
                    arg_starts.append(k + 1)
                k += 1

            for param_index, token_index in enumerate(arg_starts[:len(parameters)]):
                while token_index < boundary and analysis.tokens[token_index].kind == "WORD" and str(analysis.tokens[token_index].value).lower() == "kasta":
                    token_index += 1
                if token_index >= boundary:
                    continue
                token = analysis.tokens[token_index]
                if token.kind not in ("WORD", "NUMBER", "STRING", "LPAREN", "LBRACKET", "LBRACE"):
                    continue
                rng = token_range(token, lines)
                position = rng["start"]
                if requested and not self._position_in_range(position, requested):
                    continue
                label = parameters[param_index].rstrip("?").rstrip(".")
                result.append({
                    "position": position,
                    "label": f"{label}: ",
                    "kind": 2,
                    "paddingRight": True,
                })
            i = max(i + 1, boundary)
        return result

    @staticmethod
    def _position_in_range(position: dict[str, int], rng: dict[str, Any]) -> bool:
        return position_key(rng["start"]) <= position_key(position) <= position_key(rng["end"])

    def code_actions(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        uri = params["textDocument"]["uri"]
        lines = self._lines(uri)
        result: list[dict[str, Any]] = []
        for diagnostic in params.get("context", {}).get("diagnostics", []):
            raw = str((diagnostic.get("data") or {}).get("rawMessage") or diagnostic.get("message") or "")
            if "unterminated block" in raw or "ブロックが閉じられていません" in raw:
                end_line = len(lines) - 1
                end_char = utf16_length(lines[end_line])
                edit_range = {
                    "start": {"line": end_line, "character": end_char},
                    "end": {"line": end_line, "character": end_char},
                }
                title = "閉じ波括弧 `}` を追加" if self.analyzer.japanese else "Add closing `}`"
                result.append({
                    "title": title,
                    "kind": "quickfix",
                    "diagnostics": [diagnostic],
                    "isPreferred": True,
                    "edit": {"changes": {uri: [{"range": edit_range, "newText": "\n}"}]}},
                })
            elif "unterminated string" in raw or "文字列が閉じられていません" in raw:
                line_index = diagnostic.get("range", {}).get("start", {}).get("line", 0)
                line_index = min(max(0, line_index), len(lines) - 1)
                end_char = utf16_length(lines[line_index])
                edit_range = {
                    "start": {"line": line_index, "character": end_char},
                    "end": {"line": line_index, "character": end_char},
                }
                title = "閉じ引用符 `\"` を追加" if self.analyzer.japanese else "Add closing quote"
                result.append({
                    "title": title,
                    "kind": "quickfix",
                    "diagnostics": [diagnostic],
                    "isPreferred": True,
                    "edit": {"changes": {uri: [{"range": edit_range, "newText": "\""}]}},
                })
        return result

    @staticmethod
    def _signature_label(name: str, parameters: tuple[str, ...]) -> str:
        if not parameters:
            return f"Kisite kas {name}"
        return f"Kisite kas {name} vis " + " kasta ".join(parameters)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kisite-root", type=Path, required=True)
    parser.add_argument("--locale", default="")
    args = parser.parse_args(argv)
    analyzer = Analyzer(args.kisite_root.resolve(), japanese=args.locale.lower().startswith("ja"))
    KisiteLanguageServer(analyzer).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
