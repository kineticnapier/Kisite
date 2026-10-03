# Kisite Language Specification

[Guide](README.md) · [日本語仕様](../ja/spec.md)

This document describes the current implementation of **Kisite 0.0.14**.

Kisite is an experimental programming language based on Lisatopian (莉語 / Lisatopa) vocabulary and sentence structure. The goal is not to reproduce Lisatopian perfectly, but to preserve its character while remaining usable as a programming language.

> [!NOTE]
> Programming-language roles assigned to Lisatopian words are defined by Kisite. They are not always identical to the original meaning or usage of those words in Lisatopian.

## 1. Minimal example

```kisite
Takute kas "Hello World".
```

## 2. Statement endings and comments

Statements may end with `.` or `。`. In some places the terminator is currently optional.

`#` starts a comment that continues to the end of the line.

## 3. Values

### 3.1 Numbers

Integers and floating-point numbers are supported.

```kisite
0
123
-42
3.14
.5
```

Exponent-form numeric literals are not currently supported.

### 3.2 Strings

```kisite
"Hello"
“Kisite”
```

Common escapes include `\n`, `\t`, `\\`, and `\"`.

### 3.3 Booleans

Boolean literals are:

```kisite
Kati
Kixkati
```

They are displayed as `true` and `false`.

### 3.4 Arrays

```kisite
[]
[1, 2, 3]
[1, "two", [3, 4]]
```

Trailing commas are allowed. Indexing is zero-based.

```kisite
Sonome kas a tas [10, 20, 30].
Takute kas a[0].
Kemese kas a[1] tas 99.
```

Indices must be integers. Negative indices are not currently supported. Strings also support read-only indexing.

## 4. Variables

### 4.1 Initialization: `sonome`

```kisite
Sonome kas x tas 3.
```

```text
sonome kas <name> [sis <type>] tas <expression>
```

Initializing the same variable twice in the same scope is an error.

### 4.2 Explicit runtime types

`sis` adds a runtime type annotation.

```kisite
Sonome kas n sis minika tas 0.
Sonome kas s sis takuta tas "abc".
Sonome kas a sis kineska tas [1, 2, 3].
Sonome kas b sis kati tas Kati.
```

Current type names:

| Type name | Kisite value type |
|---|---|
| `minika` | number (integer or float) |
| `takuta` | string |
| `kineska` | array |
| `kati` | boolean |

Annotations are checked on initialization and on later whole-variable replacement through `kemese` or `polike`. Element types inside arrays are not annotated individually.

In 0.0.14 the annotation keyword changed from `pasta` to `sis`. The old `pasta` syntax is no longer accepted.

### 4.3 Assignment: `kemese`

```kisite
Kemese kas x tas x + 1.
Kemese kas a[0] tas 10.
```

```text
kemese kas <target> tas <expression>
```

## 5. Arithmetic, comparison, and logic

Arithmetic operators are `+ - * /`.

Comparisons use `kate`, `!=`, `<`, `>`, `<=`, and `>=`. Ordering operators currently require numeric operands.

Logical operations:

| Syntax | Meaning |
|---|---|
| `a kasta b` | AND |
| `a vista b` | OR |
| `kix a` | NOT |

Logical operands must be booleans. `kasta` and `vista` short-circuit.

Approximate precedence, from highest to lowest:

1. Parentheses `(...)` and indexing `[...]`
2. Unary `+`, `-`, `kix`
3. `*`, `/`
4. `+`, `-`
5. `kate`, `!=`, `<`, `>`, `<=`, `>=`
6. Logical AND `kasta`
7. Logical OR `vista`

`kasta` is also used as the function-argument separator. To pass an AND expression as one argument, parenthesize it:

```kisite
Kisite kas f vis (a kasta b) kasta c.
```

## 6. Output: `takute`

```kisite
Takute kas <expression>.
```

The expression is evaluated and printed as one output line.

## 7. Blocks

```kisite
{
    Takute kas "a".
    Takute kas "b".
}
```

A normal block does not create a new variable scope.

## 8. Conditions: `palusta` / `japalusta`

```kisite
Palusta x > 0 {
    Takute kas "positive".
} Japalusta {
    Takute kas "non-positive".
}
```

Conditions must evaluate to booleans.

### 8.1 Else-if: `japalusta palusta`

```kisite
Palusta x > 0 {
    Takute kas "positive".
} Japalusta palusta x kate 0 {
    Takute kas "zero".
} Japalusta {
    Takute kas "negative".
}
```

Any number of `japalusta palusta` branches may be chained.

## 9. Loops: `pilike`

### 9.1 While-style loop

```kisite
Pilike palusta x < 10 {
    Kemese kas x tas x + 1.
}
```

### 9.2 Foreach-style loop

```kisite
Pilike kas i pas T {
    Takute kas i.
}
```

The iterable may be an array, a string, or a range returned by `pilika`.

### 9.3 Break: `kinise`

`kinise` without `kas` exits the current loop.

```kisite
Pilike palusta Kati {
    Palusta done {
        Kinise.
    }
}
```

Using it outside a loop is an error.

### 9.4 Continue: `kinate`

```kisite
Pilike kas i pas T {
    Palusta skip {
        Kinate.
    }
    Takute kas i.
}
```

Using it outside a loop is an error.

## 10. Array append and deletion

### 10.1 Append: `putike`

```kisite
Putike kas value tas array.
Putike kas value tas nested[0].
```

The target must be an array.

### 10.2 Delete: `kinise kas`

```kisite
Kinise kas a[2].
```

The selected array element is removed and later elements shift left.

`kinise` therefore has two forms:

- `Kinise.` → break the current loop
- `Kinise kas a[i].` → delete an array element

## 11. Input: `polike`

`polike` reads whitespace-separated tokens as **strings**.

```kisite
Polike kas x vos stdin.
Polike kas a kasta b kasta c vos stdin.
```

Use `minika` explicitly when numeric conversion is needed.

```kisite
Polike kas s vos stdin.
Sonome kas n tas Kisite kas minika vis s.
```

### 11.1 File streams

A quoted path may be used instead of `stdin`.

```kisite
Polike kas a kasta b vos "input.txt".
Polike kas c vos "input.txt".
```

Repeated reads from the same file preserve the stream position during one execution.

With the CLI, relative paths are resolved from the directory containing the Kisite source file. When calling `run()`, `base_dir=` may be supplied; otherwise the current working directory is used.

## 12. Function calls: `kisite`

General form:

```text
kisite kas <function-name> [vis <argument> (kasta <argument>)*]
```

Examples:

```kisite
Kisite kas greet vis "hello".
Sonome kas n tas Kisite kas minika vis s.
```

For zero arguments, omit `vis`.

A call may be used as an expression. If its return value is not needed, it may also appear as a standalone statement.

## 13. Function definitions: `kalivisku musope`

General form:

```text
kalivisku musope kas <function-name> [vis <parameter> (kasta <parameter>)*] {
    <statement>
    ...
}
```

Example:

```kisite
Kalivisku musope kas add vis a kasta b {
    Jasepe kas a + b.
}
```

Each function call gets a local variable environment. Functions do not implicitly read caller/global variables. Recursion is supported.

## 14. Return values: `jasepe`

```kisite
Jasepe kas <expression>.
```

The current function ends and returns the expression value to the caller. Using `jasepe` outside a function is an error.

## 15. Built-in functions

### 15.1 `minika`

```kisite
Kisite kas minika vis "123"
Kisite kas minika vis "2.5"
```

Converts a number or a numeric string to a number.

### 15.2 `kipala`

Returns the length of an array, string, or `pilika` range.

```kisite
Kisite kas kipala vis [1, 2, 3]
Kisite kas kipala vis "abc"
```

### 15.3 `pilika`

`range` equivalent:

```kisite
Kisite kas pilika vis stop
Kisite kas pilika vis start kasta stop
Kisite kas pilika vis start kasta stop kasta step
```

Arguments must be integers. `step` cannot be zero. `stop` is excluded.

Example:

```kisite
Pilike kas i pas Kisite kas pilika vis 2 kasta 10 kasta 2 {
    Takute kas i.
}
```

This outputs `2, 4, 6, 8` in order.

## 16. Reserved words

At minimum, the following words cannot be used as ordinary variable names:

```text
takute
sonome
kemese
polike
pilike
putike
kinise
kinate
kisite
kalivisku
musope
jasepe
minika
kipala
pilika
takuta
kineska
kati
kixkati
kix
kate
palusta
japalusta
kasta
vista
kas
tas
pas
sis
vis
vos
stdin
```

Keywords are case-insensitive. Ordinary variable names and user-defined function names are case-sensitive.

## 17. Running Kisite

```powershell
python kisite.py path/to/program.kis
python kisite.py --version
python -m unittest discover -s tests
```

## 18. Major features not yet implemented

Features added in 0.0.13 include logic, length, array append/delete, break/continue, range, file input streams, runtime type annotations, boolean literals, and else-if chains.

Possible future work includes integer division and modulo, sorting, slicing, dictionaries/sets, output streams, and more precise types.

## 19. Kisite vocabulary mapping

| Kisite | Current programming role |
|---|---|
| `takute` | output |
| `sonome` | variable initialization |
| `kemese` | assignment |
| `sis` | type annotation |
| `kate` | equality |
| `kasta` | logical AND / item separator |
| `vista` | logical OR |
| `kix` | logical NOT |
| `kati`, `kixkati` | true / false |
| `palusta` | condition |
| `japalusta` | else branch |
| `japalusta palusta` | else-if |
| `pilike` | repetition |
| `kinise` | break / delete array element |
| `kinate` | continue |
| `putike` | append to array |
| `polike` | input |
| `kisite` | function execution/call |
| `kalivisku musope` | function definition |
| `jasepe` | return from function |
| `minika` | explicit number conversion |
| `kipala` | length |
| `pilika` | range |
| `pas` | foreach target |
| `vis` | function argument side |
| `vos` | input source |
