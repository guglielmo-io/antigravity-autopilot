#!/usr/bin/env bash
# Antigravity Auto-Retry Patch — Linux launcher
# Usage: ./patch_antigravity.sh [--root /path] [--all] [--check] [--restore] [--print-paths]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/patch_antigravity.py"

if [ ! -f "$PY_SCRIPT" ]; then
    echo "[ERROR] patch_antigravity.py not found in $SCRIPT_DIR"
    exit 1
fi

for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        exec "$cmd" "$PY_SCRIPT" "$@"
    fi
done

echo "[ERROR] Python not found. Install python3 and try again."
exit 1
