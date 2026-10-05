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
        meaning: { ja: 'もし', en: 'if' },
        role: { ja: '条件分岐を開始します。', en: 'Starts a conditional branch.' },
        example: 'Palusta x > 0 { Takute kas x. }'
    },
    japalusta: {
        meaning: { ja: 'そうでなければ', en: 'else' },
        role: { ja: 'Palusta に続く else / else-if 分岐です。', en: 'Introduces an else or else-if branch after Palusta.' },
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
        meaning: { ja: '場所 / 状態 / 時間を広く表す語', en: 'broad place / state / time relation' },
        role: { ja: 'foreach の反復対象や membership (`in`) を表します。', en: 'Marks foreach iteration sources and membership (`in`).' },
        example: 'Pilike kas x pas xs { ... }'
    },
    sis: {
        meaning: { ja: '〜として / 型マーカー', en: 'as / type marker' },
        role: { ja: '変数の型注釈を導入します。', en: 'Introduces a variable type annotation.' },
        example: 'Sonome kas x sis minika tas 0.'
    },
    vis: {
        meaning: { ja: '〜を介して / 〜によって', en: 'via / by' },
        role: { ja: '関数定義・関数呼び出しの引数列を開始します。', en: 'Starts the parameter/argument list of a function definition or call.' },
        example: 'Kisite kas add vis x kasta y'
    },
    vos: {
        meaning: { ja: '〜から', en: 'from' },
        role: { ja: '入力元を指定します。', en: 'Specifies an input source.' },
        example: 'Polike kas raw vos stdin.'
    },
    kasta: {
        meaning: { ja: 'そして / and', en: 'and' },
        role: { ja: '論理 AND。また、引数・変数などの並びの区切りにも使います。', en: 'Logical AND, and also a separator for arguments, parameters, and names.' },
        example: 'Kisite kas add vis x kasta y'
    },
    vista: {
        meaning: { ja: 'または / or', en: 'or' },
        role: { ja: '論理 OR を表します。', en: 'Logical OR.' },
        example: 'Palusta a vista b { ... }'
    },
    kix: {
        meaning: { ja: '否定', en: 'negation' },
        role: { ja: '真偽値を反転する論理 NOT です。', en: 'Logical NOT for boolean values.' },
        example: 'Palusta kix done { ... }'
    },
    kate: {
        meaning: { ja: '〜である / 等しい', en: 'is / equal' },
        role: { ja: '等値比較を表します。', en: 'Equality comparison.' },
        example: 'Palusta x kate 0 { ... }'
    },
    tuni: {
        meaning: { ja: '真 / 実', en: 'true / real' },
        role: { ja: '真を表す真偽値リテラルです。', en: 'Boolean true literal.' },
        example: 'Sonome kas ok tas Tuni.'
    },
    jatuni: {
        meaning: { ja: '偽', en: 'false' },
        role: { ja: '偽を表す真偽値リテラルです。', en: 'Boolean false literal.' },
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
        meaning: { ja: '現実 / 真偽', en: 'reality / truth' },
        role: { ja: 'Kisite の真偽値型名です。', en: 'Kisite boolean type name.' },
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
