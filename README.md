# Kisite

Kisite is an experimental programming language based on Lisatopian (莉語 / Lisatopa).

The name comes from the Lisatopian verb `kisite`, meaning “to process”.

## Current milestone

Kisite 0.0.3 currently supports:

- output with `takute kas ...`
- numeric and string literals
- `+`, `-`, `*`, `/`
- parentheses and normal arithmetic precedence
- variables
  - `sonome kas <name> tas <value>` initializes a variable
  - `kemese kas <name> tas <value>` changes an initialized variable
- equality with `kate`
- single-statement conditionals with `A kuesta B`

The arithmetic symbols are temporary surface syntax. Kisite will move toward Lisatopian vocabulary and grammar as the language design is settled.

## Examples

```kisite
Takute kas "Hello World".

Sonome kas x tas 3.
Kemese kas x tas x + 5.
Takute kas x.
Takute kas x kate 8.

x kate 8 kuesta Takute kas "x is eight".
```

Output:

```text
Hello World
8
true
x is eight
```

`kuesta` currently controls one following statement. Block syntax and an `else` equivalent are not implemented yet.

## Run

```powershell
python kisite.py examples/hello.kis
python kisite.py examples/arithmetic.kis
```

Run tests with:

```powershell
python -m unittest discover -s tests
```
