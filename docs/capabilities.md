# Capabilities reference

Everything the system can do, in one place. The README is the narrative;
this is the manual.

## The three learning loops

The template's thesis is that a career system should compound. Three
append-only, user-owned files make that real:

| Loop | File | What's learned | Where it's applied |
|---|---|---|---|
| **Voice** | `writing-feedback.md` | how you write — openers, punctuation, banned tells | every draft written in your name |
| **Fit judgment** | `fit-feedback.md` | how you weigh roles — what you upgrade, veto, ignore | every ranking, cited inline ("per your rule: ...") |
| **Outcomes** | each season's `retro.md` | what your predictions were worth against reality | the next season's strategy |

Voice and fit start with a bootstrap (writing samples; announced-on-first-
ranking) and grow from your corrections. Outcomes are generated at season
close. All three are read before the work they inform — nothing is learned
into a void.

## Engine commands

| Command | What it does |
|---|---|
| `python3 engine/onboard.py` | Interactive onboarding for the structured profile fields: searchable job-title picker (200+ titles across every field, custom entries welcome), seniority, locations, remote/onsite ceiling, comp floor, resume page budget. Comment-preserving; safe to re-run. |
| `python3 engine/build_resume.py --profile P --resume R --layout L --out O [--title T]` | Build a resume HTML from your profile + a selection file + a layout (`engine/layouts/classic` or `compact`). Fails on any bullet/project id not in your profile — the Truth Only enforcement point. |
| `python3 engine/render_check.py FILE.html [--pdf OUT.pdf] [--max-pages 1] [--skip-orphans]` | Render via headless Chrome; verify against `resume_style.max_pages` and detect orphan lines (needs `pdfminer.six`; degrades to page-count-only without it). Accepts any HTML — hand-written resumes included. |
| `python3 engine/boards.py URL-or-source [--titles-from profile.yaml] [--titles a,b] [--query Q] [--role R] [--location L] [--max N] [--json] [--list]` | Fetch a job board into one normalized posting shape. Detects the ATS from the URL (or a careers page embedding one); aggregators by name (`yc`, `hn`, …). Exit 1 = nothing matched, 2 = unsupported source. |
| `python3 engine/season.py scaffold ID` | Start a season (`searches/ID/` + tracker). IDs: `2026`, `2026b`. |
| `python3 engine/season.py close ID` | Close a season: requires every row at a terminal stage; writes `retro.md` (predicted fit vs outcome vs response time); freezes the tracker. |
| `python3 engine/todos.py ID add "do X after Y" [--company C] [--waiting-on W]` / `done N` / `list [--all]` | Todos in the tracker's `## Todos` table: blocked or pending actions ("apply to Snowflake after getting the referral link"). The after/once/when-clause becomes *Waiting on*. Numbers are stable; done rows stay, dated. Creates the section in older trackers. |
| `python3 engine/digest.py ID [--watch-days 14] [--json]` | The morning digest: counts, open todos, gone-quiet applications, live conversations, as markdown (or JSON). Same numbers as the board. Delivery is bounded by Constitution II — see the season skill. |
| `python3 engine/board.py ID [--watch-days 14] [--out P]` | Render the season to a self-contained `board.html`: tiles, stage table, silence watchlist, retro link. A view, never a source of truth — delete and regenerate freely. |
| `bash scripts/install.sh [--dev] [--with-browser] [--system]` | Environment setup (macOS/Linux): Python 3.11+ check, `.venv/` with deps, browser detection (or install), smoke test on the example data. Idempotent. |
| `bash demo/demo.sh` | The full demo on the fictional example data. |
| `scripts/audit_personal_data.sh` | Maintainer tool: greps the tree against a local blocklist. CI runs it on every push to `main` from the `AUDIT_BLOCKLIST` repo secret (the blocklist file's contents); the job fails if the secret is unset. |

## Skills (Claude Code) / workflows (AGENTS.md)

| Skill | Purpose |
|---|---|
| `setup` | First run: privacy check, profile interview, first render, first season. |
| `application-pipeline` | Board/posting URL → fit ranking (profile + fit rules) → tailored variant (built + checked) → form-field checklist → voice-checked answer drafts → tracker row. |
| `voice` | Bootstrap voice rules from your real writing; gate all drafting; log corrections. |
| `season` | Start/record/close; regenerate the board; inbox+calendar sweeps (propose-only). |
| `interview-prep` | Prep from the exact variant that company received; log the debrief. |

Non-Claude agents: `AGENTS.md` carries the same workflows; anything needing
mail/calendar connectors is Claude Code-only and degrades to manual entry.

## Tracker and stage vocabulary

One markdown table per season. Columns: Company, Role, Applied, Resume
used, **Predicted fit** (the user-approved number — what the retro audits),
Stage, First response. Stages: `applied → screen → onsite → offer`,
terminal: `rejected / withdrawn / ghosted / accepted`. The header carries
season status and last-sweep timestamp.

## Engine layout

Every engine file stays under roughly 250 lines; when one grows past that,
it splits by responsibility rather than growing.

| Path | Responsibility |
|---|---|
| `engine/build_resume.py` | profile + selection + layout → HTML; the Truth Only check |
| `engine/render_check.py` | HTML → PDF via headless Chrome; page-count and orphan-line checks |
| `engine/season.py` | season scaffold/close; the tracker-markdown parser both scripts share |
| `engine/season_state.py` | one read of the tracker bucketed for every view: live/resolved/advanced/offers, gone-quiet rows, open and done todos |
| `engine/board.py` | season state → board.html (tiles, todos, silence watchlist, stage tables) |
| `engine/todos.py` | add/done/list todos in the tracker; splits "after …" into *Waiting on* |
| `engine/digest.py` | season state → the morning digest as markdown or JSON |
| `engine/onboard.py` | interactive structured-field onboarding, comment-preserving |
| `engine/boards.py` | thin entry for the command below |
| `engine/jobboards/` | the board fetcher: `http.py` (one network call), `posting.py` (the normalized shape), `provider.py` (the contract), `providers/{ats,aggregators,portfolio}/` (one module per source), `registry.py`, `detect.py`, `cli.py` |
| `tests/boards/` | one fixture-backed test per provider; `test_registry.py` fails if a provider lacks one |

## Board coverage

`engine/boards.py` fetches postings from public endpoints and normalizes them;
every provider has a fixture-backed test.

- **ATS boards** (one company per URL): Ashby (posting API, GraphQL fallback),
  Greenhouse (form fields via `?questions=true`), Lever, Workday (best effort;
  tenants vary), SmartRecruiters, Rippling, Workable, BambooHR, Personio,
  Recruitee. A company careers page that embeds one of these is detected.
- **Aggregators** (filter by title): Y Combinator jobs (`yc`; public pages,
  applying needs the user's Work at a Startup account), Ask HN: Who is hiring
  (`hn`), Remotive, RemoteOK, Himalayas, Jobicy, Arbeitnow, We Work Remotely.
- **VC portfolio boards** (pass the board's `/jobs` URL; recognized from the
  page, not the domain): Consider-hosted (Sequoia, Kleiner Perkins, Bessemer,
  Lightspeed, First Round, …; cursor-paginated, filtered client-side, cap
  with `--max`) and Getro-hosted (Accel, …; `--query` filters server-side).
  Postings link to each company's own ATS, so the form step continues there.
- **Not supported, on purpose**: LinkedIn, Indeed, Wellfound, Welcome to the
  Jungle (login walls and terms that forbid automated access); iCIMS,
  Jobvite, Taleo (HTML-only, would require scraping JS pages).

Anything else: paste the posting; the form-review step is never skipped.

## Todos and the morning digest

A todo is an action the user cannot take yet: "apply to Snowflake after
getting the referral link". It lives in the tracker's `## Todos` table with
what it is waiting on, so it shows on the board, in the digest, and in every
inbox sweep — which reports each open todo and flags evidence that its
blocker has cleared. Done todos stay, dated, so the retro can see how long
referrals and reopenings actually took.

The digest (`engine/digest.py`) is the same state as the board, as text.
It is delivered on demand, by a scheduled Claude Code routine as a
notification, or as a Gmail *draft* to the user — never as sent mail, never
unattended (Constitution II).

## What it will not do

No auto-submit, no bulk apply, no unattended email, no auto-filled
demographics / work authorization / compensation fields, no invented facts.
These are constitution-level (`.specify/memory/constitution.md`), not
settings.
