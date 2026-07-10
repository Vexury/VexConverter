#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
    echo "Setting up environment..."
    python3 -m venv --upgrade-deps .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

python vex.py "$@"
