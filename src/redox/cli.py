"""Command-line entry point for the Redox
    redox               -> start the interactive REPL
    redox <file>        -> run a Redox file
"""
import argparse
import sys
import traceback

from redox import __version__
from redox.core.depopulate import Depopulate


def evaluate(line):
    return Depopulate.evaluate(Depopulate().all(line))


def report(err, debug=False):
    if debug:
        traceback.print_exception(err)
    else:
        print(f"{type(err).__name__}: {err}", file=sys.stderr)


def repl(debug=False):
    print(f"Redox {__version__}  -  type 'exit' to quit")
    while True:
        try:
            line = input(">>> ")
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            print()
            break

        if line.strip() == "exit":
            break
        if not line.strip():
            continue

        try:
            out = evaluate(line)
        except Exception as err:
            report(err, debug)
            continue

        if out or out == False:
            print(out)


def run_file(path, debug=False):
    if not str(path).endswith(".rdx"):
        print(f"redox: invalid file type. Only '.rdx' files are supported.", file=sys.stderr)
        return 2

    def cleaner(line):
        if line.endswith('\n'):
            line = line[:-1]
        return line

    try:
        with open(path, encoding="utf-8") as f:
            content = f.readlines()
    except OSError as err:
        print(f"redox: can't open file '{path}': {err.strerror}", file=sys.stderr)
        return 2

    content = list(map(cleaner, content))
    try:
        Depopulate().line(content)
    except Exception as err:
        report(err, debug)
        return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="redox",
        description="Redox - A small programming language I made for fun.",
    )
    parser.add_argument("file", nargs="?", help="Redox file to run (omit to start the REPL)")
    parser.add_argument("-V", "--version", action="version", version=f"Redox {__version__}")
    parser.add_argument("--debug", action="store_true", help="show full Python tracebacks on errors")
    args = parser.parse_args(argv)

    if args.file:
        return run_file(args.file, args.debug)
    repl(args.debug)
    return 0


if __name__ == "__main__":
    sys.exit(main())