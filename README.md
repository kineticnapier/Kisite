# Kisite

Kisite is an experimental programming language inspired by **Lisatopian (莉語 / Lisatopa)**.

It keeps Lisatopian vocabulary and sentence structure where practical, while using familiar mathematical notation for arithmetic and comparisons. The name comes from the Lisatopian verb `kisite`, meaning **“to process”**.

> [!IMPORTANT]
> Kisite is still experimental. The current interpreter on `main` is **0.1.1**, and syntax may change between versions.

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

Array comprehensions reuse the existing `Pilike kas ... pas ...` and `Palusta` vocabulary:

```kisite
Sonome kas doubled tas [x * 2 Pilike kas x pas [1, 2, 3]].
Sonome kas evens tas [x Pilike kas x pas (Kisite kas pilika vis 10) Palusta x % 2 kate 0].
Sonome kas scaled tas [[10 * x, 10 * y] Pilike kas x kasta y pas [[1, 2], [3, 4]]].
```

The initial comprehension syntax supports one generator. `Palusta` filtering is optional, destructuring bindings are supported, and comprehension bindings stay local to the expression.

For interactive judges, CLI output is now emitted as each `Takute` executes. Explicitly flush before waiting for the judge:

```kisite
Takute kas query.
Kisite kas flush.
Polike kas reply vos stdin.
```

0.1.0 is the first public release. The 0.1.1 development line adds interactive output/flush support, common math helpers (`pi`, trigonometry, square root, and related functions), min-heap helpers, and `bisectleft` / `bisectright` for lower/upper-bound style searches.

The English helper names introduced for competitive programming are provisional where suitable Lisatopian vocabulary has not yet been chosen.

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests
```
