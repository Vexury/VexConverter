@echo off
setlocal
cd /d "%~dp0.."

set "VENV_PY=.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo Setting up environment...
    python -m venv --upgrade-deps .venv || exit /b 1
)

"%VENV_PY%" -c "import os,sys;s='.venv/deps.stamp';sys.exit(0 if os.path.exists(s) and os.path.getmtime(s)>=os.path.getmtime('requirements.txt') else 1)" || (
    echo Installing dependencies...
    "%VENV_PY%" -m pip install -q -r requirements.txt || exit /b 1
    copy /y requirements.txt ".venv\deps.stamp" >nul
)

"%VENV_PY%" vex.py %*
