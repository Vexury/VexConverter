import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image

_PIL_FMT = {"png": "PNG", "jpg": "JPEG", "webp": "WEBP"}
_DPI = 200


def convert(input_path: str, fmt: str, opts: dict, out_dir: Path, stem: str) -> Path:
    doc   = fitz.open(input_path)
    total = len(doc)

    if fmt == "extract":
        return _extract_images(doc, out_dir, stem)

    pil_fmt = _PIL_FMT[fmt]
    mat     = fitz.Matrix(_DPI / 72, _DPI / 72)
    page    = opts.get("page")  # int (1-based) or None (all)

    if page is not None:
        out = _render_page(doc[page - 1], mat, pil_fmt, out_dir / f"{stem}_page{page}.{fmt}")
        print(f"  Rendered page {page}.")
        return out

    out = out_dir
    for i in range(total):
        print(f"\r  Rendering {i + 1}/{total}...", end="", flush=True)
        _render_page(doc[i], mat, pil_fmt, out_dir / f"{stem}_page{i + 1:03d}.{fmt}")
    print(f"\r  {total} pages saved.              ")
    return out


def _render_page(page, mat, pil_fmt: str, out: Path) -> Path:
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(str(out), pil_fmt)
    return out


def _extract_images(doc, out_dir: Path, stem: str) -> Path:
    seen  = set()
    total = 0
    for page in doc:
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            if xref in seen:
                continue
            seen.add(xref)
            total += 1
            base = doc.extract_image(xref)
            out  = out_dir / f"{stem}_img{total:03d}.{base['ext']}"
            out.write_bytes(base["image"])
    if total == 0:
        raise RuntimeError("No embedded images found in PDF.")
    print(f"  Extracted {total} image(s).")
    return out_dir
