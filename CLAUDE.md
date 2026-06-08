# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Single source of truth for the CMU MSA visual brand, communications, and web standards. The repo has two layers:

- **`cmu-msa-brand-guide.md`** — the brand guide itself. This is the only content file humans edit.
- **`tokens/tokens.json`** — machine-readable design tokens (colors, typography, spacing, radii, motion, dark mode). The single canonical source of values consumed by downstream web/mobile projects.

The PDF is a build artifact — never hand-edit it. CI rebuilds and commits it automatically on every push to `main` that touches the Markdown, build scripts, or `requirements.txt`.

## Build commands

### macOS setup (one-time)
```bash
brew install pango gdk-pixbuf libffi cairo
pip install -r requirements.txt
```

### Build the PDF locally
```bash
python build/build_pdf.py
# Optional: specify paths
python build/build_pdf.py path/to/source.md path/to/output.pdf
```

The script outputs the file size on success. Brand fonts (DM Serif Display, Plus Jakarta Sans, Lora, Amiri, Cairo) are fetched from Google Fonts at build time — an offline build succeeds but falls back to system fonts.

## Architecture

### Build pipeline
`cmu-msa-brand-guide.md` → `build/build_pdf.py` (python-markdown → HTML) → WeasyPrint → PDF

`build_pdf.py` uses these Markdown extensions: `tables`, `fenced_code`, `sane_lists`, `attr_list`, `md_in_html`, `smarty`, `toc`, `codehilite`. It auto-inserts a `[TOC]` marker after the first `---` in the Markdown if one isn't already there. The intermediate HTML is assembled as a single string with `build/style.css` inlined.

### CI (`.github/workflows/build-pdf.yml`)
Runs on `main` pushes that touch `cmu-msa-brand-guide.md`, `build/**`, `requirements.txt`, or the workflow file itself. Steps: install system libs → install Python deps → `python build/build_pdf.py` → upload PDF artifact → commit PDF back using `stefanzweifel/git-auto-commit-action@v5`. The PDF commit does not re-trigger the workflow (path filter excludes the PDF; Actions token commits don't trigger runs).

### Design tokens (`tokens/tokens.json`)
Validated against `tokens/tokens.schema.json` (JSON Schema draft-07). Required top-level keys: `$version`, `color`, `color-dark`, `typography`, `spacing`, `radius`, `motion`, `elevation`, `focus`, `border`. Color values must match `^#[0-9A-Fa-f]{6}$`. The schema is referenced in `tokens.json` via `$schema` so editors provide live validation and autocomplete.

## CSS / rendering gotchas (`build/style.css`)

- **Arabic font order**: never list an Arabic face before a Latin face in the body `font-family` stack. The layout engine will use it for English runs and silently drop digits (e.g. `2/3` renders as `/`). Arabic is substituted per-glyph automatically; it belongs only in `[lang="ar"] / .ar` rules.
- **No color emojis**: WeasyPrint cannot render color-emoji bitmap fonts — they print as empty boxes. Use text-based HTML/CSS badges (`[OK]`, `[BANNED]`, `[!]`) instead.
- **Arabic RTL**: handled automatically by CSS and the renderer. No special Markdown markup needed.
- **Debugging layout**: temporarily print the `document` string in `build_pdf.py` to inspect the intermediate HTML, or use `pdftoppm` to render individual pages.
