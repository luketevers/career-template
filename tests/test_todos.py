"""T050: todos in the tracker — add, done, list, and the after-clause split."""
import datetime as dt
import pathlib

import pytest

import season
import todos

TODAY = dt.date(2026, 9, 17)

LEGACY_TRACKER = """# Application tracker — season 2026

Status: OPEN. Last sweep: never.

## Open applications

| Company | Role | Applied | Resume used | Predicted fit | Stage | First response |
|---|---|---|---|---|---|---|
| Acme | Senior SWE | 2026-09-01 | acme/resume.html | 80% | applied | — |

## Closed

| Company | Role | Applied | Predicted fit | Outcome |
|---|---|---|---|---|

## Notes

travel 2026-10-01..05
"""


def make_season(tmp_path, monkeypatch, tracker_text=None):
    monkeypatch.chdir(tmp_path)
    season.scaffold("2026")
    if tracker_text:
        pathlib.Path("searches/2026/applications.md").write_text(tracker_text)
    return pathlib.Path("searches/2026/applications.md")


@pytest.mark.parametrize("phrase,todo_text,waiting_on", [
    ("apply to Snowflake after getting referral link", "apply to Snowflake", "getting referral link"),
    ("Ping the recruiter once the take-home is graded.", "Ping the recruiter", "the take-home is graded"),
    ("Apply to Carta when the SF req reopens", "Apply to Carta", "the SF req reopens"),
    ("update LinkedIn headline", "update LinkedIn headline", None),
])
def test_split_waiting_on(phrase, todo_text, waiting_on):
    assert todos.split_waiting_on(phrase) == (todo_text, waiting_on)


def test_add_numbers_rows_and_parses_the_after_clause(tmp_path, monkeypatch):
    tracker = make_season(tmp_path, monkeypatch)
    first = todos.add_todo("2026", "apply to Snowflake after getting referral link", company="Snowflake", today=TODAY)
    second = todos.add_todo("2026", "update LinkedIn headline", today=TODAY)
    assert (first, second) == (1, 2)
    rows = todos.load_todos("2026")
    assert rows[0]["todo"] == "apply to Snowflake"
    assert rows[0]["company"] == "Snowflake"
    assert rows[0]["waiting on"] == "getting referral link"
    assert rows[0]["added"] == "2026-09-17"
    assert todos.is_open_todo(rows[0]) and todos.is_open_todo(rows[1])
    assert rows[1]["waiting on"] == ""
    # The rest of the tracker is untouched.
    text = tracker.read_text()
    assert "## Open applications" in text and "## Notes" in text


def test_add_creates_the_section_in_a_tracker_that_predates_todos(tmp_path, monkeypatch):
    tracker = make_season(tmp_path, monkeypatch, LEGACY_TRACKER)
    assert "## Todos" not in tracker.read_text()
    todos.add_todo("2026", "apply to Snowflake after getting referral link", today=TODAY)
    text = tracker.read_text()
    assert text.index("## Todos") < text.index("## Notes")  # inserted before Notes
    assert "travel 2026-10-01..05" in text  # Notes content survived
    assert len(todos.load_todos("2026")) == 1


def test_done_stamps_the_date_and_keeps_the_row(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    todos.add_todo("2026", "apply to Snowflake after getting referral link", today=TODAY)
    todos.add_todo("2026", "update LinkedIn headline", today=TODAY)
    row = todos.complete_todo("2026", 1, today=dt.date(2026, 9, 20))
    assert row["done"] == "2026-09-20"
    rows = todos.load_todos("2026")
    assert [todos.is_open_todo(r) for r in rows] == [False, True]
    # Numbers never get reused, even after a completion.
    assert todos.add_todo("2026", "third", today=TODAY) == 3


def test_done_on_missing_or_already_done_todo_fails_clearly(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    todos.add_todo("2026", "one", today=TODAY)
    todos.complete_todo("2026", 1, today=TODAY)
    with pytest.raises(SystemExit, match="no open todo #1"):
        todos.complete_todo("2026", 1, today=TODAY)
    with pytest.raises(SystemExit, match="no open todo #9"):
        todos.complete_todo("2026", 9, today=TODAY)


def test_pipe_in_text_cannot_break_the_table(tmp_path, monkeypatch):
    make_season(tmp_path, monkeypatch)
    todos.add_todo("2026", "compare A | B offers", today=TODAY)
    rows = todos.load_todos("2026")
    assert len(rows) == 1 and rows[0]["todo"] == "compare A / B offers"


def test_cli_add_list_done(tmp_path, monkeypatch, capsys):
    make_season(tmp_path, monkeypatch)
    assert todos.main(["2026", "add", "apply to Snowflake after getting referral link", "--company", "Snowflake"]) == 0
    assert todos.main(["2026", "list"]) == 0
    listing = capsys.readouterr().out
    assert "#1 apply to Snowflake (Snowflake) — waiting on: getting referral link" in listing
    assert todos.main(["2026", "done", "1"]) == 0
    todos.main(["2026", "list"])
    assert "no open todos" in capsys.readouterr().out
    todos.main(["2026", "list", "--all"])
    assert "[done " in capsys.readouterr().out
