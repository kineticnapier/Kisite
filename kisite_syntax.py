from __future__ import annotations

from dataclasses import dataclass


VERSION = "0.0.16"


class KisiteError(Exception):
    pass


class FunctionReturn(Exception):
    def __init__(self, value: object) -> None:
        super().__init__()
        self.value = value


class LoopBreak(Exception):
    pass


class LoopContinue(Exception):
    pass


@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1
    column = 1

    def advance(text: str) -> None:
        nonlocal line, column
        for ch in text:
            if ch == "\n":
                line += 1
                column = 1
            else:
                column += 1

    while i < len(source):
        ch = source[i]

        if ch.isspace():
            advance(ch)
            i += 1
            continue

        if ch == "#":
            start = i
            while i < len(source) and source[i] != "\n":
                i += 1
            advance(source[start:i])
            continue

        if ch in ('"', "“"):
            start_line, start_col = line, column
            closing = '"' if ch == '"' else "”"
            i += 1
            advance(ch)
            chars: list[str] = []
            while i < len(source) and source[i] != closing:
                if source[i] == "\\" and i + 1 < len(source):
                    esc = source[i + 1]
                    escapes = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}
                    chars.append(escapes.get(esc, esc))
                    advance(source[i:i + 2])
                    i += 2
                    continue
                chars.append(source[i])
                advance(source[i])
                i += 1
            if i >= len(source):
                raise KisiteError(f"{start_line}:{start_col}: unterminated string")
            advance(source[i])
            i += 1
            tokens.append(Token("STRING", "".join(chars), start_line, start_col))
            continue

        if ch.isdigit() or (ch == "." and i + 1 < len(source) and source[i + 1].isdigit()):
            start_i = i
            start_line, start_col = line, column
            seen_dot = False
            while i < len(source):
                c = source[i]
                if c.isdigit():
                    i += 1
                    continue
                if c == "." and not seen_dot and i + 1 < len(source) and source[i + 1].isdigit():
                    seen_dot = True
                    i += 1
                    continue
                break
            text = source[start_i:i]
            advance(text)
            value = float(text) if "." in text else int(text)
            tokens.append(Token("NUMBER", value, start_line, start_col))
            continue

        two = source[i:i + 2]
        multi = {"<=": "LE", ">=": "GE", "!=": "NE", "//": "FLOORDIV"}
        if two in multi:
            tokens.append(Token(multi[two], two, line, column))
            advance(two)
            i += 2
            continue

        single = {
            "+": "PLUS",
            "-": "MINUS",
            "*": "STAR",
            "/": "SLASH",
            "%": "PERCENT",
            "(": "LPAREN",
            ")": "RPAREN",
            "[": "LBRACKET",
            "]": "RBRACKET",
            "{": "LBRACE",
            "}": "RBRACE",
            ",": "COMMA",
            ":": "COLON",
            "<": "LT",
            ">": "GT",
            ".": "DOT",
            "。": "DOT",
        }
        if ch in single:
            tokens.append(Token(single[ch], ch, line, column))
            advance(ch)
            i += 1
            continue

        if ch.isalpha() or ch == "_":
            start_i = i
            start_line, start_col = line, column
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1
            text = source[start_i:i]
            advance(text)
            tokens.append(Token("WORD", text, start_line, start_col))
            continue

        raise KisiteError(f"{line}:{column}: unexpected character {ch!r}")

    tokens.append(Token("EOF", None, line, column))
    return tokens


@dataclass(frozen=True)
class Literal:
    value: object


@dataclass(frozen=True)
class ArrayLiteral:
    items: tuple[object, ...]


@dataclass(frozen=True)
class SetLiteral:
    items: tuple[object, ...]


@dataclass(frozen=True)
class DictLiteral:
    items: tuple[tuple[object, object], ...]


@dataclass(frozen=True)
class Variable:
    name: str


@dataclass(frozen=True)
class Index:
    value: object
    index: object


@dataclass(frozen=True)
class Unary:
    op: str
    value: object


@dataclass(frozen=True)
class Binary:
    op: str
    left: object
    right: object


@dataclass(frozen=True)
class Call:
    name: str
    arguments: tuple[object, ...]


@dataclass(frozen=True)
class Say:
    value: object
    separator: object | None = None


@dataclass(frozen=True)
class Initialize:
    name: str
    value: object
    annotation: str | None = None


@dataclass(frozen=True)
class SetValue:
    target: object
    value: object


@dataclass(frozen=True)
class ReadFrom:
    names: tuple[str, ...]
    stream: str


@dataclass(frozen=True)
class AppendValue:
    value: object
    target: object


@dataclass(frozen=True)
class DeleteValue:
    target: object


@dataclass(frozen=True)
class BreakLoop:
    pass


@dataclass(frozen=True)
class ContinueLoop:
    pass


@dataclass(frozen=True)
class Block:
    statements: tuple[object, ...]


@dataclass(frozen=True)
class Conditional:
    condition: object
    body: Block
    otherwise: Block | Conditional | None = None


@dataclass(frozen=True)
class RepeatWhile:
    condition: object
    body: Block


@dataclass(frozen=True)
class RepeatEach:
    name: str
    iterable: object
    body: Block


@dataclass(frozen=True)
class FunctionDefinition:
    name: str
    parameters: tuple[str, ...]
    body: Block


@dataclass(frozen=True)
class ReturnValue:
    value: object


@dataclass(frozen=True)
class CallStatement:
    call: Call


RESERVED_WORDS = {
    "takute", "sonome", "kemese", "polike", "pilike", "putike",
    "kinise", "kinate", "kisite", "kalivisku", "musope", "jasepe",
    "minika", "kipala", "pilika", "paline", "japonavi", "ponavi",
    "sum", "abs", "takuta", "kineska", "tuna", "tuni", "jatuni",
    "kix", "kate", "palusta", "japalusta", "kasta", "vista", "kas",
    "tas", "pas", "sis", "vis", "vos", "stdin",
}

BUILTIN_FUNCTIONS = {
    "minika", "kipala", "pilika", "paline", "japonavi", "ponavi", "sum", "abs",
}
TYPE_NAMES = {"minika", "takuta", "kineska", "tuna"}
