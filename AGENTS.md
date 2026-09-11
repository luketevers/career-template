# AGENTS.md — running the career engine with any coding agent

This repo is a file-based career system. Claude Code users get richer
skills in `.claude/skills/`; everything below works with any capable
coding agent. Two rules are absolute (see `.specify/memory/constitution.md`):
**never state a fact absent from profile.yaml**, and **never submit, send,
or auto-fill anything — the human reviews and submits everything.**

## Files

| Path | Meaning |
|---|---|
| `profile.yaml` | the user's verified facts; sole source for generation |
| `resume/resume.yaml` | evergreen resume as a selection of profile bullet ids |
| `searches/<season>/` | one job search: tracker + per-company folders |
| `writing-feedback.md` | the user's voice rules + feedback log (append-only) |
| `engine/` | build, render-check, season scripts |

## Workflows

**Setup (new user)**: verify the repo is PRIVATE; run
`python3 engine/onboard.py` for the structured fields (searchable job-title
picker, levels, locations, comp floor, resume page budget); then interview
the user to fill the rest of `profile.yaml` (facts only, outcome-first bullets with stable ids and
metrics; honest `gaps`); build `resume/resume.yaml` as a selection of those
ids; render and check (below) until green; `python3 engine/season.py
scaffold <year>`.

**Apply to a role**:
1. Fetch postings via the ATS API, not the JS page — Ashby
   `api.ashbyhq.com/posting-api/job-board/{org}`, Greenhouse
   `boards-api.greenhouse.io/v1/boards/{org}/jobs` (`?questions=true` for
   form fields), Lever `api.lever.co/v0/postings/{org}?mode=json`, Workday
   `{tenant}.wd{N}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs` (POST).
   Unknown ATS: ask the user to paste the posting and form.
2. Rank fit against `profile.yaml` targets/strengths/gaps — name the gaps
   the posting will probe; flag comp/onsite violations rather than hiding.
3. Tailor: copy `resume/resume.yaml` into `searches/<season>/<company>/`,
   adjust selection/summary, then
   `python3 engine/build_resume.py --profile profile.yaml --resume <that
   file> --layout engine/layouts/classic --out <folder>/resume.html` and
   `python3 engine/render_check.py <folder>/resume.html --pdf <folder>/
   "<Name> Resume - <Company>.pdf"`. Must exit 0: within `resume_style.max_pages` (default 1), no orphans.
   (Hand-written HTML: skip the build, still run the check.)
4. Enumerate every form field; present a checklist starting with the apply
   link; the user fills sensitive fields themselves.
5. Draft open-ended answers only after reading `writing-feedback.md`; if it
   still has the BOOTSTRAP-REQUIRED marker, first collect 2-3 samples of
   the user's real writing and derive voice rules into that file. Append a
   dated log entry whenever the user corrects tone or content.
6. When the user says they applied, add the tracker row (include the fit
   prediction — the retro needs it), commit, push.

**Season close**: resolve every tracker row to a terminal stage, then
`python3 engine/season.py close <season>` — generates `retro.md`
(predicted fit vs stage vs response time) and freezes the season
(append-only afterward).

**Inbox/calendar sweeps** are specified in `.claude/skills/season/SKILL.md`
but require mail/calendar tool access — Claude Code connectors or your
agent's equivalent. Without them, update the tracker manually.
