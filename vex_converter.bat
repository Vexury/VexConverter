@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo Setting up environment...
    python -m venv --upgrade-deps .venv
)

call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

python vex.py %*
