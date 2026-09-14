#!/usr/bin/env python3
"""Render an HTML resume to PDF and verify its layout.

Checks (FR-004):
  1. Page count equals --max-pages (default 1).
  2. No orphan lines: a one- or two-word line that is the wrapped tail of
     the long line before it. Heuristic; needs pdfminer.six. Without it the
     check is skipped with a warning and page count is still enforced.

Works on any HTML file, including hand-written resumes that bypass
build_resume.py (the escape hatch of FR-010).

Usage: render_check.py resume.html [--pdf out.pdf] [--max-pages 1] [--skip-orphans]
Exit: 0 ok, 1 a check failed, 2 environment problem (no Chrome, no file).
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

# Tried in order. CHROME_BIN wins so CI and unusual installs can point at
# any Chromium-family binary.
CHROME_CANDIDATES = [
    os.environ.get("CHROME_BIN", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
    "chromium-browser",
]

# Orphan heuristic knobs. A "long" previous line is body text, not a
# heading; a short trailing line of at most this many words is suspect.
LONG_LINE_MIN_CHARS = 55
ORPHAN_MAX_WORDS = 2


# ------------------------------------------------------------ rendering
def find_chrome() -> str | None:
    """First candidate that exists as a path or resolves on PATH."""
    for candidate in CHROME_CANDIDATES:
        if not candidate:
            continue
        if os.path.sep in candidate and pathlib.Path(candidate).exists():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def render_pdf(html_path: pathlib.Path, pdf_path: pathlib.Path) -> None:
    """Print the HTML to PDF with headless Chrome. Exits 2 if none is found."""
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


# --------------------------------------------------------------- checks
def page_count(pdf_bytes: bytes) -> int:
    """Count page objects. Robust enough for Chrome's uncompressed page tree."""
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf_bytes))


def orphan_lines(pdf_path: pathlib.Path) -> list[str] | None:
    """Lines that look like wrapped tails, or None when pdfminer is missing."""
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        return None
    lines = [line.strip() for line in extract_text(str(pdf_path)).splitlines()]
    offenders = []
    for previous_line, line in zip(lines, lines[1:]):
        real_words = [word for word in line.split() if any(char.isalpha() for char in word)]
        if not real_words or len(real_words) > ORPHAN_MAX_WORDS:
            continue
        # A short line after long body text (not an all-caps heading) is
        # almost always the last word or two of a wrapped bullet.
        previous_is_body_text = len(previous_line) > LONG_LINE_MIN_CHARS and not previous_line.isupper()
        if previous_is_body_text:
            offenders.append(f"...{previous_line[-30:]} | ORPHAN: {line!r}")
    return offenders


# ------------------------------------------------------------------ cli
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html")
    parser.add_argument("--pdf", default=None, help="write the PDF here (else a temp file)")
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--skip-orphans", action="store_true")
    args = parser.parse_args()

    html_path = pathlib.Path(args.html)
    if not html_path.exists():
        print(f"render_check: {html_path} not found", file=sys.stderr)
        return 2

    if args.pdf:
        pdf_path = pathlib.Path(args.pdf)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        delete_pdf_after = False
    else:
        pdf_path = pathlib.Path(tempfile.mkstemp(suffix=".pdf")[1])
        delete_pdf_after = True

    try:
        render_pdf(html_path, pdf_path)
        all_checks_passed = True

        pages = page_count(pdf_path.read_bytes())
        if pages != args.max_pages:
            print(f"FAIL page-count: {pages} pages (want {args.max_pages})")
            all_checks_passed = False
        else:
            print(f"ok pages={pages}")

        if not args.skip_orphans:
            offenders = orphan_lines(pdf_path)
            if offenders is None:
                print("warn: pdfminer.six not installed — orphan check skipped")
            elif offenders:
                print("FAIL orphan-lines:")
                for offender in offenders:
                    print(f"  {offender}")
                all_checks_passed = False
            else:
                print("ok no orphan lines")
        return 0 if all_checks_passed else 1
    finally:
        if delete_pdf_after and pdf_path.exists():
            pdf_path.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
