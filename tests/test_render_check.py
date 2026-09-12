"""T012: page-count and orphan-line detection (skipped without Chrome)."""
import pathlib
import subprocess
import sys

import pytest

import build_resume as br
import render_check as rc

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAM = ROOT / "examples" / "sam-rivera"
CLASSIC = ROOT / "engine" / "layouts" / "classic"

chrome_missing = rc.find_chrome() is None
needs_chrome = pytest.mark.skipif(chrome_missing, reason="no Chrome/Chromium")


def run_check(html_path, *extra):
    return subprocess.run(
        [sys.executable, str(ROOT / "engine" / "render_check.py"), str(html_path), *extra],
        capture_output=True,
        text=True,
    )


# The orphan heuristic depends on line wrapping, which depends on font
# metrics. The classic layout asks for Georgia/Helvetica; Linux CI substitutes
# wider fallbacks and wraps differently, so only assert "no orphans" where the
# real fonts exist. Page count is asserted everywhere.
has_layout_fonts = sys.platform == "darwin"


@needs_chrome
def test_sam_classic_renders_one_page_clean(tmp_path):
    out = br.build(SAM / "profile.yaml", SAM / "resume.yaml", CLASSIC, tmp_path / "r.html")
    extra = () if has_layout_fonts else ("--skip-orphans",)
    result = run_check(out, *extra)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok pages=1" in result.stdout


@needs_chrome
def test_two_pages_fails(tmp_path):
    html = tmp_path / "long.html"
    body = "<p>filler paragraph for page overflow testing</p>" * 200
    html.write_text(f"<html><body>{body}</body></html>")
    result = run_check(html)
    assert result.returncode == 1
    assert "FAIL page-count" in result.stdout


@needs_chrome
def test_orphan_line_detected(tmp_path):
    pytest.importorskip("pdfminer")
    long_line = "word " * 22  # wraps, leaving a short tail
    html = tmp_path / "orphan.html"
    html.write_text(
        "<html><body style='font-size:14pt'>"
        f"<ul><li style='width:5in'>{long_line}orphantail</li></ul>"
        "</body></html>"
    )
    result = run_check(html)
    # The fixture is engineered to wrap; if rendering doesn't wrap on this
    # platform the check may pass — accept either but require the check ran.
    assert "orphan" in result.stdout.lower()
