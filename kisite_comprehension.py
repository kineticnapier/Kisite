from __future__ import annotations

from dataclasses import dataclass

import kisite_parser as _parser
import kisite_runtime as _runtime


@dataclass(frozen=True)
class ArrayComprehension:
    value: object
    names: tuple[str, ...]
    iterable: object
    condition: object | None = None


def _install() -> None:
    if getattr(_parser.Parser, "_kisite_array_comprehension_installed", False):
        return

    original_primary = _parser.Parser.primary
    original_evaluate = _runtime.evaluate

    def primary_with_array_comprehension(self):
        if self.current.kind != "LBRACKET":
            return original_primary(self)

        self.take("LBRACKET")
        if self.match("RBRACKET"):
            return _parser.ArrayLiteral(())

        first = self.expression()
        if self.current_word_is("pilike"):
            self.take_word("pilike")
            self.take_word("kas")
            names = [self.variable_name()]
            while self.current_word_is("kasta"):
                self.pos += 1
                names.append(self.variable_name())
            if len(set(names)) != len(names):
                raise _parser.KisiteError("array comprehension has duplicate binding names")

            self.take_word("pas")
            iterable = self.expression()
            condition = None
            if self.current_word_is("palusta"):
                self.pos += 1
                condition = self.expression()
            if self.current_word_is("pilike"):
                token = self.current
                raise _parser.KisiteError(
                    f"{token.line}:{token.column}: multiple comprehension generators are not supported yet"
                )
            self.take("RBRACKET")
            return ArrayComprehension(first, tuple(names), iterable, condition)

        items = [first]
        while self.match("COMMA"):
            if self.current.kind == "RBRACKET":
                break
            items.append(self.expression())
        self.take("RBRACKET")
        return _parser.ArrayLiteral(tuple(items))

    def evaluate_with_array_comprehension(node, env, runtime):
        if not isinstance(node, ArrayComprehension):
            return original_evaluate(node, env, runtime)

        iterable = _runtime.evaluate(node.iterable, env, runtime)
        if isinstance(iterable, _runtime.KisiteDict):
            items = iterable.keys()
        elif isinstance(
            iterable,
            (list, str, range, _runtime.KisiteSet, _runtime.KisiteCombinations),
        ):
            items = iterable
        else:
            raise _runtime.KisiteError(
                "array comprehension requires a collection or pilika range"
            )

        local_env = _runtime.Environment(dict(env.values), dict(env.types))
        result: list[object] = []
        for item in items:
            if len(node.names) == 1:
                values = [item]
            else:
                values = _runtime.destructure_values(item, len(node.names))

            for name, value in zip(node.names, values):
                local_env.types.pop(name, None)
                local_env.values[name] = value

            if node.condition is not None:
                condition = _runtime.evaluate(node.condition, local_env, runtime)
                if not isinstance(condition, bool):
                    raise _runtime.KisiteError(
                        "array comprehension palusta condition must be boolean"
                    )
                if not condition:
                    continue

            result.append(_runtime.evaluate(node.value, local_env, runtime))
        return result

    _parser.Parser.primary = primary_with_array_comprehension
    _parser.Parser._kisite_array_comprehension_installed = True
    _runtime.evaluate = evaluate_with_array_comprehension


_install()
