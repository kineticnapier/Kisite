from kisite_syntax import *

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
            raise KisiteError(f"{token.line}:{token.column}: expected {kind}, got {token.kind}")
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
            raise KisiteError(f"{token.line}:{token.column}: expected '{expected}', got '{token.value}'")
        return token

    def current_word_is(self, value: str) -> bool:
        return self.current.kind == "WORD" and str(self.current.value).lower() == value

    def variable_name(self) -> str:
        token = self.take("WORD")
        name = str(token.value)
        if name.lower() in RESERVED_WORDS:
            raise KisiteError(f"{token.line}:{token.column}: '{name}' is reserved and cannot be a variable name")
        return name

    def function_name(self, allow_builtin: bool = False) -> str:
        token = self.take("WORD")
        name = str(token.value)
        lowered = name.lower()
        if allow_builtin and lowered in BUILTIN_FUNCTIONS:
            return lowered
        if lowered in RESERVED_WORDS:
            raise KisiteError(f"{token.line}:{token.column}: '{name}' is reserved and cannot be a function name")
        return name

    def type_name(self) -> str:
        token = self.take("WORD")
        name = str(token.value).lower()
        if name not in TYPE_NAMES:
            raise KisiteError(f"{token.line}:{token.column}: unsupported type '{token.value}'")
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
            raise KisiteError(f"{token.line}:{token.column}: japalusta must follow a palusta block")

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
        otherwise: Block | Conditional | None = None
        if self.current_word_is("japalusta"):
            self.pos += 1
            if self.current_word_is("palusta"):
                otherwise = self.conditional_statement()
            else:
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
        raise KisiteError(f"{token.line}:{token.column}: pilike must be followed by 'palusta' or 'kas'")

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
            raise KisiteError(f"{token.line}:{token.column}: {owner} must be followed by a block")
        return self.block()

    def block(self) -> Block:
        opening = self.take("LBRACE")
        statements: list[object] = []
        while self.current.kind != "RBRACE":
            if self.current.kind == "EOF":
                raise KisiteError(f"{opening.line}:{opening.column}: unterminated block")
            statements.append(self.statement())
        self.take("RBRACE")
        return Block(tuple(statements))

    def simple_statement(self) -> object:
        verb = self.take("WORD")
        verb_name = str(verb.value).lower()

        if verb_name == "takute":
            self.take_word("kas")
            value = self.expression()
            separator = None
            if self.current_word_is("vis"):
                self.pos += 1
                separator = self.expression()
            return Say(value, separator)

        if verb_name == "sonome":
            self.take_word("kas")
            name = self.variable_name()
            annotation = None
            if self.current_word_is("sis"):
                self.pos += 1
                annotation = self.type_name()
            self.take_word("tas")
            return Initialize(name, self.expression(), annotation)

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
            if self.current_word_is("stdin"):
                self.pos += 1
                stream = "stdin"
            elif self.current.kind == "STRING":
                stream = str(self.take("STRING").value)
            else:
                token = self.current
                raise KisiteError(f"{token.line}:{token.column}: polike stream must be stdin or a string path")
            return ReadFrom(tuple(names), stream)

        if verb_name == "putike":
            self.take_word("kas")
            value = self.expression()
            self.take_word("tas")
            target = self.assignment_target()
            return AppendValue(value, target)

        if verb_name == "kinise":
            if self.current_word_is("kas"):
                self.pos += 1
                target = self.assignment_target()
                return DeleteValue(target)
            return BreakLoop()

        if verb_name == "kinate":
            return ContinueLoop()

        if verb_name == "jasepe":
            self.take_word("kas")
            return ReturnValue(self.expression())

        raise KisiteError(f"{verb.line}:{verb.column}: unsupported statement '{verb.value}'")

    def assignment_target(self) -> object:
        node: object = Variable(self.variable_name())
        while self.match("LBRACKET"):
            index = self.expression()
            self.take("RBRACKET")
            node = Index(node, index)
        return node

    def expression(self, *, allow_kasta: bool = True) -> object:
        return self.logical_or(allow_kasta=allow_kasta)

    def logical_or(self, *, allow_kasta: bool) -> object:
        node = self.logical_and(allow_kasta=allow_kasta)
        while self.current_word_is("vista"):
            self.pos += 1
            node = Binary("OR", node, self.logical_and(allow_kasta=allow_kasta))
        return node

    def logical_and(self, *, allow_kasta: bool) -> object:
        node = self.comparison()
        if allow_kasta:
            while self.current_word_is("kasta"):
                self.pos += 1
                node = Binary("AND", node, self.comparison())
        return node

    def comparison(self) -> object:
        node = self.additive()
        while True:
            if self.current_word_is("kate"):
                self.pos += 1
                op = "KATE"
            elif self.current_word_is("pas"):
                self.pos += 1
                op = "IN"
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
        while self.current.kind in ("STAR", "SLASH", "FLOORDIV", "PERCENT"):
            op = self.current.kind
            self.pos += 1
            node = Binary(op, node, self.unary())
        return node

    def unary(self) -> object:
        if self.match("MINUS"):
            return Unary("MINUS", self.unary())
        if self.match("PLUS"):
            return Unary("PLUS", self.unary())
        if self.current_word_is("kix"):
            self.pos += 1
            return Unary("NOT", self.unary())
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
        if self.current_word_is("tuni"):
            self.pos += 1
            return Literal(True)
        if self.current_word_is("jatuni"):
            self.pos += 1
            return Literal(False)
        if self.match("NUMBER"):
            return Literal(token.value)
        if self.match("STRING"):
            return Literal(token.value)
        if self.match("WORD"):
            name = str(token.value)
            if name.lower() in RESERVED_WORDS:
                raise KisiteError(f"{token.line}:{token.column}: expected a value, got reserved word '{name}'")
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
        if self.match("LBRACE"):
            if self.match("RBRACE"):
                return SetLiteral(())
            if self.match("COLON"):
                self.take("RBRACE")
                return DictLiteral(())
            first = self.expression()
            if self.match("COLON"):
                entries: list[tuple[object, object]] = [(first, self.expression())]
                while self.match("COMMA"):
                    if self.current.kind == "RBRACE":
                        break
                    key = self.expression()
                    self.take("COLON")
                    entries.append((key, self.expression()))
                self.take("RBRACE")
                return DictLiteral(tuple(entries))
            items = [first]
            while self.match("COMMA"):
                if self.current.kind == "RBRACE":
                    break
                items.append(self.expression())
            self.take("RBRACE")
            return SetLiteral(tuple(items))
        raise KisiteError(
            f"{token.line}:{token.column}: expected a value, collection, variable, function call, or parenthesized expression"
        )

    def call_expression(self) -> Call:
        self.take_word("kisite")
        self.take_word("kas")
        name = self.function_name(allow_builtin=True)
        arguments: list[object] = []
        if self.current_word_is("vis"):
            self.pos += 1
            arguments.append(self.expression(allow_kasta=False))
            while self.current_word_is("kasta"):
                self.pos += 1
                arguments.append(self.expression(allow_kasta=False))
        return Call(name, tuple(arguments))
