#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "ffmpeg is already installed."
    exit 0
}

if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Installing ffmpeg via winget..."
    winget install --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
} else {
    Write-Host "winget not found."
    Write-Host "Install ffmpeg manually: https://ffmpeg.org/download.html"
    exit 1
}

Write-Host ""
Write-Host "Done. Restart your terminal if ffmpeg is not yet on PATH."
