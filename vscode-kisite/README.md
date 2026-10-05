# Kisite for VS Code

VS Code language support for Kisite, backed by a persistent Python Language Server that uses the real Kisite tokenizer and parser.

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
- scope-aware symbol resolution matching Kisite's function-local runtime model
- Document Highlight for the resolved symbol under the cursor
- Signature Help while entering `vis ... kasta ...` arguments
- Semantic Tokens for keywords, functions, builtins, variables, parameters, and type annotations
- Document Symbols / Outline with function-local children
- Workspace Symbols across indexed `.kis` files
- automatic workspace re-indexing when `.kis` files are created, changed, or deleted
- Folding Ranges for Kisite blocks and consecutive comment lines
- Inlay Hints with parameter names for simple function/builtin calls
- Code Actions / Quick Fixes for selected parser errors such as unterminated blocks and strings
- Japanese identifiers in the language server index
- UTF-16-aware source positions for VS Code/LSP correctness
- Japanese UI / hover text when VS Code uses a Japanese locale
- **Kisite: Run** command
- **Kisite: Run Compiled** command
- status-bar Run / Compiled buttons while a `.kis` file is active

The editor features are provided by a persistent Python Language Server over stdio LSP. The server imports the local Kisite implementation and reuses `tokenize` and `Parser`; editing does not launch a new Python process for every diagnostic pass.

Kisite functions do not capture global variables at runtime, so the language server intentionally resolves local variables and parameters per function. A same-named variable in another function is a different symbol for F12, references, rename, highlighting, completion, and semantic coloring.

Workspace indexing covers multiple `.kis` files for Workspace Symbols. Kisite does not currently have a module/import system, so the language server does not pretend that unrelated files share runtime functions or variables.

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
- define `x` independently in two functions and verify F12/F2/Shift+F12 stay inside the correct function
- hover over `minika`, `convolution`, `bisectleft`, or a user-defined function
- place the cursor on a symbol and confirm all matching occurrences in its scope highlight
- type a call such as `Kisite kas add vis 1 kasta 2` and verify Signature Help and parameter-name Inlay Hints
- confirm functions, parameters, variables, builtins, keywords, and `sis` type annotations receive semantic coloring
- introduce an unterminated block/string and open Quick Fix (`Ctrl+.`)
- fold `{ ... }` blocks and consecutive `#` comment runs
- open the Outline view and confirm function-local symbols appear beneath functions
- use **Go to Symbol in Workspace** and search symbols from multiple `.kis` files

## Architecture

```text
VS Code
  |
  | vscode-languageclient / stdio LSP
  v
Kisite Language Server (Python)
  |
  +-- Kisite tokenizer + parser
  +-- scope-aware symbol graph
  +-- workspace .kis index
  +-- diagnostics + quick fixes
  +-- completion / hover
  +-- definitions / references / rename / highlights
  +-- signature help / inlay hints
  +-- semantic tokens
  +-- document + workspace symbols
  +-- folding ranges
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

Standard VS Code settings such as `editor.inlayHints.enabled` and semantic-highlighting/theme settings control the corresponding LSP UI features.

## Tests

Language-server analysis and IDE feature tests:

```powershell
cd F:\dev\Kisite
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
cd vscode-kisite
npm install
npx @vscode/vsce package
```
