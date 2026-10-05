# Kisite for VS Code

VS Code language support for Kisite.

## Features

- `.kis` language registration
- TextMate syntax highlighting
- `#` line comments
- bracket matching and auto-closing
- block indentation
- Kisite snippets
- completion for keywords, types, builtins, functions, and variables
- go to definition for functions and local definitions
- hover help for selected builtins
- parser-backed syntax diagnostics using the real Kisite parser
- **Kisite: Run** command
- **Kisite: Run Compiled** command
- status-bar Run / Compiled buttons while a `.kis` file is active

The run commands execute the active file in an integrated VS Code task, so interactive Kisite programs can use stdin normally.

Parser diagnostics do not execute the program. The extension sends the current unsaved document text to a short Python process that imports the local Kisite parser and only parses the source.

## Development

Open this directory as the VS Code workspace:

```powershell
code vscode-kisite
```

Then press `F5` and open a `.kis` file in the Extension Development Host.

When the `.kis` file is inside the Kisite repository, the extension walks upward from the file and automatically finds `kisite.py`.

Useful checks in the Extension Development Host:

- type part of `Sonome`, `readint`, or a local variable and invoke completion
- place the cursor on a local function/variable and press `F12`
- introduce a syntax error such as an unterminated block and confirm a Kisite diagnostic appears
- hover over builtins such as `readint`, `convolution`, or `bisectleft`

## Settings

### `kisite.pythonPath`

Python executable used to start Kisite and parser diagnostics. Default: `python`.

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

### `kisite.diagnostics.enabled`

Enable parser-backed error diagnostics. Default: `true`.

### `kisite.diagnostics.delay`

Debounce delay in milliseconds before parsing after an edit. Default: `250`.

## Packaging

The extension has no runtime npm dependencies. To build a VSIX with the standard VS Code extension packaging tool:

```powershell
npx @vscode/vsce package
```
