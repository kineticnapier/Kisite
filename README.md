# Kisite

Kisite is an experimental programming language based on Lisatopian (莉語 / Lisatopa).

The name comes from the Lisatopian verb `kisite`, meaning “to process”.

## Current milestone

The first implementation intentionally supports only:

- output with `takute kas ...`
- numeric literals
- string literals
- `+`, `-`, `*`, `/`
- parentheses and normal arithmetic precedence

The arithmetic symbols are temporary surface syntax. Kisite will move toward Lisatopian vocabulary and grammar as the language design is settled; this first milestone avoids inventing Lisatopian mathematical words that have not been verified.

## Examples

```kisite
Takute kas "Hello World".
Takute kas 3 + 5.
Takute kas (3 + 5) * 2.
```

Output:

```text
Hello World
8
16
```

## Run

```powershell
python kisite.py examples/hello.kis
python kisite.py examples/arithmetic.kis
```

Run tests with:

```powershell
python -m unittest discover -s tests
```
