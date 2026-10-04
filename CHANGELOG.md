# Changelog

Kisite is still experimental, so syntax and semantics may change between 0.x releases.

## 0.1.1 - Unreleased

- Added live CLI output so `Takute` is emitted while the program is still running instead of only after execution finishes.
- Added statement-only `flush` for interactive judges; `Kisite kas flush.` flushes the current CLI output stream before waiting for more input.
- Added provisional math helpers `pi`, `sin`, `cos`, `tan`, `sqrt`, `atan2`, `hypot`, `floor`, and `ceil`.
- Added provisional min-heap helpers `heapify`, `heappush`, `heappop`, and `heappeek`; heaps support numbers and nested numeric arrays such as pair-like `[priority, value]` entries.
- Added `bisectleft` and `bisectright` for lower-bound / upper-bound style binary searches on sorted arrays.
- Kept `run()` capture semantics for tests while adding an optional `output_stream` for live-output testing and embedding.
- Added an experimental `--compiled` backend that lowers the supported Kisite AST directly to Python AST/bytecode; the interpreter remains the default and reference backend while semantic coverage is expanded.
- Added compiled-backend regression tests and `python benchmarks/run.py --compiled` for direct performance comparison with the interpreter.

## 0.1.0 - 2026-10-04

- First public release of Kisite.
- Promoted the language from the 0.0.x prototype series after the full 156-test suite passed locally.
- Includes variables, conditions, loops, functions and recursion, arrays, sets, dictionaries, ranges, slices, destructuring, and array comprehensions.
- Includes competitive-programming helpers for input, collection construction and transformation, combinations, `gcd` / `lcm`, modular arithmetic, and convolution with an NTT fast path for modulus `998244353`.
- Keeps Lisatopian-inspired core vocabulary while some newer competitive-programming helper names remain provisional.

## 0.0.17

- Added augmented assignment: `+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `&=`, `|=`, `^=`, `<<=`, and `>>=`.
- Added negative indexing and Python-style read slices such as `a[1:-1]` and `a[::-1]`.
- Added destructuring initialization (`Sonome kas a kasta b tas ...`) and foreach destructuring (`Pilike kas x kasta y pas ...`).
- Added array comprehensions such as `[x * 2 Pilike kas x pas a]`, with optional filtering using `Palusta` and destructuring bindings such as `Pilike kas x kasta y pas points`. Comprehension bindings are local to the expression; the initial form supports one generator.
- Added array concatenation with `+` and array repetition with `*`.
- Added provisional competitive-programming helpers `readint`, `readints`, `fill`, `reverse`, `resize`, `truncate`, `combinations`, `gcd`, `lcm`, `set`, and `array` pending suitable Lisatopian vocabulary where needed.
- Sets and dictionary keys can now use nested arrays of scalar values, making point-like arrays usable as set elements.
- Added integer bitwise operators `&`, `|`, `^`, `~`, `<<`, and `>>`.
- Added provisional modular arithmetic helpers `modint`, `modpow`, and `modinv`.
- Added `convolution`; integer arrays use exact convolution unless a modulus is supplied, and modulus `998244353` uses an NTT fast path for larger inputs.
- `convolution` can infer a modulus from `modint` arrays and returns `modint` values in that form.

## 0.0.16

- Changed the canonical boolean vocabulary to `Tuni` / `Jatuni`, with `tuna` as the boolean runtime type name. `Kati` / `Jakati` and `sis kati` remain accepted as migration aliases in 0.0.16.
- Added set literals such as `{1, 2, 3}` and the empty set `{}`.
- Added dictionary literals such as `{"a": 1}` and the empty dictionary `{:}`.
- Added membership tests with `pas` for arrays, strings, ranges, sets, and dictionaries.
- Extended `putike` and `kinise kas` to add/remove set members, and indexed assignment/deletion to dictionaries.
- Extended `kipala`, foreach, and minimum/maximum helpers to the new collection types where applicable.
- Added provisional `sum` and `abs` built-ins pending suitable Lisatopian vocabulary.
- Added separator-based collection output, for example `Takute kas a vis " ".` for AtCoder-style space-separated output.
- Split the interpreter internals into syntax, parser, value, and runtime modules while keeping `import kisite` and the CLI entry point compatible.

## 0.0.15

- Added integer floor division `//` and remainder `%`.
- Added `paline` for returning a sorted copy of an array, including lexicographic sorting of nested arrays.
- Added `japonavi` / `ponavi` for minimum / maximum selection.

## 0.0.14

- Replaced the runtime type-annotation keyword `pasta` with `sis`.
- Replaced the false literal `Kixkati` with `Jakati`.
- Reorganized documentation into English and Japanese guides/specifications under `docs/en/` and `docs/ja/`.

## 0.0.13

- Added boolean literals `Kati` and `Kixkati`.
- Added logical `kasta` (AND), `vista` (OR), and `kix` (NOT), with short-circuit evaluation.
- Added `kipala` for length and `pilika` for range-style iteration.
- Added `putike` for array append and `kinise kas a[i]` for element deletion.
- Added `kinise` / `kinate` as break / continue.
- Added file-backed input streams.
- Added optional runtime type annotations.
- Added `japalusta palusta` else-if chains.

## 0.0.12

- Changed `polike` input to always produce strings.
- Added explicit numeric conversion with `minika`.
- Added function calls with `kisite`.
- Added function definitions with `kalivisku musope`.
- Added returns with `jasepe`.
- Added local function scope and recursion.

## 0.0.11

- Added array literals, zero-based indexing, and indexed assignment.
- Added `pilike palusta` while-style loops.
- Added `pilike kas x pas T` foreach-style loops for arrays and strings.

## 0.0.10

- Added `japalusta` as the fallback branch corresponding to `else`.

## 0.0.9

- Changed `palusta` from postfix syntax to prefix block syntax.

## 0.0.8

- Added `{ ... }` blocks.

## 0.0.7

- Added `<`, `>`, `<=`, `>=`, and `!=` comparisons.

## 0.0.6

- Added multiple-input `polike` syntax using `kasta`.

## 0.0.5

- Added stdin input with `polike`.

## 0.0.4

- Adopted `palusta` for conditions and removed the provisional `kuesta` syntax.

## 0.0.3

- Added the first provisional conditional syntax.

## 0.0.2

- Added variables with `sonome` / `kemese`.
- Added equality with `kate`.

## Earlier

- Added the minimal interpreter, output with `takute`, literals, and arithmetic.
