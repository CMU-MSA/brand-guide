#!/usr/bin/env python3
"""
Build the CMU MSA Brand Guide PDF from the Markdown source.

Markdown -> HTML (python-markdown) -> PDF (WeasyPrint).
WeasyPrint shapes Arabic (RTL) correctly via Pango and renders color emoji,
so the contrast-matrix symbols and the Arabic terms in the brand guide come through.

Usage:
    python build/build_pdf.py [SOURCE.md] [OUTPUT.pdf]

Defaults:
    SOURCE  = cmu-msa-brand-guide.md   (repo root)
    OUTPUT  = cmu-msa-brand-guide.pdf   (repo root)
"""

import sys
from pathlib import Path

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from pygments.formatters import HtmlFormatter
from weasyprint import HTML

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = Path(__file__).resolve().parent
DEFAULT_SRC = REPO_ROOT / "cmu-msa-brand-guide.md"
DEFAULT_OUT = REPO_ROOT / "cmu-msa-brand-guide.pdf"
CSS_PATH = BUILD_DIR / "style.css"


def build(src: Path, out: Path) -> None:
    text = src.read_text(encoding="utf-8")

    # Insert a Table of Contents marker after the document's front-matter block
    # (the first horizontal rule), so the TOC lands just before "Section 1".
    if "[TOC]" not in text:
        marker = "\n---\n"
        idx = text.find(marker)
        if idx != -1:
            cut = idx + len(marker)
            text = text[:cut] + "\n[TOC]\n" + text[cut:]

    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "sane_lists",
            "attr_list",
            "md_in_html",
            "smarty",
            "toc",
            CodeHiliteExtension(guess_lang=False, noclasses=False),
        ],
        extension_configs={"toc": {"title": None, "toc_class": "toc"}},
    )
    body_html = md.convert(text)

    pygments_css = HtmlFormatter().get_style_defs(".codehilite")
    css = CSS_PATH.read_text(encoding="utf-8")

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CMU MSA Brand Guide</title>
<style>{css}
{pygments_css}</style>
</head>
<body>
{body_html}
</body>
</html>"""

    # base_url lets WeasyPrint resolve any relative asset paths from the repo root.
    HTML(string=document, base_url=str(REPO_ROOT)).write_pdf(str(out))
    print(f"Built {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    build(src, out)
