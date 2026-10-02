# Kisite 言語仕様（日本語）

この文書は Kisite 0.0.13 の現在の実装仕様をまとめたものです。

Kisite は、莉語（Lisatopa）の語彙・文法を土台にした実験的なプログラミング言語です。莉語そのものを完全に再現することよりも、莉語らしさを残しながらプログラムとして読み書きしやすいことを優先します。

> [!NOTE]
> 各語の「プログラミング言語としての役割」は Kisite 側で定義したものです。元の莉語での意味・用法と完全に同一とは限りません。

## 1. 最小例

```kisite
Takute kas "Hello World".
```

## 2. 文の区切りとコメント

文末には `.` または `。` を書けます。現在は省略できる場合もあります。

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

指数表記の数値リテラルは未対応です。

### 3.2 文字列

```kisite
"Hello"
“Kisite”
```

主なエスケープは `\n`, `\t`, `\\`, `\"` です。

### 3.3 真偽値

真偽値リテラル:

```kisite
Kati
Kixkati
```

表示時はそれぞれ `true` / `false` になります。

### 3.4 配列

```kisite
[]
[1, 2, 3]
[1, "two", [3, 4]]
```

末尾カンマを許可します。添字は0始まりです。

```kisite
Sonome kas a tas [10, 20, 30].
Takute kas a[0].
Kemese kas a[1] tas 99.
```

添字は整数のみで、負の添字は現在未対応です。文字列も読み取り専用で添字アクセスできます。

## 4. 変数

### 4.1 初期化: `sonome`

```kisite
Sonome kas x tas 3.
```

```text
sonome kas <変数名> [pasta <型>] tas <式>
```

同じスコープで再初期化するとエラーです。

### 4.2 明示的な型指定

`pasta` で実行時型注釈を付けられます。

```kisite
Sonome kas n pasta minika tas 0.
Sonome kas s pasta takuta tas "abc".
Sonome kas a pasta kineska tas [1, 2, 3].
Sonome kas b pasta kati tas Kati.
```

現在の型名:

| 型名 | Kisite上の型 |
|---|---|
| `minika` | 数値（整数または実数） |
| `takuta` | 文字列 |
| `kineska` | 配列 |
| `kati` | 真偽値 |

注釈は初期化時と、その後の変数全体への `kemese` / `polike` で検査されます。配列要素ごとの要素型は現在指定しません。

### 4.3 設定: `kemese`

```kisite
Kemese kas x tas x + 1.
Kemese kas a[0] tas 10.
```

```text
kemese kas <代入先> tas <式>
```

## 5. 算術・比較・論理演算

算術演算子は `+ - * /` です。

比較は `kate`, `!=`, `<`, `>`, `<=`, `>=` を使います。`< > <= >=` は数値同士のみです。

論理演算:

| 構文 | 意味 |
|---|---|
| `a kasta b` | AND |
| `a vista b` | OR |
| `kix a` | NOT |

論理演算の対象は真偽値のみです。`kasta` と `vista` は短絡評価します。

優先順位は高い順に、おおむね:

1. 括弧 `(...)`、添字 `[...]`
2. 単項 `+` / `-` / `kix`
3. `*` / `/`
4. `+` / `-`
5. `kate`, `!=`, `<`, `>`, `<=`, `>=`
6. 論理 AND `kasta`
7. 論理 OR `vista`

`kasta` は関数引数の区切りにも使います。関数呼び出しの1引数として AND 式を渡す場合は括弧で囲みます。

```kisite
Kisite kas f vis (a kasta b) kasta c.
```

## 6. 出力: `takute`

```kisite
Takute kas <式>.
```

式を評価し、1行として出力します。

## 7. ブロック

```kisite
{
    Takute kas "a".
    Takute kas "b".
}
```

通常のブロック自体は新しい変数スコープを作りません。

## 8. 条件: `palusta` / `japalusta`

```kisite
Palusta x > 0 {
    Takute kas "positive".
} Japalusta {
    Takute kas "non-positive".
}
```

条件は真偽値である必要があります。

### 8.1 else-if: `japalusta palusta`

```kisite
Palusta x > 0 {
    Takute kas "positive".
} Japalusta palusta x kate 0 {
    Takute kas "zero".
} Japalusta {
    Takute kas "negative".
}
```

任意個の `japalusta palusta` を連結できます。

## 9. 繰り返し: `pilike`

### 9.1 while 相当

```kisite
Pilike palusta x < 10 {
    Kemese kas x tas x + 1.
}
```

### 9.2 foreach 相当

```kisite
Pilike kas i pas T {
    Takute kas i.
}
```

反復対象は配列、文字列、または `pilika` が返す範囲です。

### 9.3 break: `kinise`

引数なしの `kinise` は現在のループを終了します。

```kisite
Pilike palusta Kati {
    Palusta done {
        Kinise.
    }
}
```

ループ外ではエラーです。

### 9.4 continue: `kinate`

```kisite
Pilike kas i pas T {
    Palusta skip {
        Kinate.
    }
    Takute kas i.
}
```

ループ外ではエラーです。

## 10. 配列の追加・削除

### 10.1 追加: `putike`

```kisite
Putike kas value tas array.
Putike kas value tas nested[0].
```

対象は配列でなければなりません。

### 10.2 削除: `kinise kas`

```kisite
Kinise kas a[2].
```

指定した配列要素を削除し、後ろの要素を前へ詰めます。

`kinise` は構文によって意味が分かれます。

- `Kinise.` → ループを break
- `Kinise kas a[i].` → 配列要素を削除

## 11. 入力: `polike`

`polike` は空白文字で区切られたトークンを **文字列として** 読みます。

```kisite
Polike kas x vos stdin.
Polike kas a kasta b kasta c vos stdin.
```

数値化が必要なら `minika` を明示的に呼び出します。

```kisite
Polike kas s vos stdin.
Sonome kas n tas Kisite kas minika vis s.
```

### 11.1 ファイルストリーム

`stdin` の代わりに文字列パスを指定できます。

```kisite
Polike kas a kasta b vos "input.txt".
Polike kas c vos "input.txt".
```

同じファイルから複数回読む場合、実行中は読み取り位置を保持します。

CLI 実行時の相対パスは、Kisite ソースファイルが置かれているディレクトリを基準に解決します。`run()` から利用する場合は `base_dir=` を指定でき、省略時は現在の作業ディレクトリです。

## 12. 関数呼び出し: `kisite`

一般形:

```text
kisite kas <関数名> [vis <引数> (kasta <引数>)*]
```

例:

```kisite
Kisite kas greet vis "hello".
Sonome kas n tas Kisite kas minika vis s.
```

引数が0個なら `vis` を省略します。

関数呼び出しは式として使えます。戻り値を使わない場合は文として単独でも書けます。

## 13. 関数定義: `kalivisku musope`

一般形:

```text
kalivisku musope kas <関数名> [vis <仮引数> (kasta <仮引数>)*] {
    <文>
    ...
}
```

例:

```kisite
Kalivisku musope kas add vis a kasta b {
    Jasepe kas a + b.
}
```

関数呼び出しごとにローカル変数領域を作ります。呼び出し元の変数を暗黙には参照しません。再帰呼び出しは可能です。

## 14. 戻り値: `jasepe`

```kisite
Jasepe kas <式>.
```

関数をそこで終了し、式の値を呼び出し元へ返します。関数外で使うとエラーです。

## 15. 組み込み関数

### 15.1 `minika`

```kisite
Kisite kas minika vis "123"
Kisite kas minika vis "2.5"
```

数値または数値を表す文字列を数値へ変換します。

### 15.2 `kipala`

配列・文字列・`pilika` 範囲の長さを返します。

```kisite
Kisite kas kipala vis [1, 2, 3]
Kisite kas kipala vis "abc"
```

### 15.3 `pilika`

`range` 相当です。

```kisite
Kisite kas pilika vis stop
Kisite kas pilika vis start kasta stop
Kisite kas pilika vis start kasta stop kasta step
```

引数は整数で、`step` は0にできません。終了値 `stop` は含みません。

例:

```kisite
Pilike kas i pas Kisite kas pilika vis 2 kasta 10 kasta 2 {
    Takute kas i.
}
```

`2, 4, 6, 8` を順に出力します。

## 16. 予約語

少なくとも次の語は通常の変数名として使用できません。

```text
takute
sonome
kemese
polike
pilike
putike
kinise
kinate
kisite
kalivisku
musope
jasepe
minika
kipala
pilika
takuta
kineska
kati
kixkati
kix
kate
palusta
japalusta
kasta
vista
kas
tas
pas
pasta
vis
vos
stdin
```

キーワードの大文字・小文字は区別されません。通常の変数名・ユーザー定義関数名は区別されます。

## 17. 実行方法

```powershell
python kisite.py path/to/program.kis
python kisite.py --version
python -m unittest discover -s tests
```

## 18. 現在未実装の主な機能

0.0.12 までの「主な未実装」一覧にあった次の項目は 0.0.13 で実装されました。

- 論理演算
- 配列の長さ取得
- 配列への追加・削除
- `break` / `continue` 相当
- `range` 相当
- `stdin` 以外の入力ストリーム
- 明示的な型指定
- 真偽値リテラル
- `else if` 相当

今後の候補には、整数除算・剰余、ソート、配列スライス、辞書/集合、出力ストリーム、より細かい型などがあります。

## 19. 設計上の対応関係

| Kisite | 現在の役割 |
|---|---|
| `takute` | 出力 |
| `sonome` | 変数の初期化 |
| `kemese` | 値の設定 |
| `pasta` | 型注釈 |
| `kate` | 等値比較 |
| `kasta` | 論理 AND / 複数項目の区切り |
| `vista` | 論理 OR |
| `kix` | 論理 NOT |
| `kati`, `kixkati` | true / false |
| `palusta` | 条件 |
| `japalusta` | else 側 |
| `japalusta palusta` | else-if |
| `pilike` | 繰り返し |
| `kinise` | break / 配列要素の削除 |
| `kinate` | continue |
| `putike` | 配列への追加 |
| `polike` | 入力 |
| `kisite` | 関数の実行・呼び出し |
| `kalivisku musope` | 関数定義 |
| `jasepe` | 関数から値を返す |
| `minika` | 数値への明示変換 |
| `kipala` | 長さ取得 |
| `pilika` | range 相当 |
| `pas` | foreach の対象領域 |
| `vis` | 関数の引数側 |
| `vos` | 読み取り元 |
