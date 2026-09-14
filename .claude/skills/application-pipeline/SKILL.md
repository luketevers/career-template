---
name: application-pipeline
description: End-to-end job application pipeline. Pass a job board or posting URL to scan roles, rank fit against the user's profile, tailor a one-page resume variant, enumerate the application form's fields, and draft answers in the user's voice — or use without args when just drafting application content.
---

# Application pipeline

Ground rules (from the constitution, non-negotiable):

- **Truth Only.** Every claim comes from `profile.yaml`. Missing fact →
  ask the user, add it to the profile, then use it. Never fill a gap with
  plausible prose.
- **The human submits.** The pipeline ends at a checklist and drafts. Never
  submit a form, send an email, or fill demographics/work-authorization/
  compensation fields.

Read `profile.yaml` first. If it doesn't exist or is blank, stop and run
the `setup` skill.

## 1. Pull the board

Fetch postings with the engine, never by scraping the JS page:

```
python3 engine/boards.py <board-url-or-source> --titles-from profile.yaml --json
```

It detects the provider from the URL and returns one normalized shape
(`source, company, id, title, location, remote, url, apply_url, salary,
posted_at, description`). `--titles-from profile.yaml` keeps postings whose
title contains any of `targets.titles`; drop it to see the whole board.
`python3 engine/boards.py --list` prints every supported source.

- **ATS boards** (one URL = one company): Ashby, Greenhouse, Lever, Workday,
  SmartRecruiters, Rippling, Workable, BambooHR, Personio, Recruitee. Pass
  the board URL (e.g. `https://jobs.ashbyhq.com/{org}`, `https://boards.greenhouse.io/{org}`,
  `https://{tenant}.wd5.myworkdayjobs.com/{site}`). A company careers page
  that embeds one of these is detected automatically.
- **Aggregators** (many companies; filter by title): `yc` (Y Combinator's
  public jobs pages — add `--role software-engineer`, `--location remote`;
  applying goes through the user's own Work at a Startup account), `hn`
  (the latest "Ask HN: Who is hiring" thread — free-text posts, read the
  `description` for details), `remotive`, `remoteok`, `himalayas`, `jobicy`,
  `arbeitnow`, `wwr` (We Work Remotely).
- **VC portfolio boards** (custom domains — pass the `/jobs` URL): Consider-
  hosted (Sequoia, Kleiner Perkins, Bessemer, Lightspeed, First Round, …) and
  Getro-hosted (Accel, …). Detected from the page. Consider has no server
  search, so use `--titles-from profile.yaml --max 500`; Getro takes
  `--query`. Each posting's `url` is the company's own ATS — hand that to the
  form step. Custom VC boards (a16z, Greylock) aren't supported; their
  postings link to Greenhouse/Ashby pages, which are.
- **Application form fields**: Greenhouse exposes them at
  `https://boards-api.greenhouse.io/v1/boards/{org}/jobs/{id}?questions=true`;
  Ashby's hosted board GraphQL (`ApiJobPosting` on `jobs.ashbyhq.com/api/non-user-graphql`)
  lists its fields. For everything else, open `apply_url` and enumerate by hand.
- **Exit 2 / "no known job board"**: the ATS isn't supported. Ask the user
  to paste the posting and form questions. Never silently skip the
  form-review step. Adding a provider means a fetcher + a fixture test in
  `engine/boards.py` / `tests/test_boards.py`, not a prose bullet here.

## 2. Rank fit

Read from `profile.yaml`: `targets` (titles, locations, onsite_days_max,
levels, comp_floor_usd), `strengths`, `gaps`, and the history bullets.
Filter and rank the board primarily around `targets.titles` (and near
synonyms), surfacing near-misses worth a look rather than hiding them. Then read
`fit-feedback.md` — the user's logged corrections to past rankings. Apply
its learned rules and CITE them in the assessment ("per your rule: domain
match outweighs stack gaps"). If the file still carries the SEEDED-EMPTY
marker, tell the user their corrections will be learned from here on.

- Give honest fit percentages. Name which of the user's `gaps` the posting
  will probe — that's the section's purpose. A ranking that never cites a
  gap is flattery, not analysis.
- Flag postings below `comp_floor_usd` or beyond `onsite_days_max` rather
  than hiding them; those are the user's calls.
- Recommend ONE primary role per company; note a fallback req in links.md.
- When the user corrects a ranking (reorders, changes a number, vetoes):
  append a dated entry to `fit-feedback.md` — agent number, user number,
  the user's reason in their words — in the same commit, and distill a rule
  into its Fit Rules section when a pattern repeats. The TRACKER records
  the user-approved number; that is what the season retro audits.
- Check the current season's tracker (`searches/<season>/applications.md`)
  for already-applied companies.

## 3. Tailor the variant

Work in `searches/<season>/<company>/`:

1. Copy the user's evergreen `resume/resume.yaml` into the folder; adjust
   the summary and bullet selection for this posting. Only reorder, select,
   or lightly recompose — the build enforces provenance.
2. Build: `python3 engine/build_resume.py --profile profile.yaml
   --resume searches/<season>/<company>/resume.yaml
   --layout engine/layouts/<layout> --out .../resume.html --title <Company>`
3. Check: `python3 engine/render_check.py .../resume.html --pdf
   ".../<Name> Resume - <Company>.pdf" --max-pages <resume_style.max_pages>`.
   Fix and re-run until clean — within the profile's page budget (default
   one page), no orphan lines. Never hand over a failing render.
4. Write `links.md`: posting URL, comp, fit notes with named gaps,
   alternates considered.
5. Record the fit prediction in the tracker row when the user applies —
   the season retro needs it.

(Hand-written-HTML users: skip the build, run render_check on their file.)

## 4. Review the application form

Fetch every field before drafting (Greenhouse `?questions=true`; Ashby
GraphQL below; otherwise ask the user to paste the form):

```json
{"operationName":"ApiJobPosting",
 "variables":{"organizationHostedJobsPageName":"{org}","jobPostingId":"{id}"},
 "query":"query ApiJobPosting($organizationHostedJobsPageName: String!, $jobPostingId: String!) { jobPosting(organizationHostedJobsPageName: $organizationHostedJobsPageName, jobPostingId: $jobPostingId) { applicationForm { sections { fieldEntries { isRequired field } } } } }"}
```

(Each entry's `field` has `title` and `type`; the schema rejects a `fields`
selection — it's `fieldEntries`.)

Present a submit checklist that ALWAYS starts with the apply link, then
every field with suggested values from `profile.yaml` (name, email, links,
location). Flag what only the user can answer: compensation expectations,
start date, referrals, how-did-you-hear, demographics, work authorization
(show the profile's stated answer; the user types it). Surface anything the
form reveals that the posting didn't (in-office days, unposted essays).

## 5. Draft answers in the user's voice

For every open-ended question, follow the `voice` skill: it gates on the
bootstrap, applies the user's voice rules, and logs feedback. Content
rules: answer every part of multi-part questions; at most one evaluative
phrase about the company, placed late; pre-empt the user's most relevant
`gap` honestly near the end; mark any claim the profile can't back; remind
the user that retyping the draft loosely beats pasting it.

## 6. Track

When the user reports applying: add the tracker row (company, role, date,
resume file, predicted fit, stage=applied), commit, push. The user's word
is the only thing that moves a row to applied — see ground rules.
