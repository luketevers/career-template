#!/usr/bin/env python3
"""Todos: things to do before (or between) applications, kept in the tracker.

"Apply to Snowflake after getting the referral link" is not an application
yet, and it is not a queue entry either — it is blocked on something. Todos
live in a `## Todos` table in the season's applications.md so the board,
the morning digest, and the inbox sweep all see them, and so the user can
edit them by hand (Constitution VII).

    todos.py <season> add "apply to Snowflake after getting referral link" [--company Snowflake]
    todos.py <season> done 3
    todos.py <season> list [--all]

`add` splits "<todo> after|once|when <condition>" into the todo and what it
is waiting on, so the natural phrasing works as-is. Rows are numbered on
insert and keep their number forever; done rows stay, dated, for the retro.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys

from season import parse_rows, season_dir

TODOS_SECTION = "Todos"
TODOS_HEADER = "| # | Todo | Company | Waiting on | Added | Done |\n|---|---|---|---|---|---|"
NOT_DONE = "—"
# "apply to X after getting Y" → todo "apply to X", waiting on "getting Y".
WAITING_ON_SPLIT = re.compile(r"\s+(?:after|once|when|pending)\s+", re.I)
NOTES_HEADING = "## Notes"


# ------------------------------------------------------------- reading
def is_open_todo(row: dict) -> bool:
    return (row.get("done") or NOT_DONE).strip() in ("", NOT_DONE)


def split_waiting_on(phrase: str) -> tuple[str, str | None]:
    """'apply to Snowflake after getting referral link' → ('apply to Snowflake', 'getting referral link')."""
    parts = WAITING_ON_SPLIT.split(phrase.strip(), maxsplit=1)
    todo_text = parts[0].strip().rstrip(".")
    waiting_on = parts[1].strip().rstrip(".") if len(parts) > 1 else None
    return todo_text, waiting_on


def load_todos(season_id: str) -> list[dict]:
    tracker_text = (season_dir(season_id) / "applications.md").read_text()
    return parse_rows(tracker_text, TODOS_SECTION)


# ------------------------------------------------------------- writing
def _ensure_section(tracker_text: str) -> str:
    """Add an empty Todos table before Notes (or at the end) if missing."""
    if re.search(rf"^## {TODOS_SECTION}\b", tracker_text, re.M):
        return tracker_text
    block = f"## {TODOS_SECTION}\n\n{TODOS_HEADER}\n\n"
    if NOTES_HEADING in tracker_text:
        return tracker_text.replace(NOTES_HEADING, block + NOTES_HEADING, 1)
    return tracker_text.rstrip("\n") + "\n\n" + block


def _section_span(tracker_text: str) -> tuple[int, int]:
    """(start, end) character offsets of the Todos section body."""
    match = re.search(rf"^## {TODOS_SECTION}\b.*?\n(.*?)(?=^## |\Z)", tracker_text, re.S | re.M)
    assert match, "Todos section missing after _ensure_section"
    return match.start(1), match.end(1)


def add_todo(
    season_id: str,
    phrase: str,
    company: str | None = None,
    waiting_on: str | None = None,
    today: dt.date | None = None,
) -> int:
    """Append a todo row; returns its number. Splits 'after ...' unless
    waiting_on is given explicitly."""
    today = today or dt.date.today()
    todo_text, split_condition = split_waiting_on(phrase)
    waiting_on = waiting_on or split_condition
    tracker_path = season_dir(season_id) / "applications.md"
    tracker_text = _ensure_section(tracker_path.read_text())

    existing = parse_rows(tracker_text, TODOS_SECTION)
    numbers = [int(row["#"]) for row in existing if str(row.get("#", "")).isdigit()]
    number = max(numbers, default=0) + 1
    cells = [str(number), todo_text, company or "", waiting_on or "", today.isoformat(), NOT_DONE]
    new_row = "| " + " | ".join(cell.replace("|", "/") for cell in cells) + " |"

    start, end = _section_span(tracker_text)
    body = tracker_text[start:end]
    table_lines = [line for line in body.splitlines() if line.startswith("|")]
    last_table_line = table_lines[-1]
    insert_at = start + body.index(last_table_line) + len(last_table_line)
    tracker_text = tracker_text[:insert_at] + "\n" + new_row + tracker_text[insert_at:]
    tracker_path.write_text(tracker_text)
    return number


def complete_todo(season_id: str, number: int, today: dt.date | None = None) -> dict:
    """Stamp the Done column with today's date. Returns the row."""
    today = today or dt.date.today()
    tracker_path = season_dir(season_id) / "applications.md"
    tracker_text = tracker_path.read_text()
    row_pattern = re.compile(rf"^(\| {number} \|.*\|) *{NOT_DONE} *\|$", re.M)
    match = row_pattern.search(tracker_text)
    if not match:
        open_numbers = [row["#"] for row in parse_rows(tracker_text, TODOS_SECTION) if is_open_todo(row)]
        raise SystemExit(f"no open todo #{number} (open: {', '.join(open_numbers) or 'none'})")
    tracker_text = tracker_text[:match.start()] + f"{match.group(1)} {today.isoformat()} |" + tracker_text[match.end():]
    tracker_path.write_text(tracker_text)
    return next(row for row in parse_rows(tracker_text, TODOS_SECTION) if row["#"] == str(number))


# ------------------------------------------------------------------ cli
def format_todo(row: dict) -> str:
    waiting = f" — waiting on: {row['waiting on']}" if row.get("waiting on") else ""
    company = f" ({row['company']})" if row.get("company") else ""
    done = f" [done {row['done']}]" if not is_open_todo(row) else ""
    return f"#{row['#']} {row['todo']}{company}{waiting} (added {row['added']}){done}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Todos in the season tracker.")
    parser.add_argument("season")
    subcommands = parser.add_subparsers(dest="command", required=True)
    add = subcommands.add_parser("add", help='"do X after Y" — the after-clause becomes "waiting on"')
    add.add_argument("phrase")
    add.add_argument("--company", default=None)
    add.add_argument("--waiting-on", default=None, help="override the parsed condition")
    done = subcommands.add_parser("done")
    done.add_argument("number", type=int)
    listing = subcommands.add_parser("list")
    listing.add_argument("--all", action="store_true", help="include completed todos")
    args = parser.parse_args(argv)

    if args.command == "add":
        number = add_todo(args.season, args.phrase, args.company, args.waiting_on)
        print(f"added todo #{number}")
    elif args.command == "done":
        row = complete_todo(args.season, args.number)
        print(f"done: {format_todo(row)}")
    else:
        rows = load_todos(args.season)
        shown = rows if args.all else [row for row in rows if is_open_todo(row)]
        if not shown:
            print("no open todos" if not args.all else "no todos")
        for row in shown:
            print(format_todo(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
