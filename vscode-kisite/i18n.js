const vscode = require('vscode');

const JA = vscode.env.language.toLowerCase().startsWith('ja');

const STRINGS = {
    en: {
        openKisiteFile: 'Open a .kis file before running Kisite.',
        saveBeforeRun: 'Save the Kisite file before running it.',
        interpreterMissing: path => `Configured Kisite interpreter was not found: ${path}`,
        interpreterNotFound: 'Could not find kisite.py. Set kisite.interpreterPath in VS Code settings.',
        runTask: 'Run Kisite',
        runCompiledTask: 'Run Kisite (Compiled)',
        runTooltip: 'Run Kisite',
        compiledTooltip: 'Run Kisite with the compiled backend',
        keywordDetail: 'Kisite keyword',
        typeDetail: 'Kisite type',
        builtinDetail: 'Kisite builtin',
        functionDetail: 'Function in this file',
        variableDetail: 'Variable in this file',
        builtinLabel: 'Kisite builtin',
        builtins: {
            readint: 'Read one integer from stdin.',
            readints: 'Read integers from stdin.',
            kipala: 'Return the length of a collection.',
            pilika: 'Create a range-like sequence / count helper.',
            paline: 'Return a sorted array.',
            japonavi: 'Return the minimum value.',
            ponavi: 'Return the maximum value.',
            fill: 'Create an array filled with a value.',
            convolution: 'Convolution modulo the supported modulus.',
            flush: 'Flush interactive output.',
            heappush: 'Push a value onto a heap.',
            heappop: 'Pop the minimum value from a heap.',
            heappeek: 'Read the minimum value from a heap.',
            bisectleft: 'Find the left insertion position in a sorted array.',
            bisectright: 'Find the right insertion position in a sorted array.'
        }
    },
    ja: {
        openKisiteFile: 'Kisite を実行するには .kis ファイルを開いてください。',
        saveBeforeRun: '実行する前に Kisite ファイルを保存してください。',
        interpreterMissing: path => `設定された Kisite インタープリターが見つかりません: ${path}`,
        interpreterNotFound: 'kisite.py が見つかりません。VS Code の設定で kisite.interpreterPath を指定してください。',
        runTask: 'Kisite を実行',
        runCompiledTask: 'Kisite をコンパイル実行',
        runTooltip: 'Kisite を実行',
        compiledTooltip: 'コンパイル済みバックエンドで Kisite を実行',
        keywordDetail: 'Kisite キーワード',
        typeDetail: 'Kisite 型',
        builtinDetail: 'Kisite 組み込み関数',
        functionDetail: 'このファイル内の関数',
        variableDetail: 'このファイル内の変数',
        builtinLabel: 'Kisite 組み込み関数',
        builtins: {
            readint: '標準入力から整数を1つ読み取ります。',
            readints: '標準入力から複数の整数を読み取ります。',
            kipala: 'コレクションの長さを返します。',
            pilika: '範囲状の列を作成する補助関数です。',
            paline: '配列をソートして返します。',
            japonavi: '最小値を返します。',
            ponavi: '最大値を返します。',
            fill: '指定した値で埋めた配列を作成します。',
            convolution: '対応する法のもとで畳み込みを計算します。',
            flush: '対話出力を即座にフラッシュします。',
            heappush: 'ヒープに値を追加します。',
            heappop: 'ヒープから最小値を取り出します。',
            heappeek: 'ヒープの最小値を取り出さずに確認します。',
            bisectleft: 'ソート済み配列で左側の挿入位置を返します。',
            bisectright: 'ソート済み配列で右側の挿入位置を返します。'
        }
    }
};

const t = JA ? STRINGS.ja : STRINGS.en;

function localizeParserMessage(message) {
    if (!JA) {
        return message;
    }

    let match = message.match(/^expected (.+), got (.+)$/);
    if (match) {
        return `${match[1]} が必要ですが、${match[2]} でした`;
    }
    match = message.match(/^'(.+)' is reserved and cannot be a variable name$/);
    if (match) {
        return `「${match[1]}」は予約語のため変数名に使えません`;
    }
    match = message.match(/^'(.+)' is reserved and cannot be a function name$/);
    if (match) {
        return `「${match[1]}」は予約語のため関数名に使えません`;
    }
    match = message.match(/^unsupported type '(.+)'$/);
    if (match) {
        return `未対応の型です: ${match[1]}`;
    }
    match = message.match(/^unsupported statement '(.+)'$/);
    if (match) {
        return `未対応の文です: ${match[1]}`;
    }
    match = message.match(/^unexpected character (.+)$/);
    if (match) {
        return `予期しない文字です: ${match[1]}`;
    }
    if (message === 'unterminated string') {
        return '文字列が閉じられていません';
    }
    if (message === 'unterminated block') {
        return 'ブロックが閉じられていません';
    }
    if (message === 'japalusta must follow a palusta block') {
        return 'Japalusta は Palusta ブロックの直後に置く必要があります';
    }
    match = message.match(/^function '(.+)' has duplicate parameter names$/);
    if (match) {
        return `関数「${match[1]}」に重複した引数名があります`;
    }
    return message;
}

module.exports = {
    isJapanese: JA,
    t,
    localizeParserMessage,
};
