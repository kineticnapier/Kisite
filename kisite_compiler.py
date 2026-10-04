from __future__ import annotations

import ast
import bisect
import heapq
import math
from copy import deepcopy
from pathlib import Path

import kisite_parser as _parser
import kisite_runtime as _runtime
import kisite_syntax as _syntax
import kisite_values as _values


class CompiledBackendUnsupported(_syntax.KisiteError):
    pass


def _python_name(prefix: str, name: str) -> str:
    # Kisite accepts identifiers that may be Python keywords. Encode every code
    # point so the generated Python namespace is collision-free and always valid.
    return prefix + "".join(f"{ord(ch):x}_" for ch in name)


def _variable_name(name: str) -> str:
    return _python_name("_kv_", name)


def _function_name(name: str) -> str:
    return _python_name("_kf_", name)


_BINARY_OPERATORS: dict[str, ast.operator] = {
    "PLUS": ast.Add(),
    "MINUS": ast.Sub(),
    "STAR": ast.Mult(),
    "SLASH": ast.Div(),
    "FLOORDIV": ast.FloorDiv(),
    "PERCENT": ast.Mod(),
    "BITAND": ast.BitAnd(),
    "BITOR": ast.BitOr(),
    "BITXOR": ast.BitXor(),
    "LSHIFT": ast.LShift(),
    "RSHIFT": ast.RShift(),
}

_COMPARE_OPERATORS: dict[str, ast.cmpop] = {
    "KATE": ast.Eq(),
    "NE": ast.NotEq(),
    "LT": ast.Lt(),
    "GT": ast.Gt(),
    "LE": ast.LtE(),
    "GE": ast.GtE(),
    "IN": ast.In(),
}

_AUGMENT_OPERATORS = _BINARY_OPERATORS

_FAST_BUILTINS = {
    "readint": "_kc_readint",
    "readints": "_kc_readints",
    "fill": "_kc_fill",
    "pilika": "_kc_pilika",
    "kipala": "_kc_len",
}


class PythonAstCompiler:
    """Translate the performance-critical Kisite subset to Python AST.

    The interpreter remains the reference backend. This backend intentionally
    starts conservative: unsupported statement forms fail before execution
    rather than silently falling back inside hot loops.
    """

    def compile(self, statements: list[object]) -> object:
        body: list[ast.stmt] = []
        for statement in statements:
            body.extend(self.statement(statement))
        module = ast.Module(body=body, type_ignores=[])
        ast.fix_missing_locations(module)
        return compile(module, "<kisite-compiled>", "exec")

    def expression(self, node: object) -> ast.expr:
        if isinstance(node, _syntax.Literal):
            return ast.Constant(node.value)
        if isinstance(node, _syntax.ArrayLiteral):
            return ast.List([self.expression(item) for item in node.items], ast.Load())
        if isinstance(node, _syntax.SetLiteral):
            return self.helper_call("_kc_set_literal", [ast.List([self.expression(item) for item in node.items], ast.Load())])
        if isinstance(node, _syntax.DictLiteral):
            pairs = [
                ast.Tuple([self.expression(key), self.expression(value)], ast.Load())
                for key, value in node.items
            ]
            return self.helper_call("_kc_dict_literal", [ast.List(pairs, ast.Load())])
        if isinstance(node, _syntax.Variable):
            return ast.Name(_variable_name(node.name), ast.Load())
        if isinstance(node, _syntax.Index):
            return ast.Subscript(self.expression(node.value), self.expression(node.index), ast.Load())
        if isinstance(node, _syntax.Slice):
            return ast.Subscript(
                self.expression(node.value),
                ast.Slice(
                    lower=self.expression(node.start) if node.start is not None else None,
                    upper=self.expression(node.stop) if node.stop is not None else None,
                    step=self.expression(node.step) if node.step is not None else None,
                ),
                ast.Load(),
            )
        if isinstance(node, _syntax.Unary):
            operand = self.expression(node.value)
            operators: dict[str, ast.unaryop] = {
                "NOT": ast.Not(),
                "BITNOT": ast.Invert(),
                "PLUS": ast.UAdd(),
                "MINUS": ast.USub(),
            }
            if node.op not in operators:
                raise CompiledBackendUnsupported(f"compiled backend does not support unary operator {node.op}")
            return ast.UnaryOp(operators[node.op], operand)
        if isinstance(node, _syntax.Binary):
            if node.op in _BINARY_OPERATORS:
                return ast.BinOp(self.expression(node.left), _BINARY_OPERATORS[node.op], self.expression(node.right))
            if node.op in _COMPARE_OPERATORS:
                return ast.Compare(
                    self.expression(node.left),
                    [_COMPARE_OPERATORS[node.op]],
                    [self.expression(node.right)],
                )
            if node.op == "AND":
                return ast.BoolOp(ast.And(), [self.expression(node.left), self.expression(node.right)])
            if node.op == "OR":
                return ast.BoolOp(ast.Or(), [self.expression(node.left), self.expression(node.right)])
            raise CompiledBackendUnsupported(f"compiled backend does not support binary operator {node.op}")
        if isinstance(node, _syntax.Call):
            arguments = [self.expression(argument) for argument in node.arguments]
            lowered = node.name.lower()
            if lowered in _syntax.BUILTIN_FUNCTIONS:
                helper = _FAST_BUILTINS.get(lowered)
                if helper is not None:
                    return self.helper_call(helper, arguments)
                return self.helper_call("_kc_builtin", [ast.Constant(lowered), *arguments])
            return ast.Call(ast.Name(_function_name(node.name), ast.Load()), arguments, [])

        # ArrayComprehension is installed as a parser extension rather than a
        # core syntax node, so avoid importing it until the extension exists.
        try:
            from kisite_comprehension import ArrayComprehension
        except ImportError:
            ArrayComprehension = ()  # type: ignore[assignment]
        if isinstance(node, ArrayComprehension):
            target: ast.expr
            if len(node.names) == 1:
                target = ast.Name(_variable_name(node.names[0]), ast.Store())
            else:
                target = ast.Tuple(
                    [ast.Name(_variable_name(name), ast.Store()) for name in node.names],
                    ast.Store(),
                )
            generator = ast.comprehension(
                target=target,
                iter=self.expression(node.iterable),
                ifs=[self.expression(node.condition)] if node.condition is not None else [],
                is_async=0,
            )
            return ast.ListComp(self.expression(node.value), [generator])

        raise CompiledBackendUnsupported(
            f"compiled backend does not support expression {type(node).__name__}"
        )

    def assignment_target(self, node: object) -> ast.expr:
        if isinstance(node, _syntax.Variable):
            return ast.Name(_variable_name(node.name), ast.Store())
        if isinstance(node, _syntax.Index):
            return ast.Subscript(self.expression(node.value), self.expression(node.index), ast.Store())
        raise CompiledBackendUnsupported(
            f"compiled backend does not support assignment target {type(node).__name__}"
        )

    def statement(self, statement: object) -> list[ast.stmt]:
        if isinstance(statement, _syntax.Say):
            separator = self.expression(statement.separator) if statement.separator is not None else ast.Constant(None)
            return [ast.Expr(self.helper_call("_kc_say", [self.expression(statement.value), separator]))]

        if isinstance(statement, _syntax.Initialize):
            if statement.annotation is not None:
                raise CompiledBackendUnsupported("compiled backend does not support typed initialization yet")
            value = self.expression(statement.value)
            if len(statement.names) == 1:
                target: ast.expr = ast.Name(_variable_name(statement.names[0]), ast.Store())
            else:
                target = ast.Tuple(
                    [ast.Name(_variable_name(name), ast.Store()) for name in statement.names],
                    ast.Store(),
                )
            return [ast.Assign([target], value)]

        if isinstance(statement, _syntax.SetValue):
            return [ast.Assign([self.assignment_target(statement.target)], self.expression(statement.value))]

        if isinstance(statement, _syntax.AugmentValue):
            if statement.op not in _AUGMENT_OPERATORS:
                raise CompiledBackendUnsupported(
                    f"compiled backend does not support augmented operator {statement.op}"
                )
            return [
                ast.AugAssign(
                    self.assignment_target(statement.target),
                    _AUGMENT_OPERATORS[statement.op],
                    self.expression(statement.value),
                )
            ]

        if isinstance(statement, _syntax.ReadFrom):
            result: list[ast.stmt] = []
            for name in statement.names:
                result.append(
                    ast.Assign(
                        [ast.Name(_variable_name(name), ast.Store())],
                        self.helper_call("_kc_read_from", [ast.Constant(statement.stream)]),
                    )
                )
            return result

        if isinstance(statement, _syntax.AppendValue):
            return [
                ast.Expr(
                    self.helper_call(
                        "_kc_append",
                        [self.expression(statement.target), self.expression(statement.value)],
                    )
                )
            ]

        if isinstance(statement, _syntax.DeleteValue):
            if not isinstance(statement.target, _syntax.Index):
                raise CompiledBackendUnsupported("compiled delete requires an indexed target")
            return [
                ast.Expr(
                    self.helper_call(
                        "_kc_delete",
                        [self.expression(statement.target.value), self.expression(statement.target.index)],
                    )
                )
            ]

        if isinstance(statement, _syntax.BreakLoop):
            return [ast.Break()]
        if isinstance(statement, _syntax.ContinueLoop):
            return [ast.Continue()]
        if isinstance(statement, _syntax.Block):
            result: list[ast.stmt] = []
            for child in statement.statements:
                result.extend(self.statement(child))
            return result
        if isinstance(statement, _syntax.Conditional):
            body = self.statement(statement.body)
            otherwise = self.statement(statement.otherwise) if statement.otherwise is not None else []
            return [ast.If(self.expression(statement.condition), body, otherwise)]
        if isinstance(statement, _syntax.RepeatWhile):
            return [ast.While(self.expression(statement.condition), self.statement(statement.body), [])]
        if isinstance(statement, _syntax.RepeatEach):
            if len(statement.names) == 1:
                target: ast.expr = ast.Name(_variable_name(statement.names[0]), ast.Store())
            else:
                target = ast.Tuple(
                    [ast.Name(_variable_name(name), ast.Store()) for name in statement.names],
                    ast.Store(),
                )
            return [ast.For(target, self.expression(statement.iterable), self.statement(statement.body), [])]
        if isinstance(statement, _syntax.FunctionDefinition):
            arguments = ast.arguments(
                posonlyargs=[],
                args=[ast.arg(_variable_name(name)) for name in statement.parameters],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            )
            return [
                ast.FunctionDef(
                    name=_function_name(statement.name),
                    args=arguments,
                    body=self.statement(statement.body) or [ast.Pass()],
                    decorator_list=[],
                )
            ]
        if isinstance(statement, _syntax.ReturnValue):
            return [ast.Return(self.expression(statement.value))]
        if isinstance(statement, _syntax.CallStatement):
            return [ast.Expr(self.expression(statement.call))]

        raise CompiledBackendUnsupported(
            f"compiled backend does not support statement {type(statement).__name__}"
        )

    @staticmethod
    def helper_call(name: str, arguments: list[ast.expr]) -> ast.Call:
        return ast.Call(ast.Name(name, ast.Load()), arguments, [])


def _compiled_namespace(runtime: _runtime.Runtime) -> dict[str, object]:
    def argc(name: str, arguments: tuple[object, ...], minimum: int, maximum: int | None = None) -> None:
        _runtime._require_argument_count(name, list(arguments), minimum, maximum)

    def readint() -> int:
        return _values.convert_int_text(runtime.input_reader.read())

    def readints(count: object) -> list[int]:
        if not _values.is_integer(count) or count < 0:
            raise _syntax.KisiteError("readints count must be a non-negative integer")
        return [_values.convert_int_text(runtime.input_reader.read()) for _ in range(count)]

    def say(value: object, separator: object | None) -> None:
        if separator is None:
            line = _runtime.display(value)
        else:
            if not isinstance(separator, str):
                raise _syntax.KisiteError("takute separator must be a string")
            line = separator.join(_runtime.display(item) for item in _runtime.output_items(value))
        runtime.output.append(line)
        stream = getattr(runtime, "output_stream", None)
        if stream is not None:
            print(line, file=stream)

    def read_from(stream: str) -> str:
        return runtime.reader_for(stream).read()

    def set_literal(items: list[object]) -> _values.KisiteSet:
        return _values.KisiteSet(items)

    def dict_literal(items: list[tuple[object, object]]) -> _values.KisiteDict:
        result = _values.KisiteDict()
        for key, value in items:
            result.set(key, value)
        return result

    def append_value(container: object, value: object) -> None:
        if isinstance(container, list):
            container.append(value)
            return
        if isinstance(container, _values.KisiteSet):
            container.add(value)
            return
        raise _syntax.KisiteError("putike target must be an array or set")

    def delete_value(container: object, index: object) -> None:
        if isinstance(container, _values.KisiteSet):
            container.remove(index)
            return
        if isinstance(container, _values.KisiteDict):
            container.delete(index)
            return
        if not _values.is_integer(index) or not isinstance(container, list):
            raise _syntax.KisiteError("kinise kas target must be an array element, set member, or dictionary key")
        if index < 0:
            index += len(container)
        if index < 0 or index >= len(container):
            raise _syntax.KisiteError("index out of range")
        del container[index]

    def builtin(name: str, *arguments: object) -> object:
        if name == "minika":
            argc(name, arguments, 1)
            return _values.convert_minika(arguments[0])
        if name == "paline":
            return _values.make_paline(list(arguments))
        if name in {"japonavi", "ponavi"}:
            return _values.choose_extreme(name, list(arguments))
        if name == "sum":
            argc(name, arguments, 1)
            values = _values.sequence_values(arguments[0], name="sum")
            total: object = 0
            for value in values:
                total = _runtime.apply_binary_values("PLUS", total, value)
            return total
        if name == "abs":
            argc(name, arguments, 1)
            if not _values.is_number(arguments[0]):
                raise _syntax.KisiteError("abs requires a number")
            return abs(arguments[0])
        if name == "reverse":
            argc(name, arguments, 1)
            return _values.make_reverse(arguments[0])
        if name == "resize":
            argc(name, arguments, 2, 3)
            return _values.make_resize(arguments[0], arguments[1], 0 if len(arguments) == 2 else arguments[2])
        if name == "truncate":
            argc(name, arguments, 2)
            return _values.make_truncate(arguments[0], arguments[1])
        if name == "combinations":
            argc(name, arguments, 2)
            return _values.KisiteCombinations(arguments[0], arguments[1])
        if name in {"gcd", "lcm"}:
            if len(arguments) < 2 or any(not _values.is_integer(value) for value in arguments):
                raise _syntax.KisiteError(f"{name} requires at least two integer arguments")
            fn = math.gcd if name == "gcd" else math.lcm
            result = arguments[0]
            for value in arguments[1:]:
                result = fn(result, value)
            return result
        if name == "set":
            argc(name, arguments, 1)
            return _values.make_set(arguments[0])
        if name == "array":
            argc(name, arguments, 1)
            return _values.make_array(arguments[0])
        if name == "modint":
            argc(name, arguments, 2)
            return _values.KisiteModInt(arguments[0], arguments[1])
        if name == "modpow":
            argc(name, arguments, 3)
            return _values.modular_pow(arguments[0], arguments[1], arguments[2])
        if name == "modinv":
            argc(name, arguments, 2)
            return _values.modular_inverse(arguments[0], arguments[1])
        if name == "convolution":
            argc(name, arguments, 2, 3)
            left, left_mod = _values.normalize_convolution_array(arguments[0], "left argument")
            right, right_mod = _values.normalize_convolution_array(arguments[1], "right argument")
            if left_mod is not None and right_mod is not None and left_mod != right_mod:
                raise _syntax.KisiteError("convolution modint arrays must use the same modulus")
            inferred = left_mod if left_mod is not None else right_mod
            if len(arguments) == 3:
                modulus = arguments[2]
                if not _values.is_integer(modulus) or modulus <= 1:
                    raise _syntax.KisiteError("convolution modulus must be an integer greater than 1")
                return _values.convolution_mod(left, right, modulus)
            if inferred is not None:
                return [_values.KisiteModInt(value, inferred) for value in _values.convolution_mod(left, right, inferred)]
            return _values.convolution_exact(left, right)
        if name == "flush":
            argc(name, arguments, 0)
            stream = getattr(runtime, "output_stream", None)
            if stream is not None:
                stream.flush()
            return None
        if name == "pi":
            argc(name, arguments, 0)
            return math.pi
        if name in {"sin", "cos", "tan", "sqrt", "floor", "ceil"}:
            argc(name, arguments, 1)
            if not _values.is_number(arguments[0]):
                raise _syntax.KisiteError(f"{name} requires a number")
            return getattr(math, name)(arguments[0])
        if name in {"atan2", "hypot"}:
            argc(name, arguments, 2)
            if any(not _values.is_number(value) for value in arguments):
                raise _syntax.KisiteError(f"{name} requires numbers")
            return getattr(math, name)(arguments[0], arguments[1])
        if name == "heapify":
            argc(name, arguments, 1)
            if not isinstance(arguments[0], list):
                raise _syntax.KisiteError("heapify requires an array heap")
            result = deepcopy(arguments[0])
            heapq.heapify(result)
            return result
        if name == "heappush":
            argc(name, arguments, 2)
            if not isinstance(arguments[0], list):
                raise _syntax.KisiteError("heappush requires an array heap")
            heapq.heappush(arguments[0], deepcopy(arguments[1]))
            return None
        if name == "heappop":
            argc(name, arguments, 1)
            if not isinstance(arguments[0], list) or not arguments[0]:
                raise _syntax.KisiteError("heappop cannot pop an empty heap")
            return heapq.heappop(arguments[0])
        if name == "heappeek":
            argc(name, arguments, 1)
            if not isinstance(arguments[0], list) or not arguments[0]:
                raise _syntax.KisiteError("heappeek cannot read an empty heap")
            return arguments[0][0]
        if name in {"bisectleft", "bisectright"}:
            argc(name, arguments, 2)
            if not isinstance(arguments[0], list):
                raise _syntax.KisiteError("bisect requires a sorted array")
            fn = bisect.bisect_left if name == "bisectleft" else bisect.bisect_right
            return fn(arguments[0], arguments[1])
        raise CompiledBackendUnsupported(f"compiled backend does not support builtin function '{name}'")

    return {
        "__builtins__": {},
        "_kc_readint": readint,
        "_kc_readints": readints,
        "_kc_fill": _values.make_fill,
        "_kc_pilika": lambda *args: _values.make_pilika(list(args)),
        "_kc_len": len,
        "_kc_say": say,
        "_kc_read_from": read_from,
        "_kc_set_literal": set_literal,
        "_kc_dict_literal": dict_literal,
        "_kc_append": append_value,
        "_kc_delete": delete_value,
        "_kc_builtin": builtin,
    }


def run_compiled(
    source: str,
    input_data: str | None = "",
    *,
    base_dir: str | Path | None = None,
    output_stream: object | None = None,
) -> list[str]:
    parser = _parser.Parser(_syntax.tokenize(source))
    statements = parser.parse()
    code = PythonAstCompiler().compile(statements)

    output: list[str] = []
    runtime = _runtime.Runtime(
        output=output,
        input_reader=_runtime.InputReader(input_data),
        functions={},
        file_readers={},
        base_dir=Path.cwd() if base_dir is None else Path(base_dir),
    )
    runtime.output_stream = output_stream
    namespace = _compiled_namespace(runtime)
    try:
        exec(code, namespace, namespace)
    except _syntax.KisiteError:
        raise
    except (ArithmeticError, IndexError, KeyError, TypeError, ValueError) as exc:
        raise _syntax.KisiteError(f"compiled runtime error: {exc}") from exc
    return output
