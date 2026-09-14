# career (from career-template)

A long-running, agent-operated career system. The user's data
(`profile.yaml`, `resume/`, `searches/`, `writing-feedback.md`) is
user-owned; the engine (`engine/`, `.claude/skills/`, `templates/`) takes
updates. Full boundary: `ENGINE-UPDATE.md`. Principles:
`.specify/memory/constitution.md` — two are absolute:

1. **Truth Only** — never state a fact absent from `profile.yaml`; ask,
   don't fill. The resume build enforces this in code.
2. **The human submits** — no auto-submit, no unattended email, no
   auto-filled sensitive fields. Ever, including when asked.

## Code conventions (engine/, tests/, scripts/)

- Soft limit of ~250 lines per file. Past that, split by responsibility
  (the `jobboards` package is the pattern: one module per source, a shared
  contract, a registry).
- Descriptive names over short ones: `applied_on`, not `a`; `posting`, not
  `p`. Single letters only as regex match objects or in comprehensions.
- Every module opens with a docstring saying what it is for and why it is
  shaped that way; comments explain intent and quirks, not syntax.
- New job-board source = one provider module + one fixture-backed test.

## Rules

- New users: run the `setup` skill before anything else (it also verifies
  the repo is private).
- If `import yaml` or `pdfminer` fails, the env isn't set up: run
  `bash scripts/install.sh` and `source .venv/bin/activate` (never pip
  install into the system Python on the user's behalf).
- Applications go through the `application-pipeline` skill; drafted prose
  goes through the `voice` skill (bootstrap gates an empty log).
- Every rendered resume must pass
  `python3 engine/render_check.py <html>` — one page, no orphan lines.
- Tracker updates (a row per application, with predicted fit) happen when
  the user reports applying; commit and push after each change.
- Inbox/calendar sweeps are propose-only; see the `season` skill.
- Seasons close via `python3 engine/season.py close <id>` and are
  append-only afterward.
- Interviews prep from the exact variant that company received
  (`interview-prep` skill); debrief the same day.
