const { spawn } = require('child_process');
const path = require('path');
const vscode = require('vscode');
const { t, localizeParserMessage } = require('./i18n');

const KEYWORDS = [
    'Takute', 'Sonome', 'Kemese', 'Polike', 'Pilike', 'Putike',
    'Kinise', 'Kinate', 'Kisite', 'Kalivisku', 'musope', 'Jasepe',
    'Palusta', 'Japalusta', 'kas', 'tas', 'pas', 'sis', 'vis', 'vos',
    'kasta', 'vista', 'kix', 'kate', 'stdin', 'Tuni', 'Jatuni',
];

const TYPES = ['minika', 'takuta', 'kineska', 'tuna', 'kati'];

const BUILTINS = [
    'minika', 'kipala', 'pilika', 'paline', 'japonavi', 'ponavi',
    'sum', 'abs', 'fill', 'reverse', 'resize', 'truncate', 'combinations',
    'gcd', 'lcm', 'set', 'array', 'readint', 'readints',
    'modint', 'modpow', 'modinv', 'convolution',
    'flush', 'pi', 'sin', 'cos', 'tan', 'sqrt', 'atan2', 'hypot',
    'floor', 'ceil', 'heapify', 'heappush', 'heappop', 'heappeek',
    'bisectleft', 'bisectright',
];

const BUILTIN_DETAILS = new Map(Object.entries(t.builtins));

function wordRange(document, position) {
    return document.getWordRangeAtPosition(position, /[A-Za-z_][A-Za-z0-9_]*/);
}

function collectDefinitions(document) {
    const definitions = new Map();
    const functions = new Map();
    const text = document.getText();
    const lines = text.split(/\r?\n/);

    const functionPattern = /\bKalivisku\s+musope\s+kas\s+([A-Za-z_][A-Za-z0-9_]*)/gi;
    const initPattern = /\bSonome\s+kas\s+(.+?)\s+(?:sis\s+[A-Za-z_][A-Za-z0-9_]*\s+)?tas\b/i;
    const foreachPattern = /\bPilike\s+kas\s+(.+?)\s+pas\b/i;

    for (let line = 0; line < lines.length; line += 1) {
        const raw = lines[line];
        const code = raw.replace(/#.*$/, '');

        functionPattern.lastIndex = 0;
        let functionMatch;
        while ((functionMatch = functionPattern.exec(code)) !== null) {
            const name = functionMatch[1];
            const column = functionMatch.index + functionMatch[0].lastIndexOf(name);
            const location = new vscode.Location(
                document.uri,
                new vscode.Position(line, column)
            );
            functions.set(name, location);
            definitions.set(name, location);

            const tail = code.slice(functionMatch.index + functionMatch[0].length);
            const params = tail.match(/^\s+vis\s+(.+?)\s*\{/i);
            if (params) {
                for (const namePart of params[1].split(/\s+kasta\s+/i)) {
                    const param = namePart.trim();
                    if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(param) && !definitions.has(param)) {
                        const paramColumn = code.indexOf(param, functionMatch.index);
                        definitions.set(
                            param,
                            new vscode.Location(document.uri, new vscode.Position(line, paramColumn))
                        );
                    }
                }
            }
        }

        const initMatch = initPattern.exec(code);
        if (initMatch) {
            const names = initMatch[1].split(/\s+kasta\s+/i);
            for (const item of names) {
                const name = item.trim();
                if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(name) && !definitions.has(name)) {
                    const column = code.indexOf(name, initMatch.index);
                    definitions.set(
                        name,
                        new vscode.Location(document.uri, new vscode.Position(line, column))
                    );
                }
            }
        }

        const foreachMatch = foreachPattern.exec(code);
        if (foreachMatch) {
            for (const item of foreachMatch[1].split(/\s+kasta\s+/i)) {
                const name = item.trim();
                if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(name) && !definitions.has(name)) {
                    const column = code.indexOf(name, foreachMatch.index);
                    definitions.set(
                        name,
                        new vscode.Location(document.uri, new vscode.Position(line, column))
                    );
                }
            }
        }
    }

    return { definitions, functions };
}

function completionItems(document) {
    const { definitions, functions } = collectDefinitions(document);
    const items = [];

    for (const keyword of KEYWORDS) {
        const item = new vscode.CompletionItem(keyword, vscode.CompletionItemKind.Keyword);
        item.detail = t.keywordDetail;
        items.push(item);
    }
    for (const type of TYPES) {
        const item = new vscode.CompletionItem(type, vscode.CompletionItemKind.TypeParameter);
        item.detail = t.typeDetail;
        items.push(item);
    }
    for (const name of BUILTINS) {
        const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Function);
        item.detail = t.builtinDetail;
        item.documentation = BUILTIN_DETAILS.get(name) || `${t.builtinLabel}: ${name}`;
        items.push(item);
    }
    for (const [name] of functions) {
        const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Function);
        item.detail = t.functionDetail;
        items.push(item);
    }
    for (const [name] of definitions) {
        if (functions.has(name)) {
            continue;
        }
        const item = new vscode.CompletionItem(name, vscode.CompletionItemKind.Variable);
        item.detail = t.variableDetail;
        items.push(item);
    }
    return items;
}

function makeParserCommand(interpreter) {
    const interpreterDir = path.dirname(interpreter);
    const script = [
        'import sys',
        `sys.path.insert(0, ${JSON.stringify(interpreterDir)})`,
        'import kisite',
        'import kisite_syntax as s',
        'import kisite_parser as p',
        'src = sys.stdin.read()',
        'try:',
        '    p.Parser(s.tokenize(src)).parse()',
        'except Exception as exc:',
        '    print(str(exc), file=sys.stderr)',
        '    raise SystemExit(2)',
    ].join('\n');
    return script;
}

function parseError(stderr) {
    const text = stderr.trim();
    const match = text.match(/(?:^|\n)(\d+):(\d+):\s*(.+?)(?:\n|$)/);
    if (!match) {
        return null;
    }
    return {
        line: Math.max(0, Number(match[1]) - 1),
        column: Math.max(0, Number(match[2]) - 1),
        message: localizeParserMessage(match[3].trim()),
    };
}

function validateDocument(document, diagnostics, findInterpreter) {
    if (document.languageId !== 'kisite' || document.isClosed) {
        return;
    }
    const config = vscode.workspace.getConfiguration('kisite', document.uri);
    if (!config.get('diagnostics.enabled', true)) {
        diagnostics.delete(document.uri);
        return;
    }

    let interpreter;
    try {
        interpreter = findInterpreter(document);
    } catch (error) {
        diagnostics.set(document.uri, []);
        return;
    }

    const pythonPath = config.get('pythonPath', 'python');
    let child;
    try {
        child = spawn(
            pythonPath,
            ['-c', makeParserCommand(interpreter)],
            { cwd: path.dirname(interpreter), stdio: ['pipe', 'ignore', 'pipe'], windowsHide: true }
        );
    } catch (error) {
        diagnostics.set(document.uri, []);
        return;
    }

    let stderr = '';
    let spawnFailed = false;

    // A parser process can exit before the editor finishes writing stdin. On Windows
    // that may surface as EPIPE. Streams emit "error" events; without handlers an
    // EPIPE can terminate the entire Extension Host process.
    if (child.stdin) {
        child.stdin.on('error', () => {});
    }
    if (child.stderr) {
        child.stderr.setEncoding('utf8');
        child.stderr.on('data', chunk => { stderr += chunk; });
        child.stderr.on('error', () => {});
    }

    child.on('error', () => {
        spawnFailed = true;
        if (!document.isClosed) {
            diagnostics.set(document.uri, []);
        }
    });

    child.on('close', code => {
        if (spawnFailed || document.isClosed) {
            return;
        }
        if (code === 0) {
            diagnostics.set(document.uri, []);
            return;
        }
        const parsed = parseError(stderr);
        if (!parsed) {
            diagnostics.set(document.uri, []);
            return;
        }
        const line = Math.min(parsed.line, Math.max(0, document.lineCount - 1));
        const lineText = document.lineAt(line).text;
        const start = Math.min(parsed.column, lineText.length);
        const end = Math.min(lineText.length, start + 1);
        const diagnostic = new vscode.Diagnostic(
            new vscode.Range(line, start, line, end),
            parsed.message,
            vscode.DiagnosticSeverity.Error
        );
        diagnostic.source = 'Kisite';
        diagnostics.set(document.uri, [diagnostic]);
    });

    if (child.stdin) {
        try {
            child.stdin.end(document.getText(), 'utf8');
        } catch (error) {
            // The process may already have terminated. Its close/error handler above
            // owns the diagnostic result; never let this escape into Extension Host.
        }
    }
}

function registerLanguageFeatures(context, findInterpreter) {
    const selector = { language: 'kisite', scheme: 'file' };
    const diagnostics = vscode.languages.createDiagnosticCollection('kisite');
    context.subscriptions.push(diagnostics);

    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider(selector, {
            provideCompletionItems(document) {
                return completionItems(document);
            },
        }),
        vscode.languages.registerDefinitionProvider(selector, {
            provideDefinition(document, position) {
                const range = wordRange(document, position);
                if (!range) {
                    return undefined;
                }
                const word = document.getText(range);
                const { definitions } = collectDefinitions(document);
                return definitions.get(word);
            },
        }),
        vscode.languages.registerHoverProvider(selector, {
            provideHover(document, position) {
                const range = wordRange(document, position);
                if (!range) {
                    return undefined;
                }
                const word = document.getText(range);
                if (BUILTIN_DETAILS.has(word)) {
                    return new vscode.Hover([
                        new vscode.MarkdownString(`**${t.builtinLabel}** \`${word}\``),
                        new vscode.MarkdownString(BUILTIN_DETAILS.get(word)),
                    ]);
                }
                if (BUILTINS.includes(word)) {
                    return new vscode.Hover(`${t.builtinLabel}: \`${word}\``);
                }
                return undefined;
            },
        })
    );

    const timers = new Map();
    const schedule = document => {
        if (document.languageId !== 'kisite') {
            return;
        }
        const delay = vscode.workspace
            .getConfiguration('kisite', document.uri)
            .get('diagnostics.delay', 250);
        const key = document.uri.toString();
        const previous = timers.get(key);
        if (previous) {
            clearTimeout(previous);
        }
        timers.set(key, setTimeout(() => {
            timers.delete(key);
            validateDocument(document, diagnostics, findInterpreter);
        }, delay));
    };

    context.subscriptions.push(
        vscode.workspace.onDidOpenTextDocument(schedule),
        vscode.workspace.onDidChangeTextDocument(event => schedule(event.document)),
        vscode.workspace.onDidSaveTextDocument(schedule),
        vscode.workspace.onDidCloseTextDocument(document => {
            const key = document.uri.toString();
            const timer = timers.get(key);
            if (timer) {
                clearTimeout(timer);
                timers.delete(key);
            }
            diagnostics.delete(document.uri);
        }),
        { dispose() { for (const timer of timers.values()) clearTimeout(timer); } }
    );

    for (const document of vscode.workspace.textDocuments) {
        schedule(document);
    }
}

module.exports = {
    registerLanguageFeatures,
};
