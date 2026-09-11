#!/usr/bin/env python3
"""Render an HTML resume to PDF and verify layout quality.

Checks (FR-004):
  1. Page count == --max-pages (default 1).
  2. No orphan lines: a text line of 1-2 words that is the wrapped tail of a
     longer preceding line. Heuristic; requires pdfminer.six. Without it the
     check is SKIPPED with a warning (page count still enforced).

Works on any HTML file — including hand-written resumes that bypass
build_resume.py (the escape hatch of FR-010).

Usage: render_check.py resume.html [--pdf out.pdf] [--max-pages 1] [--keep]
Exit: 0 ok, 1 violation, 2 environment problem (no Chrome).
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

CHROME_CANDIDATES = [
    os.environ.get("CHROME_BIN", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser",
]


def find_chrome() -> str | None:
    for cand in CHROME_CANDIDATES:
        if not cand:
            continue
        if os.path.sep in cand and pathlib.Path(cand).exists():
            return cand
        found = shutil.which(cand)
        if found:
            return found
    return None


def render_pdf(html_path: pathlib.Path, pdf_path: pathlib.Path) -> None:
    chrome = find_chrome()
    if not chrome:
        print("render_check: no Chrome/Chromium found (set CHROME_BIN)", file=sys.stderr)
        raise SystemExit(2)
    subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
    )


def page_count(pdf_bytes: bytes) -> int:
    # Count page objects; robust enough for Chrome's uncompressed page tree.
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf_bytes))


def orphan_lines(pdf_path: pathlib.Path) -> list[str] | None:
    """Return offending lines, or None when pdfminer is unavailable."""
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        return None
    text = extract_text(str(pdf_path))
    lines = [ln.strip() for ln in text.splitlines()]
    offenders = []
    for prev, line in zip(lines, lines[1:]):
        words = [w for w in line.split() if any(ch.isalpha() for ch in w)]
        if not words or len(words) > 2:
            continue
        # Wrapped-tail heuristic: previous line is long body text (not a
        # heading), and this short line ends a sentence or list item.
        if len(prev) > 55 and not prev.isupper():
            offenders.append(f"...{prev[-30:]} | ORPHAN: {line!r}")
    return offenders


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--pdf", default=None, help="write the PDF here (else temp)")
    ap.add_argument("--max-pages", type=int, default=1)
    ap.add_argument("--skip-orphans", action="store_true")
    args = ap.parse_args()

    html_path = pathlib.Path(args.html)
    if not html_path.exists():
        print(f"render_check: {html_path} not found", file=sys.stderr)
        return 2

    if args.pdf:
        pdf_path = pathlib.Path(args.pdf)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        cleanup = False
    else:
        pdf_path = pathlib.Path(tempfile.mkstemp(suffix=".pdf")[1])
        cleanup = True

    try:
        render_pdf(html_path, pdf_path)
        data = pdf_path.read_bytes()
        pages = page_count(data)
        ok = True
        if pages != args.max_pages:
            print(f"FAIL page-count: {pages} pages (want {args.max_pages})")
            ok = False
        else:
            print(f"ok pages={pages}")
        if not args.skip_orphans:
            offenders = orphan_lines(pdf_path)
            if offenders is None:
                print("warn: pdfminer.six not installed — orphan check skipped")
            elif offenders:
                print("FAIL orphan-lines:")
                for o in offenders:
                    print(f"  {o}")
                ok = False
            else:
                print("ok no orphan lines")
        return 0 if ok else 1
    finally:
        if cleanup and pdf_path.exists():
            pdf_path.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
