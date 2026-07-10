import os
import shutil
from pathlib import Path

# Common tessdata locations across platforms (checked in order).
_DEFAULTS = [
    r"C:\Program Files\Tesseract-OCR\tessdata",
    r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
    "/opt/homebrew/share/tessdata",
    "/usr/local/share/tessdata",
    "/usr/share/tesseract-ocr/5/tessdata",
    "/usr/share/tesseract-ocr/4.00/tessdata",
    "/usr/share/tessdata",
]


def _has_traineddata(path: Path) -> bool:
    return path.is_dir() and any(path.glob("*.traineddata"))


def find_tessdata() -> str | None:
    """Locate a Tesseract tessdata directory, or None if OCR isn't available.

    PyMuPDF's OCR needs TESSDATA_PREFIX pointing at this folder; the tesseract
    binary itself does not need to be on PATH.
    """
    env = os.environ.get("TESSDATA_PREFIX")
    if env:
        p = Path(env)
        if _has_traineddata(p):
            return str(p)
        if _has_traineddata(p / "tessdata"):  # some setups point at the parent
            return str(p / "tessdata")

    for cand in _DEFAULTS:
        p = Path(cand)
        if _has_traineddata(p):
            return str(p)

    exe = shutil.which("tesseract")
    if exe:
        guess = Path(exe).parent / "tessdata"
        if _has_traineddata(guess):
            return str(guess)

    return None


def ocr_available() -> bool:
    return find_tessdata() is not None
