# Feature Specification: Todos and the Morning Digest

**Feature Branch**: `003-todos-and-digest` (implemented on `main`)

**Created**: 2026-09-17

**Status**: Implemented (scope set directly by the maintainer)

**Input**: User description: "add a todo list so a user can find roles and, if they know someone or are waiting for something before they apply, mark tasks as todos — like 'todo: apply to Snowflake after getting referral link'. Those should be reported in the sweep. Maybe a morning email with the state of the job hunt."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Park a blocked application as a todo (Priority: P1)

A user finds a role they want but cannot apply yet: a friend is sending a
referral link, a req is closed until next quarter, a recruiter said "ping
me after the offsite". They say "todo: apply to Snowflake after getting
the referral link". The agent records it in the season tracker with what it
is waiting on. It is neither a queue entry (it is not merely unranked) nor
an application row (nothing was submitted). When the blocker clears, the
todo is marked done and the application row is added as usual.

**Independent Test**: run the todos command against a scaffolded season;
the tracker gains a numbered row with the todo, company, waiting-on
clause, and date; `done` stamps the row; both survive hand edits.

**Acceptance Scenarios**:

1. **Given** an open season, **When** the user adds "apply to Snowflake after getting referral link", **Then** the tracker's `## Todos` table has a row numbered 1 with todo "apply to Snowflake" and waiting-on "getting referral link", dated today.
2. **Given** a tracker created before this feature (no Todos section), **When** a todo is added, **Then** the section is created before Notes and nothing else in the tracker changes.
3. **Given** todo #1 exists, **When** the user marks it done, **Then** its Done cell carries today's date, the row remains, and the next todo is numbered 2 — numbers are never reused.

---

### User Story 2 - Todos are visible everywhere the season is (Priority: P1)

Open todos appear on the board, in the morning digest, and in every inbox
sweep. The sweep reports each open todo with what it waits on and, when
the sweep's mail or calendar contains evidence the blocker has cleared
(the referral link arrived, the contact replied), quotes it and proposes
marking the todo done. Propose-only, as with every sweep edit.

**Independent Test**: render the board and the digest from one tracker
with one open and one done todo; both show the open one with its
waiting-on clause and neither shows the done one.

**Acceptance Scenarios**:

1. **Given** a tracker with an open todo, **When** the board renders, **Then** a Todos section lists it with company and waiting-on before the silence watchlist.
2. **Given** the same tracker, **When** the digest runs, **Then** its Todos section lists the same todo with its age in days, and the counts match the board's tiles.

---

### User Story 3 - A morning digest of the hunt (Priority: P2)

Each morning the user wants one short read: how many applications are in
flight, what is waiting on them (todos), who has gone quiet, and which
conversations are live. The digest command prints that as markdown. It
can be run on demand, by a scheduled Claude Code routine that posts it as
a notification, or written to a Gmail draft addressed to the user.

**Constitutional constraint**: Principle II forbids unattended outbound
email, including mail to the user themselves. The digest is therefore
never *sent* by the system. The requested "morning email" is delivered as
a scheduled notification or a draft; sending remains the human's act.

**Independent Test**: run the digest against a fixture season; the output
opens with the date and season, then counts, todos, gone-quiet rows, and
live conversations, in that order; `--json` yields the same data.

---

### Edge Cases

- A todo whose text contains `|` must not break the markdown table (the
  character is replaced).
- Marking a missing or already-done todo fails with a message naming the
  open numbers.
- An empty season digests to "none" in every section rather than erroring.
- The Todos table is optional in old trackers; every reader treats a
  missing section as empty.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-019**: The tracker template MUST carry a `## Todos` table with columns `#`, `Todo`, `Company`, `Waiting on`, `Added`, `Done`.
- **FR-020**: `engine/todos.py` MUST add, complete, and list todos; `add` MUST split an after/once/when/pending clause into *Waiting on*; numbers MUST be monotonic and never reused; completing MUST keep the row with a date.
- **FR-021**: `engine/board.py` and `engine/digest.py` MUST derive their numbers from one shared reader (`engine/season_state.py`) and MUST both show open todos.
- **FR-022**: The season skill MUST capture "todo:"-shaped requests via the command, report open todos in every sweep with evidence-based proposals to complete them, and describe digest delivery paths that comply with Principle II.
- **FR-023**: No code path MAY send the digest as email; the skill MUST refuse a request to do so and offer the notification or draft path.

### Success Criteria

- **SC-008**: A todo phrased naturally ("apply to X after Y") round-trips into the tracker and back out through the board and the digest without the user editing markdown.
- **SC-009**: Board tiles and digest counts are equal for any tracker (they share `season_state`).
- **SC-010**: All engine files stay under the ~250-line convention after the feature.
