import json
import re
import shutil
import subprocess
from pathlib import Path

_AUDIO = {
    "mp3":  ["-c:a", "libmp3lame", "-q:a", "2"],
    "wav":  ["-c:a", "pcm_s16le"],
    "flac": ["-c:a", "flac"],
    "aac":  ["-c:a", "aac", "-b:a", "192k"],
    "ogg":  ["-c:a", "libvorbis", "-q:a", "4"],
}
_VIDEO = {
    "mp4":  ["-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-movflags", "+faststart"],
    "mkv":  ["-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac"],
    "avi":  ["-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "mp3"],
    "webm": ["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", "-c:a", "libopus"],
    "mov":  ["-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac"],
}


def _scale_vf(dims) -> str:
    if isinstance(dims, float):
        return f"scale=iw*{dims}:ih*{dims}"
    w, h = dims
    return f"scale={w if w else '-2'}:{h if h else '-2'}"


def convert(input_path: str, fmt: str, opts: dict, out_dir: Path, stem: str) -> Path:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on PATH — download from https://ffmpeg.org")

    duration = _duration(input_path)

    dims = opts.get("dims")

    if fmt == "frame":
        t      = opts.get("time_t", 0)
        out    = out_dir / f"{stem}_frame.png"
        vf     = ["-vf", _scale_vf(dims)] if dims else []
        r      = subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", input_path, "-frames:v", "1"] + vf + [str(out)],
            capture_output=True,
        )
        if r.returncode != 0:
            raise RuntimeError(r.stderr.decode(errors="replace")[-500:])
        print("  Extracted frame.")
        return out

    if fmt in ("srt", "vtt"):
        track = opts.get("track", 0)
        out   = out_dir / f"{stem}.{fmt}"
        r     = subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-map", f"0:s:{track}", str(out)],
            capture_output=True,
        )
        if r.returncode != 0:
            raise RuntimeError("No subtitle track found — video may not contain subtitles.")
        print("  Extracted subtitles.")
        return out

    if fmt in _AUDIO:
        out = out_dir / f"{stem}.{fmt}"
        _ffmpeg(["ffmpeg", "-y", "-i", input_path, "-vn"] + _AUDIO[fmt] + [str(out)], duration)
        return out

    if fmt == "gif":
        fps     = opts.get("fps", 10)
        scale   = f"{_scale_vf(dims)}:flags=lanczos" if dims else "scale=640:-1:flags=lanczos"
        palette = out_dir / f"{stem}_palette.png"
        out     = out_dir / f"{stem}.gif"
        print("  Building palette...", end="", flush=True)
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path,
             "-vf", f"fps={fps},{scale},palettegen", str(palette)],
            capture_output=True, check=True,
        )
        print(" done!")
        _ffmpeg(
            ["ffmpeg", "-y", "-i", input_path, "-i", str(palette),
             "-filter_complex", f"fps={fps},{scale}[x];[x][1:v]paletteuse",
             "-loop", "0", str(out)],
            duration, label="  Encoding GIF",
        )
        palette.unlink(missing_ok=True)
        return out

    if fmt == "webp":
        fps   = opts.get("fps", 10)
        scale = _scale_vf(dims) if dims else "scale=640:-1"
        out   = out_dir / f"{stem}.webp"
        _ffmpeg(
            ["ffmpeg", "-y", "-i", input_path,
             "-vf", f"fps={fps},{scale}:flags=lanczos",
             "-c:v", "libwebp", "-quality", "75", "-loop", "0", "-preset", "picture", "-an",
             str(out)],
            duration, label="  Encoding WebP",
        )
        return out

    out      = out_dir / f"{stem}.{fmt}"
    flags    = _VIDEO.get(fmt, ["-c:v", "libx264", "-crf", "23", "-c:a", "aac"])
    scale_args = ["-vf", _scale_vf(dims)] if dims else []
    _ffmpeg(["ffmpeg", "-y", "-i", input_path] + flags + scale_args + [str(out)], duration)
    return out


def _ffmpeg(cmd: list, duration: float, label: str = "  Converting") -> None:
    print(f"{label}...", end="", flush=True)
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True, errors="replace")
    last = -1
    for line in proc.stderr:
        m = re.search(r"time=(\d+:\d+:\d+\.?\d*)", line)
        if m and duration > 0:
            pct = min(int(_ts(m.group(1)) / duration * 100), 99)
            if pct != last:
                print(f"\r{label}... {pct:3d}%", end="", flush=True)
                last = pct
    proc.wait()
    if proc.returncode != 0:
        print()
        raise RuntimeError(f"ffmpeg exited {proc.returncode}")
    print(f"\r{label}... done!   ")


def _duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True,
    )
    try:
        return float(json.loads(r.stdout).get("format", {}).get("duration", 0))
    except Exception:
        return 0.0


def _ts(s: str) -> float:
    m = re.match(r"(\d+):(\d+):(\d+\.?\d*)", s)
    if m:
        h, mi, sec = m.groups()
        return int(h) * 3600 + int(mi) * 60 + float(sec)
    return 0.0
