from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from functools import cmp_to_key
from itertools import combinations as itertools_combinations
from math import comb, gcd as math_gcd, lcm as math_lcm
from pathlib import Path
import sys

from kisite_parser import *


NTT_MOD = 998244353
NTT_ROOT = 3


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclass(frozen=True)
class KisiteModInt:
    value: int
    modulus: int

    def __post_init__(self) -> None:
        if not is_integer(self.modulus) or self.modulus <= 1:
            raise KisiteError("modint modulus must be an integer greater than 1")
        if not is_integer(self.value):
            raise KisiteError("modint value must be an integer")
        object.__setattr__(self, "value", self.value % self.modulus)


class KisiteCombinations:
    def __init__(self, source: object, r: int) -> None:
        if not is_integer(r) or r < 0:
            raise KisiteError("combinations r must be a non-negative integer")
        if isinstance(source, KisiteSet):
            pool = source.values()
        elif isinstance(source, (list, str, range)):
            pool = list(source)
        else:
            raise KisiteError("combinations requires an array, string, set, or pilika range")
        self.pool = pool
        self.r = r

    def __iter__(self):
        for values in itertools_combinations(self.pool, self.r):
            yield list(values)

    def __len__(self) -> int:
        if self.r > len(self.pool):
            return 0
        return comb(len(self.pool), self.r)


def collection_key(value: object) -> tuple[str, object]:
    if isinstance(value, bool):
        return ("bool", value)
    if is_number(value):
        return ("number", value)
    if isinstance(value, str):
        return ("string", value)
    if isinstance(value, KisiteModInt):
        return ("modint", (value.modulus, value.value))
    if isinstance(value, list):
        return ("array", tuple(collection_key(item) for item in value))
    raise KisiteError("set elements and dictionary keys must be scalar values or nested arrays of scalar values")


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
    if isinstance(left, KisiteModInt) and isinstance(right, KisiteModInt):
        return left.modulus == right.modulus and left.value == right.value
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
    if not is_integer(index):
        raise KisiteError("array index must be an integer")
    if not isinstance(value, (list, str)):
        raise KisiteError("indexing requires an array or string")
    if index < 0:
        index += len(value)
    if index < 0 or index >= len(value):
        raise KisiteError("index out of range")
    return value, index


def checked_slice_part(value: object, label: str) -> int | None:
    if value is None:
        return None
    if not is_integer(value):
        raise KisiteError(f"slice {label} must be an integer")
    return value


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


def convert_int_text(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise KisiteError(f"cannot convert input token {value!r} to an integer") from exc


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
    if isinstance(value, KisiteSet):
        value = value.values()
    if not isinstance(value, list):
        raise KisiteError("paline requires an array or set")
    return sorted(value, key=cmp_to_key(compare_orderable))


def choose_extreme(name: str, arguments: list[object]) -> object:
    if not arguments:
        raise KisiteError(f"function '{name}' expects at least 1 argument")
    if len(arguments) == 1:
        source = arguments[0]
        if not isinstance(source, (list, range, KisiteSet, KisiteCombinations)):
            raise KisiteError(f"function '{name}' with 1 argument requires an array, set, combinations, or pilika range")
        values = list(source)
    else:
        values = arguments
    if not values:
        raise KisiteError(f"function '{name}' cannot use an empty sequence")
    key = cmp_to_key(compare_orderable)
    return min(values, key=key) if name == "japonavi" else max(values, key=key)


def sequence_values(value: object, *, name: str) -> list[object]:
    if isinstance(value, (list, range, KisiteSet, KisiteCombinations)):
        return list(value)
    raise KisiteError(f"function '{name}' requires an array, set, combinations, or pilika range")


def destructure_values(value: object, count: int) -> list[object]:
    if isinstance(value, KisiteSet):
        items = value.values()
    elif isinstance(value, (list, str, range)):
        items = list(value)
    else:
        raise KisiteError("destructuring requires an array, string, set, or pilika range")
    if len(items) != count:
        raise KisiteError(f"destructuring expected {count} values, got {len(items)}")
    return items


def make_fill(value: object, count: object) -> list[object]:
    if not is_integer(count) or count < 0:
        raise KisiteError("fill count must be a non-negative integer")
    return [deepcopy(value) for _ in range(count)]


def make_reverse(value: object) -> object:
    if isinstance(value, str):
        return value[::-1]
    if isinstance(value, KisiteSet):
        return list(reversed(value.values()))
    if isinstance(value, (list, range, KisiteCombinations)):
        return list(reversed(list(value)))
    raise KisiteError("reverse requires an array, string, set, combinations, or pilika range")


def make_resize(value: object, size: object, fill: object = 0) -> list[object]:
    if not isinstance(value, list):
        raise KisiteError("resize requires an array")
    if not is_integer(size) or size < 0:
        raise KisiteError("resize size must be a non-negative integer")
    result = list(value[:size])
    while len(result) < size:
        result.append(deepcopy(fill))
    return result


def make_truncate(value: object, size: object) -> list[object]:
    if not isinstance(value, list):
        raise KisiteError("truncate requires an array")
    if not is_integer(size) or size < 0:
        raise KisiteError("truncate size must be a non-negative integer")
    if size > len(value):
        raise KisiteError("truncate size cannot exceed the array length")
    return list(value[:size])


def make_set(value: object) -> KisiteSet:
    if isinstance(value, KisiteSet):
        return KisiteSet(value.values())
    if isinstance(value, (list, str, range, KisiteCombinations)):
        return KisiteSet(list(value))
    raise KisiteError("set requires an iterable collection")


def make_array(value: object) -> list[object]:
    if isinstance(value, KisiteDict):
        return value.keys()
    if isinstance(value, KisiteSet):
        return value.values()
    if isinstance(value, (list, str, range, KisiteCombinations)):
        return list(value)
    raise KisiteError("array requires an iterable collection")


def modular_inverse(value: object, modulus: object) -> int:
    if not is_integer(value) or not is_integer(modulus) or modulus <= 1:
        raise KisiteError("modinv requires integer value and modulus > 1")
    value %= modulus
    if math_gcd(value, modulus) != 1:
        raise KisiteError("modular inverse does not exist")
    return pow(value, -1, modulus)


def modular_pow(base: object, exponent: object, modulus: object) -> int:
    if not is_integer(base) or not is_integer(exponent) or not is_integer(modulus):
        raise KisiteError("modpow requires integer arguments")
    if exponent < 0:
        raise KisiteError("modpow exponent must be non-negative")
    if modulus <= 1:
        raise KisiteError("modpow modulus must be greater than 1")
    return pow(base, exponent, modulus)


def _ntt(values: list[int], invert: bool) -> None:
    n = len(values)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            values[i], values[j] = values[j], values[i]

    length = 2
    while length <= n:
        root = pow(NTT_ROOT, (NTT_MOD - 1) // length, NTT_MOD)
        if invert:
            root = pow(root, NTT_MOD - 2, NTT_MOD)
        half = length >> 1
        for offset in range(0, n, length):
            w = 1
            for j in range(offset, offset + half):
                u = values[j]
                v = values[j + half] * w % NTT_MOD
                values[j] = (u + v) % NTT_MOD
                values[j + half] = (u - v) % NTT_MOD
                w = w * root % NTT_MOD
        length <<= 1

    if invert:
        inv_n = pow(n, NTT_MOD - 2, NTT_MOD)
        for i in range(n):
            values[i] = values[i] * inv_n % NTT_MOD


def convolution_mod(left: list[int], right: list[int], modulus: int) -> list[int]:
    if not left or not right:
        return []
    if modulus <= 1:
        raise KisiteError("convolution modulus must be greater than 1")

    if min(len(left), len(right)) <= 32 or modulus != NTT_MOD:
        result = [0] * (len(left) + len(right) - 1)
        for i, a in enumerate(left):
            a %= modulus
            for j, b in enumerate(right):
                result[i + j] = (result[i + j] + a * (b % modulus)) % modulus
        return result

    need = len(left) + len(right) - 1
    size = 1
    while size < need:
        size <<= 1
    if size > (1 << 23):
        raise KisiteError("998244353 convolution length exceeds the NTT limit")
    a = [value % NTT_MOD for value in left] + [0] * (size - len(left))
    b = [value % NTT_MOD for value in right] + [0] * (size - len(right))
    _ntt(a, False)
    _ntt(b, False)
    for i in range(size):
        a[i] = a[i] * b[i] % NTT_MOD
    _ntt(a, True)
    return a[:need]


def convolution_exact(left: list[int], right: list[int]) -> list[int]:
    if not left or not right:
        return []
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def normalize_convolution_array(value: object, name: str) -> tuple[list[int], int | None]:
    if not isinstance(value, list):
        raise KisiteError(f"convolution {name} must be an array")
    modulus: int | None = None
    result: list[int] = []
    for item in value:
        if isinstance(item, KisiteModInt):
            if modulus is None:
                modulus = item.modulus
            elif modulus != item.modulus:
                raise KisiteError("convolution modint arrays must use one modulus")
            result.append(item.value)
        elif is_integer(item):
            result.append(item)
        else:
            raise KisiteError("convolution arrays must contain integers or modints")
    return result, modulus
