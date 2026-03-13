import re
import shutil
import subprocess
from pathlib import Path


def convert(input_url: str, fmt: str, opts: dict, out_dir: Path, stem: str) -> Path:
    ytdlp = shutil.which("yt-dlp") or "yt-dlp"

    template = str(out_dir / "%(title)s.%(ext)s")
    base     = [ytdlp, "--no-playlist", "--newline"]

    if fmt in ("mp3", "wav", "flac", "opus"):
        cmd = base + ["-x", "--audio-format", fmt, "-o", template, input_url]
    else:
        cmd = base + ["-f", "bestvideo+bestaudio/best",
                      "--merge-output-format", fmt, "-o", template, input_url]

    print("  Downloading...", end="", flush=True)
    proc  = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, errors="replace")
    lines = []
    last  = -1
    for line in proc.stdout:
        line = line.strip()
        lines.append(line)
        m = re.search(r"\[download\]\s+(\d+\.?\d*)%", line)
        if m:
            pct = min(10 + round(float(m.group(1)) * 0.8), 90)
            if pct != last:
                print(f"\r  Downloading... {pct:3d}%", end="", flush=True)
                last = pct

    proc.wait()
    if proc.returncode != 0:
        print()
        raise RuntimeError("yt-dlp failed:\n" + "\n".join(lines[-10:]))

    print("\r  Downloading... done!   ")

    # Find the output file (yt-dlp names it after the video title)
    candidates = sorted(
        [f for f in out_dir.iterdir()
         if f.is_file() and f.suffix.lower().lstrip(".") == fmt],
        key=lambda f: f.stat().st_mtime, reverse=True,
    )
    if not candidates:
        raise RuntimeError("Downloaded file not found.")
    return candidates[0]
