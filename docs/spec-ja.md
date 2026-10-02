# Kisite 言語仕様（日本語）

この文書は Kisite 0.0.9 の現在の実装仕様をまとめたものです。

Kisite は、莉語（Lisatopa）の語彙・文法を土台にした実験的なプログラミング言語です。莉語そのものを完全に再現することよりも、莉語らしさを残しながらプログラムとして読み書きしやすいことを優先します。

言語名 `Kisite` は、莉語の `kisite`（処理する）に由来します。

> [!NOTE]
> `sonome`、`kemese`、`kate`、`palusta`、`polike` などのプログラミング言語としての意味は Kisite 側で定義したものです。元の莉語での意味・用法と完全に同一とは限りません。

## 1. 最小例

```kisite
Takute kas "Hello World".
```

標準入力から2つの値を読み、足す例:

```kisite
Polike kas a kasta b vos stdin.
Takute kas a + b.
```

入力:

```text
3 5
```

出力:

```text
8
```

## 2. 文の区切りとコメント

文末には `.` または `。` を書けます。

```kisite
Takute kas "Hello".
Takute kas "World"。
```

現在は文末記号を省略できる場合もありますが、通常は書くことを推奨します。

`#` から行末まではコメントです。

```kisite
# comment
Takute kas 1 + 2. # comment
```

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

主なエスケープ:

| 表記 | 意味 |
|---|---|
| `\n` | 改行 |
| `\t` | タブ |
| `\\` | バックスラッシュ |
| `\"` | `"` |

### 3.3 真偽値

真偽値リテラルはまだありません。`kate` や比較演算の結果として得られ、表示時は `true` / `false` になります。

## 4. 変数

変数名には英数字と `_` を使用できます。ただし先頭は数字にできません。大文字・小文字は区別されます。

### 4.1 初期化: `sonome`

```kisite
Sonome kas x tas 3.
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
kemese kas <変数名> tas <式>
```

すでに存在する変数にのみ使用できます。

## 5. 算術

| 演算子 | 意味 |
|---|---|
| `+` | 加算 |
| `-` | 減算 |
| `*` | 乗算 |
| `/` | 除算 |

数式部分では、競技プログラミングでの実用性と可読性を優先して一般的な数学記号を使います。

優先順位は高い順に:

1. 括弧 `(...)`
2. 単項 `+` / `-`
3. `*` / `/`
4. `+` / `-`
5. `kate`, `!=`, `<`, `>`, `<=`, `>=`

## 6. 比較

### 6.1 等値比較: `kate`

```kisite
Takute kas 3 kate 3.
Takute kas 3 kate 4.
```

出力:

```text
true
false
```

数値同士では整数と実数をまたいで値を比較します。それ以外では型と値の両方が一致したときに `true` です。

### 6.2 その他の比較

| 演算子 | 意味 |
|---|---|
| `!=` | 等しくない |
| `<` | より小さい |
| `>` | より大きい |
| `<=` | 以下 |
| `>=` | 以上 |

`< > <= >=` は現在数値同士にのみ使用できます。`!=` は `kate` の否定として扱われます。

## 7. 出力: `takute`

一般形:

```text
takute kas <式>
```

```kisite
Takute kas "Hello".
Takute kas 1 + 2.
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

ブロック内の文は上から順に実行されます。ブロックは入れ子にできます。

現在、ブロックは新しい変数スコープを作りません。

```kisite
{
    Sonome kas x tas 3.
    Kemese kas x tas x + 1.
}
Takute kas x.
```

これは `4` を出力します。

## 9. 条件付き実行: `palusta`

Kisite 0.0.9 では、条件を先に書き、その後ろに実行するブロックを置きます。

一般形:

```text
palusta <真偽値の式> {
    <文>
    ...
}
```

例:

```kisite
Sonome kas x tas 3.

Palusta x > 0 {
    Takute kas "positive".
    Kemese kas x tas x + 1.
}
```

条件が `true` ならブロック全体を実行し、`false` なら1文も実行しません。

入れ子も可能です。

```kisite
Palusta x > 0 {
    Palusta x > 10 {
        Takute kas "large".
    }
}
```

条件は真偽値でなければなりません。

```kisite
Palusta 1 {
    Takute kas "bad".
}
```

これはエラーです。

また、`palusta` の後ろには必ずブロックが必要です。

### 9.1 0.0.8 以前との非互換変更

旧構文:

```kisite
Takute kas "yes" palusta x > 0.
```

```kisite
{
    Takute kas "yes".
} palusta x > 0.
```

は 0.0.9 で削除されました。

新構文:

```kisite
Palusta x > 0 {
    Takute kas "yes".
}
```

を使用してください。

## 10. ストリーム入力: `polike`

現在対応しているストリームは `stdin` のみです。

### 10.1 1つ読む

```kisite
Polike kas x vos stdin.
```

### 10.2 複数読む: `kasta`

```kisite
Polike kas a kasta b vos stdin.
```

3個以上も連結できます。

```kisite
Polike kas a kasta b kasta c vos stdin.
```

一般形:

```text
polike kas <変数名> (kasta <変数名>)* vos stdin
```

入力は空白文字で区切られます。読み取った値は、整数 → 実数 → 文字列の順で解釈されます。

`polike` は未定義の変数を作成でき、既存の変数なら上書きします。

`palusta` が `false` の場合、ブロック内の `polike` は実行されないため入力も消費しません。

```kisite
Palusta flag kate 1 {
    Polike kas x vos stdin.
}
```

## 11. 予約語

Kisite 0.0.9 では、少なくとも次の語を変数名として使用できません。

```text
takute
sonome
kemese
polike
kate
palusta
kasta
kas
tas
vos
stdin
```

キーワードの大文字・小文字は区別されません。

## 12. 実行方法

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

## 13. 現在未実装の主な機能

- `else` 相当
- 論理演算
- 繰り返し
- 配列
- 関数定義
- `stdin` 以外のストリーム
- 明示的な型指定
- 真偽値リテラル

## 14. 設計上の現在の対応関係

| Kisite | 現在の役割 | おおまかな日本語 |
|---|---|---|
| `takute` | 出力 | 言う / 示す |
| `sonome` | 変数の初期化 | 初期化する |
| `kemese` | 既存変数の設定 | セットする / 設定する |
| `kate` | 等値比較 | 〜である |
| `palusta` | 条件付き実行 | もし〜ならば |
| `polike` | ストリームから読み取る | 読む / スキャンする |
| `kasta` | 複数の読み取り先をつなぐ | 〜と〜 / そして |
| `kas` | 主な対象を示す | 〜を |
| `tas` | 設定先・到達値を示す | 〜に / 〜へ |
| `vos` | 読み取り元を示す | 〜から |

数式部分では Kisite 独自の語を無理に増やさず、一般的な数学記号を使います。ブロックには `{ ... }` を使用し、`palusta` は条件を先に置く構文です。
