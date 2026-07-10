from pathlib import Path
from html.parser import HTMLParser

import fitz  # PyMuPDF

_PAGE   = "a4"
_MARGIN = 36  # 0.5 inch

_BLOCK_TAGS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "table"}
_SKIP_TAGS  = {"script", "style", "head"}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self._skip += 1
        elif tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in _SKIP_TAGS and self._skip:
            self._skip -= 1
        elif tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def text(self) -> str:
        raw = "".join(self._parts)
        lines = [ln.strip() for ln in raw.splitlines()]
        out: list[str] = []
        for ln in lines:
            if ln or (out and out[-1]):
                out.append(ln)
        return "\n".join(out).strip() + "\n"


def _html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return parser.text()


def _html_to_pdf(html: str, out: Path) -> Path:
    story  = fitz.Story(html=html)
    writer = fitz.DocumentWriter(str(out))
    rect   = fitz.paper_rect(_PAGE)
    area   = rect + (_MARGIN, _MARGIN, -_MARGIN, -_MARGIN)
    more = 1
    while more:
        dev = writer.begin_page(rect)
        more, _ = story.place(area)
        story.draw(dev)
        writer.end_page()
    writer.close()
    return out


def _read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _source_html(input_path: str, src_fmt: str) -> str:
    """Produce HTML from the source document, regardless of its original format."""
    if src_fmt in ("html", "htm"):
        return _read_text(input_path)
    if src_fmt in ("md", "markdown"):
        import markdown
        return markdown.markdown(
            _read_text(input_path),
            extensions=["extra", "sane_lists", "toc"],
        )
    if src_fmt == "docx":
        import mammoth
        with open(input_path, "rb") as fh:
            return mammoth.convert_to_html(fh).value
    raise RuntimeError(f"Unsupported document format: {src_fmt}")


def convert(input_path: str, fmt: str, opts: dict, out_dir: Path, stem: str) -> Path:
    src_fmt = Path(input_path).suffix.lower().lstrip(".")
    out     = out_dir / f"{stem}.{fmt}"
    print("  Converting...", end="", flush=True)

    if fmt == "md" and src_fmt == "docx":
        import mammoth
        with open(input_path, "rb") as fh:
            out.write_text(mammoth.convert_to_markdown(fh).value, encoding="utf-8")
        print(" done!")
        return out

    if fmt == "txt" and src_fmt == "docx":
        import mammoth
        with open(input_path, "rb") as fh:
            out.write_text(mammoth.extract_raw_text(fh).value, encoding="utf-8")
        print(" done!")
        return out

    html = _source_html(input_path, src_fmt)

    if fmt == "html":
        out.write_text(html, encoding="utf-8")
    elif fmt == "txt":
        out.write_text(_html_to_text(html), encoding="utf-8")
    elif fmt == "pdf":
        _html_to_pdf(html, out)
    else:
        raise RuntimeError(f"Unsupported document output: {fmt}")

    print(" done!")
    return out
