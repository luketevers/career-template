# Engine updates and the ownership boundary

This template is designed to be updated inside a repo that carries years of
your career data. That only works if the boundary is absolute.

## Engine-owned paths (updates may rewrite these)

- `engine/` — scripts and layouts
- `templates/` — blank starting files (copied once at setup, never re-applied)
- `.claude/skills/` — agent skills
- `AGENTS.md`, `CLAUDE.md`, `README.md`, `LICENSE`, `ENGINE-UPDATE.md`
- `scripts/` — audit and utility scripts
- `examples/` — the fictional demo persona

## User-owned paths (updates must NEVER write these)

- `profile.yaml` — your verified facts
- `resume/` — your resume source and rendered PDFs
- `searches/` — every season, open or closed
- `writing-feedback.md` — your voice rules and log
- `fit-feedback.md` — your fit-judgment rules and log

## How to take an engine update

```
git remote add template https://github.com/OWNER/career-template  # once
git fetch template
git merge template/main
```

Conflicts can only occur in engine-owned paths. If a merge ever proposes a
change to a user-owned path, abort and report it as a template bug — that is
a violation of the project constitution (Principle III).

Schema changes to `profile.yaml`/`resume.yaml` are additive-only within a
major version; `engine/build_resume.py` must keep reading older profiles.
