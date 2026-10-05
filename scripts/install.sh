#!/usr/bin/env bash
# Build Redox and install the `redox` command for the current user (Linux/macOS).
#   ./scripts/install.sh              -> installs to ~/.local/bin
#   PREFIX=/usr/local/bin sudo -E ./scripts/install.sh   -> system-wide
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -x .venv/bin/python ]; then
    echo "==> Creating virtual environment"
    python3 -m venv .venv
fi
PY=.venv/bin/python

echo "==> Installing build tools"
"$PY" -m pip install -q -e ".[build]"

echo "==> Building executable"
"$PY" scripts/build.py

DEST="${PREFIX:-$HOME/.local/bin}"
mkdir -p "$DEST"
install -m 755 dist/redox "$DEST/redox"
echo "==> Installed: $DEST/redox"

case ":$PATH:" in
    *":$DEST:"*) echo "Done! Run 'redox' to start." ;;
    *) echo "Note: $DEST is not on your PATH. Add this to ~/.bashrc (or ~/.zshrc):"
       echo "    export PATH=\"$DEST:\$PATH\"" ;;
esac
