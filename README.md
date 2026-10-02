# Kisite

Kisite is an experimental programming language based on Lisatopian (莉語 / Lisatopa).

The name comes from the Lisatopian verb `kisite`, meaning “to process”.

Japanese language specification: [`docs/spec-ja.md`](docs/spec-ja.md)

## Current milestone

Kisite 0.0.11 currently supports:

- output with `takute kas ...`
- numeric and string literals
- array literals such as `[1, 2, 3]`
- zero-based indexing such as `a[0]`
- indexed assignment such as `kemese kas a[1] tas 99`
- `+`, `-`, `*`, `/`
- parentheses and normal arithmetic precedence
- variables
  - `sonome kas <name> tas <value>` initializes a variable
  - `kemese kas <target> tas <value>` changes an initialized variable or array element
- equality with `kate`
- comparisons with `<`, `>`, `<=`, `>=`, `!=`
- statement blocks with `{ ... }`
- prefix conditionals with `palusta <condition> { ... }`
- fallback branches with `japalusta { ... }`
- while-style loops with `pilike palusta <condition> { ... }`
- foreach-style loops with `pilike kas <name> pas <array-or-string> { ... }`
- token input from standard input with `polike kas <name> vos stdin`
- multi-value input with `kasta`, such as `polike kas a kasta b vos stdin`

Kisite keeps Lisatopian vocabulary and sentence structure where practical, while ordinary mathematical notation stays concise.

## Examples

```kisite
Takute kas "Hello World".

Sonome kas x tas 3.
Kemese kas x tas x + 5.
Takute kas x.
Takute kas x kate 8.
```

Conditions come before their blocks, and `japalusta` is the `else`-equivalent branch:

```kisite
Sonome kas x tas 3.

Palusta x > 0 {
    Takute kas "positive".
} Japalusta {
    Takute kas "non-positive".
}
```

Arrays use ordinary bracket notation:

```kisite
Sonome kas T tas [10, 20, 30].
Takute kas T[0].
Kemese kas T[1] tas 99.
Takute kas T[1].
```

`pilike` supports both condition-controlled repetition and foreach-style iteration:

```kisite
Sonome kas x tas 0.

Pilike palusta x < 3 {
    Takute kas x.
    Kemese kas x tas x + 1.
}

Sonome kas T tas [10, 20, 30].
Pilike kas i pas T {
    Takute kas i.
}
```

The foreach form also accepts strings:

```kisite
Pilike kas c pas "abc" {
    Takute kas c.
}
```

Blocks execute their statements in order and currently do not create a separate variable scope. Loop variables therefore remain available after a loop and are overwritten on each iteration.

Input can be read as whitespace-separated tokens:

```kisite
Polike kas a kasta b vos stdin.
Takute kas a + b.
```

With input:

```text
3 5
```

this prints `8`.

`polike` currently supports only `stdin`. Integer-looking tokens become integers, decimal-looking tokens become floating-point values, and other tokens remain strings. Reading into an existing variable overwrites it.

## Run

```powershell
python kisite.py examples/hello.kis
python kisite.py examples/arithmetic.kis
python kisite.py examples/input.kis
python kisite.py examples/arrays_loops.kis
```

Run tests with:

```powershell
python -m unittest discover -s tests
```
