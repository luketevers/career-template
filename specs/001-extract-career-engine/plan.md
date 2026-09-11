# Implementation Plan: Extract the Career Engine

**Branch**: `001-extract-career-engine` | **Date**: 2026-09-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-extract-career-engine/spec.md`

## Summary

Rewrite the proven private-repo workflow (skills + plain files + render
checks + season tracking) into a zero-personal-data public template. The
engine is agent instructions plus small scripts; the user's data enters
only through files they create (`profile.yaml`, resume source, voice log).
Canonical resume path is structured YAML rendered through swappable HTML
layouts; user-supplied HTML is an escape hatch. Ships as Claude Code skills
plus a generic AGENTS.md, MIT licensed, demonstrated by a fictional persona
(Sam Rivera) applying to real public postings.

## Technical Context

**Language/Version**: Markdown/YAML for all state; Python 3.11+ for the few
scripts (render check, season scaffold/close, YAML→HTML resume build);
no Node dependency.

**Primary Dependencies**: headless Chrome/Chromium for PDF rendering
(documented install per OS); PyYAML; the user's own coding agent as the
runtime (Claude Code primary). No LLM API keys held by the template.

**Storage**: files in the user's private clone. No database (Constitution
VII); the tracker is a markdown table.

**Testing**: pytest for scripts (render check, resume build, season
scaffold/close, retro generation); a checked-in "Sam Rivera" fixture
profile drives script tests; skill behavior verified via the documented
acceptance walkthroughs in `examples/` (agent behavior is not unit-testable;
the walkthrough IS the test, per SC-003).

**Target Platform**: macOS/Linux dev machines with a Chromium-family
browser; agent-agnostic file layout.

**Project Type**: template repository (agent skills + scripts + docs).

**Performance Goals**: N/A beyond SC-001 (clone → first tailored variant
in under 60 minutes for a new user).

**Constraints**: zero personal data in history (SC-004: fresh repo, no
files copied from the private repo — patterns re-authored, not ported);
no auto-submit or unattended outbound anything (Constitution II);
engine updates must not touch user-owned paths (Constitution III).

**Scale/Scope**: single-user repos; a season of ~10-50 applications;
2 resume layouts at launch.

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| I. Truth Only | PASS | Resume build consumes only profile/resume YAML; drafting skill marks unverifiable claims; traceability spot-audit in example season (SC-002). |
| II. The Human Submits | PASS | No submit/send code exists; skills end at checklists + drafts; sweep (P3) is propose-only. |
| III. Engine/Data Separation | PASS | User paths (`profile.yaml`, `resume/`, `searches/`, `writing-feedback.md`) are created by setup, listed in an ENGINE-UPDATE manifest that update instructions must never write to. |
| IV. Compounding | PASS | Voice bootstrap + append-only log (US2); stage/response columns + retro (US3). |
| V. Immutable Seasons | PASS | `season close` writes retro, stamps closed date; skills refuse edits to closed seasons except append. |
| VI. User-Owned Runtime | PASS | Connectors are the user's; ATS access via public posting APIs only. |
| VII. Plain Files | JUSTIFIED EXCEPTION | The YAML→HTML resume build adds a build step. Justification: it purchases render checks, layout swapping, and claim traceability; the HTML escape hatch preserves the plain-file path for users who refuse the step. |

## Project Structure

```
career-template/
  README.md               thesis, demo, quickstart        (engine)
  LICENSE                 MIT                              (engine)
  AGENTS.md               generic-agent workflow           (engine)
  CLAUDE.md               conventions; points at skills    (engine)
  .claude/skills/
    setup/                clone → profile → first render   (engine)
    application-pipeline/ board → rank → variant → form → answers (engine)
    voice/                bootstrap + feedback logging     (engine)
    season/               start / record / sweep / close   (engine)
    interview-prep/       prep from the variant they got   (engine)
  engine/
    build_resume.py       YAML + layout → HTML
    render_check.py       PDF page count + orphan-line check
    season.py             scaffold / close / retro
    layouts/              classic/ and compact/ (HTML+CSS)
  templates/              blank profile.yaml, resume.yaml,
                          writing-feedback.md, tracker      (engine)
  examples/sam-rivera/    fictional profile, one worked
                          season w/ dated posting snapshots (fixture)
  specs/, .specify/       spec kit                          (meta)
  --- created by setup in the USER's clone, never shipped filled ---
  profile.yaml  resume/  searches/  writing-feedback.md
```

## Phases

**Phase 0 — Skeleton (gates everything)**
Repo layout above; LICENSE (FR-012); ENGINE-UPDATE manifest convention;
blank templates; CI-less test harness (`pytest engine/`). Exit: fresh
clone passes tests with the Sam fixture.

**Phase 1 — P1: end-to-end pipeline on a stranger's profile**
1. `templates/profile.yaml` schema: identity, links, targets (location/
   level/comp floor), strengths, named gaps, work history with bullet
   provenance ids.
2. `engine/build_resume.py` + two layouts + `render_check.py` (port the
   page-count/orphan checks as code; re-author, don't copy).
3. `application-pipeline` skill re-authored against the profile schema:
   ATS endpoints (Ashby REST + hosted GraphQL form query, Greenhouse
   `?questions=true`, Lever, Workday cxs), honest-fit rubric that cites
   profile gaps, variant flow, submit checklist ending "you submit".
4. Setup skill: interview the user into profile.yaml, privatize-repo
   guidance, first render.
Exit: US1 acceptance scenarios pass with Sam against a live Ashby board.

**Phase 2 — P2a: voice** — bootstrap interview (3 writing samples →
starter rules), empty-log gate in the drafting path, append-on-feedback
convention. Exit: US2 scenarios.

**Phase 3 — P2b: seasons** — `season.py` scaffold/close/retro (fit
prediction recorded at apply time is what makes the retro computable —
tracker column added in Phase 1), frozen-season guard in skills.
Exit: US3 scenarios; SC-003 walkthrough recorded in examples/.

**Phase 4 — P3: sweep** — sweep procedure in the season skill (ATS sender
list + tracker-company domains, classify, propose-only), silence
watchlist, Claude-Code-only banner. Exit: US4 scenario against a seeded
mailbox description (manual test; no mailbox fixture shippable).

**Phase 5 — Launch gate**
AGENTS.md distillation of the skills (FR-011); README with demo recording;
SC-004 audit script (`grep` list for author identifiers) run in CI-style
pre-publish check; flip repo public + template flag.

## Risks

- **Leakage** (kills SC-004): mitigated by fresh-repo rule + audit script;
  nobody ever copies a file out of the private repo.
- **Skill quality regression when parametrized**: the private repo's skills
  work partly because they encode Luke's specifics; the profile schema must
  carry equivalent richness (esp. named gaps) or fit assessments go generic.
  Mitigation: schema review against every place the current skill cites
  Luke-specific facts.
- **Workday variance**: cxs endpoints differ per tenant; ship it as
  best-effort with the manual fallback prominent.
- **Author bandwidth**: Luke is mid-search; phases are sized to be
  droppable — P1 alone is a shippable MVP (spec's design intent).

## Out of Scope (v1)

Hosted anything; the Python scoring board/tool; auto-submit (permanently);
non-English resumes; LinkedIn/profile sync automation.
