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
| `python3 engine/season.py scaffold ID` | Start a season (`searches/ID/` + tracker). IDs: `2026`, `2026b`. |
| `python3 engine/season.py close ID` | Close a season: requires every row at a terminal stage; writes `retro.md` (predicted fit vs outcome vs response time); freezes the tracker. |
| `python3 engine/board.py ID [--watch-days 14] [--out P]` | Render the season to a self-contained `board.html`: tiles, stage table, silence watchlist, retro link. A view, never a source of truth — delete and regenerate freely. |
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

## ATS coverage

Postings and application-form fields are fetched from public endpoints:
Ashby (posting API, with hosted-board GraphQL fallback), Greenhouse
(`?questions=true` for forms), Lever, Workday (best-effort; tenants vary).
Anything else: paste the posting; the form-review step is never skipped.

## What it will not do

No auto-submit, no bulk apply, no unattended email, no auto-filled
demographics / work authorization / compensation fields, no invented facts.
These are constitution-level (`.specify/memory/constitution.md`), not
settings.
