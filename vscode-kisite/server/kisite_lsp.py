from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


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


@dataclass
class Symbol:
    name: str
    kind: str
    token: Any
    parameters: tuple[str, ...] = ()


@dataclass
class Analysis:
    tokens: list[Any]
    symbols: dict[str, Symbol]
    functions: dict[str, Symbol]
    diagnostic: dict[str, Any] | None


def uri_to_path(uri: str) -> Path:
    parsed = urlparse(uri)
    raw = unquote(parsed.path)
    if parsed.scheme == "file" and re.match(r"^/[A-Za-z]:/", raw):
        raw = raw[1:]
    return Path(raw)


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


def localize_parser_message(message: str, japanese: bool) -> str:
    if not japanese:
        return message
    replacements = [
        (r"^expected (.+), got (.+)$", r"\1 が必要ですが、\2 でした"),
        (r"^'(.+)' is reserved and cannot be a variable name$", r"「\1」は予約語のため変数名に使えません"),
        (r"^'(.+)' is reserved and cannot be a function name$", r"「\1」は予約語のため関数名に使えません"),
        (r"^unexpected character (.+)$", r"予期しない文字です: \1"),
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
        import kisite  # noqa: F401 - installs runtime/parser extensions
        import kisite_parser
        import kisite_syntax

        self.parser_module = kisite_parser
        self.syntax_module = kisite_syntax
        self.japanese = japanese
        self.reserved = {str(word).lower() for word in kisite_syntax.RESERVED_WORDS}
        self.builtins = {str(word).lower() for word in kisite_syntax.BUILTIN_FUNCTIONS}

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

        symbols, functions = self._collect_symbols(tokens)
        return Analysis(tokens, symbols, functions, diagnostic)

    def _diagnostic_from_error(self, message: str, text: str) -> dict[str, Any]:
        match = re.match(r"^(\d+):(\d+):\s*(.*)$", message, re.S)
        lines = text.splitlines() or [""]
        if match:
            line_index = max(0, int(match.group(1)) - 1)
            cp_col = max(0, int(match.group(2)) - 1)
            body = localize_parser_message(match.group(3).strip(), self.japanese)
        else:
            line_index = 0
            cp_col = 0
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
        }

    def _collect_symbols(self, tokens: list[Any]) -> tuple[dict[str, Symbol], dict[str, Symbol]]:
        symbols: dict[str, Symbol] = {}
        functions: dict[str, Symbol] = {}
        n = len(tokens)

        def word(index: int, value: str | None = None) -> bool:
            if not 0 <= index < n or tokens[index].kind != "WORD":
                return False
            return value is None or str(tokens[index].value).lower() == value

        i = 0
        while i < n:
            if word(i, "kalivisku") and word(i + 1, "musope") and word(i + 2, "kas") and word(i + 3):
                name_token = tokens[i + 3]
                name = str(name_token.value)
                params: list[str] = []
                j = i + 4
                if word(j, "vis"):
                    j += 1
                    while j < n and tokens[j].kind != "LBRACE":
                        if word(j) and str(tokens[j].value).lower() != "kasta":
                            params.append(str(tokens[j].value))
                        j += 1
                symbol = Symbol(name, "function", name_token, tuple(params))
                functions[name] = symbol
                symbols.setdefault(name, symbol)
                for j in range(i + 4, min(j, n)):
                    if word(j) and str(tokens[j].value).lower() not in {"vis", "kasta"}:
                        parameter = Symbol(str(tokens[j].value), "parameter", tokens[j])
                        symbols.setdefault(parameter.name, parameter)
                i += 4
                continue

            if word(i, "sonome") and word(i + 1, "kas"):
                j = i + 2
                while j < n and not word(j, "tas") and not word(j, "sis"):
                    if word(j) and str(tokens[j].value).lower() != "kasta":
                        name = str(tokens[j].value)
                        symbols.setdefault(name, Symbol(name, "variable", tokens[j]))
                    j += 1
            elif word(i, "polike") and word(i + 1, "kas"):
                j = i + 2
                while j < n and not word(j, "vos"):
                    if word(j) and str(tokens[j].value).lower() != "kasta":
                        name = str(tokens[j].value)
                        symbols.setdefault(name, Symbol(name, "variable", tokens[j]))
                    j += 1
            elif word(i, "pilike") and word(i + 1, "kas"):
                j = i + 2
                while j < n and not word(j, "pas"):
                    if word(j) and str(tokens[j].value).lower() != "kasta":
                        name = str(tokens[j].value)
                        symbols.setdefault(name, Symbol(name, "variable", tokens[j]))
                    j += 1
            i += 1

        return symbols, functions


class KisiteLanguageServer:
    def __init__(self, analyzer: Analyzer) -> None:
        self.analyzer = analyzer
        self.documents: dict[str, str] = {}
        self.analyses: dict[str, Analysis] = {}
        self.running = True
        self.shutdown_requested = False

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
            self.respond(request_id, {
                "capabilities": {
                    "textDocumentSync": {"openClose": True, "change": 1},
                    "completionProvider": {"triggerCharacters": [" "]},
                    "hoverProvider": True,
                    "definitionProvider": True,
                    "referencesProvider": True,
                    "renameProvider": {"prepareProvider": True},
                    "signatureHelpProvider": {"triggerCharacters": [" "]},
                    "documentSymbolProvider": True,
                },
                "serverInfo": {"name": "Kisite Language Server", "version": "0.1.0"},
            })
            return
        if method == "shutdown":
            self.shutdown_requested = True
            self.respond(request_id, None)
            return
        if method == "exit":
            self.running = False
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
        if method == "textDocument/didClose":
            uri = params["textDocument"]["uri"]
            self.documents.pop(uri, None)
            self.analyses.pop(uri, None)
            self.notify("textDocument/publishDiagnostics", {"uri": uri, "diagnostics": []})
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
        }
        if method in handlers:
            self.respond(request_id, handlers[method](params))
        elif request_id is not None:
            self.respond(request_id, None)

    def _set_document(self, uri: str, text: str) -> None:
        self.documents[uri] = text
        analysis = self.analyzer.analyze(text)
        self.analyses[uri] = analysis
        diagnostics = [] if analysis.diagnostic is None else [analysis.diagnostic]
        self.notify("textDocument/publishDiagnostics", {"uri": uri, "diagnostics": diagnostics})

    def _analysis(self, uri: str) -> Analysis:
        if uri not in self.analyses:
            self._set_document(uri, self.documents.get(uri, ""))
        return self.analyses[uri]

    def _lines(self, uri: str) -> list[str]:
        return self.documents.get(uri, "").splitlines() or [""]

    def _token_at(self, uri: str, position: dict[str, int]) -> Any | None:
        analysis = self._analysis(uri)
        lines = self._lines(uri)
        line_index = position["line"]
        if not 0 <= line_index < len(lines):
            return None
        cp_index = py_index_from_utf16(lines[line_index], position["character"])
        for token in analysis.tokens:
            if token.kind != "WORD" or token.line - 1 != line_index:
                continue
            start = token.column - 1
            end = start + len(str(token.value))
            if start <= cp_index <= end:
                return token
        return None

    def _locations_for_name(self, uri: str, name: str) -> list[dict[str, Any]]:
        lines = self._lines(uri)
        result = []
        for token in self._analysis(uri).tokens:
            if token.kind == "WORD" and str(token.value) == name:
                result.append({"uri": uri, "range": token_range(token, lines)})
        return result

    def completion(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        uri = params["textDocument"]["uri"]
        analysis = self._analysis(uri)
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for keyword in KEYWORDS:
            if keyword.lower() not in seen:
                items.append({"label": keyword, "kind": 14, "detail": "Kisite キーワード" if self.analyzer.japanese else "Kisite keyword"})
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
        for symbol in analysis.symbols.values():
            if symbol.name.lower() in seen:
                continue
            kind = 3 if symbol.kind == "function" else 6
            detail = symbol.kind
            if symbol.kind == "function":
                detail = self._signature_label(symbol.name, symbol.parameters)
            items.append({"label": symbol.name, "kind": kind, "detail": detail})
            seen.add(symbol.name.lower())
        return items

    def hover(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        token = self._token_at(uri, params["position"])
        if token is None:
            return None
        name = str(token.value)
        lowered = name.lower()
        lines = self._lines(uri)
        if lowered in self.analyzer.builtins:
            docs = BUILTIN_DOCS_JA if self.analyzer.japanese else BUILTIN_DOCS_EN
            signature = self._signature_label(lowered, BUILTIN_SIGNATURES.get(lowered, ()))
            value = f"```kisite\n{signature}\n```\n\n{docs.get(lowered, 'Kisite builtin')}"
        else:
            symbol = self._analysis(uri).symbols.get(name)
            if symbol is None:
                return None
            if symbol.kind == "function":
                value = f"```kisite\n{self._signature_label(symbol.name, symbol.parameters)}\n```"
            else:
                label = "変数" if self.analyzer.japanese else "variable"
                value = f"**{label}** `{symbol.name}`"
        return {"contents": {"kind": "markdown", "value": value}, "range": token_range(token, lines)}

    def definition(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        token = self._token_at(uri, params["position"])
        if token is None:
            return None
        symbol = self._analysis(uri).symbols.get(str(token.value))
        if symbol is None:
            return None
        return {"uri": uri, "range": token_range(symbol.token, self._lines(uri))}

    def references(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        uri = params["textDocument"]["uri"]
        token = self._token_at(uri, params["position"])
        return [] if token is None else self._locations_for_name(uri, str(token.value))

    def prepare_rename(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        token = self._token_at(uri, params["position"])
        if token is None:
            return None
        name = str(token.value)
        if name.lower() in self.analyzer.reserved or name.lower() in self.analyzer.builtins:
            return None
        if name not in self._analysis(uri).symbols:
            return None
        return {"range": token_range(token, self._lines(uri)), "placeholder": name}

    def rename(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        token = self._token_at(uri, params["position"])
        if token is None:
            return None
        old = str(token.value)
        new = str(params.get("newName") or "")
        if not new or new.lower() in self.analyzer.reserved:
            return None
        edits = [{"range": loc["range"], "newText": new} for loc in self._locations_for_name(uri, old)]
        return {"changes": {uri: edits}}

    def signature_help(self, params: dict[str, Any]) -> dict[str, Any] | None:
        uri = params["textDocument"]["uri"]
        position = params["position"]
        lines = self._lines(uri)
        if not 0 <= position["line"] < len(lines):
            return None
        cp_index = py_index_from_utf16(lines[position["line"]], position["character"])
        prefix_lines = lines[: position["line"]] + [lines[position["line"]][:cp_index]]
        prefix = "\n".join(prefix_lines)
        matches = list(re.finditer(r"(?i)\bKisite\s+kas\s+([\w]+)\s+vis\s+", prefix, re.UNICODE))
        if not matches:
            return None
        match = matches[-1]
        name = match.group(1)
        tail = prefix[match.end():]
        active = len(re.findall(r"(?i)\bkasta\b", tail))
        symbol = self._analysis(uri).functions.get(name)
        if symbol is not None:
            parameters = symbol.parameters
        else:
            parameters = BUILTIN_SIGNATURES.get(name.lower())
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
        lines = self._lines(uri)
        result = []
        for symbol in self._analysis(uri).symbols.values():
            rng = token_range(symbol.token, lines)
            result.append({
                "name": symbol.name,
                "kind": 12 if symbol.kind == "function" else 13,
                "range": rng,
                "selectionRange": rng,
                "detail": self._signature_label(symbol.name, symbol.parameters) if symbol.kind == "function" else symbol.kind,
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
