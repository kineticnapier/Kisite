# Kisite

Kisite is an experimental programming language inspired by **Lisatopian (莉語 / Lisatopa)**.

It keeps Lisatopian vocabulary and sentence structure where practical, while using familiar mathematical notation for arithmetic and comparisons. The name comes from the Lisatopian verb `kisite`, meaning **“to process”**.

> [!IMPORTANT]
> Kisite is still experimental. The current interpreter is **0.0.17**, and syntax may change between versions.

## Documentation

- **English:** [Guide](docs/en/README.md) · [Cheat sheet](docs/en/cheatsheet.md) · [Language specification](docs/en/spec.md)
- **日本語:** [ガイド](docs/ja/README.md) · [チートシート](docs/ja/cheatsheet.md) · [言語仕様](docs/ja/spec.md)
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

A compact competitive-programming example:

```kisite
Sonome kas N kasta M tas Kisite kas readints vis 2.
Sonome kas a tas Kisite kas fill vis 0 kasta N.
Sonome kas i tas 0.

Pilike palusta M > 0 {
    a[i % N] += 1.
    i += 1.
    M -= 1.
}

Takute kas a vis " ".
```

0.0.17 adds competitive-programming-oriented syntax and helpers including augmented assignment, destructuring, slices, negative indexing, `combinations`, `gcd` / `lcm`, bitwise operations, modular arithmetic, and convolution with an NTT fast path for modulus `998244353`.

The English helper names introduced for competitive programming are provisional where suitable Lisatopian vocabulary has not yet been chosen.

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests
```
