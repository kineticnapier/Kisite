# Kisite

Kisite is an experimental programming language inspired by **Lisatopian (莉語 / Lisatopa)**.

It keeps Lisatopian vocabulary and sentence structure where practical, while using familiar mathematical notation for arithmetic and comparisons. The name comes from the Lisatopian verb `kisite`, meaning **“to process”**.

> [!IMPORTANT]
> Kisite is still experimental. The current interpreter is **0.0.14**, and syntax may change between versions.

## Documentation

- **English:** [Guide](docs/en/README.md) · [Language specification](docs/en/spec.md)
- **日本語:** [ガイド](docs/ja/README.md) · [言語仕様](docs/ja/spec.md)
- [Examples](examples/) · [AtCoder examples](examples/atcoder/)
- [Changelog](CHANGELOG.md)

## Quick start

Kisite currently runs as a Python interpreter and has no third-party dependencies.

```bash
git clone https://github.com/kineticnapier/Kisite.git
cd Kisite
python kisite.py --version
python kisite.py examples/hello.kis
```

A minimal Kisite program:

```kisite
Takute kas "Hello World".
```

A slightly larger example:

```kisite
Polike kas raw vos stdin.
Sonome kas n sis minika tas Kisite kas minika vis raw.
Sonome kas total sis minika tas 0.

Pilike kas i pas Kisite kas pilika vis n {
    Kemese kas total tas total + i.
}

Takute kas total.
```

Input `5` produces `10`.

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests
```
