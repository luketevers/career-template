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

## Rules

- New users: run the `setup` skill before anything else (it also verifies
  the repo is private).
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
