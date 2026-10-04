import kisite_syntax as _syntax
import kisite_parser as _parser
import kisite_values as _values
import kisite_runtime as _runtime

# Compatibility aliases introduced in 0.0.16 remain accepted.
# The canonical vocabulary is tuna / Tuni / Jatuni.
_syntax.RESERVED_WORDS.update({"kati", "jakati"})
_syntax.TYPE_NAMES.add("kati")

_original_primary = _parser.Parser.primary


def _primary_with_boolean_aliases(self):
    if self.current_word_is("kati"):
        self.pos += 1
        return _parser.Literal(True)
    if self.current_word_is("jakati"):
        self.pos += 1
        return _parser.Literal(False)
    return _original_primary(self)


_parser.Parser.primary = _primary_with_boolean_aliases
_original_type_matches = _values.type_matches


def _type_matches_with_kati_alias(annotation, value):
    if annotation == "kati":
        return isinstance(value, bool)
    return _original_type_matches(annotation, value)


_values.type_matches = _type_matches_with_kati_alias

# Install parser/runtime extensions after the compatibility aliases so they compose
# in a predictable order.
import kisite_comprehension as _comprehension
import kisite_stdlib_011 as _stdlib_011
import kisite_compiler as _compiler

# Export the patched runtime surface plus the experimental compiled backend.
from kisite_runtime import *

run_compiled = _compiler.run_compiled
CompiledBackendUnsupported = _compiler.CompiledBackendUnsupported


if __name__ == "__main__":
    raise SystemExit(main())
