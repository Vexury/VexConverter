import re
from pathlib import Path

try:
    import fitz
    _PDF_AVAILABLE = True
except ImportError:
    _PDF_AVAILABLE = False

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".ico", ".avif"}
VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm", ".flv", ".m4v", ".ts", ".mts"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus"}
PDF_EXTS   = {".pdf"}

IMAGE_OUTPUTS = ["jpg", "png", "webp", "avif", "gif", "bmp", "tiff", "pdf", "ico"]
VIDEO_OUTPUTS = ["mp4", "mkv", "webm", "avi", "mov", "gif", "webp", "mp3", "wav", "flac", "aac", "ogg", "srt", "vtt", "frame"]
AUDIO_OUTPUTS = ["mp3", "wav", "flac", "aac", "ogg", "opus", "m4a", "aiff"]
URL_OUTPUTS   = ["mp4", "mp3", "wav", "flac", "opus"]
PDF_OUTPUTS   = ["png", "jpg", "webp", "extract"]

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def detect(value: str) -> dict:
    """
    Given a filename or URL, return:
      { input_type, detected_format, available_outputs }
    Returns input_type=None if unrecognised.
    """
    if _URL_RE.match(value.strip()):
        return {
            "input_type": "url",
            "detected_format": "url",
            "available_outputs": URL_OUTPUTS,
        }

    ext = Path(value).suffix.lower()

    if ext in IMAGE_EXTS:
        return {
            "input_type": "image",
            "detected_format": ext.lstrip("."),
            "available_outputs": IMAGE_OUTPUTS,
        }
    if ext in VIDEO_EXTS:
        return {
            "input_type": "video",
            "detected_format": ext.lstrip("."),
            "available_outputs": VIDEO_OUTPUTS,
        }
    if ext in AUDIO_EXTS:
        return {
            "input_type": "audio",
            "detected_format": ext.lstrip("."),
            "available_outputs": AUDIO_OUTPUTS,
        }
    if ext in PDF_EXTS and _PDF_AVAILABLE:
        return {
            "input_type": "pdf",
            "detected_format": "pdf",
            "available_outputs": PDF_OUTPUTS,
        }

    return {"input_type": None, "detected_format": None, "available_outputs": []}
