# Kisite 言語仕様（日本語）

この文書は Kisite 0.0.11 の現在の実装仕様をまとめたものです。

Kisite は、莉語（Lisatopa）の語彙・文法を土台にした実験的なプログラミング言語です。莉語そのものを完全に再現することよりも、莉語らしさを残しながらプログラムとして読み書きしやすいことを優先します。

言語名 `Kisite` は、莉語の `kisite`（処理する）に由来します。

> [!NOTE]
> `sonome`、`kemese`、`kate`、`palusta`、`japalusta`、`pilike`、`polike` などのプログラミング言語としての意味は Kisite 側で定義したものです。元の莉語での意味・用法と完全に同一とは限りません。

## 1. 最小例

```kisite
Takute kas "Hello World".
```

標準入力から2つの値を読み、足す例:

```kisite
Polike kas a kasta b vos stdin.
Takute kas a + b.
```

## 2. 文の区切りとコメント

文末には `.` または `。` を書けます。

```kisite
Takute kas "Hello".
Takute kas "World"。
```

現在は文末記号を省略できる場合もありますが、通常は書くことを推奨します。

`#` から行末まではコメントです。

## 3. 値

### 3.1 数値

整数と実数を扱えます。

```kisite
0
123
-42
3.14
.5
```

指数表記は未対応です。

### 3.2 文字列

```kisite
"Hello"
“Kisite”
```

主なエスケープは `\n`, `\t`, `\\`, `\"` です。

### 3.3 真偽値

真偽値リテラルはまだありません。`kate` や比較演算の結果として得られ、表示時は `true` / `false` になります。

### 3.4 配列

配列リテラルは `[` と `]` で書きます。

```kisite
[]
[1, 2, 3]
[1, "two", [3, 4]]
```

末尾のカンマも許可されます。

```kisite
[1, 2, 3,]
```

配列は0始まりで添字アクセスできます。

```kisite
Sonome kas a tas [10, 20, 30].
Takute kas a[0].
Takute kas a[2].
```

添字は整数である必要があり、現在は負の添字を認めません。範囲外の添字はエラーです。

配列は入れ子にでき、添字も連続して書けます。

```kisite
Sonome kas a tas [[1, 2], [3, 4]].
Takute kas a[1][0].
```

文字列も読み取り専用の添字アクセスに対応します。

```kisite
Takute kas "abc"[1].
```

これは `b` を出力します。

## 4. 変数

変数名には英数字と `_` を使用できます。ただし先頭は数字にできません。大文字・小文字は区別されます。

### 4.1 初期化: `sonome`

```kisite
Sonome kas x tas 3.
Sonome kas a tas [1, 2, 3].
```

一般形:

```text
sonome kas <変数名> tas <式>
```

未初期化の変数にのみ使用できます。再度 `sonome` するとエラーになります。

### 4.2 設定: `kemese`

```kisite
Sonome kas x tas 3.
Kemese kas x tas x + 5.
```

一般形:

```text
kemese kas <代入先> tas <式>
```

通常の変数に加えて、配列要素も代入先にできます。

```kisite
Sonome kas a tas [10, 20, 30].
Kemese kas a[1] tas 99.
Takute kas a[1].
```

入れ子の配列にも代入できます。

```kisite
Kemese kas a[1][0] tas 7.
```

文字列への添字代入はできません。

## 5. 算術

| 演算子 | 意味 |
|---|---|
| `+` | 加算 |
| `-` | 減算 |
| `*` | 乗算 |
| `/` | 除算 |

優先順位は高い順に:

1. 括弧 `(...)`、添字 `[...]`
2. 単項 `+` / `-`
3. `*` / `/`
4. `+` / `-`
5. `kate`, `!=`, `<`, `>`, `<=`, `>=`

## 6. 比較

`kate` は等値比較です。

```kisite
Takute kas 3 kate 3.
Takute kas 3 kate 4.
```

その他の比較:

| 演算子 | 意味 |
|---|---|
| `!=` | 等しくない |
| `<` | より小さい |
| `>` | より大きい |
| `<=` | 以下 |
| `>=` | 以上 |

`< > <= >=` は現在数値同士にのみ使用できます。

## 7. 出力: `takute`

一般形:

```text
takute kas <式>
```

式を評価し、その値を標準出力へ1行として出力します。

## 8. 文ブロック: `{ ... }`

複数の文をまとめられます。

```kisite
{
    Takute kas "first".
    Takute kas "second".
}
```

ブロック内の文は上から順に実行され、入れ子にもできます。現在、ブロックは新しい変数スコープを作りません。

## 9. 条件付き実行: `palusta`

```kisite
Palusta x > 0 {
    Takute kas "positive".
}
```

一般形:

```text
palusta <真偽値の式> {
    <文>
    ...
}
```

条件は真偽値でなければなりません。

### 9.1 `japalusta`: else 相当

```kisite
Palusta x > 0 {
    Takute kas "positive".
} Japalusta {
    Takute kas "non-positive".
}
```

`japalusta` は直前の `palusta` に属し、単独では使用できません。`japalusta` の後ろにも必ずブロックが必要です。

### 9.2 0.0.8 以前との非互換変更

0.0.8 以前の後置 `palusta` は 0.0.9 で削除されました。

```kisite
# 現在の構文
Palusta x > 0 {
    Takute kas "yes".
}
```

## 10. 繰り返し: `pilike`

`pilike` は Kisite では繰り返しを表します。

### 10.1 条件付き繰り返し: `pilike palusta`

`while` 相当です。

```kisite
Sonome kas x tas 0.

Pilike palusta x < 3 {
    Takute kas x.
    Kemese kas x tas x + 1.
}
```

一般形:

```text
pilike palusta <真偽値の式> {
    <文>
    ...
}
```

各反復の前に条件を評価し、`true` の間だけブロックを繰り返します。条件は真偽値でなければなりません。

### 10.2 各要素の繰り返し: `pilike kas ... pas ...`

Python の `for i in T` に相当する形です。

```kisite
Sonome kas T tas [10, 20, 30].

Pilike kas i pas T {
    Takute kas i.
}
```

一般形:

```text
pilike kas <変数名> pas <配列または文字列の式> {
    <文>
    ...
}
```

配列なら各要素を、文字列なら各文字を先頭から順に変数へ入れてブロックを実行します。

```kisite
Pilike kas c pas "abc" {
    Takute kas c.
}
```

現在ブロックに独立スコープがないため、ループ変数も通常の変数と同じ領域に置かれます。既存の変数名を使った場合は各反復で上書きされます。空の配列・文字列を回した場合、未定義だったループ変数は作られません。

## 11. ストリーム入力: `polike`

現在対応しているストリームは `stdin` のみです。

1つ読む:

```kisite
Polike kas x vos stdin.
```

複数読む:

```kisite
Polike kas a kasta b vos stdin.
Polike kas a kasta b kasta c vos stdin.
```

一般形:

```text
polike kas <変数名> (kasta <変数名>)* vos stdin
```

入力は空白文字で区切られ、整数 → 実数 → 文字列の順で解釈されます。未定義の変数は作成され、既存なら上書きされます。

## 12. 予約語

Kisite 0.0.11 では、少なくとも次の語を変数名として使用できません。

```text
takute
sonome
kemese
polike
pilike
kate
palusta
japalusta
kasta
kas
tas
pas
vos
stdin
```

キーワードの大文字・小文字は区別されません。

## 13. 実行方法

```powershell
python kisite.py path/to/program.kis
```

バージョン確認:

```powershell
python kisite.py --version
```

テスト:

```powershell
python -m unittest discover -s tests
```

## 14. 現在未実装の主な機能

- 論理演算
- 配列の長さ取得用の専用構文
- 配列への追加・削除
- `break` / `continue` 相当
- 数値範囲を直接生成する `range` 相当
- 関数定義
- `stdin` 以外のストリーム
- 明示的な型指定
- 真偽値リテラル
- `else if` 専用構文

## 15. 設計上の現在の対応関係

| Kisite | 現在の役割 | おおまかな日本語 |
|---|---|---|
| `takute` | 出力 | 言う / 示す |
| `sonome` | 変数の初期化 | 初期化する |
| `kemese` | 既存変数・配列要素の設定 | セットする / 設定する |
| `kate` | 等値比較 | 〜である |
| `palusta` | 条件 | もし〜ならば |
| `japalusta` | `palusta` の偽側 | そうでなければ / else |
| `pilike` | 繰り返し | 繰り返す |
| `polike` | ストリームから読み取る | 読む / スキャンする |
| `kasta` | 複数の読み取り先をつなぐ | 〜と〜 / そして |
| `kas` | 主な対象を示す | 〜を |
| `tas` | 設定先・到達値を示す | 〜に / 〜へ |
| `pas` | foreach の対象領域 | 〜で / 〜に |
| `vos` | 読み取り元を示す | 〜から |

数式部分では Kisite 独自の語を無理に増やさず、一般的な数学記号を使います。配列には `[...]`、ブロックには `{ ... }` を使用します。
