import os
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image

from core.ocr_support import find_tessdata

_PIL_FMT = {"png": "PNG", "jpg": "JPEG", "webp": "WEBP"}
_DPI = 200


def convert(input_path: str, fmt: str, opts: dict, out_dir: Path, stem: str) -> Path:
    doc   = fitz.open(input_path)
    total = len(doc)

    if fmt == "extract":
        return _extract_images(doc, out_dir, stem)

    if fmt == "text":
        return _extract_text(doc, out_dir, stem)

    if fmt == "ocr":
        return _extract_text(doc, out_dir, stem, force_ocr=True)

    if fmt == "reorder":
        return _reorder(doc, opts.get("order", ""), input_path, out_dir, stem)

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


def _extract_text(doc, out_dir: Path, stem: str, force_ocr: bool = False) -> Path:
    tess = find_tessdata()
    if force_ocr and not tess:
        raise RuntimeError("OCR requested but Tesseract (tessdata) was not found.")
    if tess:
        os.environ["TESSDATA_PREFIX"] = tess

    parts     = []
    ocr_pages = 0
    for page in doc:  # keep `page` bound across the OCR call (weakref-sensitive)
        txt = page.get_text()
        if force_ocr or (not txt.strip() and tess):
            tp  = page.get_textpage_ocr(dpi=_DPI, full=True)
            txt = page.get_text(textpage=tp)
            ocr_pages += 1
        parts.append(txt)

    text = "\f".join(parts)
    out  = out_dir / f"{stem}.txt"
    out.write_text(text, encoding="utf-8")

    chars = sum(len(p) for p in parts)
    note  = f" ({ocr_pages} via OCR)" if ocr_pages else ""
    print(f"  Extracted {chars} characters from {len(doc)} page(s){note}.")
    return out


def _parse_order(order_str: str) -> list[int]:
    if not order_str.strip():
        raise RuntimeError("No page order given.")
    order = []
    for token in order_str.split(","):
        token = token.strip()
        if "-" in token.lstrip("-"):
            a, _, b = token.partition("-")
            if not (a.strip().isdigit() and b.strip().isdigit()):
                raise RuntimeError(f"Invalid range '{token}'.")
            a, b = int(a), int(b)
            step = 1 if b >= a else -1
            order.extend(range(a, b + step, step))
        elif token.isdigit():
            order.append(int(token))
        else:
            raise RuntimeError(f"Invalid page '{token}'.")
    return order


def _reorder(doc, order_str: str, input_path: str, out_dir: Path, stem: str) -> Path:
    total = len(doc)
    order = _parse_order(order_str)
    if sorted(order) != list(range(1, total + 1)):
        raise RuntimeError(
            f"Page order must list every page exactly once. "
            f"Document has {total} page(s); got {order}."
        )

    new = fitz.open()
    for i in order:
        new.insert_pdf(doc, from_page=i - 1, to_page=i - 1)

    out = out_dir / f"{stem}.pdf"
    if out.resolve() == Path(input_path).resolve():
        out = out_dir / f"{stem}_reordered.pdf"
    new.save(str(out))
    new.close()

    print(f"  Reordered {total} page(s).")
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
