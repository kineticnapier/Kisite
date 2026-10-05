const fs = require('fs');
const path = require('path');
const vscode = require('vscode');
const { LanguageClient } = require('vscode-languageclient/node');
const { t } = require('./i18n');

let languageClient;

function workspaceFolderFor(document) {
    return vscode.workspace.getWorkspaceFolder(document.uri);
}

function expandConfiguredPath(value, workspaceFolder) {
    let expanded = value;
    if (workspaceFolder) {
        expanded = expanded.replace(/\$\{workspaceFolder\}/g, workspaceFolder.uri.fsPath);
    }
    if (path.isAbsolute(expanded)) {
        return expanded;
    }
    if (workspaceFolder) {
        return path.resolve(workspaceFolder.uri.fsPath, expanded);
    }
    return path.resolve(expanded);
}

function findInterpreter(document) {
    const config = vscode.workspace.getConfiguration('kisite', document?.uri);
    const configured = config.get('interpreterPath', '').trim();
    const workspaceFolder = document ? workspaceFolderFor(document) : vscode.workspace.workspaceFolders?.[0];

    if (configured) {
        const resolved = expandConfiguredPath(configured, workspaceFolder);
        if (!fs.existsSync(resolved)) {
            throw new Error(t.interpreterMissing(resolved));
        }
        return resolved;
    }

    if (document && document.uri.scheme === 'file') {
        let current = path.dirname(document.uri.fsPath);
        while (true) {
            const candidate = path.join(current, 'kisite.py');
            if (fs.existsSync(candidate)) {
                return candidate;
            }
            const parent = path.dirname(current);
            if (parent === current) {
                break;
            }
            current = parent;
        }
    }

    for (const folder of vscode.workspace.workspaceFolders || []) {
        const candidate = path.join(folder.uri.fsPath, 'kisite.py');
        if (fs.existsSync(candidate)) {
            return candidate;
        }
    }

    const developmentCandidate = path.resolve(__dirname, '..', 'kisite.py');
    if (fs.existsSync(developmentCandidate)) {
        return developmentCandidate;
    }

    throw new Error(t.interpreterNotFound);
}

async function startLanguageServer(context) {
    const activeDocument = vscode.window.activeTextEditor?.document;
    let interpreter;
    try {
        interpreter = findInterpreter(
            activeDocument?.languageId === 'kisite' ? activeDocument : undefined
        );
    } catch (error) {
        console.warn('[Kisite LSP]', error instanceof Error ? error.message : String(error));
        return;
    }

    const config = vscode.workspace.getConfiguration('kisite', activeDocument?.uri);
    const pythonPath = config.get('pythonPath', 'python');
    const serverScript = context.asAbsolutePath(path.join('server', 'kisite_lsp.py'));
    const kisiteRoot = path.dirname(interpreter);
    const fileWatcher = vscode.workspace.createFileSystemWatcher('**/*.kis');
    context.subscriptions.push(fileWatcher);

    const serverOptions = {
        command: pythonPath,
        args: [
            serverScript,
            '--kisite-root', kisiteRoot,
            '--locale', vscode.env.language,
        ],
        options: {
            cwd: kisiteRoot,
            windowsHide: true,
        },
    };

    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'kisite' }],
        synchronize: {
            configurationSection: 'kisite',
            fileEvents: fileWatcher,
        },
        outputChannelName: 'Kisite Language Server',
        middleware: {
            handleDiagnostics(uri, diagnostics, next) {
                const enabled = vscode.workspace
                    .getConfiguration('kisite', uri)
                    .get('diagnostics.enabled', true);
                next(uri, enabled ? diagnostics : []);
            },
        },
    };

    languageClient = new LanguageClient(
        'kisiteLanguageServer',
        'Kisite Language Server',
        serverOptions,
        clientOptions
    );
    context.subscriptions.push(languageClient);
    await languageClient.start();
}

async function runActiveFile(compiled) {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'kisite') {
        vscode.window.showErrorMessage(t.openKisiteFile);
        return;
    }

    const document = editor.document;
    if (document.isUntitled) {
        vscode.window.showErrorMessage(t.saveBeforeRun);
        return;
    }

    const config = vscode.workspace.getConfiguration('kisite', document.uri);
    if (config.get('saveBeforeRun', true) && document.isDirty) {
        const saved = await document.save();
        if (!saved) {
            return;
        }
    }

    let interpreter;
    try {
        interpreter = findInterpreter(document);
    } catch (error) {
        vscode.window.showErrorMessage(error instanceof Error ? error.message : String(error));
        return;
    }

    const pythonPath = config.get('pythonPath', 'python');
    const args = [interpreter];
    if (compiled) {
        args.push('--compiled');
    }
    args.push(document.uri.fsPath);

    const workspaceFolder = workspaceFolderFor(document);
    const cwd = workspaceFolder ? workspaceFolder.uri.fsPath : path.dirname(document.uri.fsPath);
    const execution = new vscode.ProcessExecution(pythonPath, args, { cwd });
    const scope = workspaceFolder || vscode.TaskScope.Workspace;
    const name = compiled ? t.runCompiledTask : t.runTask;
    const task = new vscode.Task(
        { type: 'kisite', compiled },
        scope,
        name,
        'Kisite',
        execution,
        []
    );
    task.presentationOptions = {
        reveal: vscode.TaskRevealKind.Always,
        panel: vscode.TaskPanelKind.Dedicated,
        clear: true,
        focus: true,
    };

    await vscode.tasks.executeTask(task);
}

function updateStatusBars(runItem, compiledItem) {
    const editor = vscode.window.activeTextEditor;
    const visible = editor && editor.document.languageId === 'kisite';
    if (visible) {
        runItem.show();
        compiledItem.show();
    } else {
        runItem.hide();
        compiledItem.hide();
    }
}

async function activate(context) {
    context.subscriptions.push(
        vscode.commands.registerCommand('kisite.run', () => runActiveFile(false)),
        vscode.commands.registerCommand('kisite.runCompiled', () => runActiveFile(true))
    );

    const runItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 101);
    runItem.text = `$(play) ${t.runStatus}`;
    runItem.tooltip = t.runTooltip;
    runItem.command = 'kisite.run';

    const compiledItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    compiledItem.text = `$(rocket) ${t.compiledStatus}`;
    compiledItem.tooltip = t.compiledTooltip;
    compiledItem.command = 'kisite.runCompiled';

    context.subscriptions.push(runItem, compiledItem);
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(() => updateStatusBars(runItem, compiledItem))
    );
    updateStatusBars(runItem, compiledItem);

    await startLanguageServer(context);
}

async function deactivate() {
    if (languageClient) {
        await languageClient.stop();
        languageClient = undefined;
    }
}

module.exports = {
    activate,
    deactivate,
};
