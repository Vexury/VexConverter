from pathlib import Path


def convert(input_path: str, fmt: str, opts: dict, out_dir: Path, stem: str) -> Path:
    try:
        import cairosvg
    except ImportError:
        raise RuntimeError("cairosvg not installed — run: pip install cairosvg")

    print("  Converting...", end="", flush=True)

    out = out_dir / f"{stem}.{fmt}"

    dpi  = opts.get("dpi", 96)
    dims = opts.get("dims")

    kwargs: dict = {"dpi": dpi}
    if dims is not None:
        if isinstance(dims, float):
            kwargs["scale"] = dims
        else:
            w, h = dims
            if w:
                kwargs["output_width"] = w
            if h:
                kwargs["output_height"] = h

    cairosvg.svg2png(url=input_path, write_to=str(out), **kwargs)
    print(" done!")
    return out
