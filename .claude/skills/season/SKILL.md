---
name: season
description: Manage a job-search season — start it, keep the application tracker truthful, run inbox/calendar sweeps that propose status updates, and close the season with a calibration retro. Use for "start my search", "mark X applied", "inbox sweep", "close out the season".
---

# Season

A season is one job search: `searches/<season-id>/` (e.g. `2026`, `2026b`).
Scripts: `python3 engine/season.py scaffold|close <id>`.

## Start

Run scaffold; confirm the tracker exists. Ask the user for any standing
constraints (travel dates, notice period, referrals in flight) and record
them in the tracker's Notes.

## Record

- When the user reports applying: add the row — company, role, date, resume
  file, **predicted fit** (from the pipeline's ranking; the retro is
  computed from it), stage `applied`, first-response `—`. Commit and push.
  Only the user's report moves a row to applied. After any tracker change,
  regenerate the board: `python3 engine/board.py <season-id>`.
- Stage vocabulary: `applied → screen → onsite → offer` and terminal
  `rejected / withdrawn / ghosted / accepted`. Record First response the
  first time a human (or rejection) responds.

## Sweep (requires mail/calendar connectors — Claude Code-only)

Propose-only, always:

1. Window: since the "Last sweep" timestamp in the tracker header
   (`newer_than` accordingly); update the timestamp after.
2. Mail search: ATS senders — `ashbyhq.com`, `greenhouse-mail.io`,
   `greenhouse.io`, `lever.co`, `myworkday*`, `ats.rippling.com`,
   `smartrecruiters.com`, `workablemail.com`, `bamboohr.com`,
   `personio.de`, `recruitee.com`, `workatastartup.com` — plus
   the domain of every tracker company.
3. Classify each thread: confirmation / rejection / screen invite /
   scheduling request / offer / human-other / noise. Quote the evidence
   line for anything that changes a status.
4. Calendar: list the next ~3 weeks; flag interview-shaped events and
   conflicts with Notes constraints.
5. Output: proposed tracker edits (with evidence), a silence watchlist
   (strong-fit applications past ~14 days with no human response), and
   anything the sweep caught that isn't recruiting (e.g. a personal-site
   outage a recruiter might hit).
6. Write NOTHING until the user approves. Never reply to, label, or send
   email. Follow-up nudges: draft only via the voice skill, send only by
   the user.

Without connectors: skip to asking the user what's landed and update rows
manually.

## Close

1. Every open row must reach a terminal stage — chase the stragglers with
   the user (>45 days silence may be `ghosted`).
2. `python3 engine/season.py close <id>` — writes `retro.md` (predicted
   fit vs final stage vs days-to-first-response) and stamps the tracker
   CLOSED.
3. Fill the retro's Reads section WITH the user: did predictions track
   outcomes? which strengths converted? which gaps got probed? Where did
   the user's corrected fits diverge from the agent's — and who was right?
   (Feed the answer back into fit-feedback.md's rules.)
4. Promote durable lessons upward: resume facts → `resume/`, voice lessons
   → `writing-feedback.md`, process fixes → skills/CLAUDE.md. List what
   moved in the retro.
5. Closed seasons are append-only (Constitution V). The skill refuses
   edits to a closed season's tracker except adding notes.
