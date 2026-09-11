# Tasks: Extract the Career Engine

**Input**: Design documents from `/specs/001-extract-career-engine/`

**Prerequisites**: plan.md, spec.md (both present; no research.md/data-model.md — schema decisions live in plan.md Technical Context)

**Tests**: Included — the spec's success criteria demand verifiable behavior (SC-002/SC-003/SC-004), and engine scripts are unit-testable. Skill behavior is verified via documented walkthroughs, not unit tests.

**Organization**: Grouped by user story per spec priorities. US1 alone is the shippable MVP.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repo skeleton, license, test harness — everything later phases assume.

- [x] T001 Create directory skeleton per plan: `engine/`, `engine/layouts/classic/`, `engine/layouts/compact/`, `templates/`, `examples/sam-rivera/`, `.claude/skills/{setup,application-pipeline,voice,season,interview-prep}/`, `tests/`
- [x] T002 [P] Add `LICENSE` (MIT, FR-012) and `.gitignore` (user-owned paths from clones of the template never belong in the template repo: `profile.yaml`, `resume/`, `searches/`, `writing-feedback.md`, `.DS_Store`, `__pycache__`)
- [x] T003 [P] Add `pyproject.toml` (PyYAML, pytest; Python 3.11+) and empty `tests/conftest.py`
- [x] T004 [P] Write `ENGINE-UPDATE.md`: the manifest of engine-owned vs user-owned paths and the rule that template updates never write user paths (Constitution III)
- [x] T005 Write `scripts/audit_personal_data.sh`: greps the whole tree (excluding `.git`) against a blocklist file `scripts/audit-blocklist.txt` (author name, email, employers, domains, project names); exits nonzero on any hit. Blocklist itself is git-ignored; a `scripts/audit-blocklist.example.txt` documents the format with placeholder entries. (SC-004)

**Checkpoint**: `pytest` runs (zero tests), audit script passes on the skeleton.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The profile schema and the Sam Rivera fixture — every story reads these.

- [x] T006 Design `templates/profile.yaml` (blank, exhaustively commented): identity + links; targets (locations, remote, level, comp floor); strengths; named gaps ("things I will not pretend to have"); work history as roles containing bullets, each bullet with an id, text, and optional metrics — the provenance pool for Truth Only (FR-002, Constitution I). Schema review requirement from plan: every user-specific fact the reference skills cite must have a home here.
- [x] T007 Design `templates/resume.yaml` (blank, commented): summary, skills groups, role references into profile bullet ids (selection, not duplication), education, projects
- [x] T008 [P] Create `examples/sam-rivera/profile.yaml` + `examples/sam-rivera/resume.yaml`: fictional full-stack engineer, plausible but clearly invented (fictional employers, sam@example.com), including named gaps so honest-fit ranking is demonstrable
- [x] T009 [P] Create `templates/writing-feedback.md` (empty log with the Voice Rules/Log section structure and a "bootstrap required" marker) and `templates/tracker.md` (season tracker table: Company | Role | Applied | Resume | Predicted fit | Stage | First response)
- [x] T010 Write `tests/test_fixtures.py`: Sam fixture loads, satisfies the profile schema, contains no blocklisted strings

**Checkpoint**: Schema + fixture exist and validate; user stories can start.

---

## Phase 3: User Story 1 — End-to-end pipeline on a stranger's profile (Priority: P1) 🎯 MVP

**Goal**: Clone → profile → board URL → honest fit ranking → one-page tailored variant → form fields → voice-checked drafts → submit checklist. Nothing invented, nothing submitted.

**Independent Test**: Run the pipeline as Sam Rivera against a live Ashby board; outputs cite only Sam's facts, render one page, end in a checklist.

### Tests for User Story 1

- [x] T011 [P] [US1] `tests/test_build_resume.py`: YAML→HTML build from Sam fixture; every rendered bullet's id exists in profile; unknown ids fail the build (Truth Only enforcement point)
- [x] T012 [P] [US1] `tests/test_render_check.py`: page-count and orphan-line detection against three fixtures (one page clean, two pages, one-page-with-orphan) — fixtures generated in-test from the layouts

### Implementation for User Story 1

- [x] T013 [US1] `engine/build_resume.py`: profile.yaml + resume.yaml + layout dir → single HTML file; `--layout classic|compact`; refuses bullets absent from profile; supports `--html-passthrough <file>` escape hatch (FR-010)
- [x] T014 [P] [US1] `engine/layouts/classic/` (layout.html + style.css): one-page single-column, the proven shape (header/summary/skills/experience/projects/education)
- [x] T015 [P] [US1] `engine/layouts/compact/`: denser two-column-skills variant of the same blocks
- [x] T016 [US1] `engine/render_check.py`: headless-Chrome render → PDF page count + 1-2-word orphan-line detection from layout text extraction; nonzero exit with a named violation (FR-004)
- [x] T017 [US1] `.claude/skills/application-pipeline/SKILL.md` re-authored generic: ATS endpoints reference (Ashby posting API + non-user-graphql form query with the fieldEntries gotcha, Greenhouse `?questions=true`, Lever, Workday cxs pattern, embedded-board discovery, manual fallback per edge case); honest-fit rubric driven by profile targets/strengths/named-gaps; variant flow calling build+render scripts into `searches/<season>/<company>/`; submit checklist that ALWAYS leads with the apply link and ends with "you review, you submit" (FR-003, FR-008)
- [x] T018 [US1] `.claude/skills/setup/SKILL.md`: interview the user to fill profile.yaml + resume.yaml, guide repo privatization, run first build+render, confirm audit script passes on their answers being absent from engine files
- [x] T019 [US1] `AGENTS.md`: the US1 workflow written agent-agnostically (fetch endpoints, run scripts, file conventions), with connector-dependent steps marked Claude Code-only (FR-011)
- [x] T020 [US1] `examples/sam-rivera/walkthrough-us1.md`: the recorded acceptance run — board URL, ranking excerpt, variant, checklist — with dated posting snapshots in `examples/sam-rivera/snapshots/` (per clarification)

**Checkpoint**: US1 acceptance scenarios pass; this is the demoable MVP.

---

## Phase 4: User Story 2 — Voice bootstrap (Priority: P2)

**Goal**: Empty voice log triggers a bootstrap interview before any drafting; corrections append as dated entries.

**Independent Test**: Empty log + draft request → interview → seeded rules; a correction lands as a dated entry.

- [x] T021 [US2] `.claude/skills/voice/SKILL.md`: bootstrap (request 2-3 real writing samples; derive starter rules: openers, punctuation habits, banned AI-tells list seeded from the generic set; write Voice Rules section), the empty-log gate, and the append-on-feedback convention (same-commit rule) (FR-005)
- [x] T022 [US2] Wire the gate into `application-pipeline/SKILL.md` and `interview-prep/SKILL.md` drafting steps: "if writing-feedback.md has the bootstrap marker, run voice bootstrap first"
- [x] T023 [P] [US2] `examples/sam-rivera/writing-feedback.md`: Sam's seeded rules + two dated example entries showing the compounding pattern
- [x] T024 [P] [US2] Extend `examples/sam-rivera/walkthrough-us1.md` or add `walkthrough-us2.md`: bootstrap transcript excerpt + a correction landing in the log

**Checkpoint**: US2 scenarios pass; drafts blocked until bootstrap on fresh clones.

---

## Phase 5: User Story 3 — Season lifecycle and calibration (Priority: P2)

**Goal**: Scaffold a season, record fit predictions at apply time, close with a prediction-vs-outcome retro; closed seasons freeze.

**Independent Test**: Scaffold → seed fictional applications with outcomes → close → retro table present, folder marked frozen.

- [x] T025 [P] [US3] `tests/test_season.py`: scaffold creates tracker + style snapshot; season ids accept `2026` and `2026b`; close on a seeded tracker emits retro rows (company, predicted fit, stage, days-to-first-response) and stamps the close date; close refuses when rows lack terminal stages
- [x] T026 [US3] `engine/season.py`: `scaffold <id>`, `close <id>` (parses tracker markdown, computes response times, writes `retro.md` from a template, stamps `CLOSED <date>` in tracker header) (FR-006, FR-007)
- [x] T027 [US3] `.claude/skills/season/SKILL.md`: start/record conventions (predicted fit recorded in the tracker row at apply time), the frozen-season guard (append-only after close), and the close ritual (resolve all rows → run close → promote durable lessons to evergreen files) (Constitution V)
- [x] T028 [P] [US3] `examples/sam-rivera/searches/2026/`: a worked mini-season — 5 fictional applications against the snapshot postings, mixed outcomes, generated `retro.md` (SC-003)

**Checkpoint**: US3 scenarios pass; the compounding claim is demonstrable.

---

## Phase 6: User Story 4 — Propose-only sweep (Priority: P3)

**Goal**: Connector users get inbox/calendar sweeps that classify responses and propose tracker updates; nothing written or sent without approval.

**Independent Test**: Seeded tracker + described test mailbox → correct classification, proposals only.

- [x] T029 [US4] Add the sweep procedure to `.claude/skills/season/SKILL.md`: ATS sender list (ashbyhq, greenhouse-mail, lever, myworkday*, ats.rippling) + tracker-company domains, since-last-sweep windowing (timestamp line in tracker header), classification taxonomy (rejection/screen/scheduling/offer/human-other/noise), silence watchlist, propose-only output format, Claude Code-only banner (FR-008)
- [x] T030 [P] [US4] Calendar half: interview-event detection + conflict flags against tracker constraints; feeds `interview-prep`
- [x] T031 [P] [US4] `.claude/skills/interview-prep/SKILL.md` re-authored generic: prep from the exact variant the company received, gap answers driven by profile named-gaps, same-day debrief into `interview.md`, stage update

**Checkpoint**: US4 scenario verified by walkthrough; degrades gracefully without connectors (manual entry documented).

---

## Phase 7: Polish & Launch Gate

**Purpose**: Everything between "works" and "public".

- [x] T032 [P] `README.md`: the thesis ("the resume that compounds"), anti-spam positioning, quickstart (clone → setup skill → first variant), architecture sketch, Sam demo pointers
- [x] T033 [P] `CLAUDE.md`: conventions distilled from the constitution for in-repo agent sessions (mirrors the private repo's, re-authored)
- [ ] T034 Record the demo: US1 run as Sam against a live board (asciinema or video), linked from README
- [x] T035 Populate `scripts/audit-blocklist.txt` locally (author identifiers) and run `scripts/audit_personal_data.sh` clean; fix any hits
- [ ] T036 Cross-check every FR against the tree (checklist in `specs/001-extract-career-engine/launch-check.md`); verify SC-001 with one non-author test user if available
- [ ] T037 Flip repo public, enable GitHub template flag, tag `v0.1.0`

---

## Dependencies & Execution Order

- **Setup (P1..T005)** → **Foundational (T006–T010)** → user stories.
- **US1 (T011–T020)** blocks nothing but is the MVP; **US2 (T021–T024)** touches the pipeline skill (T017) so runs after US1; **US3 (T025–T028)** independent of US2; **US4 (T029–T031)** needs US3's tracker conventions.
- **Launch gate (T032–T037)** last; T035/T036 are hard gates for T037.
- Within stories: tests (T011/T012/T025) before their implementations; layouts (T014/T015) parallel; example artifacts ([P]) parallel with docs.

## Implementation Strategy

MVP-first: ship through T020, validate with the Sam walkthrough, then decide
how much of P2-P3 lands before launch vs after. T037 never runs before T035
passes. Commit after each task; every commit on this repo must survive the
audit script from T005 onward.
