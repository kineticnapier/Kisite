from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import sys


VERSION = "0.0.3"


class KisiteError(Exception):
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

        single = {
            "+": "PLUS",
            "-": "MINUS",
            "*": "STAR",
            "/": "SLASH",
            "(": "LPAREN",
            ")": "RPAREN",
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
class Variable:
    name: str


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
class Say:
    value: object


@dataclass(frozen=True)
class Initialize:
    name: str
    value: object


@dataclass(frozen=True)
class SetValue:
    name: str
    value: object


@dataclass(frozen=True)
class Conditional:
    condition: object
    body: object


RESERVED_WORDS = {
    "takute",
    "sonome",
    "kemese",
    "kate",
    "kuesta",
    "kas",
    "tas",
}


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def take(self, kind: str) -> Token:
        token = self.current
        if token.kind != kind:
            raise KisiteError(
                f"{token.line}:{token.column}: expected {kind}, got {token.kind}"
            )
        self.pos += 1
        return token

    def match(self, kind: str) -> bool:
        if self.current.kind == kind:
            self.pos += 1
            return True
        return False

    def take_word(self, expected: str) -> Token:
        token = self.take("WORD")
        if str(token.value).lower() != expected:
            raise KisiteError(
                f"{token.line}:{token.column}: expected '{expected}', got '{token.value}'"
            )
        return token

    def current_word_is(self, value: str) -> bool:
        return (
            self.current.kind == "WORD"
            and str(self.current.value).lower() == value
        )

    def parse(self) -> list[object]:
        statements: list[object] = []
        while self.current.kind != "EOF":
            statements.append(self.statement())
        return statements

    def statement(self) -> object:
        if self.current.kind == "WORD":
            verb_name = str(self.current.value).lower()

            if verb_name == "takute":
                self.pos += 1
                self.take_word("kas")
                value = self.expression()
                self.match("DOT")
                return Say(value)

            if verb_name in ("sonome", "kemese"):
                self.pos += 1
                self.take_word("kas")
                name_token = self.take("WORD")
                name = str(name_token.value)
                if name.lower() in RESERVED_WORDS:
                    raise KisiteError(
                        f"{name_token.line}:{name_token.column}: '{name}' is reserved and cannot be a variable name"
                    )
                self.take_word("tas")
                value = self.expression()
                self.match("DOT")
                if verb_name == "sonome":
                    return Initialize(name, value)
                return SetValue(name, value)

        # Lisatopian uses "A kuesta B" for an A-then-B / when-A-B relation.
        # Kisite uses the same shape for a single-statement conditional.
        condition = self.expression()
        self.take_word("kuesta")
        body = self.statement()
        return Conditional(condition, body)

    def expression(self) -> object:
        node = self.additive()
        while self.current_word_is("kate"):
            self.pos += 1
            node = Binary("KATE", node, self.additive())
        return node

    def additive(self) -> object:
        node = self.term()
        while self.current.kind in ("PLUS", "MINUS"):
            op = self.current.kind
            self.pos += 1
            node = Binary(op, node, self.term())
        return node

    def term(self) -> object:
        node = self.unary()
        while self.current.kind in ("STAR", "SLASH"):
            op = self.current.kind
            self.pos += 1
            node = Binary(op, node, self.unary())
        return node

    def unary(self) -> object:
        if self.match("MINUS"):
            return Unary("MINUS", self.unary())
        if self.match("PLUS"):
            return Unary("PLUS", self.unary())
        return self.primary()

    def primary(self) -> object:
        token = self.current
        if self.match("NUMBER"):
            return Literal(token.value)
        if self.match("STRING"):
            return Literal(token.value)
        if self.match("WORD"):
            name = str(token.value)
            if name.lower() in RESERVED_WORDS:
                raise KisiteError(
                    f"{token.line}:{token.column}: expected a value, got reserved word '{name}'"
                )
            return Variable(name)
        if self.match("LPAREN"):
            node = self.expression()
            self.take("RPAREN")
            return node
        raise KisiteError(
            f"{token.line}:{token.column}: expected a number, string, variable, or parenthesized expression"
        )


def evaluate(node: object, variables: dict[str, object]) -> object:
    if isinstance(node, Literal):
        return node.value

    if isinstance(node, Variable):
        if node.name not in variables:
            raise KisiteError(f"variable '{node.name}' is not initialized")
        return variables[node.name]

    if isinstance(node, Unary):
        value = evaluate(node.value, variables)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise KisiteError("unary arithmetic requires a number")
        return +value if node.op == "PLUS" else -value

    if isinstance(node, Binary):
        left = evaluate(node.left, variables)
        right = evaluate(node.right, variables)

        if node.op == "KATE":
            if (
                isinstance(left, (int, float))
                and not isinstance(left, bool)
                and isinstance(right, (int, float))
                and not isinstance(right, bool)
            ):
                return left == right
            return type(left) is type(right) and left == right

        if (
            not isinstance(left, (int, float))
            or isinstance(left, bool)
            or not isinstance(right, (int, float))
            or isinstance(right, bool)
        ):
            raise KisiteError("arithmetic requires numbers")
        if node.op == "PLUS":
            return left + right
        if node.op == "MINUS":
            return left - right
        if node.op == "STAR":
            return left * right
        if node.op == "SLASH":
            if right == 0:
                raise KisiteError("division by zero")
            return left / right

    raise KisiteError(f"cannot evaluate {type(node).__name__}")


def display(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def execute_statement(
    statement: object,
    variables: dict[str, object],
    output: list[str],
) -> None:
    if isinstance(statement, Say):
        output.append(display(evaluate(statement.value, variables)))
        return

    if isinstance(statement, Initialize):
        if statement.name in variables:
            raise KisiteError(
                f"variable '{statement.name}' is already initialized"
            )
        variables[statement.name] = evaluate(statement.value, variables)
        return

    if isinstance(statement, SetValue):
        if statement.name not in variables:
            raise KisiteError(
                f"variable '{statement.name}' is not initialized"
            )
        variables[statement.name] = evaluate(statement.value, variables)
        return

    if isinstance(statement, Conditional):
        condition = evaluate(statement.condition, variables)
        if not isinstance(condition, bool):
            raise KisiteError("kuesta condition must be boolean")
        if condition:
            execute_statement(statement.body, variables, output)
        return

    raise KisiteError(f"unknown statement {type(statement).__name__}")


def run(source: str) -> list[str]:
    parser = Parser(tokenize(source))
    output: list[str] = []
    variables: dict[str, object] = {}

    for statement in parser.parse():
        execute_statement(statement, variables, output)

    return output


def main(argv: list[str] | None = None) -> int:
    argp = argparse.ArgumentParser(prog="kisite")
    argp.add_argument("--version", action="version", version=f"Kisite {VERSION}")
    argp.add_argument("source", type=Path)
    args = argp.parse_args(argv)

    try:
        source = args.source.read_text(encoding="utf-8")
        for line in run(source):
            print(line)
        return 0
    except (OSError, KisiteError) as exc:
        print(f"kisite: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
