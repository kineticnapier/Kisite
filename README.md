# Kisite

Kisite is an experimental programming language based on Lisatopian (莉語 / Lisatopa).

The name comes from the Lisatopian verb `kisite`, meaning “to process”.

Japanese language specification: [`docs/spec-ja.md`](docs/spec-ja.md)

## Current milestone

Kisite 0.0.8 currently supports:

- output with `takute kas ...`
- numeric and string literals
- `+`, `-`, `*`, `/`
- parentheses and normal arithmetic precedence
- variables
  - `sonome kas <name> tas <value>` initializes a variable
  - `kemese kas <name> tas <value>` changes an initialized variable
- equality with `kate`
- comparisons with `<`, `>`, `<=`, `>=`, `!=`
- statement blocks with `{ ... }`
- conditionals with `<statement-or-block> palusta <condition>`
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

Takute kas "x is large" palusta x > 5.
```

Multiple statements can be grouped with braces and controlled by one `palusta` condition:

```kisite
Sonome kas x tas 3.
{
    Takute kas "positive".
    Kemese kas x tas x + 1.
    Takute kas x.
} palusta x > 0.
```

Blocks execute their statements in order and currently do not create a separate variable scope.

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

More values can be chained with `kasta`:

```kisite
Polike kas a kasta b kasta c vos stdin.
```

`polike` currently supports only `stdin`. Integer-looking tokens become integers, decimal-looking tokens become floating-point values, and other tokens remain strings. Reading into an existing variable overwrites it.

`palusta` can control either one statement or an entire block. An `else` equivalent is not implemented yet.

## Run

```powershell
python kisite.py examples/hello.kis
python kisite.py examples/arithmetic.kis
python kisite.py examples/input.kis
```

Run tests with:

```powershell
python -m unittest discover -s tests
```
