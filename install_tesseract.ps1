#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

$default = "C:\Program Files\Tesseract-OCR\tesseract.exe"

if ((Get-Command tesseract -ErrorAction SilentlyContinue) -or (Test-Path $default)) {
    Write-Host "tesseract is already installed."
    exit 0
}

if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Installing tesseract via winget..."
    winget install --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements
} else {
    Write-Host "winget not found."
    Write-Host "Install tesseract manually: https://github.com/UB-Mannheim/tesseract/wiki"
    exit 1
}

Write-Host ""
Write-Host "Done. English language data is included by default."
Write-Host "VexConverter auto-detects the tessdata folder, so no PATH or TESSDATA_PREFIX setup is required."
Write-Host "Restart your terminal to use the 'tesseract' command directly."
