"""Smoke test: run every converter on generated inputs. Usage: python tests/smoke.py [--net] [--keep]"""

import importlib.metadata as md
import shutil
import subprocess
import sys
import tempfile
import traceback
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pymupdf
import pillow_heif
from PIL import Image, ImageDraw

from converters import audio, document, image, pdf, url, video
from core.ocr_support import find_tessdata

NET  = "--net" in sys.argv
KEEP = "--keep" in sys.argv

_DOCX_PARTS = {
    "[Content_Types].xml": '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
    "_rels/.rels": '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
    "word/document.xml": '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Docx paragraph</w:t></w:r></w:p></w:body></w:document>',
}


def make_fixtures(fx: Path, ffmpeg: bool) -> None:
    pillow_heif.register_heif_opener()
    img = Image.new("RGBA", (320, 200), (30, 60, 200, 255))
    ImageDraw.Draw(img).text((20, 80), "HELLO 123", fill="white")
    img.save(fx / "a.png")
    img.convert("RGB").save(fx / "a.heic")

    scan = Image.new("RGB", (1200, 300), "white")
    ImageDraw.Draw(scan).text((50, 100), "SCANNED WORDS HERE", fill="black", font_size=80)
    scan.save(fx / "scan.png")

    doc = pymupdf.open()
    pg = doc.new_page()
    pg.insert_text((72, 72), "Page one")
    pg.insert_image(pymupdf.Rect(72, 100, 392, 300), filename=str(fx / "a.png"))
    doc.new_page().insert_text((72, 72), "Page two")
    doc.new_page().insert_text((72, 72), "Page three")
    sp = doc.new_page()
    sp.insert_image(sp.rect, filename=str(fx / "scan.png"))
    doc.save(fx / "d.pdf")

    (fx / "d.md").write_text("# Title\n\nSome **bold** text.\n\n- a\n- b\n\n| x | y |\n|---|---|\n| 1 | 2 |\n", encoding="utf-8")
    with zipfile.ZipFile(fx / "d.docx", "w") as z:
        for name, data in _DOCX_PARTS.items():
            z.writestr(name, data)

    if ffmpeg:
        ff = ["ffmpeg", "-y", "-loglevel", "error"]
        subprocess.run(ff + ["-f", "lavfi", "-i", "testsrc=size=320x240:rate=15:duration=2",
                             "-f", "lavfi", "-i", "sine=duration=2", "-shortest",
                             "-c:v", "libx264", "-c:a", "aac", str(fx / "v.mp4")], check=True)
        subprocess.run(ff + ["-f", "lavfi", "-i", "sine=duration=2", str(fx / "s.wav")], check=True)


def _text(d: Path) -> str:
    return (d / "o.txt").read_text(encoding="utf-8").upper()


def check_text(d: Path) -> None:
    t = _text(d)
    assert "PAGE ONE" in t, "text layer missing"
    if find_tessdata():
        assert "SCANNED" in t, "OCR fallback missing"


def check_ocr(d: Path) -> None:
    assert "SCANNED" in _text(d), "OCR text missing"


def check_reorder(d: Path) -> None:
    pages = [p.get_text().strip() for p in pymupdf.open(d / "o.pdf")]
    assert pages[1:] == ["Page three", "Page two", "Page one"], pages


def cases(fx: Path, ffmpeg: bool, ocr: bool) -> list:
    c = [
        ("image png->jpg",     image,    "a.png",  "jpg",     {"quality": 80},        None),
        ("image png->webp",    image,    "a.png",  "webp",    {"dims": (160, None)},  None),
        ("image png->avif",    image,    "a.png",  "avif",    {},                     None),
        ("image png->ico",     image,    "a.png",  "ico",     {},                     None),
        ("image png->pdf",     image,    "a.png",  "pdf",     {},                     None),
        ("image png->tiff",    image,    "a.png",  "tiff",    {},                     None),
        ("image heic->png",    image,    "a.heic", "png",     {},                     None),
        ("pdf ->png all",      pdf,      "d.pdf",  "png",     {"page": None},         None),
        ("pdf ->jpg page 2",   pdf,      "d.pdf",  "jpg",     {"page": 2},            None),
        ("pdf text",           pdf,      "d.pdf",  "text",    {},                     check_text),
        ("pdf extract",        pdf,      "d.pdf",  "extract", {},                     None),
        ("pdf reorder",        pdf,      "d.pdf",  "reorder", {"order": "4,3-1"},     check_reorder),
        ("doc md->pdf",        document, "d.md",   "pdf",     {},                     None),
        ("doc md->html",       document, "d.md",   "html",    {},                     None),
        ("doc md->txt",        document, "d.md",   "txt",     {},                     None),
        ("doc docx->md",       document, "d.docx", "md",      {},                     None),
        ("doc docx->txt",      document, "d.docx", "txt",     {},                     None),
        ("doc docx->pdf",      document, "d.docx", "pdf",     {},                     None),
    ]
    if ocr:
        c.append(("pdf ocr", pdf, "d.pdf", "ocr", {}, check_ocr))
    if ffmpeg:
        c += [
            ("video ->webm",   video, "v.mp4", "webm", {"codec": "vp9"}, None),
            ("video ->gif",    video, "v.mp4", "gif",  {"fps": 5},       None),
            ("video ->mp3",    video, "v.mp4", "mp3",  {},               None),
            ("audio wav->flac", audio, "s.wav", "flac", {},              None),
        ]
    return c


def main() -> int:
    for p in ["pillow", "pillow-heif", "pymupdf", "markdown", "mammoth", "yt-dlp"]:
        print(f"{p}=={md.version(p)}")

    ffmpeg = shutil.which("ffmpeg") is not None
    ocr    = find_tessdata() is not None
    skipped = [n for n, ok in [("video/audio (no ffmpeg)", ffmpeg), ("ocr (no Tesseract)", ocr),
                               ("url (pass --net)", NET and ffmpeg)] if not ok]

    work = Path(tempfile.mkdtemp(prefix="vexc-smoke-"))
    fx, out = work / "fx", work / "out"
    fx.mkdir(); out.mkdir()
    make_fixtures(fx, ffmpeg)

    failed = []
    for i, (name, mod, src, fmt, opts, check) in enumerate(cases(fx, ffmpeg, ocr)):
        d = out / f"{i:02d}"
        d.mkdir()
        try:
            mod.convert(str(fx / src), fmt, dict(opts), d, "o")
            files = list(d.iterdir())
            assert files and all(f.stat().st_size > 0 for f in files), "no output"
            if check:
                check(d)
            print(f"OK   {name}")
        except Exception:
            failed.append(name)
            print(f"FAIL {name}")
            traceback.print_exc(limit=3)

    if NET and ffmpeg:
        d = out / "url"
        d.mkdir()
        try:
            url.convert("https://www.youtube.com/watch?v=jNQXAC9IVRw", "mp4", {"max_height": 240}, d, "o")
            print("OK   url ->mp4")
        except Exception:
            failed.append("url ->mp4")
            print("FAIL url ->mp4")
            traceback.print_exc(limit=3)

    print()
    if skipped:
        print("Skipped: " + ", ".join(skipped))
    if failed or KEEP:
        print(f"Output kept in {work}")
    else:
        shutil.rmtree(work, ignore_errors=True)
    print(f"{len(failed)} failed" if failed else "All passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
