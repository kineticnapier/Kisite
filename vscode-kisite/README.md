# Kisite for VS Code

VS Code language support for Kisite.

## Features

- `.kis` language registration
- TextMate syntax highlighting
- `#` line comments
- bracket matching and auto-closing
- block indentation
- Kisite snippets
- **Kisite: Run** command
- **Kisite: Run Compiled** command
- status-bar Run / Compiled buttons while a `.kis` file is active

The run commands execute the active file in an integrated VS Code task, so interactive Kisite programs can use stdin normally.

## Development

Open this directory as the VS Code workspace:

```powershell
code vscode-kisite
```

Then press `F5` and open a `.kis` file in the Extension Development Host.

When the `.kis` file is inside the Kisite repository, the extension walks upward from the file and automatically finds `kisite.py`.

## Settings

### `kisite.pythonPath`

Python executable used to start Kisite. Default: `python`.

Example:

```json
"kisite.pythonPath": "py"
```

### `kisite.interpreterPath`

Explicit path to `kisite.py`. Leave empty for automatic parent-directory discovery. `${workspaceFolder}` is supported.

```json
"kisite.interpreterPath": "${workspaceFolder}/kisite.py"
```

### `kisite.saveBeforeRun`

Save the active file before running. Default: `true`.

## Packaging

The extension has no runtime npm dependencies. To build a VSIX with the standard VS Code extension packaging tool:

```powershell
npx @vscode/vsce package
```
