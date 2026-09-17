"""T051: the morning digest and the shared season state behind it and the board."""
import datetime as dt
import json
import pathlib

import board
import digest
import season
import season_state
import todos

TODAY = dt.date(2026, 9, 17)

TRACKER = """# Application tracker — season 2026

Status: OPEN. Last sweep: 2026-09-15.

## Open applications

| Company | Role | Applied | Resume used | Predicted fit | Stage | First response |
|---|---|---|---|---|---|---|
| Acme | Senior SWE | 2026-08-20 | acme/resume.html | 80% | applied | — |
| Beacon | Staff SWE | 2026-09-01 | beacon/resume.html | 70% | screen | 2026-09-05 |
| Cairn | Staff SWE | 2026-09-10 | cairn/resume.html | 85% | applied | — |
| Delta | Senior SWE | 2026-08-23 | delta/resume.html | 60% | rejected | 2026-09-01 |

## Closed

| Company | Role | Applied | Predicted fit | Outcome |
|---|---|---|---|---|

## Todos

| # | Todo | Company | Waiting on | Added | Done |
|---|---|---|---|---|---|
| 1 | apply to Snowflake | Snowflake | getting referral link | 2026-09-14 | — |
| 2 | send thank-you note | Beacon |  | 2026-09-06 | 2026-09-06 |

## Notes
"""


def make_season(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    season.scaffold("2026")
    pathlib.Path("searches/2026/applications.md").write_text(TRACKER)


def test_state_buckets_rows_and_todos(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    state = season_state.load_state("2026", 14, today=TODAY)
    assert [company["company"] for company in state.live] == ["Acme", "Beacon", "Cairn"]
    assert [row["company"] for row in state.resolved] == ["Delta"]
    assert dict((label, count) for count, label in state.counts) == {
        "in flight": 3, "screen or beyond": 1, "offers": 0, "resolved": 1,
    }
    # Acme: 28 days silent → waiting. Cairn: 7 days → not yet. Beacon responded.
    assert [(w.row["company"], w.days_silent) for w in state.waiting] == [("Acme", 28)]
    assert [t["#"] for t in state.open_todos] == ["1"]
    assert [t["#"] for t in state.done_todos] == ["2"]


def test_digest_markdown_reads_top_to_bottom(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    text = digest.digest_markdown(season_state.load_state("2026", 14, today=TODAY), 14)
    assert text.startswith("# Job hunt — 2026-09-17 (season 2026)")
    assert "**3 in flight · 1 screen or beyond · 0 offers · 1 resolved**" in text
    assert "## Todos (1 open)" in text
    assert "[#1] apply to Snowflake (Snowflake) — waiting on: getting referral link (added 2026-09-14, 3 days)" in text
    assert "send thank-you note" not in text  # done todos stay out of the morning view
    assert "- Acme — Senior SWE: 28 days" in text
    assert "- Beacon — Staff SWE: screen (first response 2026-09-05)" in text
    assert "todos.py 2026 done <#>" in text


def test_digest_json_is_machine_readable(tmp_path, monkeypatch, capsys):
    make_season(tmp_path, monkeypatch)
    capsys.readouterr()  # drop scaffold's "scaffolded ..." line
    assert digest.main(["2026", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["counts"]["in flight"] == 3
    assert payload["open_todos"][0]["todo"] == "apply to Snowflake"
    assert payload["waiting"][0]["row"]["company"] == "Acme"


def test_digest_with_nothing_pending_says_so(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    season.scaffold("2026")  # empty tracker straight from the template
    text = digest.digest_markdown(season_state.load_state("2026", 14, today=TODAY), 14)
    assert "## Todos (0 open)\n- none" in text
    assert "- nothing past the threshold" in text
    assert "- none yet" in text


def test_board_shows_open_todos_and_agrees_with_digest(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    html = board.render("2026", 14, today=TODAY)
    todos_block = html.split("<h2>Todos (1 open)</h2>")[1].split("<h2>Silence watchlist")[0]
    assert "apply to Snowflake" in todos_block and "waiting on: getting referral link" in todos_block
    assert "send thank-you note" not in todos_block
    # The tiles and the digest counts come from the same state.
    assert "<b>3</b><span>in flight</span>" in html
    todos.add_todo("2026", "apply to Carta when the SF req reopens", today=TODAY)
    assert "Todos (2 open)" in board.render("2026", 14, today=TODAY)
