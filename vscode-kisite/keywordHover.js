const vscode = require('vscode');

const JA = vscode.env.language.toLowerCase().startsWith('ja');

// `meaning` is only filled where the Lisatopa meaning is already established.
// Do not guess vocabulary here: words with an uncertain lexical origin still get
// a Kisite grammar-role explanation, but no claimed Lisatopa translation.
const DOCS = {
    takute: {
        meaning: { ja: '言う / 表示する', en: 'say / show' },
        role: { ja: '値を出力します。', en: 'Outputs a value.' },
        example: 'Takute kas value.'
    },
    sonome: {
        meaning: { ja: '初期化する', en: 'initialize' },
        role: { ja: '変数を初期化します。', en: 'Initializes variables.' },
        example: 'Sonome kas x tas 0.'
    },
    kemese: {
        meaning: { ja: '設定する', en: 'set' },
        role: { ja: '既存の変数・要素へ値を設定します。', en: 'Sets an existing variable or element.' },
        example: 'Kemese kas x tas 10.'
    },
    polike: {
        meaning: { ja: '読む / 読み取る', en: 'read / scan' },
        role: { ja: '入力元から値を読み取ります。', en: 'Reads values from an input source.' },
        example: 'Polike kas raw vos stdin.'
    },
    pilike: {
        meaning: { ja: '繰り返す / 複製する', en: 'repeat / copy' },
        role: { ja: 'Kisite では while / foreach の反復構文を開始します。', en: 'Starts while/foreach repetition in Kisite.' },
        example: 'Pilike kas x pas xs { Takute kas x. }'
    },
    putike: {
        meaning: { ja: '加える', en: 'add' },
        role: { ja: '配列や集合へ値を追加します。', en: 'Adds a value to an array or set.' },
        example: 'Putike kas value tas xs.'
    },
    kinise: {
        meaning: { ja: '切る / 削除する / 中断する', en: 'cut / delete / break' },
        role: { ja: 'ループを抜ける、または要素を削除します。', en: 'Breaks a loop or deletes an element.' },
        example: 'Kinise.'
    },
    kinate: {
        meaning: { ja: '続ける', en: 'continue' },
        role: { ja: '現在の反復を打ち切り、次の反復へ進みます。', en: 'Continues with the next loop iteration.' },
        example: 'Kinate.'
    },
    kisite: {
        meaning: { ja: '処理する', en: 'process' },
        role: { ja: '関数・組み込み関数の呼び出しを開始します。', en: 'Starts a function or builtin call.' },
        example: 'Kisite kas add vis x kasta y'
    },
    kalivisku: {
        meaning: { ja: '意味的に / 意味を定めるように', en: 'semantically / in a meaning-defining way' },
        grammar: { ja: '`kalivi` に副詞化の語素 `-sku` が付いた形です。`kalivi musopa` は「定義」。', en: 'An adverbial form built from `kalivi` with the adverbializing element `-sku`; `kalivi musopa` means “definition”.' },
        role: { ja: '`musope`（決める）を修飾し、`Kalivisku musope` 全体で「意味を定める → 定義する」として関数定義を開始します。', en: 'Modifies `musope` (“decide/set”), so `Kalivisku musope` means “define” and starts a function definition.' },
        example: 'Kalivisku musope kas add vis x kasta y { Jasepe kas x + y. }'
    },
    musope: {
        meaning: { ja: '決まる / 決める / 約束する', en: 'be decided / decide / promise' },
        grammar: { ja: '動詞。`musope kas X` で「X を決める」と表せます。', en: 'Verb. `musope kas X` can express “decide/set X”.' },
        role: { ja: '`Kalivisku musope` の一部として「定義する」を表し、関数名を `kas` の後に取ります。', en: 'As part of `Kalivisku musope`, expresses “define” and takes the function name after `kas`.' },
        example: 'Kalivisku musope kas add { Jasepe kas 0. }'
    },
    jasepe: {
        meaning: { ja: '返す', en: 'return' },
        role: { ja: '関数から値を返します。', en: 'Returns a value from a function.' },
        example: 'Jasepe kas value.'
    },
    palusta: {
        meaning: { ja: 'もし / もし〜 / もしも〜 / 〜ならば', en: 'if / if ... / provided that' },
        grammar: { ja: '接続詞。条件を導入します。', en: 'A conjunction introducing a condition.' },
        role: { ja: '条件分岐を開始します。', en: 'Starts a conditional branch.' },
        example: 'Palusta x > 0 { Takute kas x. }'
    },
    japalusta: {
        meaning: { ja: '〜ことがない限り / 〜しない限り / もし〜しないなら', en: 'unless / if ... not' },
        grammar: { ja: '接続詞。莉語本来では否定条件を導入します。', en: 'A conjunction introducing a negative condition in Lisatopa.' },
        role: { ja: 'Kisite では `Palusta` に続く else / else-if 分岐として使います。莉語本来の語義とは役割が少し異なります。', en: 'In Kisite, introduces an else or else-if branch after `Palusta`; this differs somewhat from its original Lisatopa meaning.' },
        example: 'Japalusta { Takute kas 0. }'
    },
    kas: {
        meaning: { ja: '〜を', en: 'object marker / accusative' },
        grammar: { ja: '対格を表す助詞。対象につけます。', en: 'An accusative particle attached to the object.' },
        role: { ja: '文や命令の対象を導入します。出力する値、初期化する変数名、関数名などの前に置かれます。', en: 'Introduces the object of a statement or command, such as an output value, initialized variable name, or function name.' },
        examples: [
            'Takute kas value.',
            'Sonome kas x tas 0.',
            'Kisite kas add vis x kasta y'
        ]
    },
    tas: {
        meaning: { ja: '〜に', en: 'to' },
        grammar: { ja: '方向・到達先を表す前置詞。英語の `to` に近い語です。', en: 'A preposition marking direction or destination, similar to English `to`.' },
        role: { ja: 'Kisite では初期化・代入・追加などの代入先・到達先を示します。', en: 'In Kisite, marks the destination/target of initialization, assignment, or insertion.' },
        example: 'Sonome kas x tas 0.'
    },
    pas: {
        meaning: { ja: '〜で / 〜に / 〜にて / 〜の中で', en: 'at / in / within' },
        grammar: { ja: '場所・位置・内部を表す前置詞です。', en: 'A preposition marking place, position, or being within something.' },
        role: { ja: 'Kisite では反復対象・所属先を示します。`x pas xs` の「xs の中で x」という関係から、foreach と membership (`in`) に使われます。', en: 'In Kisite, marks an iteration source or membership container. The relation in `x pas xs` is used for foreach and membership (`in`).' },
        example: 'Pilike kas x pas xs { ... }'
    },
    sis: {
        meaning: { ja: '〜として / 〜という / 〜である', en: 'as / called / being' },
        grammar: { ja: '前置詞。身分・名称・性質などを示します。', en: 'A preposition marking role, name, or identity/property.' },
        role: { ja: 'Kisite では型注釈を導入し、「x を minika として扱う」のように型を示します。', en: 'In Kisite, introduces a type annotation, treating a value as a given type.' },
        example: 'Sonome kas x sis minika tas 0.'
    },
    vis: {
        meaning: { ja: '〜によって / 〜を使って / 〜のせいで', en: 'by / using / because of' },
        grammar: { ja: '手段・原因・作用主などを表す前置詞です。', en: 'A preposition marking means, cause, or agent.' },
        role: { ja: 'Kisite では関数定義・関数呼び出しで、引数を「〜を使って処理する」ための引数列として導入します。', en: 'In Kisite, introduces function parameters/arguments as the values used by a function call or definition.' },
        example: 'Kisite kas add vis x kasta y'
    },
    vos: {
        meaning: { ja: '〜から', en: 'from' },
        role: { ja: '入力元を指定します。', en: 'Specifies an input source.' },
        example: 'Polike kas raw vos stdin.'
    },
    kasta: {
        meaning: { ja: 'そして / 〜と', en: 'and / with' },
        grammar: { ja: '接続詞。語や節を並列につなぎます。', en: 'A conjunction joining words or clauses in coordination.' },
        role: { ja: 'Kisite では論理 AND を表すほか、引数・変数などの並びの区切りにも使います。', en: 'In Kisite, represents logical AND and also separates arguments, parameters, and names.' },
        example: 'Kisite kas add vis x kasta y'
    },
    vista: {
        meaning: { ja: 'もしくは / または / あるいは / つまり', en: 'or / alternatively / in other words' },
        grammar: { ja: '接続詞。選択・言い換えなどを表します。', en: 'A conjunction expressing alternatives or restatement.' },
        role: { ja: 'Kisite では論理 OR を表します。', en: 'In Kisite, represents logical OR.' },
        example: 'Palusta a vista b { ... }'
    },
    kix: {
        meaning: { ja: '否定', en: 'negation' },
        role: { ja: '真偽値を反転する論理 NOT です。', en: 'Logical NOT for boolean values.' },
        example: 'Palusta kix done { ... }'
    },
    kate: {
        meaning: { ja: '〜である', en: 'be / is' },
        grammar: { ja: '動詞。莉語ではコピュラとして「〜である」を表します。', en: 'A verb functioning as a copula meaning “be”.' },
        role: { ja: 'Kisite では等値比較として使います。莉語本来の「〜である」を比較演算に対応させています。', en: 'In Kisite, used for equality comparison, extending the Lisatopa copular meaning into a comparison operator.' },
        example: 'Palusta x kate 0 { ... }'
    },
    tuni: {
        meaning: { ja: '本当な / 本当の / 現実的な / 実際の', en: 'true / real / actual' },
        grammar: { ja: '形容詞。真実性・現実性を表します。', en: 'An adjective expressing truth or reality.' },
        role: { ja: 'Kisite では真を表す真偽値リテラルです。', en: 'In Kisite, the boolean true literal.' },
        example: 'Sonome kas ok tas Tuni.'
    },
    jatuni: {
        meaning: { ja: '偽りな / 虚偽な', en: 'false / untrue' },
        grammar: { ja: '形容詞。偽・虚偽を表します。', en: 'An adjective expressing falsity.' },
        role: { ja: 'Kisite では偽を表す真偽値リテラルです。', en: 'In Kisite, the boolean false literal.' },
        example: 'Sonome kas ok tas Jatuni.'
    },
    stdin: {
        role: { ja: '標準入力を表す予約語です。', en: 'Reserved word for standard input.' },
        example: 'Polike kas raw vos stdin.'
    },
    takuta: {
        role: { ja: 'Kisite の文字列型名です。', en: 'Kisite string type name.' },
        example: 'Sonome kas text sis takuta tas "hello".'
    },
    kineska: {
        role: { ja: 'Kisite の配列型名です。', en: 'Kisite array type name.' },
        example: 'Sonome kas xs sis kineska tas [1, 2, 3].'
    },
    tuna: {
        meaning: { ja: '現実', en: 'reality' },
        grammar: { ja: '名詞。現実を表します。', en: 'A noun meaning reality.' },
        role: { ja: 'Kisite では真偽値型名として使います。`tuni` / `jatuni` を値として持つ型です。', en: 'In Kisite, used as the boolean type name whose values are `tuni` and `jatuni`.' },
        example: 'Sonome kas ok sis tuna tas Tuni.'
    }
};

function localized(value) {
    if (!value) return undefined;
    return JA ? value.ja : value.en;
}

function renderHover(word, doc) {
    const title = JA ? 'Kisite 予約語' : 'Kisite reserved word';
    const roleTitle = JA ? 'Kisite での役割' : 'Role in Kisite';
    const meaningTitle = JA ? '莉語での語義' : 'Lisatopa meaning';
    const grammarTitle = JA ? '文法' : 'Grammar';
    const exampleTitle = JA ? '例' : 'Example';
    const parts = [`**${title}: \`${word}\`**`];
    const meaning = localized(doc.meaning);
    if (meaning) {
        parts.push(`**${meaningTitle}:** ${meaning}`);
    }
    const grammar = localized(doc.grammar);
    if (grammar) {
        parts.push(`**${grammarTitle}:** ${grammar}`);
    }
    parts.push(`**${roleTitle}:** ${localized(doc.role)}`);
    const examples = doc.examples || (doc.example ? [doc.example] : []);
    if (examples.length) {
        parts.push(`**${exampleTitle}:**\n\n\`\`\`kisite\n${examples.join('\n')}\n\`\`\``);
    }
    return new vscode.MarkdownString(parts.join('\n\n'));
}

function registerKeywordHover(context) {
    const provider = vscode.languages.registerHoverProvider(
        { language: 'kisite', scheme: 'file' },
        {
            provideHover(document, position) {
                const range = document.getWordRangeAtPosition(position, /[\p{L}_][\p{L}\p{N}_]*/u);
                if (!range) return undefined;
                const raw = document.getText(range);
                const doc = DOCS[raw.toLowerCase()];
                if (!doc) return undefined;
                return new vscode.Hover(renderHover(raw, doc), range);
            },
        }
    );
    context.subscriptions.push(provider);
}

module.exports = { registerKeywordHover };
