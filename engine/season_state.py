#!/usr/bin/env python3
"""One read of a season tracker, bucketed the way every view wants it.

board.py (HTML) and digest.py (text) both need the same numbers: what is
in flight, who has gone quiet, what todos are open. Computing them here
once means the board and the morning digest can never disagree.

Read-only. Nothing here writes the tracker.
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field

from season import CLOSED_SECTION, OPEN_SECTION, TERMINAL, parse_date, parse_rows, season_dir, stage_of
from todos import TODOS_SECTION, is_open_todo

# Stages past the initial application.
ADVANCED_STAGES = {"screen", "onsite", "offer", "accepted"}
OFFER_STAGES = {"offer", "accepted"}
DEFAULT_WATCH_DAYS = 14


@dataclass
class WaitingRow:
    row: dict
    days_silent: int


@dataclass
class SeasonState:
    season_id: str
    today: dt.date
    status_line: str                       # "Status: OPEN. Last sweep: ..." verbatim
    has_retro: bool
    live: list[dict] = field(default_factory=list)       # not at a terminal stage
    resolved: list[dict] = field(default_factory=list)   # terminal, plus the Closed table
    advanced: list[dict] = field(default_factory=list)   # screen or beyond
    offers: list[dict] = field(default_factory=list)
    waiting: list[WaitingRow] = field(default_factory=list)   # applied, silent past the threshold
    open_todos: list[dict] = field(default_factory=list)
    done_todos: list[dict] = field(default_factory=list)

    @property
    def counts(self) -> list[tuple[int, str]]:
        """The four summary tiles, in display order."""
        return [
            (len(self.live), "in flight"),
            (len(self.advanced), "screen or beyond"),
            (len(self.offers), "offers"),
            (len(self.resolved), "resolved"),
        ]


def days_waiting(row: dict, today: dt.date) -> int | None:
    """Days from application to first response, or to today if still open."""
    applied_on = parse_date(row.get("applied", ""))
    responded_on = parse_date(row.get("first response", ""))
    if applied_on and responded_on:
        return (responded_on - applied_on).days
    if applied_on and stage_of(row) not in TERMINAL:
        return (today - applied_on).days
    return None


def load_state(season_id: str, watch_days: int = DEFAULT_WATCH_DAYS, today: dt.date | None = None) -> SeasonState:
    today = today or dt.date.today()
    season_path = season_dir(season_id)
    tracker_text = (season_path / "applications.md").read_text()

    status_match = re.search(r"^Status: (\w+)[^\n]*", tracker_text, re.M)
    state = SeasonState(
        season_id=season_id,
        today=today,
        status_line=status_match.group(0) if status_match else "Status: unknown",
        has_retro=(season_path / "retro.md").exists(),
    )

    open_rows = parse_rows(tracker_text, OPEN_SECTION)
    closed_rows = parse_rows(tracker_text, CLOSED_SECTION)
    state.live = [row for row in open_rows if stage_of(row) not in TERMINAL]
    state.resolved = [row for row in open_rows if stage_of(row) in TERMINAL] + closed_rows
    state.advanced = [row for row in open_rows if stage_of(row) in ADVANCED_STAGES]
    state.offers = [row for row in open_rows + closed_rows if stage_of(row) in OFFER_STAGES]

    for row in state.live:
        if stage_of(row) != "applied":
            continue
        applied_on = parse_date(row.get("applied", ""))
        responded_on = parse_date(row.get("first response", ""))
        if applied_on and not responded_on and (today - applied_on).days >= watch_days:
            state.waiting.append(WaitingRow(row, (today - applied_on).days))

    todo_rows = parse_rows(tracker_text, TODOS_SECTION)
    state.open_todos = [row for row in todo_rows if is_open_todo(row)]
    state.done_todos = [row for row in todo_rows if not is_open_todo(row)]
    return state
