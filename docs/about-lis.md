# Kisite

> [!NOTE]
> これは、Kisite を莉語で説明するための試作です。語彙はできる限り公式辞書・用例にあるものを使っていますが、文章全体はまだ未添削です。

Kisite kate piniki tatema.

Kisite pase kas Lisatopaksi takuta.

Kisiteksi mana lupe vos Lisatopaksi takuta `kisite`.

Usapi nika pasale ses Kisite.

## Takute

`takute` kate takuta pasta takute.

```kisite
Takute kas "Hello World".
```

Usapi pata takute kas "Hello World".

## Sonome

```kisite
Sonome kas x tas 3.
```

Usapi pata sonome kas x tas 3.

## Kemese

```kisite
Kemese kas x tas 5.
```

Usapi pata kemese kas x tas 5.

## Kate

```kisite
Takute kas x kate 5.
```

`kate` kalive kas "〜である" pas Lisatopa.

Pas Kisite, `x kate 5` pasale kasasta x kate 5.

## Palusta / Japalusta

```kisite
Palusta x kate 5 {
    Takute kas "yes".
} Japalusta {
    Takute kas "no".
}
```

Pas Kisite, `palusta` lapi kas sapaki kisita, kasta pata kisita lupe pas `{ ... }`.

`japalusta` pase pas Kisite masasta takuta pasta "else".

## Polike

`polike` kate takuta pasta polike.

```kisite
Polike kas a kasta b vos stdin.
Takute kas a + b.
```

Usapi pata polike kas a kasta b vos stdin.

## Samana

```kisite
Polike kas a kasta b vos stdin.
Takute kas a + b.
```

Pase kas Kisite masasta kisite kas piniki sapa.
