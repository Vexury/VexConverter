#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

VENV_PY=".venv/bin/python"

if [ ! -x "$VENV_PY" ]; then
    echo "Setting up environment..."
    python3 -m venv --upgrade-deps .venv
fi

if [ ! -f ".venv/deps.stamp" ] || [ requirements.txt -nt ".venv/deps.stamp" ]; then
    echo "Installing dependencies..."
    "$VENV_PY" -m pip install -q -r requirements.txt
    touch ".venv/deps.stamp"
fi

exec "$VENV_PY" vex.py "$@"
