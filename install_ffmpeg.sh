#!/usr/bin/env bash
set -e

if command -v ffmpeg >/dev/null 2>&1; then
    echo "ffmpeg is already installed."
    exit 0
fi

if command -v brew >/dev/null 2>&1; then
    echo "Installing ffmpeg via Homebrew..."
    brew install ffmpeg
elif command -v apt >/dev/null 2>&1; then
    echo "Installing ffmpeg via apt..."
    sudo apt update && sudo apt install -y ffmpeg
elif command -v dnf >/dev/null 2>&1; then
    echo "Installing ffmpeg via dnf..."
    sudo dnf install -y ffmpeg
elif command -v pacman >/dev/null 2>&1; then
    echo "Installing ffmpeg via pacman..."
    sudo pacman -S --noconfirm ffmpeg
else
    echo "No supported package manager found (brew, apt, dnf, pacman)."
    echo "Install ffmpeg manually: https://ffmpeg.org/download.html"
    exit 1
fi

echo
echo "Done. Restart your terminal if ffmpeg is not yet on PATH."
