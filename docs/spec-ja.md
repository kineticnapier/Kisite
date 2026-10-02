# Kisite 言語仕様（日本語）

この文書は Kisite 0.0.12 の現在の実装仕様をまとめたものです。

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

真偽値リテラルはまだありません。`kate` や比較演算の結果として得られ、表示時は `true` / `false` になります。

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
sonome kas <変数名> tas <式>
```

同じスコープで再初期化するとエラーです。

### 4.2 設定: `kemese`

```kisite
Kemese kas x tas x + 1.
Kemese kas a[0] tas 10.
```

```text
kemese kas <代入先> tas <式>
```

## 5. 算術と比較

算術演算子は `+ - * /` です。

比較は `kate`, `!=`, `<`, `>`, `<=`, `>=` を使います。`< > <= >=` は現在数値同士のみです。

優先順位は高い順に、おおむね:

1. 括弧 `(...)`、添字 `[...]`
2. 単項 `+` / `-`
3. `*` / `/`
4. `+` / `-`
5. `kate`, `!=`, `<`, `>`, `<=`, `>=`

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

条件は真偽値である必要があります。`japalusta` は直前の `palusta` に属します。

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

反復対象は配列または文字列です。

## 10. 入力: `polike`

```kisite
Polike kas x vos stdin.
Polike kas a kasta b kasta c vos stdin.
```

入力は空白文字で区切られます。

### 10.1 0.0.12 の非互換変更

0.0.12 以降、`polike` が読み取る値は **必ず文字列** です。

入力が

```text
101
```

なら、

```kisite
Polike kas S vos stdin.
```

の `S` は数値 `101` ではなく文字列 `"101"` です。

数値化が必要なら `minika` を明示的に呼び出します。

```kisite
Polike kas s vos stdin.
Sonome kas n tas Kisite kas minika vis s.
```

`minika` は整数として解釈できれば整数を返し、それ以外では実数への変換を試みます。変換できない文字列はエラーです。

## 11. 関数呼び出し: `kisite`

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

複雑な式の中で呼び出し結果にさらに演算を続ける場合は、境界を明確にするため括弧を使うことを推奨します。

```kisite
Takute kas (Kisite kas twice vis 5) + 1.
```

## 12. 関数定義: `kalivisku musope`

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

同名関数の再定義はエラーです。組み込み関数 `minika` は再定義できません。

関数は実行時に定義されるため、通常は呼び出しより前に定義を書きます。再帰呼び出しは可能です。

### 12.1 関数スコープ

関数呼び出しごとにローカル変数領域を作ります。

- 仮引数はローカル変数です。
- 関数内の `sonome` もローカルです。
- 呼び出し元の同名変数は上書きされません。
- 呼び出し元の変数を暗黙には参照しません。必要な値は引数で渡します。

配列は可変オブジェクトなので、配列そのものを引数として渡して要素を書き換えた場合、その配列への変更は呼び出し元からも見えます。

## 13. 戻り値: `jasepe`

```kisite
Jasepe kas <式>.
```

関数をそこで終了し、式の値を呼び出し元へ返します。

```kisite
Kalivisku musope kas square vis x {
    Jasepe kas x * x.
}
```

`jasepe` を関数外で使うとエラーです。

戻り値のない関数は文として呼び出せますが、その呼び出しを式として値が必要な場所で使うとエラーです。

## 14. 組み込み関数

### 14.1 `minika`

```kisite
Kisite kas minika vis "123"
Kisite kas minika vis "2.5"
```

数値または数値を表す文字列を数値へ変換します。引数は1個です。

## 15. 予約語

少なくとも次の語は変数名として使用できません。

```text
takute
sonome
kemese
polike
pilike
kisite
kalivisku
musope
jasepe
minika
kate
palusta
japalusta
kasta
kas
tas
pas
vis
vos
stdin
```

キーワードの大文字・小文字は区別されません。通常の変数名・ユーザー定義関数名は区別されます。

## 16. 実行方法

```powershell
python kisite.py path/to/program.kis
python kisite.py --version
python -m unittest discover -s tests
```

## 17. 現在未実装の主な機能

- 論理演算
- 配列の長さ取得
- 配列への追加・削除
- `break` / `continue` 相当
- `range` 相当
- `stdin` 以外のストリーム
- 明示的な型指定
- 真偽値リテラル
- `else if` 専用構文

## 18. 設計上の対応関係

| Kisite | 現在の役割 |
|---|---|
| `takute` | 出力 |
| `sonome` | 変数の初期化 |
| `kemese` | 値の設定 |
| `kate` | 等値比較 |
| `palusta` | 条件 |
| `japalusta` | else 側 |
| `pilike` | 繰り返し |
| `polike` | 入力 |
| `kisite` | 関数の実行・呼び出し |
| `kalivisku musope` | 関数定義 |
| `jasepe` | 関数から値を返す |
| `minika` | 数値への明示変換 |
| `kasta` | 複数項目の連結 |
| `pas` | foreach の対象領域 |
| `vis` | 関数の引数側 |
| `vos` | 読み取り元 |
