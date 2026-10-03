# Kisite Guide

[日本語](../ja/README.md) · [Language specification](spec.md) · [Examples](../../examples/)

Kisite is an experimental programming language inspired by **Lisatopian (莉語 / Lisatopa)**. It keeps Lisatopian vocabulary and sentence structure where practical, while using familiar mathematical notation for arithmetic and comparisons.

The name comes from the Lisatopian verb `kisite`, meaning **“to process”**.

> [!IMPORTANT]
> Kisite is still experimental. This guide describes **Kisite 0.0.14**. Syntax may change between versions.
>
> Kisite assigns programming-language roles to Lisatopian words. Those roles are not always identical to their use in Lisatopian itself.

## Quick start

Kisite currently runs as a Python interpreter and has no third-party dependencies.

```bash
git clone https://github.com/kineticnapier/Kisite.git
cd Kisite
python kisite.py --version
python kisite.py examples/hello.kis
```

A Kisite source file usually uses the `.kis` extension:

```kisite
Takute kas "Hello World".
```

Run it with:

```bash
python kisite.py hello.kis
```

## A small program

`polike` reads whitespace-separated input tokens as **strings**, so numeric input is converted explicitly with `minika`.

```kisite
Polike kas raw vos stdin.
Sonome kas n sis minika tas Kisite kas minika vis raw.
Sonome kas total sis minika tas 0.

Pilike kas i pas Kisite kas pilika vis n {
    Kemese kas total tas total + i.
}

Takute kas total.
```

Input:

```text
5
```

Output:

```text
10
```

## Language at a glance

| Familiar idea | Kisite |
|---|---|
| Print a value | `Takute kas x.` |
| Initialize a variable | `Sonome kas x tas 0.` |
| Initialize with a runtime type | `Sonome kas x sis minika tas 0.` |
| Assign a new value | `Kemese kas x tas x + 1.` |
| Equality | `x kate y` |
| `if` | `Palusta condition { ... }` |
| `else if` | `Japalusta palusta condition { ... }` |
| `else` | `Japalusta { ... }` |
| `while` | `Pilike palusta condition { ... }` |
| `for x in xs` | `Pilike kas x pas xs { ... }` |
| Define a function | `Kalivisku musope kas f vis x { ... }` |
| Call a function | `Kisite kas f vis x` |
| Return a value | `Jasepe kas x.` |

Keywords are case-insensitive, so `Takute`, `takute`, and `TAKUTE` are equivalent. Normal variable and user-defined function names remain case-sensitive.

## Values and expressions

Kisite currently has numbers, strings, booleans, arrays, and `pilika` ranges.

```kisite
123
3.14
"hello"
Kati
Jakati
[1, 2, 3]
```

Arithmetic uses ordinary symbols:

```kisite
x + y
x - y
x * y
x / y
```

Comparisons use `kate` for equality and the usual symbols for ordering:

```kisite
x kate y
x != y
x < y
x <= y
x > y
x >= y
```

Logical operations are:

```kisite
a kasta b   # AND
a vista b   # OR
Kix a       # NOT
```

`kasta` and `vista` short-circuit and require boolean operands.

## Variables and runtime types

Initialize with `sonome` and update with `kemese`:

```kisite
Sonome kas x tas 3.
Kemese kas x tas x + 5.
Takute kas x.
```

Optional runtime type annotations use `sis`:

```kisite
Sonome kas n sis minika tas 0.
Sonome kas s sis takuta tas "abc".
Sonome kas a sis kineska tas [1, 2, 3].
Sonome kas b sis kati tas Kati.
```

Current type names:

| Type name | Value type |
|---|---|
| `minika` | number |
| `takuta` | string |
| `kineska` | array |
| `kati` | boolean |

The annotation is checked when the variable is initialized and when the whole variable is later replaced.

## Conditions

```kisite
Palusta x > 0 {
    Takute kas "positive".
} Japalusta palusta x kate 0 {
    Takute kas "zero".
} Japalusta {
    Takute kas "negative".
}
```

Conditions must evaluate to a boolean; numbers are not used as implicit truth values.

## Loops

Condition-controlled loop:

```kisite
Pilike palusta x < 10 {
    Kemese kas x tas x + 1.
}
```

Foreach loop:

```kisite
Pilike kas x pas [10, 20, 30] {
    Takute kas x.
}
```

`kinise` breaks the current loop and `kinate` continues with the next iteration:

```kisite
Pilike kas i pas Kisite kas pilika vis 10 {
    Palusta i kate 3 {
        Kinate.
    }
    Palusta i kate 8 {
        Kinise.
    }
    Takute kas i.
}
```

## Arrays

Arrays use bracket syntax and zero-based indexing:

```kisite
Sonome kas a tas [10, 20, 30].
Takute kas a[0].
Kemese kas a[1] tas 99.
```

Append with `putike`:

```kisite
Putike kas 40 tas a.
```

Delete an element with `kinise kas`:

```kisite
Kinise kas a[1].
```

## Input and streams

Read one or more whitespace-separated tokens from standard input:

```kisite
Polike kas x vos stdin.
Polike kas a kasta b kasta c vos stdin.
```

All tokens are strings. Convert numeric text explicitly:

```kisite
Polike kas raw vos stdin.
Sonome kas n tas Kisite kas minika vis raw.
```

A quoted file path can be used as another input stream:

```kisite
Polike kas a kasta b vos "input.txt".
Polike kas c vos "input.txt".
```

Repeated reads from the same file keep their position. With the CLI, relative paths are resolved from the directory containing the `.kis` source file.

## Functions

Define a function with `kalivisku musope`, call it with `kisite`, and return with `jasepe`:

```kisite
Kalivisku musope kas add vis a kasta b {
    Jasepe kas a + b.
}

Sonome kas answer tas Kisite kas add vis 2 kasta 3.
Takute kas answer.
```

Functions have local variables, do not implicitly capture caller/global variables, and can call themselves recursively.

`kasta` is also the function-argument separator. If one argument itself is a logical AND expression, put that expression in parentheses:

```kisite
Kisite kas f vis (a kasta b) kasta c
```

## Built-in functions

### `minika` — number conversion

```kisite
Kisite kas minika vis "123"
Kisite kas minika vis "2.5"
```

### `kipala` — length

```kisite
Kisite kas kipala vis "abc"
Kisite kas kipala vis [1, 2, 3]
```

### `pilika` — range

```kisite
Kisite kas pilika vis 5
Kisite kas pilika vis 2 kasta 6
Kisite kas pilika vis 2 kasta 10 kasta 2
```

These correspond roughly to Python's `range(5)`, `range(2, 6)`, and `range(2, 10, 2)`.

## Run the included examples

```bash
python kisite.py examples/hello.kis
python kisite.py examples/arithmetic.kis
python kisite.py examples/input.kis
python kisite.py examples/arrays_loops.kis
python kisite.py examples/functions.kis
```

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests
```

For exact, version-specific syntax and semantics, see the [language specification](spec.md).
