# career-template — the resume that compounds

A career is decades long; job-search tools are built for one frantic month.
This template is the other thing: **a private repo, operated by your coding
agent, that holds your resume, every search you run, and the lessons from
every application, rating, and rejection — and gets smarter each time.**

## The idea: three learning loops

Most AI job tools generate output. This one also captures what you thought
of the output, in three append-only files it re-reads before every piece of
work:

1. **Voice** (`writing-feedback.md`) — bootstrapped from samples of your
   real writing; every "too formal", "I'd never say that" becomes a logged
   rule. Drafts converge on how you actually write.
2. **Fit judgment** (`fit-feedback.md`) — when the agent ranks roles and
   you disagree — force-rank them, raise a number, veto a company — your
   correction and reason are logged, and future rankings cite your rules
   back to you ("per your rule: domain match outweighs a stack gap").
3. **Outcomes** (each season's `retro.md`) — every application records its
   fit prediction; closing a season generates the audit: predicted fit vs
   stage reached vs response time. Season N+1 starts from evidence.

Your resume, your voice, and your judgment persist between searches. The
next time you look — in six months or six years — nothing starts from
scratch.

## What it refuses to do (on purpose)

The market is full of tools that spray five hundred AI-written applications
while you sleep, and ATSs are learning to detect and bin them. This system
is architecturally the opposite, permanently, by constitution:

- **It never invents a fact.** Every resume line and drafted answer traces
  to your `profile.yaml`; the build *fails* on a claim you didn't supply —
  watch it happen in the demo.
- **It never submits anything.** No auto-apply, no unattended email, no
  auto-filled demographics/authorization/compensation fields. It prepares;
  you review and submit.
- **It holds no keys and phones no home.** Runs inside your own coding
  agent, with your credentials, in your private repo.

Low volume, high tailoring, human accountability.

**Who it's for**: anyone comfortable driving a coding agent, hunting any
kind of role — the job-title picker spans engineering to nursing to
finance, and the resume page budget is yours to set (one page by default;
two-plus for academic/federal/exec formats). The personalization loops are
field-agnostic by design: they learn from *you*.

## The workflow

```
setup ─► discover ─► rank (+your corrections) ─► tailor ─► apply ─► track ─► interview ─► close
  │                        │                        │                  │                     │
  profile.yaml       fit-feedback.md         build + render      board.html            retro.md
  (your facts)       (loop 2 learns)         checks (1 page,     + sweeps              (loop 3
  voice bootstrap                            no lies, no         (propose-only)         audits)
  (loop 1 learns)                            orphan lines)
```

1. **Setup** — the agent interviews you into `profile.yaml` (facts with
   provenance ids, strengths, and the gaps you refuse to bluff), builds
   your evergreen resume, checks the render, scaffolds a season. ~an hour.
2. **Discover** — point it at any job board; postings come from public
   ATS endpoints (Ashby, Greenhouse, Lever, Workday, SmartRecruiters,
   Rippling, Workable, BambooHR, Personio, Recruitee) or aggregators
   (Y Combinator, Ask HN: Who is hiring, Remotive, RemoteOK, and more) or
   VC portfolio boards (Sequoia, Accel, Kleiner Perkins, …), normalized by
   `engine/boards.py`.
3. **Rank** — honest fit percentages that cite your stated gaps and your
   learned fit rules. Correct it freely; corrections are the point.
4. **Tailor** — a one-page variant selected from your verified bullets,
   verified in code: exactly one page, no orphan lines, no invented claims.
5. **Apply** — every form field enumerated into a checklist; answers
   drafted in your voice; **you** submit.
6. **Track** — every application logged with its fit prediction;
   blocked actions ("apply to Snowflake after getting the referral link")
   are todos with what they wait on; `board.html` gives you the season at
   a glance (tiles, todos, stages, a silence watchlist); a morning digest
   prints the same state as text; with email/calendar connectors, sweeps
   classify responses, report todos, and propose updates.
7. **Interview** — prep sheets built from the exact variant that company
   received; same-day debriefs.
8. **Close** — the season freezes; the retro tells you what your
   predictions were worth; durable lessons promote into your evergreen
   files. The compounding is the product.

## Quickstart

1. **Use this template** → create a **private** repo → clone it.
2. **Install** (macOS or Linux):

   ```
   bash scripts/install.sh          # add --with-browser to install Chrome/Chromium too
   source .venv/bin/activate
   ```

   It finds Python 3.11+, creates `.venv/` with the two dependencies
   (`pyyaml`, `pdfminer.six`), checks for a Chromium-family browser (PDF
   rendering), and smoke-tests the engine on the fictional example. Nothing
   is written into the repo. Activate the venv in each shell before running
   the engine or your agent.
3. `python3 engine/onboard.py` — pick your target titles from a searchable
   list, set levels, locations, comp floor, and resume page budget.
4. Open it in Claude Code (other agents: [`AGENTS.md`](AGENTS.md)) and say
   **"run setup"** — the agent interviews you through the rest (history,
   strengths, gaps) and builds your first resume.
5. Give it a job board URL.

<details>
<summary>Installing by hand instead</summary>

Python 3.11+; `pip install pyyaml pdfminer.six` (or `pip install -e ".[checks]"`);
Chrome or Chromium on your `PATH`, or `export CHROME_BIN=/path/to/chrome`.
Linux: `apt-get install chromium fonts-liberation`. macOS: `brew install --cask google-chrome`.
</details>

## See it work

**37-second demo** (recorded live against the engine and a real job board):

```
uvx asciinema play demo/demo.cast     # or run it yourself: bash demo/demo.sh
```

`examples/sam-rivera/` is a complete fictional user: profile, rendered
one-page resume, voice and fit-feedback logs with worked corrections (one
of Sam's fit corrections turned out to predict his offer), a season
**board**, and a closed season with its generated retro — reproducible via
[`examples/sam-rivera/walkthrough.md`](examples/sam-rivera/walkthrough.md).

## Docs

- [`docs/capabilities.md`](docs/capabilities.md) — the full reference:
  every command, skill, loop, and stage.
- [`AGENTS.md`](AGENTS.md) — the workflows for non-Claude coding agents.
- [`ENGINE-UPDATE.md`](ENGINE-UPDATE.md) — how template updates coexist
  with years of your data.
- [`.specify/memory/constitution.md`](.specify/memory/constitution.md) —
  the non-negotiables, and why.

## Developing the engine

```
bash scripts/install.sh --dev     # adds pytest
pytest                            # 24 tests; render tests skip without a browser
```

CI (`.github/workflows/ci.yml`) runs the suite on Linux with Chrome on every
push and pull request, and runs `scripts/audit_personal_data.sh` on pushes to
`main` against a blocklist held in the `AUDIT_BLOCKLIST` repo secret — the
gate that keeps a maintainer's personal data out of the public template.
Engine changes ship to users via [`ENGINE-UPDATE.md`](ENGINE-UPDATE.md), so
the suite has to stay green.

## Layout

| Path | What |
|---|---|
| `profile.yaml`* | your verified facts — the only source of claims |
| `resume/`* | your evergreen resume (YAML → HTML → checked PDF) |
| `searches/<season>/`* | one search: tracker, variants, board, retro |
| `writing-feedback.md`* / `fit-feedback.md`* | loops 1 and 2 |
| `engine/` | build, render-check, season, board scripts + two layouts; `jobboards/` fetches job boards (one module per source) |
| `.claude/skills/` | setup, application-pipeline, voice, season, interview-prep |

\* user-owned: created at setup, never touched by template updates.

MIT licensed.
