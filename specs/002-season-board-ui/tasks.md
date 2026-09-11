# Tasks: Season Board, Fit Personalization, and Docs

- [ ] T038 [US1] `engine/board.py`: parse tracker (reuse season.parse_rows), compute stage buckets/day counts/watchlist, emit self-contained board.html; CLI `board.py <season> [--watch-days N] [--out]` (FR-013/014)
- [ ] T039 [US1] `tests/test_board.py`: renders from a fixture tracker; watchlist logic; offer highlighted; regenerating overwrites cleanly
- [ ] T040 [US1] Generate and commit `examples/sam-rivera/searches/2026/board.html` (SC-005)
- [ ] T041 [US2] `templates/fit-feedback.md` (rules + log structure, seeded marker) (FR-015)
- [ ] T042 [US2] Wire fit loop into `application-pipeline` (read-before-rank, cite rules, log corrections, tracker gets user-approved fit) and `season` (board regen after updates; retro divergence note) and `setup` (copy template) (FR-016/017)
- [ ] T043 [US2] `examples/sam-rivera/fit-feedback.md` with two entries + a ranking excerpt in walkthrough showing a rule applied (SC-006)
- [ ] T044 [US3] `docs/capabilities.md` — the full reference (loops, commands, skills, stages, connectors) (FR-018)
- [ ] T045 [US3] README overhaul: the workflow narrative, three loops, board, docs links
- [ ] T046 Doc audit (SC-007) + full tests + personal-data audit; tick tasks
