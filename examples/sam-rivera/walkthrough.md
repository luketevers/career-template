# Walkthrough: Sam Rivera's example season

Everything in this folder was produced by the engine on 2026-09-11. Sam is
fictional; the postings referenced are real and public (see `snapshots/`).
Reproduce any step from the repo root.

## US1 — build and check a resume

```
python3 engine/build_resume.py \
  --profile examples/sam-rivera/profile.yaml \
  --resume  examples/sam-rivera/resume.yaml \
  --layout  engine/layouts/classic \
  --out     examples/sam-rivera/resume.html

python3 engine/render_check.py examples/sam-rivera/resume.html \
  --pdf "examples/sam-rivera/Sam Rivera Resume.pdf"
# → ok pages=1 / ok no orphan lines
```

Truth Only in action: add a bullet id that isn't in `profile.yaml` to
`resume.yaml` and the build fails with `unknown bullet id` — try it.

An earlier draft of Sam's profile had a project blurb that wrapped into a
two-word orphan line; `render_check` failed the build and the text was
tightened. That failure is the feature.

## US1 — the pipeline against a live board

With the repo's skills loaded, "check jobs.ashbyhq.com/linear against my
profile" produces a ranking like (excerpt from the recorded run):

> **Senior/Staff Product Engineer, AI — ~75%.** Sam's LLM-feature work
> with offline evaluation (500-case eval set gating the exception-triage
> launch) maps directly to the role's applied-AI product surface; the
> named gaps to expect in a screen: no model training (API-level work
> only) and no Kubernetes operations if the role leans infra.

...and ends in a submit checklist headed by the apply link, with Sam's
work-authorization line shown for Sam to type — never auto-filled.

## US2 — voice

`writing-feedback.md` here shows the post-bootstrap state: rules derived
from Sam's writing samples plus one logged correction ("cut the last
line, I'd never compliment a company's blog") that became a standing rule.

## US2b — fit judgment that learns

`fit-feedback.md` holds Sam's two logged corrections. A later ranking run
applies them visibly (excerpt from the recorded run):

> **Vanta-adjacent compliance role — ~82%** (base ~72%; per your rule:
> regulated-workflow domain familiarity from the Bluejay years upgrades
> compliance products ~10 points). **Mintlify-style role — ranked last
> regardless of 78% fit: 4 days in office, and your rule makes the onsite
> ceiling a sort key, not a footnote.**

The Vanta correction is the loop's proof: Sam overrode the agent's 70% to
80%, and the season retro shows that application becoming the offer.

## US3 — season lifecycle

```
cd examples/sam-rivera
python3 ../../engine/season.py scaffold 2026   # (already run)
python3 ../../engine/season.py close 2026      # (already run)
```

`searches/2026/applications.md` is the tracker with fit predictions
recorded at apply time; `searches/2026/retro.md` is the generated
calibration table — note the 80%-fit application converting to an offer in
4 days while the 60% one took 13 days to reject. That table is what "the
resume that compounds" means: season N's predictions, audited, feeding
season N+1's judgment.
