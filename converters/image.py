from pathlib import Path
from PIL import Image

_FMT = {
    "jpg": "JPEG", "jpeg": "JPEG",
    "png": "PNG", "webp": "WEBP", "gif": "GIF",
    "bmp": "BMP", "tiff": "TIFF", "tif": "TIFF", "pdf": "PDF", "ico": "ICO", "avif": "AVIF",
}
_NO_ALPHA = {"JPEG", "BMP", "PDF"}


def convert(input_path: str, fmt: str, opts: dict, out_dir: Path, stem: str) -> Path:
    print("  Converting...", end="", flush=True)

    img = Image.open(input_path)
    pil_fmt = _FMT.get(fmt, fmt.upper())

    if hasattr(img, "n_frames") and img.n_frames > 1 and fmt != "gif":
        img.seek(0)
        img = img.copy()

    img = _fix_mode(img, pil_fmt)

    dims = opts.get("dims")
    if dims is not None:
        ow, oh = img.size
        if isinstance(dims, float):
            w, h = round(ow * dims), round(oh * dims)
        else:
            w, h = dims
            if not w:
                w = round(ow * h / oh)
            if not h:
                h = round(oh * w / ow)
        img = img.resize((w, h), Image.LANCZOS)

    out = out_dir / f"{stem}.{fmt}"
    kwargs: dict = {}
    q = opts.get("quality", 85)
    if pil_fmt == "JPEG":
        kwargs = {"quality": q, "optimize": True}
    elif pil_fmt == "WEBP":
        kwargs = {"quality": q}
    elif pil_fmt == "TIFF":
        kwargs = {"compression": "lzw"}
    elif pil_fmt == "PNG":
        kwargs = {"optimize": True}

    img.save(str(out), pil_fmt, **kwargs)
    print(" done!")
    return out


def _fix_mode(img: Image.Image, pil_fmt: str) -> Image.Image:
    if pil_fmt in _NO_ALPHA and img.mode in ("RGBA", "LA", "PA", "P"):
        if img.mode == "P":
            img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        return bg
    if img.mode == "P":
        return img.convert("RGBA")
    if img.mode not in ("RGB", "RGBA", "L", "LA") and pil_fmt != "GIF":
        return img.convert("RGB")
    return img
