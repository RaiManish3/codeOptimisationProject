# Code Optimizer for C programs
Using pycparser to accomplish replacement of sensitive snippets to more healthy ones.<br>

## Explaination
This extension is made for **vscode** . The extension uses the power of **pycparser** to generate an *AST* of C file in an active editor window.<br>
The C file may possibly contain harmful snippets which cause buffer overflow and these may write to sensitive blocks of memory.<br>.
To avoid that we replace those snippets of code with their better halfs.<br>

## Requirements
- pycparser from [https://github.com/eliben/pycparser][1].
- python shell from [https://github.com/extrabacon/python-shell][2]
- node.js.
- vscode *OFCOURCE*

## Installation
- clone the repo
- put the whole folder as decribed below:
-- Linux / Mac : $HOME/.vscode/extensions
-- Windows : %USERPROFILE%\.vscode\extensions

__Currently we are facing some issues regarding installation__

