# Tasks: Todos and the Morning Digest (003)

- [x] T049 [US1] `templates/tracker.md`: `## Todos` table (`# | Todo | Company | Waiting on | Added | Done`) with a one-line explainer (FR-019)
- [x] T050 [US1] `engine/todos.py`: `add` (after/once/when/pending split → Waiting on; stable numbering; creates the section in older trackers before Notes), `done` (dates the row, keeps it), `list [--all]`; `tests/test_todos.py` (FR-020)
- [x] T051 [US2] `engine/season_state.py`: one reader for live/resolved/advanced/offers, gone-quiet rows, open and done todos; `engine/board.py` rewritten on top of it with a Todos section; `engine/digest.py` markdown + `--json`; `tests/test_digest.py` (FR-021, SC-009)
- [x] T052 [US2] `season` skill: Todos section (capture, done, list), sweep step 5 reports todos with evidence-based completion proposals (FR-022)
- [x] T053 [US3] `season` skill: Morning digest section — on-demand, scheduled routine as notification, Gmail draft; never sent, never unattended, with the refusal wording (FR-023)
- [x] T054 Docs: `docs/capabilities.md` (commands, engine layout, "Todos and the morning digest" section), README workflow step 6, `AGENTS.md`, `CLAUDE.md` rule
- [x] T055 Example: Sam Rivera's season gains a completed todo; `board.html` regenerated
- [x] T056 Full suite + personal-data audit green; every engine file under ~250 lines (SC-010)

## Not done, on purpose

- Sending the digest by email. Constitution II. The maintainer asked "might
  be good to set up a morning email"; the answer is a scheduled notification
  or a draft, documented in the season skill.
