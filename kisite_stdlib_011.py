from __future__ import annotations

import argparse
import heapq
import math
import sys
from copy import deepcopy
from pathlib import Path

import kisite_parser as _parser
import kisite_runtime as _runtime
import kisite_syntax as _syntax
import kisite_values as _values


VERSION = "0.1.1"
_NEW_BUILTINS = {
    "flush",
    "pi", "sin", "cos", "tan", "sqrt", "atan2", "hypot", "floor", "ceil",
    "heapify", "heappush", "heappop", "heappeek",
    "bisectleft", "bisectright",
}


for _module in (_syntax, _parser, _values, _runtime):
    _module.VERSION = VERSION
_syntax.RESERVED_WORDS.update(_NEW_BUILTINS)
_syntax.BUILTIN_FUNCTIONS.update(_NEW_BUILTINS)


_original_invoke_function = _runtime.invoke_function
_original_execute_statement = _runtime.execute_statement


def _require_numeric(name: str, value: object) -> int | float:
    if not _runtime.is_number(value):
        raise _runtime.KisiteError(f"{name} requires a number")
    return value


def _heap_value_supported(value: object) -> bool:
    if _runtime.is_number(value):
        return True
    if isinstance(value, list):
        return all(_heap_value_supported(item) for item in value)
    return False


def _require_heap(name: str, value: object) -> list[object]:
    if not isinstance(value, list):
        raise _runtime.KisiteError(f"{name} requires an array heap")
    if any(not _heap_value_supported(item) for item in value):
        raise _runtime.KisiteError(f"{name} heap values must be numbers or nested numeric arrays")
    return value


def _bisect(array: object, value: object, *, right: bool) -> int:
    if not isinstance(array, list):
        raise _runtime.KisiteError("bisect requires a sorted array")
    low = 0
    high = len(array)
    while low < high:
        mid = (low + high) // 2
        try:
            comparison = _runtime.compare_orderable(array[mid], value)
        except _runtime.KisiteError as exc:
            raise _runtime.KisiteError("bisect requires comparable numbers or arrays") from exc
        if comparison < 0 or (right and comparison == 0):
            low = mid + 1
        else:
            high = mid
    return low


def invoke_function_011(
    name: str,
    argument_nodes: tuple[object, ...],
    env: _runtime.Environment,
    runtime: _runtime.Runtime,
    *,
    require_value: bool,
) -> object:
    lowered = name.lower()
    if lowered not in _NEW_BUILTINS:
        return _original_invoke_function(
            name, argument_nodes, env, runtime, require_value=require_value
        )

    arguments = [_runtime.evaluate(argument, env, runtime) for argument in argument_nodes]

    if lowered == "flush":
        _runtime._require_argument_count("flush", arguments, 0)
        if require_value:
            raise _runtime.KisiteError("function 'flush' does not return a value")
        stream = getattr(runtime, "output_stream", None)
        if stream is not None:
            stream.flush()
        return None

    if lowered == "pi":
        _runtime._require_argument_count("pi", arguments, 0)
        return math.pi

    if lowered in {"sin", "cos", "tan", "sqrt", "floor", "ceil"}:
        _runtime._require_argument_count(lowered, arguments, 1)
        value = _require_numeric(lowered, arguments[0])
        function = {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "floor": math.floor,
            "ceil": math.ceil,
        }[lowered]
        try:
            return function(value)
        except (ValueError, OverflowError) as exc:
            raise _runtime.KisiteError(f"{lowered} domain error") from exc

    if lowered in {"atan2", "hypot"}:
        _runtime._require_argument_count(lowered, arguments, 2)
        left = _require_numeric(lowered, arguments[0])
        right = _require_numeric(lowered, arguments[1])
        function = math.atan2 if lowered == "atan2" else math.hypot
        return function(left, right)

    if lowered == "heapify":
        _runtime._require_argument_count("heapify", arguments, 1)
        source = _require_heap("heapify", arguments[0])
        result = deepcopy(source)
        heapq.heapify(result)
        return result

    if lowered == "heappush":
        _runtime._require_argument_count("heappush", arguments, 2)
        if require_value:
            raise _runtime.KisiteError("function 'heappush' does not return a value")
        heap = _require_heap("heappush", arguments[0])
        value = arguments[1]
        if not _heap_value_supported(value):
            raise _runtime.KisiteError("heappush value must be a number or nested numeric array")
        heapq.heappush(heap, deepcopy(value))
        return None

    if lowered == "heappop":
        _runtime._require_argument_count("heappop", arguments, 1)
        heap = _require_heap("heappop", arguments[0])
        if not heap:
            raise _runtime.KisiteError("heappop cannot pop an empty heap")
        return heapq.heappop(heap)

    if lowered == "heappeek":
        _runtime._require_argument_count("heappeek", arguments, 1)
        heap = _require_heap("heappeek", arguments[0])
        if not heap:
            raise _runtime.KisiteError("heappeek cannot read an empty heap")
        return heap[0]

    if lowered in {"bisectleft", "bisectright"}:
        _runtime._require_argument_count(lowered, arguments, 2)
        return _bisect(arguments[0], arguments[1], right=lowered == "bisectright")

    raise _runtime.KisiteError(f"unknown builtin function '{name}'")


def execute_statement_011(
    statement: object,
    env: _runtime.Environment,
    runtime: _runtime.Runtime,
    *,
    in_function: bool = False,
    loop_depth: int = 0,
) -> None:
    if not isinstance(statement, _runtime.Say):
        return _original_execute_statement(
            statement,
            env,
            runtime,
            in_function=in_function,
            loop_depth=loop_depth,
        )

    value = _runtime.evaluate(statement.value, env, runtime)
    if statement.separator is None:
        line = _runtime.display(value)
    else:
        separator = _runtime.evaluate(statement.separator, env, runtime)
        if not isinstance(separator, str):
            raise _runtime.KisiteError("takute separator must be a string")
        line = separator.join(
            _runtime.display(item) for item in _runtime.output_items(value)
        )
    runtime.output.append(line)
    stream = getattr(runtime, "output_stream", None)
    if stream is not None:
        print(line, file=stream)


def run_011(
    source: str,
    input_data: str | None = "",
    *,
    base_dir: str | Path | None = None,
    output_stream: object | None = None,
) -> list[str]:
    parser = _runtime.Parser(_runtime.tokenize(source))
    output: list[str] = []
    env = _runtime.Environment.empty()
    runtime = _runtime.Runtime(
        output=output,
        input_reader=_runtime.InputReader(input_data),
        functions={},
        file_readers={},
        base_dir=Path.cwd() if base_dir is None else Path(base_dir),
    )
    runtime.output_stream = output_stream
    for statement in parser.parse():
        _runtime.execute_statement(statement, env, runtime)
    return output


def main_011(argv: list[str] | None = None) -> int:
    argp = argparse.ArgumentParser(prog="kisite")
    argp.add_argument("--version", action="version", version=f"Kisite {VERSION}")
    argp.add_argument("source", type=Path)
    args = argp.parse_args(argv)
    try:
        source = args.source.read_text(encoding="utf-8")
        run_011(
            source,
            input_data=None,
            base_dir=args.source.parent,
            output_stream=sys.stdout,
        )
        return 0
    except (OSError, _runtime.KisiteError) as exc:
        print(f"kisite: {exc}", file=sys.stderr)
        return 1


_runtime.invoke_function = invoke_function_011
_runtime.execute_statement = execute_statement_011
_runtime.run = run_011
_runtime.main = main_011
