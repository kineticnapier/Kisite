# Kisite 言語仕様（日本語）

この文書は Kisite 0.0.8 の現在の実装仕様をまとめたものです。

Kisite は、莉語（Lisatopa）の語彙・文法を土台にした実験的なプログラミング言語です。莉語そのものを完全に再現することよりも、莉語として自然な形を保ちながらプログラムを記述できることを目標としています。

言語名 `Kisite` は、莉語の `kisite`（処理する）に由来します。

> [!NOTE]
> この文書で説明する `sonome`、`kemese`、`kate`、`palusta`、`polike` などの**プログラミング言語としての意味**は Kisite 側で定義したものです。元の莉語での意味・用法と完全に同一とは限りません。

## 1. 最小例

```kisite
Takute kas "Hello World".
```

出力:

```text
Hello World
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

## 2. 文の区切り

文末には `.` または `。` を書けます。

```kisite
Takute kas "Hello".
Takute kas "World"。
```

現在の処理系では文末記号を省略できる場合もありますが、原則として文末記号を書くことを推奨します。

空白と改行は、文字列の外では基本的に区切りとして扱われます。

## 3. コメント

`#` から行末まではコメントです。

```kisite
# これはコメント
Takute kas 1 + 2. # ここもコメント
```

## 4. 値

### 4.1 整数

```kisite
0
123
-42
```

負号は単項演算として扱われます。

### 4.2 実数

```kisite
3.14
0.5
.5
```

指数表記は現在未対応です。

### 4.3 文字列

通常の二重引用符を使用できます。

```kisite
"Hello"
"Kisite"
```

曲がった二重引用符も使用できます。

```kisite
“jaa”
```

使用できる主なエスケープは次の通りです。

| 表記 | 意味 |
|---|---|
| `\n` | 改行 |
| `\t` | タブ |
| `\\` | バックスラッシュ |
| `\"` | `"` |

### 4.4 真偽値

現在、真偽値リテラルはありません。

真偽値は `kate` や比較演算の結果として得られ、表示時は `true` または `false` になります。

## 5. 変数

変数名には英数字と `_` を使用できます。ただし先頭は数字にできません。

変数名の大文字・小文字は区別されます。

### 5.1 初期化: `sonome`

```kisite
Sonome kas x tas 3.
```

意味:

> `x` を `3` に初期化する。

一般形:

```text
sonome kas <変数名> tas <式>
```

`sonome` は未初期化の変数にのみ使用できます。同じ変数を再度 `sonome` するとエラーになります。

### 5.2 設定: `kemese`

```kisite
Sonome kas x tas 3.
Kemese kas x tas 10.
```

意味:

> `x` を `10` に設定する。

一般形:

```text
kemese kas <変数名> tas <式>
```

`kemese` はすでに存在する変数にのみ使用できます。

自己参照を含む更新も可能です。

```kisite
Sonome kas x tas 0.
Kemese kas x tas x + 1.
```

## 6. 四則演算

現在は次の演算子を使用します。

| 演算子 | 意味 |
|---|---|
| `+` | 加算 |
| `-` | 減算 |
| `*` | 乗算 |
| `/` | 除算 |

数式部分では、読みやすさと競技プログラミングでの実用性のため、一般的な数学記号を使用します。

### 6.1 優先順位

現在の優先順位は高い順に次の通りです。

1. 括弧 `(...)`
2. 単項 `+` / `-`
3. `*` / `/`
4. `+` / `-`
5. `kate`, `!=`, `<`, `>`, `<=`, `>=`

```kisite
Takute kas 2 + 3 * 4.
```

は `14` になります。

```kisite
Takute kas 2 + 3 < 6.
```

は `(2 + 3) < 6` と解釈され、`true` になります。

## 7. 比較

### 7.1 等値比較: `kate`

`kate` は Kisite では「〜である」を等値比較として扱います。

```text
<式> kate <式>
```

例:

```kisite
Takute kas 3 kate 3.
Takute kas 3 kate 4.
```

出力:

```text
true
false
```

数値同士では整数と実数をまたいで値を比較します。それ以外では型と値の両方が一致したときに `true` になります。

### 7.2 大小比較

大小比較には一般的な記号を使用します。

| 演算子 | 意味 |
|---|---|
| `<` | より小さい |
| `>` | より大きい |
| `<=` | 以下 |
| `>=` | 以上 |

```kisite
Takute kas 2 < 3.
Takute kas 3 >= 3.
```

大小比較は現在、数値同士にのみ使用できます。文字列などを大小比較するとエラーになります。

### 7.3 非等値比較: `!=`

```kisite
Takute kas 3 != 4.
Takute kas "a" != "a".
```

出力:

```text
true
false
```

`!=` は `kate` の否定として扱われます。そのため、数値の整数・実数間の扱いも `kate` と同じです。

## 8. 出力: `takute`

一般形:

```text
takute kas <式>
```

式を評価し、その値を標準出力へ1行として出力します。

```kisite
Takute kas "Hello".
Takute kas 1 + 2.
```

整数値と等しい実数は、小数点以下を付けずに表示されます。

## 9. 文ブロック: `{ ... }`

複数の文を `{` と `}` でまとめて1つのブロックとして扱えます。

```kisite
{
    Takute kas "first".
    Takute kas "second".
}
```

ブロック内の文は上から順に実行されます。

ブロックは現在、新しい変数スコープを作りません。そのため、ブロック内で初期化・変更した変数は外側からもそのまま参照できます。

```kisite
{
    Sonome kas x tas 3.
    Kemese kas x tas x + 1.
}
Takute kas x.
```

出力:

```text
4
```

ブロックは入れ子にできます。

## 10. 条件付き実行: `palusta`

`palusta` は Kisite では「もし〜ならば」を表します。直前の1文、または直前のブロックを条件付きで実行します。

1文の場合:

```text
<実行する文> palusta <真偽値の式>
```

```kisite
Sonome kas x tas 11.
Takute kas "big" palusta x > 10.
```

ブロックの場合:

```text
{
    <文>
    <文>
    ...
} palusta <真偽値の式>
```

例:

```kisite
Sonome kas x tas 3.
{
    Takute kas "positive".
    Kemese kas x tas x + 1.
    Takute kas x.
} palusta x > 0.
```

条件が `true` の場合はブロック全体を上から順に実行し、`false` の場合はブロック内の文を1つも実行しません。

したがって、条件が `false` ならブロック内の `polike` も入力を消費しません。

```kisite
{
    Polike kas x vos stdin.
    Takute kas x.
} palusta flag > 0.
```

条件は真偽値でなければなりません。

```kisite
Takute kas "bad" palusta 1. # エラー
```

現在 `else` 相当の構文は未実装です。

## 11. ストリーム入力: `polike`

`polike` は Kisite ではストリームから値を「読む」操作として扱います。

現在対応しているストリームは `stdin` のみです。

### 11.1 1つ読む

```kisite
Polike kas x vos stdin.
```

意味:

> `stdin` から `x` を読む。

一般形:

```text
polike kas <変数名> vos stdin
```

### 11.2 複数読む: `kasta`

複数の値を一度に読む場合は、読み取り先を `kasta` でつなぎます。

```kisite
Polike kas a kasta b vos stdin.
```

意味:

> `stdin` から `a` と `b` を読む。

入力が

```text
3 5
```

なら、`a` に `3`、`b` に `5` が入ります。

3個以上も同様に連結できます。

```kisite
Polike kas a kasta b kasta c vos stdin.
```

一般形:

```text
polike kas <変数名> (kasta <変数名>)* vos stdin
```

このため、Python の

```python
a, b = map(int, input().split())
```

に近い処理は Kisite では

```kisite
Polike kas a kasta b vos stdin.
```

と書けます。

### 11.3 入力の分割と型

入力は空白文字で区切られます。`polike` は指定された変数の個数だけ、先頭から順に要素を消費します。

読み取った各値は次の順序で型が決まります。

1. 整数として解釈できる → 整数
2. 実数として解釈できる → 実数
3. それ以外 → 文字列

`polike` は、対象の変数が未定義なら新しく作成し、すでに存在するなら上書きします。

入力を最後まで読み切った後にさらに値を要求するとエラーになります。

### 11.4 `palusta` との組み合わせ

1文だけ条件付きで読むこともできます。

```kisite
Polike kas x vos stdin palusta flag kate 1.
```

複数入力でも同様です。

```kisite
Polike kas a kasta b vos stdin palusta flag > 0.
```

## 12. 予約語

Kisite 0.0.8 では、少なくとも次の語を変数名として使用できません。

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

```kisite
Takute kas 1.
takute kas 1.
TAKUTE KAS 1.
```

はいずれも同じ命令として扱われます。

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

Kisite 0.0.8 では、次の機能はまだ実装されていません。

- 論理演算
- `else` 相当
- 繰り返し
- 配列
- 関数定義
- ファイルなど `stdin` 以外のストリーム
- 明示的な型指定
- 真偽値リテラル

## 15. 設計上の現在の対応関係

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

比較演算や四則演算などの数式部分では、Kisite 独自の語を無理に増やさず、一般的な数学記号を使う方針です。ブロックについても、将来の配列構文と区別しやすいよう `{ ... }` を使用します。
