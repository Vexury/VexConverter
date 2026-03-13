#!/usr/bin/env python3
"""VexConverter — convert a file or URL from the command line."""

import sys
from pathlib import Path

from core.detector import detect

# (note, tool) per input_type → format
_DETAILS: dict[str, dict[str, tuple[str, str]]] = {
    "image": {
        "jpg":  ("Quality option (1-100)", "Pillow"),
        "png":  ("",                       "Pillow"),
        "webp": ("Quality option (1-100)", "Pillow"),
        "gif":  ("",                       "Pillow"),
        "bmp":  ("",                       "Pillow"),
        "tiff": ("LZW compressed",         "Pillow"),
        "pdf":  ("",                       "Pillow"),
        "ico":  ("",                       "Pillow"),
        "avif": ("",                       "Pillow"),
    },
    "video": {
        "mp4":   ("H.264 + AAC",            "ffmpeg"),
        "mkv":   ("H.264 + AAC",            "ffmpeg"),
        "webm":  ("VP9 + Opus",             "ffmpeg"),
        "avi":   ("H.264 + MP3",            "ffmpeg"),
        "mov":   ("H.264 + AAC",            "ffmpeg"),
        "gif":   ("640px wide, FPS option", "ffmpeg"),
        "mp3":   ("Audio only",             "ffmpeg"),
        "wav":   ("Audio only",             "ffmpeg"),
        "flac":  ("Audio only, lossless",   "ffmpeg"),
        "aac":   ("Audio only",             "ffmpeg"),
        "ogg":   ("Audio only",             "ffmpeg"),
        "webp":  ("640px wide, FPS option", "ffmpeg"),
        "srt":   ("Subtitles, track option","ffmpeg"),
        "vtt":   ("Subtitles, track option","ffmpeg"),
        "frame": ("Single PNG frame",       "ffmpeg"),
    },
    "audio": {
        "mp3":  ("",         "ffmpeg"),
        "wav":  ("",         "ffmpeg"),
        "flac": ("Lossless", "ffmpeg"),
        "aac":  ("",         "ffmpeg"),
        "ogg":  ("",         "ffmpeg"),
        "opus": ("",         "ffmpeg"),
        "m4a":  ("",         "ffmpeg"),
        "aiff": ("Lossless", "ffmpeg"),
    },
    "pdf": {
        "png":     ("200 DPI", "PyMuPDF"),
        "jpg":     ("200 DPI", "PyMuPDF"),
        "webp":    ("200 DPI", "PyMuPDF"),
        "extract": ("Embedded images, native format", "PyMuPDF"),
    },
    "url": {
        "mp4":  ("Best available quality", "yt-dlp"),
        "mp3":  ("Audio only",             "yt-dlp + ffmpeg"),
        "wav":  ("Audio only",             "yt-dlp + ffmpeg"),
        "flac": ("Audio only, lossless",   "yt-dlp + ffmpeg"),
        "opus": ("Audio only",             "yt-dlp + ffmpeg"),
    },
}


def prompt_format(available: list[str], input_type: str) -> str:
    details  = _DETAILS.get(input_type, {})
    labels   = ["PNG frame" if f == "frame" else f.upper() for f in available]
    label_w  = max(len(l) for l in labels)
    note_w   = max((len(details.get(f, ("", ""))[0]) for f in available), default=0)

    for i, (fmt, label) in enumerate(zip(available, labels), 1):
        note, tool = details.get(fmt, ("", ""))
        line = f"  {i:2}) {label:<{label_w}}"
        if note_w:
            line += f"  {note:<{note_w}}"
        if tool:
            line += f"  [{tool}]"
        print(line)

    print()
    while True:
        raw = input("  Format: ").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(available):
                return available[idx]
        elif raw.lower() in available:
            return raw.lower()
        print("  Invalid — enter a number or format name.")


_NO_DIMS = {"mp3", "wav", "flac", "aac", "ogg", "opus", "m4a", "aiff", "srt", "vtt", "extract"}


def _parse_dims(raw: str) -> tuple[int | None, int | None] | float | None:
    raw = raw.lower().replace(" ", "")
    if raw.endswith("%"):
        n = raw[:-1]
        return float(n) / 100 if n.replace(".", "").isdigit() else None
    if "x" in raw:
        w, h = raw.split("x", 1)
        return (int(w) if w.isdigit() else None, int(h) if h.isdigit() else None)
    if raw.isdigit():
        return (int(raw), None)
    return None


def prompt_options(fmt: str, input_type: str) -> dict:
    opts = {}
    if fmt == "frame":
        raw = input("  Time in seconds [0]: ").strip()
        opts["time_t"] = float(raw) if raw else 0.0
    if fmt in ("gif", "webp") and input_type == "video":
        raw = input("  FPS [10]: ").strip()
        opts["fps"] = int(raw) if raw else 10
    if fmt in ("srt", "vtt"):
        raw = input("  Subtitle track [0]: ").strip()
        opts["track"] = int(raw) if raw.isdigit() else 0
    if fmt in ("jpg", "jpeg", "webp") and input_type == "image":
        raw = input("  Quality 1–100 [85]: ").strip()
        opts["quality"] = int(raw) if raw else 85
    if input_type == "pdf" and fmt != "extract":
        raw = input("  Page number [all]: ").strip()
        opts["page"] = int(raw) if raw.isdigit() else None
    if input_type in ("image", "video") and fmt not in _NO_DIMS:
        raw = input("  Dimensions WxH [original]: ").strip()
        if raw:
            opts["dims"] = _parse_dims(raw)
    return opts


def main():
    if len(sys.argv) < 2:
        print("Usage: vex_converter.bat <file_or_url>")
        sys.exit(1)

    arg = sys.argv[1]
    info = detect(arg)

    if not info["input_type"]:
        print(f"  Unsupported input: {Path(arg).suffix or arg}")
        sys.exit(1)

    input_type = info["input_type"]
    available  = info["available_outputs"]

    if input_type != "url" and not Path(arg).exists():
        print(f"  File not found: {arg}")
        sys.exit(1)

    name = arg if input_type == "url" else Path(arg).name

    print(f"\n  {name}  [{input_type}]")

    try:
        fmt  = prompt_format(available, input_type)
    except KeyboardInterrupt:
        print()
        sys.exit(0)

    opts = prompt_options(fmt, input_type)
    print()

    if input_type == "url":
        out_dir = Path.cwd()
        stem    = "output"
    else:
        p       = Path(arg).resolve()
        out_dir = p.parent
        stem    = p.stem
        if (out_dir / f"{stem}.{fmt}").resolve() == p:
            stem = f"{stem}_out"

    try:
        if input_type == "image":
            from converters.image import convert
        elif input_type == "video":
            from converters.video import convert
        elif input_type == "audio":
            from converters.audio import convert
        elif input_type == "pdf":
            from converters.pdf import convert
        else:
            from converters.url import convert

        out = convert(arg, fmt, opts, out_dir, stem)
    except Exception as exc:
        print(f"\n  Error: {exc}")
        sys.exit(1)

    print(f"  → {out}\n")


if __name__ == "__main__":
    main()
