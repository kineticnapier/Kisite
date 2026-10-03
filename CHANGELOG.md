# Changelog

Kisite is still experimental, so syntax and semantics may change between 0.x releases.

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
