# Kisite

Kisite is an experimental programming language based on Lisatopian (莉語 / Lisatopa).

The name comes from the Lisatopian verb `kisite`, meaning “to process”.

Japanese language specification: [`docs/spec-ja.md`](docs/spec-ja.md)

## Current milestone

Kisite 0.0.12 currently supports:

- output with `takute kas ...`
- numeric and string literals
- array literals such as `[1, 2, 3]`
- zero-based indexing and indexed assignment
- `+`, `-`, `*`, `/`
- variables with `sonome` / `kemese`
- equality with `kate`
- comparisons with `<`, `>`, `<=`, `>=`, `!=`
- blocks with `{ ... }`
- `palusta` / `japalusta` conditionals
- `pilike palusta` while-style loops
- `pilike kas ... pas ...` foreach-style loops
- whitespace-token input with `polike`
- function calls with `kisite`
- function definitions with `kalivisku musope`
- returns with `jasepe`
- explicit number conversion with the builtin `minika`

Kisite keeps Lisatopian vocabulary and sentence structure where practical, while ordinary mathematical notation stays concise.

## Examples

```kisite
Takute kas "Hello World".

Sonome kas x tas 3.
Kemese kas x tas x + 5.
Takute kas x.
```

Arrays and loops:

```kisite
Sonome kas T tas [10, 20, 30].

Pilike kas i pas T {
    Takute kas i.
}

Sonome kas x tas 0.
Pilike palusta x < 3 {
    Kemese kas x tas x + 1.
}
```

### Input is string-valued in 0.0.12

`polike` still reads whitespace-separated tokens, but every token is now a string.

```kisite
Polike kas S vos stdin.
Pilike kas c pas S {
    Takute kas c.
}
```

With input `101`, `S` is the string `"101"` and the loop prints `1`, `0`, `1`.

Use `minika` through the normal function-call syntax when a number is needed:

```kisite
Polike kas a kasta b vos stdin.
Sonome kas x tas Kisite kas minika vis a.
Sonome kas y tas Kisite kas minika vis b.
Takute kas x + y.
```

`minika` produces an integer when the text is integer-shaped and otherwise tries a floating-point value.

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

A zero-argument function omits `vis`:

```kisite
Kalivisku musope kas answer {
    Jasepe kas 42.
}

Takute kas Kisite kas answer.
```

A function call can also be used as a statement when its return value is not needed:

```kisite
Kalivisku musope kas greet vis name {
    Takute kas name.
}

Kisite kas greet vis "hello".
```

Function variables are local. Parameters and variables initialized inside a function do not overwrite same-named variables in the caller. Functions do not implicitly capture caller/global variables; pass required values as arguments. Recursion is supported.

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
