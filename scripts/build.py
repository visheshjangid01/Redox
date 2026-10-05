"""Build a standalone `redox` executable (redox.exe on Windows) into dist/.

The result bundles Python itself, so it runs on machines without Python.
PyInstaller can't cross-compile: build on Linux for Linux, on Windows for Windows.

    python scripts/build.py
"""
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).resolve().parent.parent

PyInstaller.__main__.run([
    str(ROOT / "src" / "redox" / "cli.py"),
    "--name", "redox",
    "--onefile",
    "--console",
    "--clean",
    "--noconfirm",
    "--log-level", "WARN",
    "--paths", str(ROOT / "src"),
    "--distpath", str(ROOT / "dist"),
    "--workpath", str(ROOT / "build"),
    "--specpath", str(ROOT / "build"),
])
