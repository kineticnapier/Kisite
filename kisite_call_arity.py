from __future__ import annotations

import kisite_parser as _parser


# Exact-arity builtins can terminate a nested call before the surrounding
# call's `kasta` separator. Variable-arity builtins intentionally keep the
# legacy greedy behavior because their boundary is genuinely ambiguous.
_EXACT_BUILTIN_ARITIES = {
    "minika": 1,
    "kipala": 1,
    "sum": 1,
    "abs": 1,
    "fill": 2,
    "reverse": 1,
    "truncate": 2,
    "combinations": 2,
    "set": 1,
    "array": 1,
    "readint": 0,
    "readints": 1,
    "modint": 2,
    "modpow": 3,
    "modinv": 2,
    "flush": 0,
    "pi": 0,
    "sin": 1,
    "cos": 1,
    "tan": 1,
    "sqrt": 1,
    "floor": 1,
    "ceil": 1,
    "atan2": 2,
    "hypot": 2,
    "heapify": 1,
    "heappush": 2,
    "heappop": 1,
    "heappeek": 1,
    "bisectleft": 2,
    "bisectright": 2,
}


_original_init = _parser.Parser.__init__


def _scan_function_arities(tokens: list[object]) -> dict[str, int]:
    arities: dict[str, int] = {}
    i = 0
    limit = len(tokens)

    def word_at(index: int, value: str) -> bool:
        if index >= limit:
            return False
        token = tokens[index]
        return token.kind == "WORD" and str(token.value).lower() == value

    while i + 3 < limit:
        if not (
            word_at(i, "kalivisku")
            and word_at(i + 1, "musope")
            and word_at(i + 2, "kas")
            and tokens[i + 3].kind == "WORD"
        ):
            i += 1
            continue

        name = str(tokens[i + 3].value)
        j = i + 4
        count = 0
        if word_at(j, "vis"):
            j += 1
            if j < limit and tokens[j].kind == "WORD":
                count = 1
                j += 1
                while word_at(j, "kasta"):
                    j += 1
                    if j >= limit or tokens[j].kind != "WORD":
                        break
                    count += 1
                    j += 1
        arities[name] = count
        i = j
    return arities


def _init_with_arities(self, tokens):
    _original_init(self, tokens)
    self._kisite_function_arities = _scan_function_arities(tokens)
    self._kisite_call_argument_depth = 0


def _parse_call_argument(self):
    self._kisite_call_argument_depth += 1
    try:
        return self.expression(allow_kasta=False)
    finally:
        self._kisite_call_argument_depth -= 1


def _known_exact_arity(self, name: str) -> int | None:
    lowered = name.lower()
    if lowered in _EXACT_BUILTIN_ARITIES:
        return _EXACT_BUILTIN_ARITIES[lowered]
    return self._kisite_function_arities.get(name)


def _call_expression_with_nested_boundaries(self):
    self.take_word("kisite")
    self.take_word("kas")
    name = self.function_name(allow_builtin=True)
    arguments: list[object] = []

    if not self.current_word_is("vis"):
        return _parser.Call(name, tuple(arguments))

    self.pos += 1
    nested = self._kisite_call_argument_depth > 0
    exact_arity = _known_exact_arity(self, name) if nested else None

    if exact_arity == 0:
        # Preserve the old behavior for an invalid explicit argument so the
        # runtime can still report the function arity error normally.
        arguments.append(_parse_call_argument(self))
        while self.current_word_is("kasta"):
            self.pos += 1
            arguments.append(_parse_call_argument(self))
        return _parser.Call(name, tuple(arguments))

    arguments.append(_parse_call_argument(self))

    if exact_arity is not None:
        while len(arguments) < exact_arity and self.current_word_is("kasta"):
            self.pos += 1
            arguments.append(_parse_call_argument(self))
        return _parser.Call(name, tuple(arguments))

    while self.current_word_is("kasta"):
        self.pos += 1
        arguments.append(_parse_call_argument(self))
    return _parser.Call(name, tuple(arguments))


_parser.Parser.__init__ = _init_with_arities
_parser.Parser.call_expression = _call_expression_with_nested_boundaries
