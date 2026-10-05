# Kisite for VS Code

VS Code language support for Kisite, backed by a Python Language Server that uses the real Kisite tokenizer and parser.

## Features

- `.kis` language registration
- TextMate syntax highlighting
- `#` line comments
- bracket matching and auto-closing
- block indentation
- Kisite snippets
- LSP-backed completion for keywords, builtins, functions, parameters, and variables
- parser-backed syntax diagnostics using the real Kisite parser
- hover documentation and function signatures
- Go to Definition (`F12`)
- Find All References (`Shift+F12`)
- Rename Symbol (`F2`)
- Signature Help while entering `vis ... kasta ...` arguments
- Document Symbols / Outline
- Japanese identifiers in the language server index
- Japanese UI / hover text when VS Code uses a Japanese locale
- **Kisite: Run** command
- **Kisite: Run Compiled** command
- status-bar Run / Compiled buttons while a `.kis` file is active

The editor features are provided by a persistent Python Language Server over LSP. The server imports the local Kisite implementation and reuses `tokenize` and `Parser`; editing no longer launches a new Python process for every diagnostic pass.

The run commands still execute the active file in an integrated VS Code task, so interactive Kisite programs can use stdin normally.

## Development

Install the VS Code Language Client dependency once:

```powershell
cd vscode-kisite
npm install
```

Then open the extension directory:

```powershell
code .
```

Press `F5` and open a `.kis` file in the Extension Development Host.

When developing inside the Kisite repository, the extension automatically finds the repository's `kisite.py`. When installed elsewhere, it searches upward from the active `.kis` file, or you can configure `kisite.interpreterPath` explicitly.

Useful checks in the Extension Development Host:

- type part of `Sonome`, `readint`, a local function, or a local variable and invoke completion
- hover over `minika`, `convolution`, `bisectleft`, or a user-defined function
- place the cursor on a local function/variable and press `F12`
- press `Shift+F12` to list references
- press `F2` on a user-defined symbol and rename it
- type a call such as `Kisite kas add vis 1 kasta ...` and verify Signature Help
- introduce a syntax error and confirm a Kisite diagnostic appears
- open the Outline view and confirm functions/variables appear

## Architecture

```text
VS Code
  |
  | vscode-languageclient / stdio LSP
  v
Kisite Language Server (Python)
  |
  +-- Kisite tokenizer
  +-- Kisite parser
  +-- symbol index
  +-- diagnostics
  +-- completion
  +-- hover
  +-- definitions / references / rename
  +-- signature help
  +-- document symbols
```

The language server implementation is in:

```text
vscode-kisite/server/kisite_lsp.py
```

It intentionally has no third-party Python dependencies.

## Settings

### `kisite.pythonPath`

Python executable used to run Kisite and the language server. Default: `python`.

Example:

```json
"kisite.pythonPath": "py"
```

### `kisite.interpreterPath`

Explicit path to `kisite.py`. Leave empty for automatic discovery. `${workspaceFolder}` is supported.

```json
"kisite.interpreterPath": "${workspaceFolder}/kisite.py"
```

### `kisite.saveBeforeRun`

Save the active file before running. Default: `true`.

### `kisite.diagnostics.enabled`

Show diagnostics reported by the Kisite Language Server. Default: `true`.

## Tests

Language-server analysis tests:

```powershell
python -m unittest tests.test_lsp -v
```

Function/parser regression tests, including nested calls:

```powershell
python -m unittest tests.test_functions -v
```

Full suite:

```powershell
python -m unittest discover -s tests
```

## Packaging

Install dependencies first, then build a VSIX with the standard VS Code extension packaging tool:

```powershell
npm install
npx @vscode/vsce package
```
