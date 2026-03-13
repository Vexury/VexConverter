from pathlib import Path

import yt_dlp

_AUDIO_FMTS = {"mp3", "wav", "flac", "opus"}


class _SilentLogger:
    def debug(self, msg): pass
    def info(self, msg):  pass
    def warning(self, msg): pass
    def error(self, msg): pass


def convert(input_url: str, fmt: str, opts: dict, out_dir: Path, stem: str) -> Path:
    template = str(out_dir / "%(title)s.%(ext)s")
    last_pct  = [-1]

    def _progress(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            done  = d.get("downloaded_bytes", 0)
            if total > 0:
                pct = min(10 + round(done / total * 80), 90)
                if pct != last_pct[0]:
                    print(f"\r  Downloading... {pct:3d}%", end="", flush=True)
                    last_pct[0] = pct

    def _pp_hook(d):
        if d["status"] == "started":
            name = d.get("postprocessor", "")
            if "Merge" in name:
                print("\r  Merging streams...      ", end="", flush=True)
            else:
                print("\r  Converting...           ", end="", flush=True)

    common = {
        "outtmpl":            template,
        "noplaylist":         True,
        "quiet":              True,
        "no_warnings":        True,
        "logger":             _SilentLogger(),
        "progress_hooks":     [_progress],
        "postprocessor_hooks": [_pp_hook],
    }

    if fmt in _AUDIO_FMTS:
        ydl_opts = {**common,
            "format":         "bestaudio/best",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": fmt}],
        }
    else:
        h      = opts.get("max_height")
        fmt_sel = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]" if h else "bestvideo+bestaudio/best"
        ydl_opts = {**common,
            "format":               fmt_sel,
            "merge_output_format":  fmt,
            "postprocessor_args":   {"merger": ["-c:v", "copy", "-c:a", "aac"]},
        }

    print("  Downloading...", end="", flush=True)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([input_url])
    except yt_dlp.utils.DownloadError as e:
        print()
        raise RuntimeError(str(e))

    print("\r  Done!                   ")

    candidates = sorted(
        [f for f in out_dir.iterdir()
         if f.is_file() and f.suffix.lower().lstrip(".") == fmt],
        key=lambda f: f.stat().st_mtime, reverse=True,
    )
    if not candidates:
        raise RuntimeError("Downloaded file not found.")
    return candidates[0]
