---
name: setup
description: First-run setup for the career repo — interview the user into profile.yaml and resume.yaml, verify the repo is private, and produce their first rendered resume. Use on a fresh clone or whenever profile.yaml is missing or empty.
---

# Setup

Goal: clone → filled profile → first clean one-page render, in under an
hour (SC-001). Everything created here is user-owned (see ENGINE-UPDATE.md)
and never leaves their machine except via their own git remote.

## 0. Privacy first

Before collecting a single fact, confirm the repo is private:
`gh repo view --json isPrivate` (or ask the user to check). This repo will
hold their career history, application record, and voice — it must never be
a public fork of the template. If they created it from the GitHub template
button, verify they chose Private.

## 0b. Environment

If `python3 -c "import yaml, pdfminer"` fails or no Chrome/Chromium is
found, have the user run `bash scripts/install.sh` (add `--with-browser` to
install one) and `source .venv/bin/activate`, then continue. The script is
idempotent and writes nothing into the repo.

## 1. Onboard the structured fields

Run the interactive onboarding: `python3 engine/onboard.py`. It fills the
enumerable half of profile.yaml — identity basics, target job titles (a
searchable list of 200+ titles across every field, custom entries welcome),
seniority levels, locations, remote/onsite ceiling, compensation floor, and
the resume page budget (`resume_style.max_pages`) — creating the file from
the template with all schema comments intact. Safe to re-run when targets
change.

## 1b. Interview the rest into profile.yaml

Fill the remaining sections in conversation. Guidance per section:

- **identity/links**: verbatim from the user.
- **targets**: make the user commit to numbers — comp floor, max onsite
  days, level names. Vague targets make every later fit ranking mushy.
- **strengths**: 3-5 short claims, each must be backed by at least one
  history bullet. If a strength has no bullet, get the bullet first.
- **gaps**: push for honesty here; explain that gaps power the honest fit
  rankings and pre-empted interview answers, and are never shown to
  employers. "Things you'd dread being asked about" is a good prompt.
- **history bullets**: outcome first, plain language a non-technical
  recruiter can scan, numbers included and echoed in `metrics`. Assign
  stable ids (`<companyslug>-<topic>`). 3-6 bullets per recent role. Push
  back on vague bullets ("responsible for...") the way an editor would —
  ask "what changed because you did this, and by how much?"
- If the user has an existing resume (PDF/doc), read it and convert bullets
  WITH the user confirming each fact — do not import claims unverified.

## 2. Build resume.yaml

Copy `templates/resume.yaml` to `resume/resume.yaml`. Select and order
bullets with the user; write the summary together (2-4 sentences, their
strongest true claims). Copy `templates/writing-feedback.md` and `templates/fit-feedback.md` to
the root — the voice skill bootstraps the first on first drafting; the
pipeline announces the second on first ranking.

## 3. First render

```
python3 engine/build_resume.py --profile profile.yaml \
  --resume resume/resume.yaml --layout engine/layouts/classic \
  --out resume/resume.html
python3 engine/render_check.py resume/resume.html --pdf resume/resume.pdf \
  --max-pages $(python3 -c "import yaml;print(yaml.safe_load(open('profile.yaml'))['resume_style']['max_pages'])")
```

Show both layouts (`classic`, `compact`), let the user pick. Iterate until
the check passes: within the profile's page budget (one page for most
industries), no orphan lines. If content overflows,
cut with the user — never shrink fonts below the layout's design.

## 4. Start the season

Scaffold the first season: `python3 engine/season.py scaffold <year>`.
Commit everything and confirm the push target is their private repo.

Done when: profile complete, render check green, tracker scaffolded, repo
private, first commit pushed.
