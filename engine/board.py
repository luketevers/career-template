#!/usr/bin/env python3
"""Render a season tracker into a self-contained HTML board.

A view, never a source of truth (FR-014): derived entirely from
searches/<season>/applications.md (plus retro.md when present). Safe to
delete and regenerate at any time. No server, no JS, prints legibly.

The numbers come from season_state.py, shared with the morning digest, so
the two can never disagree. This file is only HTML.

Usage: board.py <season-id> [--watch-days 14] [--out path]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from season import TERMINAL, season_dir, stage_of  # noqa: E402
from season_state import DEFAULT_WATCH_DAYS, OFFER_STAGES, SeasonState, days_waiting, load_state  # noqa: E402

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
.watch, .todos { border-radius: 8px; padding: 10px 14px; }
.watch { background: #fff8e6; border: 1px solid #eadfb2; }
.todos { background: #eef4fb; border: 1px solid #c9d9ee; }
.watch li, .todos li { margin-left: 18px; }
.todos .waiting { color: #555; }
.offer-row { background: #f0faf3; }
footer { margin-top: 26px; color: #888; font-size: 12px; }
@media print { body { background: #fff; padding: 0; } }
"""


# ------------------------------------------------------------ helpers
def escape(text: str | None) -> str:
    return html.escape(text or "")


def stage_badge(stage: str) -> str:
    color = STAGE_COLORS.get(stage, DEFAULT_STAGE_COLOR)
    return f'<span class="badge" style="background:{color}">{escape(stage or "—")}</span>'


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


def silence_watchlist(state: SeasonState) -> str:
    if not state.waiting:
        return "<p class='sub'>nothing waiting past the threshold</p>"
    items = "".join(
        f"<li><b>{escape(w.row.get('company'))}</b> — {escape(w.row.get('role'))}: {w.days_silent} days, no response</li>"
        for w in state.waiting
    )
    return f"<ul>{items}</ul>"


def todo_list(state: SeasonState) -> str:
    if not state.open_todos:
        return "<p class='sub'>nothing blocked or pending</p>"
    items = []
    for todo in state.open_todos:
        company = f" <b>{escape(todo.get('company'))}</b>" if todo.get("company") else ""
        waiting = f" <span class='waiting'>— waiting on: {escape(todo.get('waiting on'))}</span>" if todo.get("waiting on") else ""
        items.append(f"<li>#{escape(todo.get('#'))} {escape(todo.get('todo'))}{company}{waiting} <span class='sub'>(added {escape(todo.get('added'))})</span></li>")
    return "<ul>" + "".join(items) + "</ul>"


def summary_tiles(counts: list[tuple[int, str]]) -> str:
    return "".join(f"<div class='tile'><b>{count}</b><span>{label}</span></div>" for count, label in counts)


# -------------------------------------------------------------- render
def render(season_id: str, watch_days: int, today: dt.date | None = None) -> str:
    state = load_state(season_id, watch_days, today)
    retro_html = (
        '<p><a href="retro.md">retro.md</a> — the calibration record.</p>'
        if state.has_retro else "<p class='sub'>generated at season close</p>"
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8" />
<title>Season {escape(season_id)} board</title>
<style>{CSS}</style></head><body>
<h1>Season {escape(season_id)}</h1>
<p class="sub">{escape(state.status_line)} · board generated {state.today.isoformat()}</p>
<div class="tiles">{summary_tiles(state.counts)}</div>
<h2>Todos ({len(state.open_todos)} open)</h2>
<div class="todos">{todo_list(state)}</div>
<h2>Silence watchlist (&ge;{watch_days} days)</h2>
<div class="watch">{silence_watchlist(state)}</div>
<h2>In flight</h2>
{applications_table(state.live, state.today)}
<h2>Resolved</h2>
{applications_table(state.resolved, state.today)}
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
    parser.add_argument("--watch-days", type=int, default=DEFAULT_WATCH_DAYS)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    out_path = pathlib.Path(args.out) if args.out else season_dir(args.season) / "board.html"
    out_path.write_text(render(args.season, args.watch_days))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
