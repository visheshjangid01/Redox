# Redox

A small programming language I made for fun.

I'm a student and wanted to see how programming languages actually work, so I started building one in Python. It's nothing serious, just a side project I keep adding stuff to whenever I learn something new. Expect bugs 🙂

## Install

This builds a standalone `redox` executable (Python bundled inside) and puts it on your PATH. You only need Python 3.10+ to *build* it.

**Linux / macOS**

```bash
git clone https://github.com/visheshjangid01/Redox.git
cd Redox
./scripts/install.sh            # installs to ~/.local/bin/redox
```

**Windows** (PowerShell)

```powershell
git clone https://github.com/visheshjangid01/Redox.git
cd Redox
powershell -ExecutionPolicy Bypass -File scripts\install.ps1
```

Then open a new terminal and you're good to go.

## Usage

Open the REPL:

```
$ redox
Redox 0.1.0  -  type 'exit' to quit
>>> x -> 5
>>> x * 2
10
>>> exit
```

Run a file:

```bash
redox examples/hello.rdx
```

Other flags: `redox --version`, `redox --help`, `redox --debug file.rdx` (full Python tracebacks).

## The syntax, quickly

### Variables

```
name -> "Redox"     # mutable variable
pi => 3.14          # constant, can't be reassigned
count -> 1
count +> 4          # compound assign: +> -->  *>  />  //>  %>
```

### Printing

```
out("hello", name, count)
```

### Operators

```
2 + 3 * 4           # 14
7 // 2              # 3
"a" + 1             # 'a1'
[1, 2, 3] - [2]     # [1, 3]
x = 5               # equality is a single '='
x != 3
```

### If / elseif / else

```
if count > 10:
    out("big")
elseif count = 5:
    out("five!")
else:
    out("small")
```

### Loops

```
loop for [1, 2, 3] as i:
    out("item", i)

k -> 0
loop while k < 3:
    k +> 1
    out("k is", k)
```

### Literals

`true` / `false` / `null` (or the shorthands `t`, `f`, `n`), numbers, `"strings"`, `[lists]`, `{sets}` and `(tuples)`. Comments start with `#`.

> Heads up: since `t`, `f` and `n` are shorthands, you can't use them as variable names.

## Project layout

```
src/redox/
├── cli.py          # the `redox` command: REPL + file runner
├── __main__.py     # entry for `python -m redox` and the executable
├── memory.py       # environments / scopes and blocks
└── core/
    ├── tools.py       # tokenizer (Splitter) + helpers
    ├── parser.py      # values, operators, block parsing
    ├── depopulate.py  # evaluator + keywords (if, loop...)
    └── reserved.py    # operators and keywords
scripts/
├── build.py        # builds dist/redox (or redox.exe) with PyInstaller
├── install.sh      # build + install on Linux/macOS
└── install.ps1     # build + install on Windows
```


If you don't want to install anything at all, you can run the code directly from the source directory. This will prompt you for a `Filepath:` (leave blank to open the REPL):

**Linux / macOS:**
```bash
PYTHONPATH=src python -m redox
```

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH="src"; python -m redox
```

To uninstall the app, just delete `~/.local/bin/redox` (or `%LOCALAPPDATA%\Programs\Redox` on Windows).

## AI disclosure

The language itself (tokenizer, parser, evaluator) is written by me. I used AI tools to help with a few parts:

- Writing the installation scripts for Linux and Windows
- Testing edge cases and simulating different inputs
- Helping track down and fix bugs
- Formatting the project and writing this README

## License

GPL-2.0. See [LICENSE](LICENSE).
