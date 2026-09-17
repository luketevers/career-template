#!/usr/bin/env python3
"""The morning digest: the state of the job hunt as short markdown.

    digest.py <season> [--watch-days 14] [--json]

Reads the tracker (via season_state) and prints what a person wants to
see first thing: counts, open todos and what they wait on, applications
that have gone quiet, and the conversations that are live. Text, not
HTML, so it drops into a terminal, a notification, or a draft.

Delivery is the season skill's job, and the constitution bounds it: the
system never sends unattended outbound email (Principle II). The digest
can be printed on demand, run by a scheduled agent routine that posts it
as a notification, or written to a draft the user sends to themselves.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from season import stage_of
from season_state import DEFAULT_WATCH_DAYS, SeasonState, load_state


def digest_markdown(state: SeasonState, watch_days: int) -> str:
    lines = [
        f"# Job hunt — {state.today.isoformat()} (season {state.season_id})",
        "",
        state.status_line,
        "",
        "**" + " · ".join(f"{count} {label}" for count, label in state.counts) + "**",
        "",
        f"## Todos ({len(state.open_todos)} open)",
    ]
    if state.open_todos:
        for todo in state.open_todos:
            waiting = f" — waiting on: {todo['waiting on']}" if todo.get("waiting on") else ""
            company = f" ({todo['company']})" if todo.get("company") else ""
            age = _days_since(todo.get("added", ""), state.today)
            age_note = f", {age} days" if age is not None else ""
            lines.append(f"- [#{todo['#']}] {todo['todo']}{company}{waiting} (added {todo['added']}{age_note})")
    else:
        lines.append("- none")

    lines += ["", f"## Gone quiet (applied ≥{watch_days} days ago, no response)"]
    if state.waiting:
        for waiting_row in state.waiting:
            row = waiting_row.row
            lines.append(f"- {row.get('company', '')} — {row.get('role', '')}: {waiting_row.days_silent} days")
    else:
        lines.append("- nothing past the threshold")

    conversations = [row for row in state.live if stage_of(row) != "applied"]
    lines += ["", f"## Live conversations ({len(conversations)})"]
    if conversations:
        for row in conversations:
            responded = row.get("first response", "") or "—"
            lines.append(f"- {row.get('company', '')} — {row.get('role', '')}: {stage_of(row)} (first response {responded})")
    else:
        lines.append("- none yet")

    lines += ["", "## Next", "- inbox sweep for anything new; then `python3 engine/board.py " + state.season_id + "`"]
    if state.open_todos:
        lines.append("- clear a todo: `python3 engine/todos.py " + state.season_id + " done <#>`")
    return "\n".join(lines) + "\n"


def digest_json(state: SeasonState) -> dict:
    return {
        "season": state.season_id,
        "date": state.today.isoformat(),
        "status": state.status_line,
        "counts": {label: count for count, label in state.counts},
        "open_todos": state.open_todos,
        "waiting": [{"row": w.row, "days_silent": w.days_silent} for w in state.waiting],
        "conversations": [row for row in state.live if stage_of(row) != "applied"],
    }


def _days_since(date_text: str, today: dt.date) -> int | None:
    try:
        return (today - dt.date.fromisoformat(date_text.strip())).days
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the state of the job hunt.")
    parser.add_argument("season")
    parser.add_argument("--watch-days", type=int, default=DEFAULT_WATCH_DAYS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    state = load_state(args.season, args.watch_days)
    if args.json:
        json.dump(digest_json(state), sys.stdout, indent=2)
        print()
    else:
        sys.stdout.write(digest_markdown(state, args.watch_days))
    return 0


if __name__ == "__main__":
    sys.exit(main())
