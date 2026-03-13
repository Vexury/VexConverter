# VexConverter

A minimal command-line tool for converting files and URLs. Drop a file or URL in, pick an output format, and it handles the rest.

## Usage

```
vex_converter.bat <file_or_url>
```

The tool detects the input type automatically, lists the available output formats, and prompts you to choose. Depending on the format, you will be offered additional options:

- **Dimensions** — `1920x1080`, `1920`, `x1080`, or `60%` (images and video)
- **Trim** — start and end time in seconds or `HH:MM:SS` (video and audio)
- **Speed** — playback speed multiplier, e.g. `0.5` or `2.0` (video and audio)
- **Strip audio** — remove the audio track from a video output
- **Resolution** — max download resolution for URL video, e.g. `1080`, `720` (URL)

All options are optional — press Enter to use the default.

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org) on PATH — required for video and audio

Run `install_ffmpeg.bat` to install ffmpeg automatically, or install it manually with `winget install Gyan.FFmpeg`.

## Conversions

### Image
Input: `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp` `.tiff` `.tif` `.ico` `.avif`

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
| webm | VP9 + Opus |
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
| extract | Extracts all embedded images in their native format |

### URL
Input: any URL supported by yt-dlp (YouTube, Vimeo, and many more)

| Output | Notes |
|--------|-------|
| mp4 | Resolution option (default: best available) |
| mp3 | Audio only |
| wav | Audio only |
| flac | Audio only, lossless |
| opus | Audio only |

## Built with

- [Pillow](https://python-pillow.org) — image conversion
- [PyMuPDF](https://pymupdf.readthedocs.io) — PDF rendering and image extraction
- [ffmpeg](https://ffmpeg.org) — video and audio conversion
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — URL / video site downloading
