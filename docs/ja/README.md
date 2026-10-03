# Kisite ガイド

[English](../en/README.md) · [言語仕様](spec.md) · [サンプル](../../examples/)

Kisite は **莉語（Lisatopa）** をもとにした実験的なプログラミング言語です。できるだけ莉語の語彙や語順を残しつつ、算術や比較には普通の数学記号を使います。

名前の `Kisite` は、莉語の動詞 `kisite`（「処理する」）から取っています。

> [!IMPORTANT]
> Kisite はまだ実験段階です。このガイドは **Kisite 0.0.14** の実装を説明しています。今後、構文が変更される可能性があります。
>
> Kisite では莉語の単語にプログラミング言語としての役割を割り当てています。その役割は、元の莉語での意味・用法と完全に同じとは限りません。

## まず動かす

Kisite は現在 Python 製のインタプリタとして動き、外部依存パッケージはありません。

```bash
git clone https://github.com/kineticnapier/Kisite.git
cd Kisite
python kisite.py --version
python kisite.py examples/hello.kis
```

Kisite のソースファイルは通常 `.kis` 拡張子を使います。

```kisite
Takute kas "Hello World".
```

実行:

```bash
python kisite.py hello.kis
```

## 小さなプログラム

`polike` は空白区切りの入力を **文字列として** 読みます。数値として使う場合は `minika` で明示的に変換します。

```kisite
Polike kas raw vos stdin.
Sonome kas n sis minika tas Kisite kas minika vis raw.
Sonome kas total sis minika tas 0.

Pilike kas i pas Kisite kas pilika vis n {
    Kemese kas total tas total + i.
}

Takute kas total.
```

入力:

```text
5
```

出力:

```text
10
```

## 構文早見表

| よくある構文 | Kisite |
|---|---|
| 値を出力 | `Takute kas x.` |
| 変数を初期化 | `Sonome kas x tas 0.` |
| 型を指定して初期化 | `Sonome kas x sis minika tas 0.` |
| 変数を更新 | `Kemese kas x tas x + 1.` |
| 等値比較 | `x kate y` |
| `if` | `Palusta condition { ... }` |
| `else if` | `Japalusta palusta condition { ... }` |
| `else` | `Japalusta { ... }` |
| `while` | `Pilike palusta condition { ... }` |
| `for x in xs` | `Pilike kas x pas xs { ... }` |
| 関数定義 | `Kalivisku musope kas f vis x { ... }` |
| 関数呼び出し | `Kisite kas f vis x` |
| 値を返す | `Jasepe kas x.` |

キーワードは大文字・小文字を区別しません。`Takute`, `takute`, `TAKUTE` は同じ意味です。一方、通常の変数名とユーザー定義関数名は大文字・小文字を区別します。

## 値と式

現在は数値、文字列、真偽値、配列、`pilika` が返す範囲を扱えます。

```kisite
123
3.14
"hello"
Kati
Jakati
[1, 2, 3]
```

算術演算は普通の記号です。

```kisite
x + y
x - y
x * y
x / y
```

等値比較には `kate`、大小比較には通常の記号を使います。

```kisite
x kate y
x != y
x < y
x <= y
x > y
x >= y
```

論理演算:

```kisite
a kasta b   # AND
a vista b   # OR
Kix a       # NOT
```

`kasta` と `vista` は短絡評価され、オペランドは真偽値である必要があります。

## 変数と実行時型指定

`sonome` で初期化し、`kemese` で更新します。

```kisite
Sonome kas x tas 3.
Kemese kas x tas x + 5.
Takute kas x.
```

`sis` を使うと実行時型注釈を付けられます。

```kisite
Sonome kas n sis minika tas 0.
Sonome kas s sis takuta tas "abc".
Sonome kas a sis kineska tas [1, 2, 3].
Sonome kas b sis kati tas Kati.
```

現在の型名:

| 型名 | 値の種類 |
|---|---|
| `minika` | 数値 |
| `takuta` | 文字列 |
| `kineska` | 配列 |
| `kati` | 真偽値 |

型注釈は初期化時と、その後に変数全体を置き換えるときに検査されます。

## 条件分岐

```kisite
Palusta x > 0 {
    Takute kas "positive".
} Japalusta palusta x kate 0 {
    Takute kas "zero".
} Japalusta {
    Takute kas "negative".
}
```

条件式は真偽値である必要があります。数値の暗黙的な truthy / falsy 判定はしません。

## ループ

条件付きループ:

```kisite
Pilike palusta x < 10 {
    Kemese kas x tas x + 1.
}
```

foreach:

```kisite
Pilike kas x pas [10, 20, 30] {
    Takute kas x.
}
```

`kinise` は現在のループを終了し、`kinate` は次の反復へ進みます。

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

## 配列

配列は通常の `[]` と0始まり添字を使います。

```kisite
Sonome kas a tas [10, 20, 30].
Takute kas a[0].
Kemese kas a[1] tas 99.
```

末尾へ追加:

```kisite
Putike kas 40 tas a.
```

要素を削除:

```kisite
Kinise kas a[1].
```

## 入力とストリーム

標準入力から空白区切りのトークンを読みます。

```kisite
Polike kas x vos stdin.
Polike kas a kasta b kasta c vos stdin.
```

読み込んだ値はすべて文字列です。数値が必要なら明示的に変換します。

```kisite
Polike kas raw vos stdin.
Sonome kas n tas Kisite kas minika vis raw.
```

文字列でファイルパスを指定すると、ファイルも入力ストリームとして使えます。

```kisite
Polike kas a kasta b vos "input.txt".
Polike kas c vos "input.txt".
```

同じファイルを続けて読むと読み取り位置を引き継ぎます。CLI では相対パスを `.kis` ファイルがあるディレクトリ基準で解決します。

## 関数

`kalivisku musope` で定義し、`kisite` で呼び出し、`jasepe` で値を返します。

```kisite
Kalivisku musope kas add vis a kasta b {
    Jasepe kas a + b.
}

Sonome kas answer tas Kisite kas add vis 2 kasta 3.
Takute kas answer.
```

関数内の変数はローカルです。呼び出し元やグローバル変数を暗黙には参照しません。再帰呼び出しもできます。

`kasta` は関数引数の区切りにも使います。論理 AND 式そのものを1個の引数として渡したい場合は括弧で囲みます。

```kisite
Kisite kas f vis (a kasta b) kasta c
```

## 組み込み関数

### `minika` — 数値変換

```kisite
Kisite kas minika vis "123"
Kisite kas minika vis "2.5"
```

### `kipala` — 長さ

```kisite
Kisite kas kipala vis "abc"
Kisite kas kipala vis [1, 2, 3]
```

### `pilika` — range

```kisite
Kisite kas pilika vis 5
Kisite kas pilika vis 2 kasta 6
Kisite kas pilika vis 2 kasta 10 kasta 2
```

それぞれ Python の `range(5)`, `range(2, 6)`, `range(2, 10, 2)` にだいたい対応します。

## 付属サンプルを実行

```bash
python kisite.py examples/hello.kis
python kisite.py examples/arithmetic.kis
python kisite.py examples/input.kis
python kisite.py examples/arrays_loops.kis
python kisite.py examples/functions.kis
```

## 開発

テスト:

```bash
python -m unittest discover -s tests
```

正確な構文と実装仕様は [言語仕様](spec.md) を参照してください。
