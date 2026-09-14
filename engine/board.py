#!/usr/bin/env python3
"""Render a season tracker into a self-contained HTML board.

A view, never a source of truth (FR-014): derived entirely from
searches/<season>/applications.md (plus retro.md when present). Safe to
delete and regenerate at any time. No server, no JS, prints legibly.

Usage: board.py <season-id> [--watch-days 14] [--out path]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from season import (  # noqa: E402
    CLOSED_SECTION,
    OPEN_SECTION,
    TERMINAL,
    parse_date,
    parse_rows,
    season_dir,
    stage_of,
)

# Stages past the initial application: the "screen or beyond" tile.
ADVANCED_STAGES = {"screen", "onsite", "offer", "accepted"}
OFFER_STAGES = {"offer", "accepted"}

STAGE_COLORS = {
    "applied": "#5b6068",
    "screen": "#0f5c8c",
    "onsite": "#6b4ba3",
    "offer": "#0f7a3d",
    "accepted": "#0f7a3d",
    "rejected": "#a33131",
    "withdrawn": "#8a6d1f",
    "ghosted": "#777",
    "closed": "#777",
}
DEFAULT_STAGE_COLOR = "#5b6068"

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, Helvetica, Arial, sans-serif; color: #1b1d21;
       background: #f6f7f9; padding: 28px; font-size: 14px; }
h1 { font-size: 20px; } h2 { font-size: 13px; text-transform: uppercase;
     letter-spacing: 1px; color: #555; margin: 26px 0 8px; }
.sub { color: #666; margin-top: 4px; }
.tiles { display: flex; gap: 12px; margin-top: 18px; flex-wrap: wrap; }
.tile { background: #fff; border: 1px solid #e2e4e8; border-radius: 8px;
        padding: 12px 18px; min-width: 110px; }
.tile b { display: block; font-size: 22px; }
.tile span { color: #666; font-size: 12px; }
table { border-collapse: collapse; width: 100%; background: #fff;
        border: 1px solid #e2e4e8; border-radius: 8px; overflow: hidden; }
th, td { text-align: left; padding: 8px 12px; border-top: 1px solid #eceef1; }
th { background: #fafbfc; font-size: 12px; color: #555; border-top: none; }
.badge { display: inline-block; padding: 2px 9px; border-radius: 10px;
         color: #fff; font-size: 11.5px; font-weight: 600; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.watch { background: #fff8e6; border: 1px solid #eadfb2; border-radius: 8px;
         padding: 10px 14px; }
.watch li { margin-left: 18px; }
.offer-row { background: #f0faf3; }
footer { margin-top: 26px; color: #888; font-size: 12px; }
@media print { body { background: #fff; padding: 0; } }
"""


# ------------------------------------------------------------ helpers
def escape(text: str | None) -> str:
    return html.escape(text or "")


def days_between(start: dt.date | None, end: dt.date | None) -> int | None:
    return (end - start).days if start and end else None


def stage_badge(stage: str) -> str:
    color = STAGE_COLORS.get(stage, DEFAULT_STAGE_COLOR)
    return f'<span class="badge" style="background:{color}">{escape(stage or "—")}</span>'


def days_waiting(row: dict, today: dt.date) -> int | None:
    """Days from application to first response, or to today if still open."""
    applied_on = parse_date(row.get("applied", ""))
    responded_on = parse_date(row.get("first response", ""))
    elapsed = days_between(applied_on, responded_on)
    if elapsed is None and applied_on and stage_of(row) not in TERMINAL:
        elapsed = (today - applied_on).days
    return elapsed


# ------------------------------------------------------------ sections
def applications_table(rows: list[dict], today: dt.date) -> str:
    if not rows:
        return "<p class='sub'>none</p>"
    parts = [
        "<table><tr><th>Company</th><th>Role</th><th>Applied</th>"
        "<th>Fit</th><th>Stage</th><th class='num'>First response</th>"
        "<th class='num'>Days</th></tr>"
    ]
    for row in rows:
        stage = stage_of(row)
        elapsed = days_waiting(row, today)
        row_class = ' class="offer-row"' if stage in OFFER_STAGES else ""
        parts.append(
            f"<tr{row_class}><td><b>{escape(row.get('company'))}</b></td>"
            f"<td>{escape(row.get('role'))}</td>"
            f"<td>{escape(row.get('applied'))}</td>"
            f"<td>{escape(row.get('predicted fit'))}</td>"
            f"<td>{stage_badge(stage)}</td>"
            f"<td class='num'>{escape(row.get('first response')) or '—'}</td>"
            f"<td class='num'>{elapsed if elapsed is not None else '—'}</td></tr>"
        )
    parts.append("</table>")
    return "".join(parts)


def silence_watchlist(live_rows: list[dict], watch_days: int, today: dt.date) -> str:
    """Applications with no response for at least `watch_days`."""
    waiting = []
    for row in live_rows:
        if stage_of(row) != "applied":
            continue
        applied_on = parse_date(row.get("applied", ""))
        responded_on = parse_date(row.get("first response", ""))
        if applied_on and not responded_on and (today - applied_on).days >= watch_days:
            waiting.append((row, (today - applied_on).days))
    if not waiting:
        return "<p class='sub'>nothing waiting past the threshold</p>"
    items = "".join(
        f"<li><b>{escape(row.get('company'))}</b> — {escape(row.get('role'))}: {days} days, no response</li>"
        for row, days in waiting
    )
    return f"<ul>{items}</ul>"


def summary_tiles(counts: list[tuple[int, str]]) -> str:
    return "".join(f"<div class='tile'><b>{count}</b><span>{label}</span></div>" for count, label in counts)


# -------------------------------------------------------------- render
def render(season_id: str, watch_days: int, today: dt.date | None = None) -> str:
    today = today or dt.date.today()
    season_path = season_dir(season_id)
    tracker_text = (season_path / "applications.md").read_text()
    open_rows = parse_rows(tracker_text, OPEN_SECTION)
    closed_rows = parse_rows(tracker_text, CLOSED_SECTION)
    status_line = re.search(r"^Status: (\w+)[^\n]*", tracker_text, re.M)
    status = status_line.group(0) if status_line else "Status: unknown"
    has_retro = (season_path / "retro.md").exists()

    live_rows = [row for row in open_rows if stage_of(row) not in TERMINAL]
    resolved_rows = [row for row in open_rows if stage_of(row) in TERMINAL] + closed_rows
    advanced_rows = [row for row in open_rows if stage_of(row) in ADVANCED_STAGES]
    offer_rows = [row for row in open_rows + closed_rows if stage_of(row) in OFFER_STAGES]

    tiles = summary_tiles([
        (len(live_rows), "in flight"),
        (len(advanced_rows), "screen or beyond"),
        (len(offer_rows), "offers"),
        (len(resolved_rows), "resolved"),
    ])
    retro_html = (
        '<p><a href="retro.md">retro.md</a> — the calibration record.</p>'
        if has_retro else "<p class='sub'>generated at season close</p>"
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8" />
<title>Season {escape(season_id)} board</title>
<style>{CSS}</style></head><body>
<h1>Season {escape(season_id)}</h1>
<p class="sub">{escape(status)} · board generated {today.isoformat()}</p>
<div class="tiles">{tiles}</div>
<h2>Silence watchlist (&ge;{watch_days} days)</h2>
<div class="watch">{silence_watchlist(live_rows, watch_days, today)}</div>
<h2>In flight</h2>
{applications_table(live_rows, today)}
<h2>Resolved</h2>
{applications_table(resolved_rows, today)}
<h2>Retro</h2>
{retro_html}
<footer>A view, not a source of truth — regenerate any time:
<code>python3 engine/board.py {escape(season_id)}</code></footer>
</body></html>
"""


# ------------------------------------------------------------------ cli
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("season")
    parser.add_argument("--watch-days", type=int, default=14)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    out_path = pathlib.Path(args.out) if args.out else season_dir(args.season) / "board.html"
    out_path.write_text(render(args.season, args.watch_days))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
