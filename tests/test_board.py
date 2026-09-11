"""T039: board rendering from a fixture tracker."""
import datetime as dt
import pathlib

import board
import season

TRACKER = """# Application tracker — season 2026

Status: OPEN. Last sweep: never.

## Open applications

| Company | Role | Applied | Resume used | Predicted fit | Stage | First response |
|---|---|---|---|---|---|---|
| Acme | Senior SWE | 2026-08-01 | acme/resume.html | 80% | applied | — |
| Beacon | Staff SWE | 2026-08-20 | beacon/resume.html | 70% | screen | 2026-08-24 |
| Cairn | Staff SWE | 2026-08-22 | cairn/resume.html | 85% | offer | 2026-08-25 |
| Delta | Senior SWE | 2026-08-23 | delta/resume.html | 60% | rejected | 2026-09-01 |

## Closed

| Company | Role | Applied | Predicted fit | Outcome |
|---|---|---|---|---|

## Notes
"""

TODAY = dt.date(2026, 9, 11)


def make_season(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    season.scaffold("2026")
    pathlib.Path("searches/2026/applications.md").write_text(TRACKER)


def test_board_renders_all_rows_and_tiles(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    html = board.render("2026", 14, today=TODAY)
    for company in ("Acme", "Beacon", "Cairn", "Delta"):
        assert company in html
    # offer is a terminal stage (matches season.close semantics)
    assert "<b>2</b><span>in flight</span>" in html
    assert "<b>2</b><span>screen or beyond</span>" in html
    assert "<b>1</b><span>offers</span>" in html
    assert "<b>2</b><span>resolved</span>" in html


def test_watchlist_catches_silence(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    html = board.render("2026", 14, today=TODAY)
    # Acme: applied 08-01, no response, 41 days -> watchlist
    assert "Acme" in html.split("Silence watchlist")[1].split("In flight")[0]
    assert "41 days, no response" in html
    # Beacon responded -> not on watchlist
    assert "Beacon" not in html.split("Silence watchlist")[1].split("In flight")[0]


def test_offer_highlighted_and_days_computed(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    html = board.render("2026", 14, today=TODAY)
    assert "offer-row" in html
    # Delta: applied 08-23, responded 09-01 -> 9 days
    assert ">9</td>" in html


def test_regenerate_overwrites(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    out = pathlib.Path("searches/2026/board.html")
    out.write_text("stale")
    out.write_text(board.render("2026", 14, today=TODAY))
    assert "stale" not in out.read_text()
    assert "Season 2026" in out.read_text()
