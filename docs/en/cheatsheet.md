# Kisite Cheat Sheet

[Guide](README.md) · [Language specification](spec.md) · [日本語](../ja/cheatsheet.md)

Quick reference for **Kisite 0.0.14**.

## Basics

```kisite
# comment
Takute kas "Hello World".
```

- Keywords are case-insensitive.
- Variables and user-defined function names are case-sensitive.
- Statements normally end with `.` or `。`.

## Values

```kisite
123
3.14
"hello"
Kati       # true
Jakati     # false
[1, 2, 3]
```

## Variables and runtime types

```kisite
Sonome kas x tas 0.                    # initialize
Kemese kas x tas x + 1.                # assign

Sonome kas n sis minika tas 0.         # number
Sonome kas s sis takuta tas "abc".    # string
Sonome kas a sis kineska tas [1, 2].   # array
Sonome kas b sis kati tas Kati.        # boolean
```

## Arithmetic, comparison, and logic

```kisite
x + y
x - y
x * y
x / y

x kate y
x != y
x < y
x <= y
x > y
x >= y

a kasta b    # AND
a vista b    # OR
Kix a        # NOT
```

`kasta` and `vista` require boolean operands and short-circuit.

### Precedence

Highest to lowest:

1. `(...)`, indexing `[...]`
2. unary `+`, `-`, `kix`
3. `*`, `/`
4. `+`, `-`
5. `kate`, `!=`, `<`, `<=`, `>`, `>=`
6. `kasta`
7. `vista`

## Output

```kisite
Takute kas x.
```

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

Conditions must evaluate to booleans.

## Loops

### While-style

```kisite
Pilike palusta x < 10 {
    Kemese kas x tas x + 1.
}
```

### Foreach-style

```kisite
Pilike kas x pas items {
    Takute kas x.
}
```

Arrays, strings, and `pilika` ranges can be iterated.

### Break / continue

```kisite
Kinise.   # break
Kinate.   # continue
```

## Arrays and indexing

```kisite
Sonome kas a tas [10, 20, 30].
Takute kas a[0].
Kemese kas a[1] tas 99.

Putike kas 40 tas a.   # append
Kinise kas a[1].       # delete element
```

- Indexing is zero-based.
- Indices must be non-negative integers.
- Strings support read-only indexing.

## Input

```kisite
Polike kas x vos stdin.
Polike kas a kasta b kasta c vos stdin.
```

`polike` always reads whitespace-separated **strings**.

Convert numeric input explicitly:

```kisite
Polike kas raw vos stdin.
Sonome kas n tas Kisite kas minika vis raw.
```

Read from a file:

```kisite
Polike kas x vos "input.txt".
```

Repeated reads from the same file keep their stream position during one run.

## Functions

### Define

```kisite
Kalivisku musope kas add vis a kasta b {
    Jasepe kas a + b.
}
```

### Call

```kisite
Kisite kas add vis 2 kasta 3
```

### Zero arguments

```kisite
Kisite kas foo
```

Functions use local variables and support recursion.

`kasta` is both logical AND and the argument separator. Parenthesize an AND expression when passing it as one argument:

```kisite
Kisite kas f vis (a kasta b) kasta c
```

## Built-ins

### `minika` — convert to number

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

Equivalent in shape to Python's `range(stop)`, `range(start, stop)`, and `range(start, stop, step)`. `stop` is excluded.

## Common gotchas

- `Polike` returns strings; use `minika` when a number is needed.
- Boolean literals are `Kati` and `Jakati`.
- Conditions do not use implicit truthy/falsy conversion.
- Runtime type annotations use `sis`.
- `kasta` means logical AND in expressions, but also separates multiple inputs, parameters, and arguments.
- Array/string indices start at `0`; negative indices are not supported.
- `Kinise.` means break, while `Kinise kas a[i].` deletes an array element.
