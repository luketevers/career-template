# Feature Specification: Extract the Career Engine

**Feature Branch**: `001-extract-career-engine`

**Created**: 2026-09-11

**Status**: Clarified

**Input**: User description: "extract the career engine from the private repo into a reusable template: parametrized skills reading profile.yaml, voice bootstrap, season scaffolding, resume templates with render checks, fictional example season"

## Clarifications

### Session 2026-09-11

- Q: Resume authoring model? -> A: Both — structured YAML is the canonical path rendered through layouts; hand-written HTML is a supported escape hatch (keeps render checks, loses layout swapping).
- Q: Agent targets for v1? -> A: Claude Code skills plus a generic AGENTS.md so other coding agents can run the file-based workflow; connector-dependent features (inbox/calendar sweeps) documented as Claude Code-only.
- Q: Example season data? -> A: Fictional applicant (Sam Rivera) applying to REAL public postings; committed examples carry dated snapshots of the public posting data, live fetches happen in the demo.
- Q: License? -> A: MIT.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New user runs a real application end to end (Priority: P1)

A technical job-seeker clones the template, fills in `profile.yaml` and their
resume content, points their coding agent at a job board URL, and gets: a
ranked fit assessment against THEIR profile, a tailored one-page resume
variant, the application form's fields enumerated, and drafted answers in
THEIR voice — with every generated claim traceable to their profile and
nothing submitted on their behalf.

**Why this priority**: This is the product. If the pipeline only works for
its original author, there is no template.

**Independent Test**: Create a fictional profile ("Sam Rivera"), run the
pipeline against a live Ashby board, and verify the outputs mention only
Sam's facts, render to one page, and include a submit checklist. No trace
of the original author's data anywhere in the run.

**Acceptance Scenarios**:

1. **Given** a completed `profile.yaml` and resume source, **When** the user gives the agent a job board URL, **Then** the agent produces fit rankings citing the profile's stated strengths and gaps, not anyone else's.
2. **Given** a selected role, **When** the agent tailors a variant, **Then** every bullet on it exists in the user's resume source and the PDF renders to exactly one page with no orphan lines.
3. **Given** an application form with open-ended questions, **When** the agent drafts answers, **Then** drafts follow the user's voice rules, mark unverifiable claims for the user, and the agent instructs the user to review and submit themselves.

---

### User Story 2 - Voice bootstrap from a cold start (Priority: P2)

A new user has an empty voice log. On first drafting request, the system
runs a short bootstrap: it asks for 2-3 samples of the user's real writing,
derives starter voice rules from them, seeds `writing-feedback.md`, and
thereafter appends dated entries whenever the user corrects a draft.

**Why this priority**: The compounding loop (Principle IV) needs a cold-start
path or new users get generic AI voice, which is the failure mode the
product exists to prevent.

**Independent Test**: With an empty log, request an answer draft; verify the
bootstrap interview triggers, produces a rules section, and a subsequent
correction ("too formal") lands as a dated log entry.

**Acceptance Scenarios**:

1. **Given** an empty `writing-feedback.md`, **When** the user asks for any drafted content, **Then** the bootstrap runs before any draft is produced.
2. **Given** seeded rules, **When** the user gives tone feedback on a draft, **Then** a dated entry is appended in the same commit as the revised work.

---

### User Story 3 - Season lifecycle and calibration (Priority: P2)

A user starts a season (scaffolded tracker + style snapshot), records
applications with stage and response data as they go, and closes the season
with a generated retro that maps predicted fit to outcomes — the artifact
that makes their next search smarter.

**Why this priority**: "Improves with every job/rating/rejection" is the
marketing claim; the retro is where it becomes true and demonstrable.

**Independent Test**: Scaffold a season, add fictional applications with
mixed outcomes, close the season; verify the retro contains the
prediction-vs-outcome table and the folder is marked frozen.

**Acceptance Scenarios**:

1. **Given** no current season, **When** the user starts one, **Then** `searches/<year>/` exists with an empty tracker (Stage and First-response columns) and a style snapshot.
2. **Given** a season with resolved applications, **When** the user closes it, **Then** a retro is generated with per-application predicted fit, stage reached, and response time, and the season is marked closed.

---

### User Story 4 - Inbox and calendar sweep on the user's own connectors (Priority: P3)

A user with email/calendar connectors runs a sweep: the agent searches ATS
senders plus the domains of applied companies, classifies responses
(rejection / screen / scheduling / offer), and proposes tracker updates for
approval. Nothing is written or sent without consent.

**Why this priority**: High leverage but depends on P1's tracker existing
and on connectors the user may not have; the pipeline is useful without it.

**Independent Test**: With a seeded tracker and a test mailbox containing a
rejection and a screen invite, run the sweep; verify both are classified
correctly and presented as proposals, not writes.

**Acceptance Scenarios**:

1. **Given** applied companies in the tracker, **When** the sweep runs, **Then** it reports classified changes and a silence watchlist, and writes nothing until approved.

---

### Edge Cases

- Profile is half-filled: pipeline must refuse to invent the missing halves and name exactly what it needs (Principle I).
- A posting's ATS is unrecognized: fall back to page fetch + ask the user to paste form questions; never silently skip the form-review step.
- Template update applied to a repo with 3 years of user data: user files (profile, resume, searches, voice log) must never be overwritten by engine updates.
- Two seasons in one calendar year: season IDs must allow a suffix.
- The user asks for auto-submit: the agent declines and cites the constitution.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The template MUST ship with zero personal data; all examples use a clearly fictional persona whose data lives only in `examples/`.
- **FR-002**: All agent skills MUST derive the user's identity, strengths, gaps, targets (location/level/comp floor), and links exclusively from `profile.yaml`.
- **FR-003**: The pipeline skill MUST support Ashby, Greenhouse, Lever, and Workday-hosted boards via their public endpoints, with a documented manual fallback for anything else.
- **FR-004**: Variant generation MUST copy from the user's evergreen resume source, verify one-page rendering and absence of 1-2 word orphan lines, and fail loudly otherwise.
- **FR-005**: Drafted content MUST pass through voice rules; if the voice log is empty, the bootstrap interview MUST run first.
- **FR-006**: The season tracker MUST record per application: company, role, date, resume file, stage, first-response date; sweeps and user reports update it.
- **FR-007**: Season close MUST generate a retro (predicted fit vs stage reached vs response time) and freeze the season folder.
- **FR-008**: There MUST be no code path or skill instruction that submits applications, sends email, or fills sensitive fields (demographics, work auth, comp) without explicit per-item user approval.
- **FR-009**: A setup flow (documented, agent-runnable) MUST take a new user from clone to first tailored variant, including repo privatization guidance.
- **FR-010**: The canonical resume source MUST be structured YAML rendered through at least two layout templates with a shared render-check script; a user-supplied HTML resume MUST also be accepted (render checks still apply; layout swapping does not).
- **FR-011**: The engine MUST ship as Claude Code skills plus an equivalent generic AGENTS.md workflow; features requiring connectors are marked Claude Code-only and everything else MUST be runnable by any capable coding agent.
- **FR-012**: The repository MUST be MIT licensed with a LICENSE file present from the first public commit.

### Key Entities

- **Profile**: the user's verified facts — identity, contact links, work history bullets with provenance, strengths, named gaps, targets. Single source for all generation.
- **Evergreen resume**: the user's canonical resume source and rendered PDF; archive of prior eras.
- **Season**: a bounded search — tracker, per-company folders (variant, links, interview notes), style snapshot, retro on close.
- **Voice log**: rules plus dated feedback entries; append-only.
- **Application record**: one row per submission with stage transitions and outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user (not the author) reaches a submitted-quality tailored variant for a real posting in under 60 minutes from clone, including profile setup.
- **SC-002**: 100% of factual claims in generated variants/answers are traceable to the user's profile in spot-audits of the example season.
- **SC-003**: The fictional example season demonstrates the full loop — apply, feedback entry, rejection recorded, retro generated — reproducible by running documented commands.
- **SC-004**: Grep of the published template for the author's name, email, employers, or history returns nothing outside git-ignored local files.

## Assumptions

- Primary target is Claude Code; the AGENTS.md path is best-effort compatible with other coding agents. Email/calendar connectors are optional; the tracker supports manual status entry without them.
- Distribution is a public GitHub template repo; users create private copies. No hosted service, accounts, or telemetry in v1.
- The private `career` repo remains the reference implementation; extraction is a rewrite-into-clean-history, not a fork, to guarantee SC-004.
- The Python tool (scoring board, adapters) is OUT OF SCOPE for v1 beyond documentation pointers; v1 is the skills-and-files engine. Revisit after the private repo's own tool reconciliation.
