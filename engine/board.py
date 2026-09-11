#!/usr/bin/env python3
"""Render a season tracker into a self-contained HTML board.

A view, never a source of truth (FR-014): derived entirely from
searches/<season>/applications.md (+ retro.md when present), safe to delete
and regenerate at any time. No server, no JS dependencies, prints legibly.

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
from season import TERMINAL, parse_date, parse_rows, season_dir  # noqa: E402

ADVANCED = {"screen", "onsite", "offer", "accepted"}

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


def days_between(a: dt.date | None, b: dt.date | None) -> int | None:
    return (b - a).days if a and b else None


def stage_of(row: dict) -> str:
    return (row.get("stage") or row.get("outcome") or "").split()[0].lower()


def badge(stage: str) -> str:
    color = STAGE_COLORS.get(stage, "#5b6068")
    return f'<span class="badge" style="background:{color}">{html.escape(stage or "—")}</span>'


def render(season: str, watch_days: int, today: dt.date | None = None) -> str:
    today = today or dt.date.today()
    d = season_dir(season)
    tracker = (d / "applications.md").read_text()
    open_rows = parse_rows(tracker, "Open applications")
    closed_rows = parse_rows(tracker, "Closed")
    status_m = re.search(r"^Status: (\w+)[^\n]*", tracker, re.M)
    status = status_m.group(0) if status_m else "Status: unknown"
    retro = (d / "retro.md") if (d / "retro.md").exists() else None

    live = [r for r in open_rows if stage_of(r) not in TERMINAL]
    resolved = [r for r in open_rows if stage_of(r) in TERMINAL] + closed_rows
    advanced = [r for r in open_rows if stage_of(r) in ADVANCED]
    offers = [r for r in open_rows + closed_rows if stage_of(r) in {"offer", "accepted"}]

    watchlist = []
    for r in live:
        if stage_of(r) != "applied":
            continue
        applied = parse_date(r.get("applied", ""))
        responded = parse_date(r.get("first response", ""))
        if applied and not responded and (today - applied).days >= watch_days:
            watchlist.append((r, (today - applied).days))

    def table(rows: list[dict]) -> str:
        if not rows:
            return "<p class='sub'>none</p>"
        out = [
            "<table><tr><th>Company</th><th>Role</th><th>Applied</th>"
            "<th>Fit</th><th>Stage</th><th class='num'>First response</th>"
            "<th class='num'>Days</th></tr>"
        ]
        for r in rows:
            st = stage_of(r)
            applied = parse_date(r.get("applied", ""))
            responded = parse_date(r.get("first response", ""))
            days = days_between(applied, responded)
            if days is None and applied and st not in TERMINAL:
                days = (today - applied).days
            cls = ' class="offer-row"' if st in {"offer", "accepted"} else ""
            out.append(
                f"<tr{cls}><td><b>{html.escape(r.get('company',''))}</b></td>"
                f"<td>{html.escape(r.get('role',''))}</td>"
                f"<td>{html.escape(r.get('applied',''))}</td>"
                f"<td>{html.escape(r.get('predicted fit',''))}</td>"
                f"<td>{badge(st)}</td>"
                f"<td class='num'>{html.escape(r.get('first response','') or '—')}</td>"
                f"<td class='num'>{days if days is not None else '—'}</td></tr>"
            )
        out.append("</table>")
        return "".join(out)

    watch_html = (
        "<ul>"
        + "".join(
            f"<li><b>{html.escape(r.get('company',''))}</b> — "
            f"{html.escape(r.get('role',''))}: {n} days, no response</li>"
            for r, n in watchlist
        )
        + "</ul>"
        if watchlist
        else "<p class='sub'>nothing waiting past the threshold</p>"
    )

    retro_html = (
        f'<p><a href="retro.md">retro.md</a> — the calibration record.</p>'
        if retro
        else "<p class='sub'>generated at season close</p>"
    )

    tiles = "".join(
        f"<div class='tile'><b>{n}</b><span>{label}</span></div>"
        for n, label in [
            (len(live), "in flight"),
            (len(advanced), "screen or beyond"),
            (len(offers), "offers"),
            (len(resolved), "resolved"),
        ]
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8" />
<title>Season {html.escape(season)} board</title>
<style>{CSS}</style></head><body>
<h1>Season {html.escape(season)}</h1>
<p class="sub">{html.escape(status)} · board generated {today.isoformat()}</p>
<div class="tiles">{tiles}</div>
<h2>Silence watchlist (&ge;{watch_days} days)</h2>
<div class="watch">{watch_html}</div>
<h2>In flight</h2>
{table(live)}
<h2>Resolved</h2>
{table(resolved)}
<h2>Retro</h2>
{retro_html}
<footer>A view, not a source of truth — regenerate any time:
<code>python3 engine/board.py {html.escape(season)}</code></footer>
</body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("season")
    ap.add_argument("--watch-days", type=int, default=14)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = pathlib.Path(args.out) if args.out else season_dir(args.season) / "board.html"
    out.write_text(render(args.season, args.watch_days))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
