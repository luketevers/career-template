# Feature Specification: Season Board, Fit Personalization, and Docs

**Feature Branch**: `002-season-board-ui`

**Created**: 2026-09-11

**Status**: Clarified (scope set directly by the maintainer)

**Input**: User description: "season board UI, fit-ranking personalization loop, and capability docs plus a workflow README"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See the season at a glance (Priority: P1)

A user regenerates a static, zero-server dashboard from their season
tracker: summary tiles (open / screens+ / closed / offers), the application
table with stage badges and day counts, a silence watchlist, and a link to
the retro once closed. One command, one self-contained HTML file, opens in
any browser. No database, no server (Constitution VII).

**Independent Test**: run the board command against Sam Rivera's example
season; the HTML shows all five applications with correct stages, days to
first response, and the offer highlighted.

**Acceptance Scenarios**:

1. **Given** a season tracker, **When** the user runs the board command, **Then** a self-contained board.html is written next to the tracker with tiles, table, and watchlist derived only from tracker content.
2. **Given** an application at stage `applied` with no response past the watch threshold, **When** the board renders, **Then** it appears in the silence watchlist with days elapsed.

---

### User Story 2 - Fit judgment that learns (force-rank loop) (Priority: P1)

When the pipeline ranks roles, the user can correct it — reorder, raise or
lower a fit number, veto. Each correction is appended (dated, with the
user's reason) to `fit-feedback.md`; the pipeline reads that file BEFORE
every future ranking, so the user's judgment compounds exactly like their
voice does. The tracker records the user-approved fit number, which the
season retro then audits against outcomes.

**Independent Test**: with a fit-feedback file containing "user consistently
downgrades >3 onsite days", a ranking run cites that rule; a new correction
lands as a dated log entry.

**Acceptance Scenarios**:

1. **Given** an empty fit-feedback log, **When** the pipeline first ranks roles, **Then** it announces that corrections will be learned and the file is seeded from the template.
2. **Given** a user correction ("that's a 90, not a 75 — domain match outweighs the stack gap"), **Then** a dated entry with the reason is appended in the same commit and the tracker row carries the corrected number.
3. **Given** prior fit-feedback entries, **When** a new board/role is ranked, **Then** the assessment explicitly applies and cites the learned rules.

---

### User Story 3 - A user can learn the whole system from the repo (Priority: P2)

The README explains the full workflow (setup → discover → rank+correct →
tailor → apply → track/sweep → interview → close → compound) and the three
learning loops; `docs/` carries a capabilities reference deep enough that a
user never needs the maintainer.

**Independent Test**: every command and skill named in README/docs exists;
every engine command is documented somewhere in docs/.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-013**: `engine/board.py <season>` MUST render the season tracker to a single self-contained `board.html` (no external assets, no server) showing summary tiles, per-application rows with stage and day counts, a configurable silence watchlist (default 14 days), and the retro when present.
- **FR-014**: The board MUST be derived exclusively from the tracker file (and retro.md if present); it is a view, never a second source of truth, and is safe to delete/regenerate.
- **FR-015**: A `templates/fit-feedback.md` MUST exist (learned-rules + dated-log structure, mirroring writing-feedback.md); setup copies it; it is user-owned.
- **FR-016**: The application-pipeline skill MUST read `fit-feedback.md` before ranking, cite applicable learned rules in its assessments, append dated entries (with the user's stated reason) when the user corrects a ranking, and record the user-approved fit in the tracker.
- **FR-017**: The season skill MUST regenerate the board after tracker changes and the retro MUST note where user-corrected fits diverged from agent fits.
- **FR-018**: `docs/` MUST document: the three learning loops (voice, fit, outcomes), every engine command, the skills, the tracker/stage vocabulary, and connector-dependent features — with README as the narrative overview linking into docs/.

### Key Entities

- **Board**: generated HTML view of a season; disposable.
- **Fit feedback**: user-owned learned-rules file + append-only log; third compounding loop.

## Success Criteria *(mandatory)*

- **SC-005**: Sam's example season renders a correct board (committed as an example artifact) reproducibly via one command.
- **SC-006**: The fit loop is demonstrable in the example: at least one logged Sam correction whose rule is visibly applied in a later ranking excerpt.
- **SC-007**: A doc-audit finds no engine command or skill missing from docs/README, and no documented command that doesn't exist.

## Assumptions

- Board styling is intentionally minimal and readable; no JS beyond optional collapse toggles; must be legible printed.
- Fit-feedback influences agent judgment via instructions (like voice); no numeric model is trained in v1.
