#!/usr/bin/env python3
"""Season lifecycle: scaffold a new search, close it with a calibration retro.

Usage:
  season.py scaffold <season-id>       # e.g. 2026 or 2026b
  season.py close <season-id>

A season lives in searches/<season-id>/ with one tracker, applications.md.
Closing requires every open row to be at a terminal stage, computes days
to first response, writes retro.md, and stamps the tracker CLOSED. After
that the season is append-only (Constitution V).

board.py imports the tracker parsing helpers from here so both scripts
read the same markdown the same way.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

# Stages a row can end in. Anything else is still in flight.
TERMINAL = {"rejected", "withdrawn", "ghosted", "offer", "accepted", "closed"}
SEASON_ID_FORMAT = re.compile(r"^\d{4}[a-z]?$")  # 2026, 2026b

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TRACKER_TEMPLATE = REPO_ROOT / "templates" / "tracker.md"
SEARCHES_DIR = pathlib.Path("searches")  # relative: scripts run from the repo root

OPEN_SECTION = "Open applications"
CLOSED_SECTION = "Closed"


# ----------------------------------------------------------- locations
def season_dir(season_id: str) -> pathlib.Path:
    if not SEASON_ID_FORMAT.match(season_id):
        raise SystemExit(f"season id must look like 2026 or 2026b, got {season_id!r}")
    return SEARCHES_DIR / season_id


def scaffold(season_id: str) -> None:
    """Create searches/<id>/applications.md from the tracker template."""
    season_path = season_dir(season_id)
    if season_path.exists():
        raise SystemExit(f"{season_path} already exists")
    season_path.mkdir(parents=True)
    tracker_text = TRACKER_TEMPLATE.read_text().replace("{SEASON}", season_id)
    (season_path / "applications.md").write_text(tracker_text)
    print(f"scaffolded {season_path}/applications.md")


# ------------------------------------------------------ tracker parsing
def parse_rows(tracker_text: str, heading: str) -> list[dict]:
    """Rows of the markdown table under `## <heading>`, keyed by lowercase
    column name. Returns [] when the section is missing."""
    section = re.search(rf"^## {re.escape(heading)}.*?\n(.*?)(?=^## |\Z)", tracker_text, re.S | re.M)
    if not section:
        return []
    rows: list[dict] = []
    column_names: list[str] = []
    for line in section.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not column_names:
            column_names = [cell.lower() for cell in cells]
            continue
        is_divider_row = set("".join(cells)) <= {"-", ":", " "}
        if is_divider_row:
            continue
        rows.append(dict(zip(column_names, cells)))
    return rows


def parse_date(text: str) -> dt.date | None:
    """ISO date, tolerating a leading '~' for 'approximately'."""
    try:
        return dt.date.fromisoformat(text.strip().lstrip("~"))
    except ValueError:
        return None


def stage_of(row: dict) -> str:
    """First word of the stage (or outcome) column, lowercased."""
    return (row.get("stage") or row.get("outcome") or "").split()[0].lower() if (row.get("stage") or row.get("outcome")) else ""


# ---------------------------------------------------------------- close
def close(season_id: str, today: dt.date | None = None) -> None:
    today = today or dt.date.today()
    season_path = season_dir(season_id)
    tracker_path = season_path / "applications.md"
    tracker_text = tracker_path.read_text()
    if "Status: CLOSED" in tracker_text:
        raise SystemExit(f"season {season_id} is already closed")

    open_rows = parse_rows(tracker_text, OPEN_SECTION)
    closed_rows = parse_rows(tracker_text, CLOSED_SECTION)
    unresolved = [row for row in open_rows if stage_of(row) not in TERMINAL]
    if unresolved:
        companies = ", ".join(row.get("company", "?") for row in unresolved)
        raise SystemExit(
            f"cannot close: {len(unresolved)} rows not at a terminal stage ({companies}). "
            "Resolve them (rejected/withdrawn/ghosted/offer/accepted) first."
        )

    (season_path / "retro.md").write_text(retro_markdown(season_id, open_rows + closed_rows, today))
    tracker_path.write_text(stamp_closed(tracker_text, today))
    print(f"closed season {season_id}: wrote {season_path / 'retro.md'}, stamped tracker")


def retro_markdown(season_id: str, rows: list[dict], today: dt.date) -> str:
    """The calibration table plus prompts the user fills in by hand."""
    lines = [
        f"# Season {season_id} retro",
        "",
        f"Closed {today.isoformat()}. Calibration: predicted fit vs what happened.",
        "",
        "| Company | Role | Predicted fit | Final stage | Days to first response |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        applied_on = parse_date(row.get("applied", ""))
        responded_on = parse_date(row.get("first response", ""))
        days_to_response = (responded_on - applied_on).days if applied_on and responded_on else "—"
        final_stage = row.get("stage") or row.get("outcome", "")
        lines.append(
            f"| {row.get('company', '')} | {row.get('role', '')} | "
            f"{row.get('predicted fit', '')} | {final_stage} | {days_to_response} |"
        )
    lines += [
        "",
        "## Reads",
        "",
        "_(fill in: did fit predictions track conversions? which strengths",
        "earned responses? which gaps got probed? what does the next season",
        "do differently?)_",
        "",
        "## Durable lessons promoted",
        "",
        "_(list what moved to profile.yaml, writing-feedback.md, resume/)_",
    ]
    return "\n".join(lines) + "\n"


def stamp_closed(tracker_text: str, today: dt.date) -> str:
    """Replace 'Status: OPEN.' with the closed stamp, or prepend one."""
    stamp = f"Status: CLOSED {today.isoformat()}."
    stamped = re.sub(r"^Status: OPEN\.", stamp, tracker_text, count=1, flags=re.M)
    if "Status: CLOSED" not in stamped:
        stamped = f"{stamp}\n\n" + stamped
    return stamped


# ------------------------------------------------------------------ cli
def main() -> int:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)
    for command in ("scaffold", "close"):
        subcommands.add_parser(command).add_argument("season")
    args = parser.parse_args()
    if args.command == "scaffold":
        scaffold(args.season)
    else:
        close(args.season)
    return 0


if __name__ == "__main__":
    sys.exit(main())
