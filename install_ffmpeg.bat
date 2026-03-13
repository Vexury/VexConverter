@echo off
where ffmpeg >nul 2>&1
if %errorlevel% == 0 (
    echo ffmpeg is already installed.
    pause
    exit /b 0
)

echo Installing ffmpeg via winget...
winget install Gyan.FFmpeg

echo.
echo Done. Restart your terminal for ffmpeg to be available on PATH.
pause
