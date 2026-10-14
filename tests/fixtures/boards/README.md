# Board fixtures

Trimmed to two items each. Captured live on 2026-09-14 from public endpoints
(company names are those of public postings on that day), except the three
marked synthetic, where no tenant with open postings was found on capture day
and the shape follows the provider's public documentation:

- synthetic: `workable.json`, `bamboohr.json`, `recruitee.json`
- `paraform.html`: one role (a share link is always one role), captured
  2026-10-14 and trimmed: description shortened, company prose and the
  hiring manager's name replaced, Next.js build id dropped.

Re-capture: see the endpoint in each `fetch_*` in `engine/boards.py`.
