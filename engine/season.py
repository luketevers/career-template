#!/usr/bin/env python3
"""Season lifecycle: scaffold a new search, close it with a calibration retro.

Usage:
  season.py scaffold <season-id>       # e.g. 2026 or 2026b
  season.py close <season-id>

Seasons live in searches/<season-id>/. Close requires every open row to be
resolved to a terminal stage, computes response times, writes retro.md, and
stamps the tracker CLOSED (Constitution V: frozen afterward).
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

TERMINAL = {"rejected", "withdrawn", "ghosted", "offer", "accepted", "closed"}
SEASON_ID = re.compile(r"^\d{4}[a-z]?$")

TRACKER_TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "templates" / "tracker.md"


def season_dir(season: str) -> pathlib.Path:
    if not SEASON_ID.match(season):
        raise SystemExit(f"season id must look like 2026 or 2026b, got {season!r}")
    return pathlib.Path("searches") / season


def scaffold(season: str) -> None:
    d = season_dir(season)
    if d.exists():
        raise SystemExit(f"{d} already exists")
    d.mkdir(parents=True)
    tracker = TRACKER_TEMPLATE.read_text().replace("{SEASON}", season)
    (d / "applications.md").write_text(tracker)
    print(f"scaffolded {d}/applications.md")


def parse_rows(text: str, heading: str) -> list[dict]:
    """Parse the markdown table under `heading` into dicts."""
    m = re.search(rf"^## {re.escape(heading)}.*?\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return []
    rows = []
    header: list[str] = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not header:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= {"-", ":", " "}:
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def parse_date(s: str) -> dt.date | None:
    s = s.strip().lstrip("~")
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        return None


def close(season: str, today: dt.date | None = None) -> None:
    today = today or dt.date.today()
    d = season_dir(season)
    tracker_path = d / "applications.md"
    text = tracker_path.read_text()
    if "Status: CLOSED" in text:
        raise SystemExit(f"season {season} is already closed")

    open_rows = parse_rows(text, "Open applications")
    closed_rows = parse_rows(text, "Closed")
    unresolved = [
        r for r in open_rows
        if r.get("stage", "").split()[0].lower() not in TERMINAL
    ]
    if unresolved:
        names = ", ".join(r.get("company", "?") for r in unresolved)
        raise SystemExit(
            f"cannot close: {len(unresolved)} rows not at a terminal stage "
            f"({names}). Resolve them (rejected/withdrawn/ghosted/offer/"
            f"accepted) first."
        )

    lines = [
        f"# Season {season} retro",
        "",
        f"Closed {today.isoformat()}. Calibration: predicted fit vs what happened.",
        "",
        "| Company | Role | Predicted fit | Final stage | Days to first response |",
        "|---|---|---|---|---|",
    ]
    for r in open_rows + closed_rows:
        applied = parse_date(r.get("applied", ""))
        responded = parse_date(r.get("first response", ""))
        days = (responded - applied).days if applied and responded else "—"
        stage = r.get("stage") or r.get("outcome", "")
        lines += [
            f"| {r.get('company','')} | {r.get('role','')} | "
            f"{r.get('predicted fit','')} | {stage} | {days} |"
        ]
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
    (d / "retro.md").write_text("\n".join(lines) + "\n")

    text = re.sub(
        r"^Status: OPEN\.", f"Status: CLOSED {today.isoformat()}.", text, count=1, flags=re.M
    )
    if "Status: CLOSED" not in text:
        text = f"Status: CLOSED {today.isoformat()}.\n\n" + text
    tracker_path.write_text(text)
    print(f"closed season {season}: wrote {d/'retro.md'}, stamped tracker")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for cmd in ("scaffold", "close"):
        p = sub.add_parser(cmd)
        p.add_argument("season")
    args = ap.parse_args()
    if args.cmd == "scaffold":
        scaffold(args.season)
    else:
        close(args.season)
    return 0


if __name__ == "__main__":
    sys.exit(main())
