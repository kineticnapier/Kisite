# Kisite

Kisite is an experimental programming language based on Lisatopian (莉語 / Lisatopa).

The name comes from the Lisatopian verb `kisite`, meaning “to process”.

## Current milestone

Kisite 0.0.2 supports:

- output with `takute kas ...`
- variables
  - `sonome kas NAME tas VALUE` initializes a variable
  - `kemese kas NAME tas VALUE` sets an initialized variable
- equality with `kate`, which returns a boolean
- numeric and string literals
- `+`, `-`, `*`, `/`
- parentheses and normal arithmetic precedence

The arithmetic symbols are temporary surface syntax. Kisite will move toward Lisatopian vocabulary and grammar as the language design is settled.

## Examples

```kisite
Takute kas "Hello World".

Sonome kas x tas 3.
Kemese kas x tas x + 5.
Takute kas x.
Takute kas x kate 8.
```

Output:

```text
Hello World
8
true
```

`sonome` only initializes a new variable. Initializing the same variable twice is an error. `kemese` only changes an already initialized variable.

`kate` has lower precedence than arithmetic, so:

```kisite
Takute kas 2 + 3 kate 1 + 4.
```

prints `true`.

## Run

```powershell
python kisite.py examples/hello.kis
python kisite.py examples/arithmetic.kis
python kisite.py examples/variables.kis
```

Run tests with:

```powershell
python -m unittest discover -s tests
```
