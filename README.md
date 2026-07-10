# VexConverter

A minimal command-line tool for converting files and URLs. Drop a file or URL in, pick an output format, and it handles the rest.

## Usage

Windows:

```
bin\vex_converter.bat <file_or_url>
```

Linux / macOS:

```
bin/vex_converter.sh <file_or_url>
```

The launcher creates a virtual environment and installs dependencies on first run. The tool detects the input type automatically, lists the available output formats, and prompts you to choose. Depending on the format, you will be offered additional options:

- **Dimensions** — `1920x1080`, `1920`, `x1080`, or `60%` (images and video)
- **Trim** — start and end time in seconds or `HH:MM:SS` (video and audio)
- **Speed** — playback speed multiplier, e.g. `0.5` or `2.0` (video and audio)
- **Strip audio** — remove the audio track from a video output
- **Resolution** — max download resolution for URL video, e.g. `1080`, `720` (URL)

All options are optional — press Enter to use the default.

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org) on PATH — required for video, audio, and URL conversions
- [Tesseract](https://tesseract-ocr.github.io) — optional, enables OCR for scanned PDFs

Both are external tools. Install scripts are provided per platform, and each checks for an existing install first:

| Tool | Windows | macOS / Linux |
|------|---------|---------------|
| ffmpeg | `.\install_ffmpeg.ps1` | `./install_ffmpeg.sh` |
| Tesseract | `.\install_tesseract.ps1` | `./install_tesseract.sh` |

The Windows scripts use `winget`; the macOS / Linux scripts detect Homebrew, apt, dnf, or pacman. To install manually:

- **ffmpeg** — **Windows** `winget install Gyan.FFmpeg`, **macOS** `brew install ffmpeg`, **Linux** `sudo apt install ffmpeg`
- **Tesseract** — **Windows** `winget install UB-Mannheim.TesseractOCR`, **macOS** `brew install tesseract`, **Linux** `sudo apt install tesseract-ocr`

Tesseract is only needed for the PDF `ocr` output and the OCR fallback on scanned PDFs; VexConverter auto-detects it, so no `PATH` or `TESSDATA_PREFIX` setup is required.

## Conversions

### Image
Input: `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp` `.tiff` `.tif` `.ico` `.avif` `.heic` `.heif`

| Output | Notes |
|--------|-------|
| jpg | Quality option (1–100) |
| png | |
| webp | Quality option (1–100) |
| gif | |
| bmp | |
| tiff | LZW compressed |
| pdf | |
| ico | |
| avif | |

### Video
Input: `.mp4` `.mkv` `.avi` `.mov` `.wmv` `.webm` `.flv` `.m4v` `.ts` `.mts`

| Output | Notes |
|--------|-------|
| mp4 | H.264 + AAC |
| mkv | H.264 + AAC |
| webm | VP9 (default) or VP8, codec option |
| avi | H.264 + MP3 |
| mov | H.264 + AAC |
| gif | Animated, 640px wide, FPS option (default: 10) |
| webp | Animated, 640px wide, FPS option (default: 10) |
| mp3 | Audio only |
| wav | Audio only |
| flac | Audio only, lossless |
| aac | Audio only |
| ogg | Audio only |
| srt | Subtitles, track option (default: first track) |
| vtt | Subtitles, track option (default: first track) |
| frame | Single PNG frame, time option in seconds |

### Audio
Input: `.mp3` `.wav` `.flac` `.aac` `.ogg` `.m4a` `.wma` `.opus`

| Output | Notes |
|--------|-------|
| mp3 | |
| wav | |
| flac | Lossless |
| aac | |
| ogg | |
| opus | |
| m4a | |
| aiff | Lossless |

### PDF
Input: `.pdf`

| Output | Notes |
|--------|-------|
| png | 200 DPI, page number option (default: all pages) |
| jpg | 200 DPI, page number option (default: all pages) |
| webp | 200 DPI, page number option (default: all pages) |
| text | Extracts the text layer; falls back to OCR per page when empty and Tesseract is available |
| ocr | Forces OCR on every page (requires Tesseract) |
| extract | Extracts all embedded images in their native format |

### Document
Input: `.md` `.markdown` `.html` `.htm` `.docx`

Available outputs depend on the input format:

| Input | Outputs | Notes |
|-------|---------|-------|
| Markdown (`.md`, `.markdown`) | pdf, html | PDF is rendered from the generated HTML |
| HTML (`.html`, `.htm`) | pdf, txt | txt strips tags to plain text |
| DOCX (`.docx`) | pdf, html, txt, md | PDF is rendered from the document's HTML, not a faithful reproduction of Word's page layout |

### URL
Input: any URL supported by yt-dlp (YouTube, Vimeo, and many more)

| Output | Notes |
|--------|-------|
| mp4 | Resolution option (default: best available) |
| mp3 | Audio only |
| wav | Audio only |
| flac | Audio only, lossless |
| opus | Audio only |

## Building a standalone executable

Two Windows build scripts bundle the tool into a single `dist\vex_converter.exe` with [PyInstaller](https://pyinstaller.org). Each sets up a `.venv`, installs dependencies, and runs the build:

| Script | PDF / document support | Binary size |
|--------|------------------------|-------------|
| `build_full.ps1` | Yes (bundles PyMuPDF, Markdown, Mammoth) | Larger |
| `build_slim.ps1` | No (excludes PyMuPDF) | Smaller |

Use `build_slim.ps1` when you don't need PDF or document conversions and want the smallest possible executable. Both bundle HEIC/HEIF image support.

## Built with

- [Pillow](https://python-pillow.org) — image conversion
- [pillow-heif](https://github.com/bigcat88/pillow_heif) — HEIC / HEIF decoding
- [PyMuPDF](https://pymupdf.readthedocs.io) — PDF rendering, text extraction, and OCR
- [Python-Markdown](https://python-markdown.github.io) — Markdown → HTML
- [Mammoth](https://github.com/mwilliamson/python-mammoth) — DOCX → HTML / Markdown
- [ffmpeg](https://ffmpeg.org) — video and audio conversion
- [Tesseract](https://tesseract-ocr.github.io) — OCR for scanned PDFs
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — URL / video site downloading
