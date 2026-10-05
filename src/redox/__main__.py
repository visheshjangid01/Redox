import sys
from redox.cli import repl, run_file, main as cli_main


def prompt_main():
    if len(sys.argv) > 1:
        return cli_main()
        
    try:
        user_input = input("Filepath: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return 0

    if not user_input:
        repl()
    else:
        run_file(user_input)
    return 0


if __name__ == "__main__":
    sys.exit(prompt_main())
