# Kisite

Kisite is an experimental programming language based on Lisatopian (莉語 / Lisatopa).

The name comes from the Lisatopian verb `kisite`, meaning “to process”.

Japanese language specification: [`docs/spec-ja.md`](docs/spec-ja.md)

## Current milestone

Kisite 0.0.14 currently supports:

- output with `takute kas ...`
- numeric, string, boolean, and array literals
- zero-based indexing and indexed assignment
- `+`, `-`, `*`, `/`
- variables with `sonome` / `kemese`
- optional runtime type annotations with `sis`
- equality with `kate`
- comparisons with `<`, `>`, `<=`, `>=`, `!=`
- logical `kasta` / `vista` / `kix`
- blocks with `{ ... }`
- `palusta` / `japalusta` conditionals
- `japalusta palusta` else-if chains
- `pilike palusta` while-style loops
- `pilike kas ... pas ...` foreach-style loops
- `kinise` / `kinate` break and continue
- arrays with `putike` append and `kinise kas a[i]` deletion
- whitespace-token input with `polike`
- file-backed input streams in addition to `stdin`
- function calls with `kisite`
- function definitions with `kalivisku musope`
- returns with `jasepe`
- builtins `minika`, `kipala`, and `pilika`

Kisite keeps Lisatopian vocabulary and sentence structure where practical, while ordinary mathematical notation stays concise.

## Examples

```kisite
Takute kas "Hello World".

Sonome kas x tas 3.
Kemese kas x tas x + 5.
Takute kas x.
```

### Boolean and logical expressions

```kisite
Sonome kas a tas Kati.
Sonome kas b tas Kixkati.

Takute kas a kasta b.
Takute kas a vista b.
Takute kas Kix a.
```

`kasta` is logical AND in ordinary expressions, `vista` is OR, and `kix` is NOT. Logical operators require boolean operands and short-circuit.

Function arguments also use `kasta` as their separator. To pass one logical-AND expression as a single argument, parenthesize it:

```kisite
Kisite kas f vis (a kasta b) kasta c
```

### Arrays and loops

```kisite
Sonome kas T tas [10, 20, 30].
Putike kas 40 tas T.
Kinise kas T[1].

Pilike kas i pas T {
    Takute kas i.
}
```

`kinise` without `kas` breaks the current loop, while `kinate` continues with the next iteration:

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

`pilika` is the `range`-equivalent builtin:

```kisite
Kisite kas pilika vis 5
Kisite kas pilika vis 2 kasta 6
Kisite kas pilika vis 2 kasta 10 kasta 2
```

These correspond to `range(5)`, `range(2, 6)`, and `range(2, 10, 2)`.

Use `kipala` for length:

```kisite
Takute kas Kisite kas kipala vis T.
Takute kas Kisite kas kipala vis "abc".
```

### Input

`polike` reads whitespace-separated tokens as strings.

```kisite
Polike kas a kasta b vos stdin.
Sonome kas x tas Kisite kas minika vis a.
Sonome kas y tas Kisite kas minika vis b.
Takute kas x + y.
```

A quoted path can be used as another input stream:

```kisite
Polike kas a kasta b vos "input.txt".
Polike kas c vos "input.txt".
```

Repeated reads from the same file continue from the previous position. Relative paths are resolved from the source file directory when using the CLI.

### Runtime type annotations

```kisite
Sonome kas n sis minika tas 0.
Sonome kas s sis takuta tas "abc".
Sonome kas a sis kineska tas [1, 2, 3].
Sonome kas b sis kati tas Kati.
```

The current type names mean number, string, array, and boolean respectively. The annotation is checked on initialization and later whole-variable assignment/input.

### Conditions and else-if

```kisite
Palusta x > 0 {
    Takute kas "positive".
} Japalusta palusta x kate 0 {
    Takute kas "zero".
} Japalusta {
    Takute kas "negative".
}
```

### Functions

Function calls use `kisite`:

```kisite
Kisite kas f vis a kasta b
```

Function definitions use `kalivisku musope`:

```kisite
Kalivisku musope kas add vis a kasta b {
    Jasepe kas a + b.
}

Sonome kas answer tas Kisite kas add vis 2 kasta 3.
Takute kas answer.
```

Function variables are local. Functions do not implicitly capture caller/global variables. Recursion is supported.

## Run

```powershell
python kisite.py examples/hello.kis
python kisite.py examples/arithmetic.kis
python kisite.py examples/input.kis
python kisite.py examples/arrays_loops.kis
python kisite.py examples/functions.kis
```

Run tests with:

```powershell
python -m unittest discover -s tests
```
