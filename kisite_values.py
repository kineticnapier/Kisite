from __future__ import annotations

from functools import cmp_to_key
from pathlib import Path
import sys

from kisite_parser import *

def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def collection_key(value: object) -> tuple[str, object]:
    if isinstance(value, bool):
        return ("bool", value)
    if is_number(value):
        return ("number", value)
    if isinstance(value, str):
        return ("string", value)
    raise KisiteError("set elements and dictionary keys must be numbers, strings, or booleans")


class KisiteSet:
    def __init__(self, values: list[object] | None = None) -> None:
        self._items: dict[tuple[str, object], object] = {}
        for value in values or []:
            self.add(value)

    def add(self, value: object) -> None:
        self._items[collection_key(value)] = value

    def remove(self, value: object) -> None:
        key = collection_key(value)
        if key not in self._items:
            raise KisiteError("set element does not exist")
        del self._items[key]

    def contains(self, value: object) -> bool:
        return collection_key(value) in self._items

    def values(self) -> list[object]:
        return list(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items.values())


class KisiteDict:
    def __init__(self) -> None:
        self._items: dict[tuple[str, object], tuple[object, object]] = {}

    def set(self, key: object, value: object) -> None:
        self._items[collection_key(key)] = (key, value)

    def get(self, key: object) -> object:
        normalized = collection_key(key)
        if normalized not in self._items:
            raise KisiteError("dictionary key does not exist")
        return self._items[normalized][1]

    def delete(self, key: object) -> None:
        normalized = collection_key(key)
        if normalized not in self._items:
            raise KisiteError("dictionary key does not exist")
        del self._items[normalized]

    def contains(self, key: object) -> bool:
        return collection_key(key) in self._items

    def keys(self) -> list[object]:
        return [key for key, _ in self._items.values()]

    def entries(self) -> list[tuple[object, object]]:
        return list(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self.keys())


def values_equal(left: object, right: object) -> bool:
    if is_number(left) and is_number(right):
        return left == right
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(values_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, KisiteSet) and isinstance(right, KisiteSet):
        if len(left) != len(right):
            return False
        return all(right.contains(value) for value in left)
    if isinstance(left, KisiteDict) and isinstance(right, KisiteDict):
        if len(left) != len(right):
            return False
        for key, value in left.entries():
            if not right.contains(key) or not values_equal(value, right.get(key)):
                return False
        return True
    return type(left) is type(right) and left == right


def checked_index(value: object, index: object) -> tuple[object, int]:
    if not isinstance(index, int) or isinstance(index, bool):
        raise KisiteError("array index must be an integer")
    if not isinstance(value, (list, str)):
        raise KisiteError("indexing requires an array or string")
    if index < 0 or index >= len(value):
        raise KisiteError("index out of range")
    return value, index


def type_matches(annotation: str, value: object) -> bool:
    if annotation == "minika":
        return is_number(value)
    if annotation == "takuta":
        return isinstance(value, str)
    if annotation == "kineska":
        return isinstance(value, list)
    if annotation == "tuna":
        return isinstance(value, bool)
    raise KisiteError(f"unknown type '{annotation}'")


def require_type(annotation: str, value: object, name: str) -> None:
    if not type_matches(annotation, value):
        raise KisiteError(f"variable '{name}' requires type {annotation}, got {type(value).__name__}")


class InputReader:
    def __init__(self, data: str | None = None, *, label: str = "stdin") -> None:
        self.tokens = data.split() if data is not None else []
        self.index = 0
        self.live = data is None
        self.label = label

    def read(self) -> str:
        while self.index >= len(self.tokens):
            if not self.live:
                if self.label == "stdin":
                    raise KisiteError("stdin is exhausted")
                raise KisiteError(f"stream {self.label!r} is exhausted")
            line = sys.stdin.readline()
            if line == "":
                raise KisiteError("stdin is exhausted")
            self.tokens.extend(line.split())
        text = self.tokens[self.index]
        self.index += 1
        return text


@dataclass
class Environment:
    values: dict[str, object]
    types: dict[str, str]

    @classmethod
    def empty(cls) -> "Environment":
        return cls({}, {})

    def initialize(self, name: str, value: object, annotation: str | None = None) -> None:
        if name in self.values:
            raise KisiteError(f"variable '{name}' is already initialized")
        if annotation is not None:
            require_type(annotation, value, name)
            self.types[name] = annotation
        self.values[name] = value

    def set(self, name: str, value: object, *, allow_create: bool = False) -> None:
        if name not in self.values and not allow_create:
            raise KisiteError(f"variable '{name}' is not initialized")
        annotation = self.types.get(name)
        if annotation is not None:
            require_type(annotation, value, name)
        self.values[name] = value


@dataclass
class Runtime:
    output: list[str]
    input_reader: InputReader
    functions: dict[str, FunctionDefinition]
    file_readers: dict[str, InputReader]
    base_dir: Path

    def reader_for(self, stream: str) -> InputReader:
        if stream == "stdin":
            return self.input_reader
        path = Path(stream)
        if not path.is_absolute():
            path = self.base_dir / path
        try:
            key = str(path.resolve())
        except OSError:
            key = str(path)
        if key not in self.file_readers:
            try:
                data = path.read_text(encoding="utf-8")
            except OSError as exc:
                raise KisiteError(f"cannot open stream {stream!r}: {exc}") from exc
            self.file_readers[key] = InputReader(data, label=stream)
        return self.file_readers[key]


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


def make_pilika(arguments: list[object]) -> range:
    if not 1 <= len(arguments) <= 3:
        raise KisiteError(f"function 'pilika' expects 1 to 3 arguments, got {len(arguments)}")
    if any(not is_integer(value) for value in arguments):
        raise KisiteError("pilika arguments must be integers")
    if len(arguments) == 1:
        return range(arguments[0])
    if len(arguments) == 2:
        return range(arguments[0], arguments[1])
    if arguments[2] == 0:
        raise KisiteError("pilika step cannot be zero")
    return range(arguments[0], arguments[1], arguments[2])


def compare_orderable(left: object, right: object) -> int:
    if is_number(left) and is_number(right):
        return (left > right) - (left < right)
    if isinstance(left, list) and isinstance(right, list):
        for left_item, right_item in zip(left, right):
            comparison = compare_orderable(left_item, right_item)
            if comparison != 0:
                return comparison
        return (len(left) > len(right)) - (len(left) < len(right))
    raise KisiteError("ordering helpers require comparable numbers or arrays")


def make_paline(arguments: list[object]) -> list[object]:
    if len(arguments) != 1:
        raise KisiteError(f"function 'paline' expects 1 argument, got {len(arguments)}")
    value = arguments[0]
    if not isinstance(value, list):
        raise KisiteError("paline requires an array")
    return sorted(value, key=cmp_to_key(compare_orderable))


def choose_extreme(name: str, arguments: list[object]) -> object:
    if not arguments:
        raise KisiteError(f"function '{name}' expects at least 1 argument")
    if len(arguments) == 1:
        source = arguments[0]
        if not isinstance(source, (list, range, KisiteSet)):
            raise KisiteError(f"function '{name}' with 1 argument requires an array, set, or pilika range")
        values = list(source)
    else:
        values = arguments
    if not values:
        raise KisiteError(f"function '{name}' cannot use an empty sequence")
    key = cmp_to_key(compare_orderable)
    return min(values, key=key) if name == "japonavi" else max(values, key=key)


def sequence_values(value: object, *, name: str) -> list[object]:
    if isinstance(value, (list, range, KisiteSet)):
        return list(value)
    raise KisiteError(f"function '{name}' requires an array, set, or pilika range")
