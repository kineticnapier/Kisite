from __future__ import annotations

from pathlib import Path
import argparse

from kisite_values import *

def invoke_function(
    name: str,
    argument_nodes: tuple[object, ...],
    env: Environment,
    runtime: Runtime,
    *,
    require_value: bool,
) -> object:
    arguments = [evaluate(argument, env, runtime) for argument in argument_nodes]
    lowered = name.lower()

    if lowered == "minika":
        if len(arguments) != 1:
            raise KisiteError(f"function 'minika' expects 1 argument, got {len(arguments)}")
        return convert_minika(arguments[0])

    if lowered == "kipala":
        if len(arguments) != 1:
            raise KisiteError(f"function 'kipala' expects 1 argument, got {len(arguments)}")
        value = arguments[0]
        if not isinstance(value, (list, str, range, KisiteSet, KisiteDict)):
            raise KisiteError("kipala requires an array, string, set, dictionary, or pilika range")
        return len(value)

    if lowered == "pilika":
        return make_pilika(arguments)

    if lowered == "paline":
        return make_paline(arguments)

    if lowered in ("japonavi", "ponavi"):
        return choose_extreme(lowered, arguments)

    if lowered == "sum":
        if len(arguments) != 1:
            raise KisiteError(f"function 'sum' expects 1 argument, got {len(arguments)}")
        values = sequence_values(arguments[0], name="sum")
        if any(not is_number(value) for value in values):
            raise KisiteError("sum requires numeric values")
        return sum(values)

    if lowered == "abs":
        if len(arguments) != 1:
            raise KisiteError(f"function 'abs' expects 1 argument, got {len(arguments)}")
        if not is_number(arguments[0]):
            raise KisiteError("abs requires a number")
        return abs(arguments[0])

    if name not in runtime.functions:
        raise KisiteError(f"function '{name}' is not defined")
    function = runtime.functions[name]
    if len(arguments) != len(function.parameters):
        raise KisiteError(f"function '{name}' expects {len(function.parameters)} arguments, got {len(arguments)}")
    local_env = Environment(dict(zip(function.parameters, arguments)), {})
    try:
        execute_statement(function.body, local_env, runtime, in_function=True, loop_depth=0)
    except FunctionReturn as returned:
        return returned.value
    if require_value:
        raise KisiteError(f"function '{name}' did not return a value")
    return None


def collection_contains(container: object, value: object) -> bool:
    if isinstance(container, list):
        return any(values_equal(value, item) for item in container)
    if isinstance(container, str):
        if not isinstance(value, str):
            raise KisiteError("string membership requires a string on the left")
        return value in container
    if isinstance(container, range):
        return is_integer(value) and value in container
    if isinstance(container, KisiteSet):
        return container.contains(value)
    if isinstance(container, KisiteDict):
        return container.contains(value)
    raise KisiteError("pas membership requires an array, string, range, set, or dictionary")


def evaluate(node: object, env: Environment, runtime: Runtime) -> object:
    if isinstance(node, Literal):
        return node.value
    if isinstance(node, ArrayLiteral):
        return [evaluate(item, env, runtime) for item in node.items]
    if isinstance(node, SetLiteral):
        return KisiteSet([evaluate(item, env, runtime) for item in node.items])
    if isinstance(node, DictLiteral):
        result = KisiteDict()
        for key_node, value_node in node.items:
            result.set(evaluate(key_node, env, runtime), evaluate(value_node, env, runtime))
        return result
    if isinstance(node, Variable):
        if node.name not in env.values:
            raise KisiteError(f"variable '{node.name}' is not initialized")
        return env.values[node.name]
    if isinstance(node, Index):
        value = evaluate(node.value, env, runtime)
        index = evaluate(node.index, env, runtime)
        if isinstance(value, KisiteDict):
            return value.get(index)
        value, index = checked_index(value, index)
        return value[index]
    if isinstance(node, Call):
        return invoke_function(node.name, node.arguments, env, runtime, require_value=True)
    if isinstance(node, Unary):
        value = evaluate(node.value, env, runtime)
        if node.op == "NOT":
            if not isinstance(value, bool):
                raise KisiteError("kix requires a boolean")
            return not value
        if not is_number(value):
            raise KisiteError("unary arithmetic requires a number")
        return +value if node.op == "PLUS" else -value
    if isinstance(node, Binary):
        if node.op == "AND":
            left = evaluate(node.left, env, runtime)
            if not isinstance(left, bool):
                raise KisiteError("kasta logical operands must be boolean")
            if not left:
                return False
            right = evaluate(node.right, env, runtime)
            if not isinstance(right, bool):
                raise KisiteError("kasta logical operands must be boolean")
            return right
        if node.op == "OR":
            left = evaluate(node.left, env, runtime)
            if not isinstance(left, bool):
                raise KisiteError("vista logical operands must be boolean")
            if left:
                return True
            right = evaluate(node.right, env, runtime)
            if not isinstance(right, bool):
                raise KisiteError("vista logical operands must be boolean")
            return right

        left = evaluate(node.left, env, runtime)
        right = evaluate(node.right, env, runtime)
        if node.op == "KATE":
            return values_equal(left, right)
        if node.op == "NE":
            return not values_equal(left, right)
        if node.op == "IN":
            return collection_contains(right, left)
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
        if node.op in ("FLOORDIV", "PERCENT"):
            if not is_integer(left) or not is_integer(right):
                raise KisiteError("// and % require integer operands")
            if right == 0:
                if node.op == "FLOORDIV":
                    raise KisiteError("integer division by zero")
                raise KisiteError("remainder by zero")
            return left // right if node.op == "FLOORDIV" else left % right
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


def assign(target: object, value: object, env: Environment, runtime: Runtime) -> None:
    if isinstance(target, Variable):
        env.set(target.name, value)
        return
    if isinstance(target, Index):
        container = evaluate(target.value, env, runtime)
        index = evaluate(target.index, env, runtime)
        if isinstance(container, KisiteDict):
            container.set(index, value)
            return
        if not isinstance(index, int) or isinstance(index, bool):
            raise KisiteError("array index must be an integer")
        if not isinstance(container, list):
            raise KisiteError("indexed assignment requires an array or dictionary")
        if index < 0 or index >= len(container):
            raise KisiteError("index out of range")
        container[index] = value
        return
    raise KisiteError("invalid assignment target")


def append_value(target: object, value: object, env: Environment, runtime: Runtime) -> None:
    container = evaluate(target, env, runtime)
    if isinstance(container, list):
        container.append(value)
        return
    if isinstance(container, KisiteSet):
        container.add(value)
        return
    raise KisiteError("putike target must be an array or set")


def delete_value(target: object, env: Environment, runtime: Runtime) -> None:
    if not isinstance(target, Index):
        raise KisiteError("kinise kas requires an indexed array element, set member, or dictionary key")
    container = evaluate(target.value, env, runtime)
    index = evaluate(target.index, env, runtime)
    if isinstance(container, KisiteSet):
        container.remove(index)
        return
    if isinstance(container, KisiteDict):
        container.delete(index)
        return
    if not isinstance(index, int) or isinstance(index, bool):
        raise KisiteError("array index must be an integer")
    if not isinstance(container, list):
        raise KisiteError("kinise kas target must be an array element, set member, or dictionary key")
    if index < 0 or index >= len(container):
        raise KisiteError("index out of range")
    del container[index]


def display(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, range):
        return str(list(value))
    if isinstance(value, list):
        return str(value)
    if isinstance(value, KisiteSet):
        return "{" + ", ".join(display(item) for item in value) + "}"
    if isinstance(value, KisiteDict):
        return "{" + ", ".join(f"{display(key)}: {display(item)}" for key, item in value.entries()) + "}"
    return str(value)


def output_items(value: object) -> list[object]:
    if isinstance(value, (list, range, KisiteSet)):
        return list(value)
    if isinstance(value, KisiteDict):
        return value.keys()
    raise KisiteError("takute with vis requires an array, range, set, or dictionary")


def execute_statement(
    statement: object,
    env: Environment,
    runtime: Runtime,
    *,
    in_function: bool = False,
    loop_depth: int = 0,
) -> None:
    if isinstance(statement, Say):
        value = evaluate(statement.value, env, runtime)
        if statement.separator is None:
            runtime.output.append(display(value))
        else:
            separator = evaluate(statement.separator, env, runtime)
            if not isinstance(separator, str):
                raise KisiteError("takute separator must be a string")
            runtime.output.append(separator.join(display(item) for item in output_items(value)))
        return
    if isinstance(statement, Initialize):
        value = evaluate(statement.value, env, runtime)
        env.initialize(statement.name, value, statement.annotation)
        return
    if isinstance(statement, SetValue):
        assign(statement.target, evaluate(statement.value, env, runtime), env, runtime)
        return
    if isinstance(statement, ReadFrom):
        reader = runtime.reader_for(statement.stream)
        values = [reader.read() for _ in statement.names]
        for name, value in zip(statement.names, values):
            env.set(name, value, allow_create=True)
        return
    if isinstance(statement, AppendValue):
        append_value(statement.target, evaluate(statement.value, env, runtime), env, runtime)
        return
    if isinstance(statement, DeleteValue):
        delete_value(statement.target, env, runtime)
        return
    if isinstance(statement, BreakLoop):
        if loop_depth <= 0:
            raise KisiteError("kinise without kas can only be used inside a loop")
        raise LoopBreak()
    if isinstance(statement, ContinueLoop):
        if loop_depth <= 0:
            raise KisiteError("kinate can only be used inside a loop")
        raise LoopContinue()
    if isinstance(statement, Block):
        for child in statement.statements:
            execute_statement(child, env, runtime, in_function=in_function, loop_depth=loop_depth)
        return
    if isinstance(statement, Conditional):
        condition = evaluate(statement.condition, env, runtime)
        if not isinstance(condition, bool):
            raise KisiteError("palusta condition must be boolean")
        if condition:
            execute_statement(statement.body, env, runtime, in_function=in_function, loop_depth=loop_depth)
        elif statement.otherwise is not None:
            execute_statement(statement.otherwise, env, runtime, in_function=in_function, loop_depth=loop_depth)
        return
    if isinstance(statement, RepeatWhile):
        while True:
            condition = evaluate(statement.condition, env, runtime)
            if not isinstance(condition, bool):
                raise KisiteError("pilike palusta condition must be boolean")
            if not condition:
                break
            try:
                execute_statement(statement.body, env, runtime, in_function=in_function, loop_depth=loop_depth + 1)
            except LoopContinue:
                continue
            except LoopBreak:
                break
        return
    if isinstance(statement, RepeatEach):
        iterable = evaluate(statement.iterable, env, runtime)
        if isinstance(iterable, KisiteDict):
            items = iterable.keys()
        elif isinstance(iterable, (list, str, range, KisiteSet)):
            items = iterable
        else:
            raise KisiteError("pilike foreach requires an array or string, range, set, or dictionary")
        for item in items:
            env.set(statement.name, item, allow_create=True)
            try:
                execute_statement(statement.body, env, runtime, in_function=in_function, loop_depth=loop_depth + 1)
            except LoopContinue:
                continue
            except LoopBreak:
                break
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
        raise FunctionReturn(evaluate(statement.value, env, runtime))
    if isinstance(statement, CallStatement):
        invoke_function(statement.call.name, statement.call.arguments, env, runtime, require_value=False)
        return
    raise KisiteError(f"unknown statement {type(statement).__name__}")


def run(source: str, input_data: str | None = "", *, base_dir: str | Path | None = None) -> list[str]:
    parser = Parser(tokenize(source))
    output: list[str] = []
    env = Environment.empty()
    runtime = Runtime(
        output=output,
        input_reader=InputReader(input_data),
        functions={},
        file_readers={},
        base_dir=Path.cwd() if base_dir is None else Path(base_dir),
    )
    for statement in parser.parse():
        execute_statement(statement, env, runtime)
    return output


def main(argv: list[str] | None = None) -> int:
    argp = argparse.ArgumentParser(prog="kisite")
    argp.add_argument("--version", action="version", version=f"Kisite {VERSION}")
    argp.add_argument("source", type=Path)
    args = argp.parse_args(argv)
    try:
        source = args.source.read_text(encoding="utf-8")
        for line in run(source, input_data=None, base_dir=args.source.parent):
            print(line)
        return 0
    except (OSError, KisiteError) as exc:
        print(f"kisite: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
