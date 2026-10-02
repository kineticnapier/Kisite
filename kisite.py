from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import sys


VERSION = "0.0.12"


class KisiteError(Exception):
    pass


class FunctionReturn(Exception):
    def __init__(self, value: object) -> None:
        super().__init__()
        self.value = value


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
        multi = {"<=": "LE", ">=": "GE", "!=": "NE"}
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
            "(": "LPAREN",
            ")": "RPAREN",
            "[": "LBRACKET",
            "]": "RBRACKET",
            "{": "LBRACE",
            "}": "RBRACE",
            ",": "COMMA",
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


@dataclass(frozen=True)
class Initialize:
    name: str
    value: object


@dataclass(frozen=True)
class SetValue:
    target: object
    value: object


@dataclass(frozen=True)
class ReadFrom:
    names: tuple[str, ...]
    stream: str


@dataclass(frozen=True)
class Block:
    statements: tuple[object, ...]


@dataclass(frozen=True)
class Conditional:
    condition: object
    body: Block
    otherwise: Block | None = None


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
    "takute",
    "sonome",
    "kemese",
    "polike",
    "pilike",
    "kisite",
    "kalivisku",
    "musope",
    "jasepe",
    "minika",
    "kate",
    "palusta",
    "japalusta",
    "kasta",
    "kas",
    "tas",
    "pas",
    "vis",
    "vos",
    "stdin",
}


BUILTIN_FUNCTIONS = {"minika"}


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

    def variable_name(self) -> str:
        token = self.take("WORD")
        name = str(token.value)
        if name.lower() in RESERVED_WORDS:
            raise KisiteError(
                f"{token.line}:{token.column}: '{name}' is reserved and cannot be a variable name"
            )
        return name

    def function_name(self, allow_builtin: bool = False) -> str:
        token = self.take("WORD")
        name = str(token.value)
        lowered = name.lower()
        if allow_builtin and lowered in BUILTIN_FUNCTIONS:
            return lowered
        if lowered in RESERVED_WORDS:
            raise KisiteError(
                f"{token.line}:{token.column}: '{name}' is reserved and cannot be a function name"
            )
        return name

    def parse(self) -> list[object]:
        statements: list[object] = []
        while self.current.kind != "EOF":
            statements.append(self.statement())
        return statements

    def statement(self) -> object:
        if self.current_word_is("palusta"):
            return self.conditional_statement()

        if self.current_word_is("pilike"):
            return self.loop_statement()

        if self.current_word_is("kalivisku"):
            return self.function_definition()

        if self.current_word_is("kisite"):
            call = self.call_expression()
            self.match("DOT")
            return CallStatement(call)

        if self.current_word_is("japalusta"):
            token = self.current
            raise KisiteError(
                f"{token.line}:{token.column}: japalusta must follow a palusta block"
            )

        if self.current.kind == "LBRACE":
            body: object = self.block()
        else:
            body = self.simple_statement()

        if self.current_word_is("palusta"):
            token = self.current
            raise KisiteError(
                f"{token.line}:{token.column}: postfix palusta syntax was removed in Kisite 0.0.9; "
                "use 'palusta <condition> { ... }'"
            )

        self.match("DOT")
        return body

    def conditional_statement(self) -> Conditional:
        self.take_word("palusta")
        condition = self.expression()
        body = self.required_block("palusta condition")

        otherwise = None
        if self.current_word_is("japalusta"):
            self.pos += 1
            otherwise = self.required_block("japalusta")

        self.match("DOT")
        return Conditional(condition, body, otherwise)

    def loop_statement(self) -> object:
        self.take_word("pilike")

        if self.current_word_is("palusta"):
            self.pos += 1
            condition = self.expression()
            body = self.required_block("pilike palusta condition")
            self.match("DOT")
            return RepeatWhile(condition, body)

        if self.current_word_is("kas"):
            self.pos += 1
            name = self.variable_name()
            self.take_word("pas")
            iterable = self.expression()
            body = self.required_block("pilike foreach expression")
            self.match("DOT")
            return RepeatEach(name, iterable, body)

        token = self.current
        raise KisiteError(
            f"{token.line}:{token.column}: pilike must be followed by 'palusta' or 'kas'"
        )

    def function_definition(self) -> FunctionDefinition:
        self.take_word("kalivisku")
        self.take_word("musope")
        self.take_word("kas")
        name = self.function_name()
        parameters: list[str] = []
        if self.current_word_is("vis"):
            self.pos += 1
            parameters.append(self.variable_name())
            while self.current_word_is("kasta"):
                self.pos += 1
                parameters.append(self.variable_name())

        if len(set(parameters)) != len(parameters):
            raise KisiteError(f"function '{name}' has duplicate parameter names")

        body = self.required_block("function definition")
        self.match("DOT")
        return FunctionDefinition(name, tuple(parameters), body)

    def required_block(self, owner: str) -> Block:
        if self.current.kind != "LBRACE":
            token = self.current
            raise KisiteError(
                f"{token.line}:{token.column}: {owner} must be followed by a block"
            )
        return self.block()

    def block(self) -> Block:
        opening = self.take("LBRACE")
        statements: list[object] = []
        while self.current.kind != "RBRACE":
            if self.current.kind == "EOF":
                raise KisiteError(
                    f"{opening.line}:{opening.column}: unterminated block"
                )
            statements.append(self.statement())
        self.take("RBRACE")
        return Block(tuple(statements))

    def simple_statement(self) -> object:
        verb = self.take("WORD")
        verb_name = str(verb.value).lower()

        if verb_name == "takute":
            self.take_word("kas")
            return Say(self.expression())

        if verb_name == "sonome":
            self.take_word("kas")
            name = self.variable_name()
            self.take_word("tas")
            return Initialize(name, self.expression())

        if verb_name == "kemese":
            self.take_word("kas")
            target = self.assignment_target()
            self.take_word("tas")
            return SetValue(target, self.expression())

        if verb_name == "polike":
            self.take_word("kas")
            names = [self.variable_name()]
            while self.current_word_is("kasta"):
                self.pos += 1
                names.append(self.variable_name())
            self.take_word("vos")
            stream = str(self.take("WORD").value).lower()
            if stream != "stdin":
                raise KisiteError(
                    f"unsupported stream '{stream}'; Kisite 0.0.12 supports only stdin"
                )
            return ReadFrom(tuple(names), stream)

        if verb_name == "jasepe":
            self.take_word("kas")
            return ReturnValue(self.expression())

        raise KisiteError(
            f"{verb.line}:{verb.column}: unsupported statement '{verb.value}'"
        )

    def assignment_target(self) -> object:
        node: object = Variable(self.variable_name())
        while self.match("LBRACKET"):
            index = self.expression()
            self.take("RBRACKET")
            node = Index(node, index)
        return node

    def expression(self) -> object:
        node = self.additive()
        while True:
            if self.current_word_is("kate"):
                self.pos += 1
                op = "KATE"
            elif self.current.kind in ("LT", "GT", "LE", "GE", "NE"):
                op = self.current.kind
                self.pos += 1
            else:
                break
            node = Binary(op, node, self.additive())
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
        return self.postfix()

    def postfix(self) -> object:
        node = self.primary()
        while self.match("LBRACKET"):
            index = self.expression()
            self.take("RBRACKET")
            node = Index(node, index)
        return node

    def primary(self) -> object:
        token = self.current
        if self.current_word_is("kisite"):
            return self.call_expression()
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
        if self.match("LBRACKET"):
            items: list[object] = []
            if self.current.kind != "RBRACKET":
                while True:
                    items.append(self.expression())
                    if not self.match("COMMA"):
                        break
                    if self.current.kind == "RBRACKET":
                        break
            self.take("RBRACKET")
            return ArrayLiteral(tuple(items))
        raise KisiteError(
            f"{token.line}:{token.column}: expected a number, string, array, variable, function call, or parenthesized expression"
        )

    def call_expression(self) -> Call:
        self.take_word("kisite")
        self.take_word("kas")
        name = self.function_name(allow_builtin=True)
        arguments: list[object] = []
        if self.current_word_is("vis"):
            self.pos += 1
            arguments.append(self.expression())
            while self.current_word_is("kasta"):
                self.pos += 1
                arguments.append(self.expression())
        return Call(name, tuple(arguments))


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def values_equal(left: object, right: object) -> bool:
    if is_number(left) and is_number(right):
        return left == right
    return type(left) is type(right) and left == right


def checked_index(value: object, index: object) -> tuple[object, int]:
    if not isinstance(index, int) or isinstance(index, bool):
        raise KisiteError("array index must be an integer")
    if not isinstance(value, (list, str)):
        raise KisiteError("indexing requires an array or string")
    if index < 0 or index >= len(value):
        raise KisiteError("index out of range")
    return value, index


class InputReader:
    def __init__(self, data: str | None = None) -> None:
        self.tokens = data.split() if data is not None else []
        self.index = 0
        self.live = data is None

    def read(self) -> str:
        while self.index >= len(self.tokens):
            if not self.live:
                raise KisiteError("stdin is exhausted")
            line = sys.stdin.readline()
            if line == "":
                raise KisiteError("stdin is exhausted")
            self.tokens.extend(line.split())

        text = self.tokens[self.index]
        self.index += 1
        return text


@dataclass
class Runtime:
    output: list[str]
    input_reader: InputReader
    functions: dict[str, FunctionDefinition]


def convert_minika(value: object) -> object:
    if is_number(value):
        return value
    if not isinstance(value, str):
        raise KisiteError("minika requires a string or number")
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError as exc:
            raise KisiteError(f"minika cannot convert {value!r} to a number") from exc


def invoke_function(
    name: str,
    argument_nodes: tuple[object, ...],
    variables: dict[str, object],
    runtime: Runtime,
    *,
    require_value: bool,
) -> object:
    arguments = [evaluate(argument, variables, runtime) for argument in argument_nodes]

    if name.lower() == "minika":
        if len(arguments) != 1:
            raise KisiteError(
                f"function 'minika' expects 1 argument, got {len(arguments)}"
            )
        return convert_minika(arguments[0])

    if name not in runtime.functions:
        raise KisiteError(f"function '{name}' is not defined")

    function = runtime.functions[name]
    if len(arguments) != len(function.parameters):
        raise KisiteError(
            f"function '{name}' expects {len(function.parameters)} arguments, got {len(arguments)}"
        )

    local_variables = dict(zip(function.parameters, arguments))
    try:
        execute_statement(
            function.body,
            local_variables,
            runtime,
            in_function=True,
        )
    except FunctionReturn as returned:
        return returned.value

    if require_value:
        raise KisiteError(f"function '{name}' did not return a value")
    return None


def evaluate(node: object, variables: dict[str, object], runtime: Runtime) -> object:
    if isinstance(node, Literal):
        return node.value

    if isinstance(node, ArrayLiteral):
        return [evaluate(item, variables, runtime) for item in node.items]

    if isinstance(node, Variable):
        if node.name not in variables:
            raise KisiteError(f"variable '{node.name}' is not initialized")
        return variables[node.name]

    if isinstance(node, Index):
        value = evaluate(node.value, variables, runtime)
        index = evaluate(node.index, variables, runtime)
        value, index = checked_index(value, index)
        return value[index]

    if isinstance(node, Call):
        return invoke_function(
            node.name,
            node.arguments,
            variables,
            runtime,
            require_value=True,
        )

    if isinstance(node, Unary):
        value = evaluate(node.value, variables, runtime)
        if not is_number(value):
            raise KisiteError("unary arithmetic requires a number")
        return +value if node.op == "PLUS" else -value

    if isinstance(node, Binary):
        left = evaluate(node.left, variables, runtime)
        right = evaluate(node.right, variables, runtime)

        if node.op == "KATE":
            return values_equal(left, right)
        if node.op == "NE":
            return not values_equal(left, right)

        if node.op in ("LT", "GT", "LE", "GE"):
            if not is_number(left) or not is_number(right):
                raise KisiteError("ordering comparison requires numbers")
            if node.op == "LT":
                return left < right
            if node.op == "GT":
                return left > right
            if node.op == "LE":
                return left <= right
            return left >= right

        if not is_number(left) or not is_number(right):
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


def assign(
    target: object,
    value: object,
    variables: dict[str, object],
    runtime: Runtime,
) -> None:
    if isinstance(target, Variable):
        if target.name not in variables:
            raise KisiteError(f"variable '{target.name}' is not initialized")
        variables[target.name] = value
        return

    if isinstance(target, Index):
        container = evaluate(target.value, variables, runtime)
        index = evaluate(target.index, variables, runtime)
        if not isinstance(index, int) or isinstance(index, bool):
            raise KisiteError("array index must be an integer")
        if not isinstance(container, list):
            raise KisiteError("indexed assignment requires an array")
        if index < 0 or index >= len(container):
            raise KisiteError("index out of range")
        container[index] = value
        return

    raise KisiteError("invalid assignment target")


def display(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def execute_statement(
    statement: object,
    variables: dict[str, object],
    runtime: Runtime,
    *,
    in_function: bool = False,
) -> None:
    if isinstance(statement, Say):
        runtime.output.append(display(evaluate(statement.value, variables, runtime)))
        return

    if isinstance(statement, Initialize):
        if statement.name in variables:
            raise KisiteError(
                f"variable '{statement.name}' is already initialized"
            )
        variables[statement.name] = evaluate(statement.value, variables, runtime)
        return

    if isinstance(statement, SetValue):
        assign(
            statement.target,
            evaluate(statement.value, variables, runtime),
            variables,
            runtime,
        )
        return

    if isinstance(statement, ReadFrom):
        values = [runtime.input_reader.read() for _ in statement.names]
        for name, value in zip(statement.names, values):
            variables[name] = value
        return

    if isinstance(statement, Block):
        for child in statement.statements:
            execute_statement(
                child,
                variables,
                runtime,
                in_function=in_function,
            )
        return

    if isinstance(statement, Conditional):
        condition = evaluate(statement.condition, variables, runtime)
        if not isinstance(condition, bool):
            raise KisiteError("palusta condition must be boolean")
        if condition:
            execute_statement(
                statement.body,
                variables,
                runtime,
                in_function=in_function,
            )
        elif statement.otherwise is not None:
            execute_statement(
                statement.otherwise,
                variables,
                runtime,
                in_function=in_function,
            )
        return

    if isinstance(statement, RepeatWhile):
        while True:
            condition = evaluate(statement.condition, variables, runtime)
            if not isinstance(condition, bool):
                raise KisiteError("pilike palusta condition must be boolean")
            if not condition:
                break
            execute_statement(
                statement.body,
                variables,
                runtime,
                in_function=in_function,
            )
        return

    if isinstance(statement, RepeatEach):
        iterable = evaluate(statement.iterable, variables, runtime)
        if not isinstance(iterable, (list, str)):
            raise KisiteError("pilike foreach requires an array or string")
        for item in iterable:
            variables[statement.name] = item
            execute_statement(
                statement.body,
                variables,
                runtime,
                in_function=in_function,
            )
        return

    if isinstance(statement, FunctionDefinition):
        if statement.name.lower() in BUILTIN_FUNCTIONS:
            raise KisiteError(f"cannot redefine builtin function '{statement.name}'")
        if statement.name in runtime.functions:
            raise KisiteError(f"function '{statement.name}' is already defined")
        runtime.functions[statement.name] = statement
        return

    if isinstance(statement, ReturnValue):
        if not in_function:
            raise KisiteError("jasepe can only be used inside a function")
        raise FunctionReturn(evaluate(statement.value, variables, runtime))

    if isinstance(statement, CallStatement):
        invoke_function(
            statement.call.name,
            statement.call.arguments,
            variables,
            runtime,
            require_value=False,
        )
        return

    raise KisiteError(f"unknown statement {type(statement).__name__}")


def run(source: str, input_data: str | None = "") -> list[str]:
    parser = Parser(tokenize(source))
    output: list[str] = []
    variables: dict[str, object] = {}
    runtime = Runtime(output, InputReader(input_data), {})

    for statement in parser.parse():
        execute_statement(statement, variables, runtime)

    return output


def main(argv: list[str] | None = None) -> int:
    argp = argparse.ArgumentParser(prog="kisite")
    argp.add_argument("--version", action="version", version=f"Kisite {VERSION}")
    argp.add_argument("source", type=Path)
    args = argp.parse_args(argv)

    try:
        source = args.source.read_text(encoding="utf-8")
        for line in run(source, input_data=None):
            print(line)
        return 0
    except (OSError, KisiteError) as exc:
        print(f"kisite: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
