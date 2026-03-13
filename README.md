# VexConverter

Command-line file and URL converter.

## Usage

```
vex_converter.bat <file_or_url>
```

The tool detects the input type, lists available output formats, and prompts you to choose.

## Requirements

- Python 3.10+
- ffmpeg on PATH (`winget install Gyan.FFmpeg`) — required for video and audio

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
| gif | 640px wide, FPS option (default 10) |
| webp | Animated, 640px wide, FPS option (default 10) |
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
| extract | Embedded images saved in their native format |

### URL (YouTube / most video sites)
Input: any URL supported by yt-dlp

| Output | Notes |
|--------|-------|
| mp4 | Best available quality |
| mp3 | Audio extracted and converted via ffmpeg |
| wav | Audio extracted and converted via ffmpeg |
| flac | Audio extracted and converted via ffmpeg |
| opus | Audio extracted and converted via ffmpeg |
