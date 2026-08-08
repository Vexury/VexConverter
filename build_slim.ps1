#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
    Write-Host "Setting up environment..."
    python -m venv .venv
}

& .\.venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
pip install -q pyinstaller

$pyiArgs = @(
    "--onefile", "--name", "vexc",
    "--hidden-import", "converters.image",
    "--hidden-import", "converters.video",
    "--hidden-import", "converters.audio",
    "--hidden-import", "converters.pdf",
    "--hidden-import", "converters.url",
    "--collect-all", "pillow_heif",
    "--collect-all", "yt_dlp",
    "--exclude-module", "fitz",
    "--exclude-module", "pymupdf",
    "vex.py"
)
pyinstaller @pyiArgs

Write-Host ""
Write-Host "Slim build complete (no PDF or document support): dist\vexc.exe"
