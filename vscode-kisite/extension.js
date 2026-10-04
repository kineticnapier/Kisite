const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

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
    const config = vscode.workspace.getConfiguration('kisite', document.uri);
    const configured = config.get('interpreterPath', '').trim();
    const workspaceFolder = workspaceFolderFor(document);

    if (configured) {
        const resolved = expandConfiguredPath(configured, workspaceFolder);
        if (!fs.existsSync(resolved)) {
            throw new Error(`Configured Kisite interpreter was not found: ${resolved}`);
        }
        return resolved;
    }

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

    throw new Error(
        'Could not find kisite.py. Set kisite.interpreterPath in VS Code settings.'
    );
}

async function runActiveFile(compiled) {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'kisite') {
        vscode.window.showErrorMessage('Open a .kis file before running Kisite.');
        return;
    }

    const document = editor.document;
    if (document.isUntitled) {
        vscode.window.showErrorMessage('Save the Kisite file before running it.');
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
    const name = compiled ? 'Run Kisite (Compiled)' : 'Run Kisite';
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

function activate(context) {
    context.subscriptions.push(
        vscode.commands.registerCommand('kisite.run', () => runActiveFile(false)),
        vscode.commands.registerCommand('kisite.runCompiled', () => runActiveFile(true))
    );

    const runItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 101);
    runItem.text = '$(play) Kisite';
    runItem.tooltip = 'Run Kisite';
    runItem.command = 'kisite.run';

    const compiledItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    compiledItem.text = '$(rocket) Compiled';
    compiledItem.tooltip = 'Run Kisite with the compiled backend';
    compiledItem.command = 'kisite.runCompiled';

    context.subscriptions.push(runItem, compiledItem);
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(() => updateStatusBars(runItem, compiledItem))
    );
    updateStatusBars(runItem, compiledItem);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate,
};
