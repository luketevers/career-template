# career-template — the resume that compounds

A career is decades long; job-search tools are built for one frantic month.
This template is the other thing: **a private repo, operated by your coding
agent, that holds your resume, every search you run, and the lessons from
every application, rating, and rejection — and gets smarter each time.**

You clone it once. Your resume lives here and evolves for years. Each
search is a **season** that freezes into history when it ends, closing with
a calibration retro: what fit we predicted per application, what actually
happened, what to do differently. Your writing voice is learned from your
real writing and sharpened by every correction you make. The next time you
look — in six months or six years — you start from the record, not from
scratch.

## What it refuses to do (on purpose)

The market is full of tools that spray five hundred AI-written applications
while you sleep. ATSs are learning to detect and discard them. This system
is architecturally the opposite, and its constitution makes that permanent:

- **It never invents a fact.** Every resume line and drafted answer traces
  to your `profile.yaml`; the build *fails* on a claim you didn't supply.
- **It never submits anything.** No auto-apply, no unattended email, no
  auto-filled demographics/authorization/compensation fields. It prepares;
  you review and submit.
- **It holds no keys and phones no home.** It runs inside your own coding
  agent, with your credentials, in your private repo.

Low volume, high tailoring, human accountability. That's the bet.

## What a season looks like

1. **Point it at a job board.** It pulls postings via the ATS APIs (Ashby,
   Greenhouse, Lever, Workday) and ranks fit against *your* stated targets,
   strengths, and — crucially — the gaps you told it never to paper over.
2. **Tailor.** A one-page variant built from your verified bullets, checked
   in code: exactly one page, no orphan lines, no invented claims.
3. **Apply.** It enumerates every form field into a checklist; drafts
   answers in your voice (bootstrapped from your real writing); you submit.
4. **Track.** Every application recorded with its fit prediction. With
   email/calendar connectors (Claude Code), sweeps classify responses and
   propose updates — approve before anything is written.
5. **Close.** The season freezes; the retro tells you what your predictions
   were worth. Season N+1 reads it.

## Quickstart

1. **Use this template** → create a **private** repo → clone it.
2. Open it in Claude Code (other agents: see `AGENTS.md`) and say
   **"run setup"** — it interviews you into `profile.yaml`, builds your
   resume, and scaffolds your first season. ~an hour.
3. Give it a job board URL.

Requirements: Python 3.11+, a Chromium-family browser for PDF rendering,
`pip install pyyaml pdfminer.six` (or `uv pip install -e ".[dev]"`).

## See it work

`examples/sam-rivera/` is a complete fictional user: profile, rendered
one-page resume, seeded voice log, and a closed season with a generated
calibration retro — reproducible command by command via
[`examples/sam-rivera/walkthrough.md`](examples/sam-rivera/walkthrough.md).

## Layout

| Path | What |
|---|---|
| `profile.yaml`* | your verified facts — the only source of claims |
| `resume/`* | your evergreen resume (YAML → HTML → checked PDF) |
| `searches/<season>/`* | one search: tracker, variants, retro |
| `writing-feedback.md`* | your voice rules + feedback log |
| `engine/` | build, render-check, season scripts + two layouts |
| `.claude/skills/` | setup, application-pipeline, voice, season, interview-prep |
| `AGENTS.md` | the same workflows for non-Claude agents |

\* user-owned: created at setup, never touched by template updates
(`ENGINE-UPDATE.md`).

MIT licensed. Constitution in `.specify/memory/constitution.md`.
