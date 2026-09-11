# Career Template Constitution

The product: a long-running, agent-operated career system. A user's resume,
job searches, and the lessons from every application, rating, and rejection
live in one private repo that compounds across seasons. This template is the
engine; the user's data never lives in it.

## Core Principles

### I. Truth Only (NON-NEGOTIABLE)
Nothing the system writes on a user's behalf may state a fact the user has
not supplied. Resume bullets, answers, and cover notes are selected or
recomposed from the user's verified profile — never invented. Every
generated claim must be traceable to a profile entry. When a fact is
missing, the system asks; it does not fill.

### II. The Human Submits (NON-NEGOTIABLE)
There is no auto-submit code path, no bulk-apply queue, and no unattended
outbound email. The system prepares; the user reviews and sends. Sensitive
fields (demographics, work authorization, compensation expectations) are
never auto-filled. This is a positioning choice as much as an ethical one:
low volume, high tailoring, zero spam.

### III. Engine/Data Separation
The template contains no personal data. All user-specific content — resume
facts, voice rules, fit profile, application history — lives in files the
user owns (`profile.yaml`, `resume/`, `searches/`, `writing-feedback.md`)
created after cloning. Template updates must merge cleanly into a repo
carrying years of user data.

### IV. Compounding by Design
Every interaction leaves a durable trace the system reads next time: voice
feedback appends to a log, application outcomes append to a season tracker,
seasons close with a calibration retro. A feature that produces output
without capturing feedback is incomplete.

### V. Seasons Are Immutable History
A job search is a season (`searches/<year>/`). While open it is the working
state; once closed it freezes as the record the next season learns from.
The evergreen layer (resume, voice log, skills) is the only thing seasons
mutate.

### VI. User-Owned Runtime
The system runs inside the user's own coding agent with the user's own
credentials and connectors (email, calendar). The template ships no hosted
service, collects no telemetry, and holds no keys. Public ATS APIs are used
read-only for postings; no scraping behind auth.

### VII. Plain Files Over Machinery
State lives in human-readable files (markdown, YAML, HTML) a user can edit
without the agent. Tooling that adds a database or build step must justify
itself against "the user opens the file and types."

## Constraints

- Rendered resumes verified against the profile's declared page budget
  (`resume_style.max_pages`, default one page); no orphan lines.
  *(Amended 1.0.0→1.1.0: a fixed one-page rule excluded academic, federal,
  and senior-exec resumes; the budget is now the user's, the check stays.)*
- Skills read the user profile; they never hardcode a person.
- The template's example data is fictional and marked as such.

## Governance

This constitution supersedes convenience. Any spec, plan, or task that
conflicts with Principles I or II is rejected, including user requests to
add auto-submit ("the feature that collapses the differentiation").
Amendments require a documented rationale in this file's history.

**Version**: 1.1.0 | **Ratified**: 2026-09-11 | **Last Amended**: 2026-09-11
