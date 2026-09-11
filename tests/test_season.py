"""T025: season scaffold/close behavior."""
import pathlib
import re

import pytest

import season

TRACKER = """# Application tracker — season 2026

Status: OPEN. Last sweep: never.

## Open applications

| Company | Role | Applied | Resume used | Predicted fit | Stage | First response |
|---|---|---|---|---|---|---|
| Acme | Senior SWE | 2026-03-01 | acme/resume.html | 80% | rejected | 2026-03-09 |
| Beacon | Staff SWE | 2026-03-02 | beacon/resume.html | 70% | offer | 2026-03-05 |

## Closed

| Company | Role | Applied | Predicted fit | Outcome |
|---|---|---|---|---|

## Notes
"""


def in_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_scaffold_creates_tracker(tmp_path, monkeypatch):
    in_dir(tmp_path, monkeypatch)
    season.scaffold("2026")
    tracker = pathlib.Path("searches/2026/applications.md").read_text()
    assert "season 2026" in tracker
    assert "Predicted fit" in tracker and "First response" in tracker


def test_season_id_suffix_allowed(tmp_path, monkeypatch):
    in_dir(tmp_path, monkeypatch)
    season.scaffold("2026b")
    assert pathlib.Path("searches/2026b").is_dir()
    with pytest.raises(SystemExit):
        season.season_dir("march-2026")


def test_close_requires_terminal_stages(tmp_path, monkeypatch):
    in_dir(tmp_path, monkeypatch)
    season.scaffold("2026")
    p = pathlib.Path("searches/2026/applications.md")
    p.write_text(TRACKER.replace("| rejected |", "| applied |"))
    with pytest.raises(SystemExit, match="not at a terminal stage"):
        season.close("2026")


def test_close_writes_retro_and_freezes(tmp_path, monkeypatch):
    in_dir(tmp_path, monkeypatch)
    season.scaffold("2026")
    p = pathlib.Path("searches/2026/applications.md")
    p.write_text(TRACKER)
    season.close("2026")
    retro = pathlib.Path("searches/2026/retro.md").read_text()
    assert "| Acme | Senior SWE | 80% | rejected | 8 |" in retro
    assert "| Beacon | Staff SWE | 70% | offer | 3 |" in retro
    assert re.search(r"Status: CLOSED \d{4}-\d{2}-\d{2}", p.read_text())
    with pytest.raises(SystemExit, match="already closed"):
        season.close("2026")
