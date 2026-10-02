# Kisite 言語仕様（日本語）

この文書は Kisite 0.0.5 の現在の実装仕様をまとめたものです。

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

複数の値を入力して計算する例:

```kisite
Polike kas a vos stdin.
Polike kas b vos stdin.
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

現在の処理系では文末記号を省略できる場合もありますが、読みやすさと将来の互換性のため、原則として文末記号を書くことを推奨します。

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

負号は数値そのものではなく単項演算として扱われます。

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

莉語の文章などを書きやすいように、曲がった二重引用符も使用できます。

```kisite
“jaa”
```

通常の文字列では、次のエスケープを使用できます。

| 表記 | 意味 |
|---|---|
| `\n` | 改行 |
| `\t` | タブ |
| `\\` | バックスラッシュ |
| `\"` | `"` |

### 4.4 真偽値

現在、真偽値リテラルはありません。

真偽値は `kate` などの式の結果として得られます。表示時は次の文字列になります。

```text
true
false
```

## 5. 変数

変数名には英数字と `_` を使用できます。ただし、先頭は数字にできません。

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

`sonome` は未初期化の変数にのみ使用できます。同じ変数をもう一度 `sonome` するとエラーになります。

```kisite
Sonome kas x tas 3.
Sonome kas x tas 4. # エラー
```

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

`kemese` はすでに初期化されている変数にのみ使用できます。

```kisite
Kemese kas x tas 3. # x が存在しないのでエラー
```

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

```kisite
Takute kas 3 + 5.
Takute kas 10 - 4.
Takute kas 6 * 7.
Takute kas 20 / 5.
```

出力:

```text
8
6
42
4
```

`+ - * /` は暫定構文です。莉語側の算術語彙・Kisite の文法が固まった段階で、莉語らしい表現を追加または置き換える可能性があります。

### 6.1 優先順位

現在の優先順位は高い順に次の通りです。

1. 括弧 `(...)`
2. 単項 `+` / `-`
3. `*` / `/`
4. `+` / `-`
5. `kate`

したがって、

```kisite
Takute kas 2 + 3 * 4.
```

は `14` になります。

括弧も使用できます。

```kisite
Takute kas (2 + 3) * 4.
```

これは `20` になります。

## 7. 等値比較: `kate`

`kate` は Kisite では「〜である」を等値比較として扱います。

```kisite
Takute kas 3 kate 3.
Takute kas 3 kate 4.
```

出力:

```text
true
false
```

一般形:

```text
<式> kate <式>
```

数値同士では整数と実数をまたいで値を比較します。それ以外では型と値の両方が一致したときに `true` になります。

`kate` は四則演算より優先順位が低いため、

```kisite
Takute kas 2 + 3 kate 1 + 4.
```

は次と同じ意味です。

```text
(2 + 3) kate (1 + 4)
```

結果は `true` です。

## 8. 出力: `takute`

```kisite
Takute kas "Hello".
Takute kas 1 + 2.
```

一般形:

```text
takute kas <式>
```

式を評価し、その値を標準出力へ1行として出力します。

整数値と等しい実数は、小数点以下を付けずに表示されます。

```kisite
Takute kas 20 / 5.
```

出力:

```text
4
```

## 9. 条件付き実行: `palusta`

`palusta` は Kisite では「もし〜ならば」を表し、**直前の1文**を条件付きで実行します。

```kisite
Sonome kas x tas 8.
Takute kas "yes" palusta x kate 8.
```

意味:

> `x` が `8` ならば `"yes"` と言う。

一般形:

```text
<実行する文> palusta <真偽値の式>
```

条件は真偽値でなければなりません。

```kisite
Takute kas "bad" palusta 1. # エラー
```

変数の変更にも使用できます。

```kisite
Sonome kas x tas 1.
Kemese kas x tas 2 palusta x kate 1.
Takute kas x.
```

出力:

```text
2
```

現在は複数文をまとめるブロック、`else` 相当の構文は未実装です。

## 10. 標準入力: `polike`

`polike` は Kisite ではストリームから値を「読む」操作として扱います。

現在対応しているストリームは `stdin` のみです。

```kisite
Polike kas x vos stdin.
```

意味:

> `stdin` から `x` を読む。

一般形:

```text
polike kas <変数名> vos stdin
```

入力は空白文字で区切られ、1回の `polike` で1要素を読みます。

```kisite
Polike kas a vos stdin.
Polike kas b vos stdin.
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

読み取った値は次の順序で型が決まります。

1. 整数として解釈できる → 整数
2. 実数として解釈できる → 実数
3. それ以外 → 文字列

`polike` は、対象の変数が未定義なら新しく作成し、すでに存在するなら上書きします。

入力を最後まで読み切った後にさらに `polike` するとエラーになります。

### 10.1 `palusta` との組み合わせ

```kisite
Polike kas x vos stdin palusta flag kate 1.
```

条件が `false` の場合は `polike` 自体が実行されないため、入力も消費されません。

## 11. 予約語

Kisite 0.0.5 では、少なくとも次の語を変数名として使用できません。

```text
takute
sonome
kemese
polike
kate
palusta
kas
tas
vos
stdin
```

キーワードの大文字・小文字は区別されません。

したがって、次は同じ命令として扱われます。

```kisite
Takute kas 1.
takute kas 1.
TAKUTE KAS 1.
```

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

Kisite 0.0.5 では、次の機能はまだ実装されていません。

- 大小比較（`<`, `>`, `<=`, `>=` 相当）
- 論理演算
- 複数文ブロック
- `else` 相当
- 繰り返し
- 配列
- 関数定義
- ファイルなど `stdin` 以外のストリーム
- 明示的な型指定
- 真偽値リテラル
- 莉語の語彙による四則演算

## 14. 設計上の現在の対応関係

| Kisite | 現在の役割 | おおまかな日本語 |
|---|---|---|
| `takute` | 出力 | 言う / 示す |
| `sonome` | 変数の初期化 | 初期化する |
| `kemese` | 既存変数の設定 | セットする / 設定する |
| `kate` | 等値比較 | 〜である |
| `palusta` | 条件付き実行 | もし〜ならば |
| `polike` | ストリームから読み取る | 読む / スキャンする |
| `kas` | 主な対象を示す | 〜を |
| `tas` | 設定先・到達値を示す | 〜に / 〜へ |
| `vos` | 読み取り元を示す | 〜から |

この対応は今後の言語設計に応じて変更される可能性があります。
