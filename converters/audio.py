import json
import re
import shutil
import subprocess
from pathlib import Path

_CODECS = {
    "mp3":  ["-c:a", "libmp3lame", "-q:a", "2"],
    "wav":  ["-c:a", "pcm_s16le"],
    "flac": ["-c:a", "flac"],
    "aac":  ["-c:a", "aac", "-b:a", "192k"],
    "ogg":  ["-c:a", "libvorbis", "-q:a", "4"],
    "opus": ["-c:a", "libopus", "-b:a", "128k"],
    "m4a":  ["-c:a", "aac", "-b:a", "192k"],
    "aiff": ["-c:a", "pcm_s16be"],
}


def convert(input_path: str, fmt: str, opts: dict, out_dir: Path, stem: str) -> Path:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on PATH — download from https://ffmpeg.org")

    duration = _duration(input_path)
    out      = out_dir / f"{stem}.{fmt}"
    flags    = _CODECS.get(fmt, ["-c:a", "copy"])

    trim = []
    if opts.get("trim_start"):
        trim += ["-ss", opts["trim_start"]]
    if opts.get("trim_end"):
        trim += ["-to", opts["trim_end"]]

    speed = opts.get("speed")
    af_args = []
    if speed and speed != 1.0:
        s = speed
        chain = []
        while s > 2.0:
            chain.append("atempo=2.0")
            s /= 2.0
        while s < 0.5:
            chain.append("atempo=0.5")
            s *= 2.0
        chain.append(f"atempo={s:.6f}")
        af_args = ["-af", ",".join(chain)]

    print("  Converting...", end="", flush=True)
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-i", input_path] + trim + flags + af_args + [str(out)],
        stderr=subprocess.PIPE, text=True, errors="replace",
    )
    last = -1
    for line in proc.stderr:
        m = re.search(r"time=(\d+:\d+:\d+\.?\d*)", line)
        if m and duration > 0:
            pct = min(int(_ts(m.group(1)) / duration * 100), 99)
            if pct != last:
                print(f"\r  Converting... {pct:3d}%", end="", flush=True)
                last = pct
    proc.wait()
    if proc.returncode != 0:
        print()
        raise RuntimeError(f"ffmpeg exited {proc.returncode}")
    print("\r  Converting... done!   ")
    return out


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
