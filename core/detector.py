import re
from pathlib import Path

try:
    import fitz
    _PDF_AVAILABLE = True
except ImportError:
    _PDF_AVAILABLE = False

try:
    import pillow_heif  # noqa: F401
    _HEIF_AVAILABLE = True
except ImportError:
    _HEIF_AVAILABLE = False

try:
    import markdown  # noqa: F401
    _MD_AVAILABLE = True
except ImportError:
    _MD_AVAILABLE = False

try:
    import mammoth  # noqa: F401
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False

HEIF_EXTS     = {".heic", ".heif"}
MARKDOWN_EXTS = {".md", ".markdown"}
HTML_EXTS     = {".html", ".htm"}
DOCX_EXTS     = {".docx"}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".ico", ".avif"}
VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm", ".flv", ".m4v", ".ts", ".mts"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus"}
PDF_EXTS   = {".pdf"}

IMAGE_OUTPUTS = ["jpg", "png", "webp", "avif", "gif", "bmp", "tiff", "pdf", "ico"]
VIDEO_OUTPUTS = ["mp4", "mkv", "webm", "avi", "mov", "gif", "webp", "mp3", "wav", "flac", "aac", "ogg", "srt", "vtt", "frame"]
AUDIO_OUTPUTS = ["mp3", "wav", "flac", "aac", "ogg", "opus", "m4a", "aiff"]
URL_OUTPUTS   = ["mp4", "mp3", "wav", "flac", "opus"]
PDF_OUTPUTS   = ["png", "jpg", "webp", "text", "extract"]

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def _document_outputs(ext: str) -> list[str]:
    """Available document outputs for a given input extension, gated on installed libs."""
    if ext in MARKDOWN_EXTS:
        return (["pdf"] if _PDF_AVAILABLE else []) + ["html"]
    if ext in HTML_EXTS:
        return (["pdf"] if _PDF_AVAILABLE else []) + ["txt"]
    if ext in DOCX_EXTS:
        return (["pdf"] if _PDF_AVAILABLE else []) + ["html", "txt", "md"]
    return []


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

    if ext in IMAGE_EXTS or (ext in HEIF_EXTS and _HEIF_AVAILABLE):
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

    is_doc = (
        (ext in MARKDOWN_EXTS and _MD_AVAILABLE)
        or ext in HTML_EXTS
        or (ext in DOCX_EXTS and _DOCX_AVAILABLE)
    )
    if is_doc:
        return {
            "input_type": "document",
            "detected_format": ext.lstrip("."),
            "available_outputs": _document_outputs(ext),
        }

    return {"input_type": None, "detected_format": None, "available_outputs": []}
