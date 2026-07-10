#!/usr/bin/env bash
set -e

if command -v tesseract >/dev/null 2>&1; then
    echo "tesseract is already installed."
    exit 0
fi

if command -v brew >/dev/null 2>&1; then
    echo "Installing tesseract via Homebrew..."
    brew install tesseract
elif command -v apt >/dev/null 2>&1; then
    echo "Installing tesseract via apt..."
    sudo apt update && sudo apt install -y tesseract-ocr
elif command -v dnf >/dev/null 2>&1; then
    echo "Installing tesseract via dnf..."
    sudo dnf install -y tesseract
elif command -v pacman >/dev/null 2>&1; then
    echo "Installing tesseract via pacman..."
    sudo pacman -S --noconfirm tesseract tesseract-data-eng
else
    echo "No supported package manager found (brew, apt, dnf, pacman)."
    echo "Install tesseract manually: https://tesseract-ocr.github.io/tessdoc/Installation.html"
    exit 1
fi

echo
echo "Done. English language data is included by default."
echo "For more languages, install the matching data package (e.g. tesseract-ocr-deu)."
echo "Restart your terminal if tesseract is not yet on PATH."
