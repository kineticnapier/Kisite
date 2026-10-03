# Kisite チートシート

[ガイド](README.md) · [言語仕様](spec.md) · [English](../en/cheatsheet.md)

**Kisite 0.0.14** のクイックリファレンスです。

## 基本

```kisite
# コメント
Takute kas "Hello World".
```

- キーワードは大文字・小文字を区別しません。
- 変数名とユーザー定義関数名は大文字・小文字を区別します。
- 文末は通常 `.` または `。` です。

## 値

```kisite
123
3.14
"hello"
Kati       # true
Jakati     # false
[1, 2, 3]
```

## 変数と実行時型

```kisite
Sonome kas x tas 0.                    # 初期化
Kemese kas x tas x + 1.                # 代入

Sonome kas n sis minika tas 0.         # 数値
Sonome kas s sis takuta tas "abc".    # 文字列
Sonome kas a sis kineska tas [1, 2].   # 配列
Sonome kas b sis kati tas Kati.        # 真偽値
```

## 算術・比較・論理

```kisite
x + y
x - y
x * y
x / y

x kate y
x != y
x < y
x <= y
x > y
x >= y

a kasta b    # AND
a vista b    # OR
Kix a        # NOT
```

`kasta` と `vista` は真偽値のみを受け取り、短絡評価します。

### 優先順位

高い順:

1. `(...)`、添字 `[...]`
2. 単項 `+`、`-`、`kix`
3. `*`、`/`
4. `+`、`-`
5. `kate`、`!=`、`<`、`<=`、`>`、`>=`
6. `kasta`
7. `vista`

## 出力

```kisite
Takute kas x.
```

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

条件式は真偽値である必要があります。

## ループ

### while 相当

```kisite
Pilike palusta x < 10 {
    Kemese kas x tas x + 1.
}
```

### foreach 相当

```kisite
Pilike kas x pas items {
    Takute kas x.
}
```

配列、文字列、`pilika` が返す範囲を反復できます。

### break / continue

```kisite
Kinise.   # break
Kinate.   # continue
```

## 配列と添字

```kisite
Sonome kas a tas [10, 20, 30].
Takute kas a[0].
Kemese kas a[1] tas 99.

Putike kas 40 tas a.   # 末尾へ追加
Kinise kas a[1].       # 要素を削除
```

- 添字は0始まりです。
- 添字は0以上の整数のみです。
- 文字列も読み取り専用で添字アクセスできます。

## 入力

```kisite
Polike kas x vos stdin.
Polike kas a kasta b kasta c vos stdin.
```

`polike` は空白区切りの入力を必ず **文字列** として読みます。

数値が必要なら明示的に変換します。

```kisite
Polike kas raw vos stdin.
Sonome kas n tas Kisite kas minika vis raw.
```

ファイルから読む場合:

```kisite
Polike kas x vos "input.txt".
```

同じファイルを複数回読むと、1回の実行中は読み取り位置を引き継ぎます。

## 関数

### 定義

```kisite
Kalivisku musope kas add vis a kasta b {
    Jasepe kas a + b.
}
```

### 呼び出し

```kisite
Kisite kas add vis 2 kasta 3
```

### 引数0個

```kisite
Kisite kas foo
```

関数内の変数はローカルで、再帰呼び出しもできます。

`kasta` は論理 AND と関数引数区切りを兼ねます。AND式を1個の引数として渡す場合は括弧で囲みます。

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

### `pilika` — range 相当

```kisite
Kisite kas pilika vis 5
Kisite kas pilika vis 2 kasta 6
Kisite kas pilika vis 2 kasta 10 kasta 2
```

形としては Python の `range(stop)`、`range(start, stop)`、`range(start, stop, step)` に対応します。`stop` は含みません。

## よくある注意

- `Polike` の戻り値は文字列。数値が必要なら `minika` を使う。
- 真偽値リテラルは `Kati` / `Jakati`。
- 条件式に暗黙の truthy / falsy 判定はない。
- 実行時型注釈は `sis`。
- `kasta` は論理 AND だけでなく、複数入力・仮引数・実引数の区切りにも使う。
- 配列・文字列の添字は0始まりで、負の添字は未対応。
- `Kinise.` は break、`Kinise kas a[i].` は配列要素の削除。
