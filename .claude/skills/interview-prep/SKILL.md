---
name: interview-prep
description: Prepare the user for a screen or interview with a specific company, grounded in the exact resume that company received. Use when an interview is scheduled or the user asks to prep.
---

# Interview prep

Ground rule: prep from what THIS company has and asked for — not from the
current state of the evergreen resume. Variants drift across a season; the
interviewer probes the copy they're holding.

## 1. Reconstruct what they're looking at

- Open `searches/<season>/<company>/`: the exact `resume.html`/PDF sent,
  `links.md` (posting URL, fit notes, the gaps named at application time),
  and any drafted answers.
- Re-fetch the posting (endpoints in the application-pipeline skill) in
  case it changed; note any interview-process description.
- Diff the sent variant against the current evergreen resume; if facts
  were later refined (numbers tightened, wording corrected), the user
  answers to THEIR copy first, then may add the refinement aloud.

## 2. Build the prep sheet — `searches/<season>/<company>/interview.md`

- **Expected probes**: each posting requirement mapped to the user's
  evidence; each profile `gap` the posting touches, with the honest
  pre-empt ("I haven't done X in production; here's the adjacent thing I
  have done and why it transfers"). Never coach a claim the profile can't
  back.
- **Stories to deploy**: pick 2-3 history bullets whose shape matches the
  company's values (ownership story, rigor story, craft story); note which
  and why.
- **The user's questions**: comp band if unposted (flag if the posting's
  floor is below `targets.comp_floor_usd`), onsite days if a form revealed
  them, team/roadmap specifics.
- **Logistics**: calendar check for conflicts against tracker Notes
  constraints (connector users).

## 3. Same-day debrief

Append to `interview.md`: questions actually asked, what landed, what
stumbled, next steps and dates. Update the tracker row's Stage. This is
calibration data for the season retro — capture it while it's fresh.
