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

## Todos

Anything the user cannot apply to yet — a referral link on its way, a req
that hasn't reopened, a contact to hear back from — is a todo, not a queue
entry and not an application row.

- When the user says "todo: apply to Snowflake after getting the referral
  link" (or anything shaped like a blocked action), run
  `python3 engine/todos.py <season> add "<their words>" --company <Company>`.
  The after/once/when-clause becomes the "Waiting on" column automatically;
  pass `--waiting-on` when the phrasing is different. Read the number back
  to the user ("todo #3").
- When the blocker clears or the application goes out:
  `python3 engine/todos.py <season> done <#>`, then add the application row
  as usual. Done todos stay in the table, dated, for the retro.
- `python3 engine/todos.py <season> list` shows what is open. The board and
  the digest show the same list; regenerate the board after changes.

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
5. Todos: list every open todo with what it is waiting on. For each one,
   say whether anything in this sweep's mail or calendar looks like the
   blocker clearing (a referral link arriving, a contact replying, a req
   reopening) and quote the evidence. Propose `todos.py done <#>` only
   when the evidence is explicit; otherwise report "still waiting, N days".
6. Output: proposed tracker edits (with evidence), the todo report, a
   silence watchlist (strong-fit applications past ~14 days with no human
   response), and anything the sweep caught that isn't recruiting (e.g. a
   personal-site outage a recruiter might hit).
7. Write NOTHING until the user approves. Never reply to, label, or send
   email. Follow-up nudges: draft only via the voice skill, send only by
   the user.

Without connectors: skip to asking the user what's landed and update rows
manually.

## Morning digest

`python3 engine/digest.py <season>` prints the state of the hunt as short
markdown: counts, open todos and what they wait on, applications gone
quiet, live conversations. Same numbers as the board.

How it reaches the user is bounded by Constitution II — the system never
sends unattended outbound email, and that includes mail to the user
themselves. Three delivery paths are fine:

1. On demand: the user asks "where am I?" and the agent runs the digest
   (with connectors, run a sweep first so it is current).
2. Scheduled: a Claude Code routine (`/schedule`, the user's own account)
   runs the digest each morning and delivers it as a notification in the
   session. Propose-only still applies to anything the routine's sweep
   finds.
3. Draft: with the Gmail connector, the agent may create a *draft*
   addressed to the user containing the digest. The user sends it or not.

Never `send_message` the digest, never on a schedule, even when asked —
say why and offer paths 2 or 3 instead.

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
