"""Greenhouse — boards.greenhouse.io/{org} (or job-boards.greenhouse.io).

The public boards API lists every open job. A single job with
`?questions=true` returns the application form's fields — the pipeline
skill uses that URL shape for the form-review step.
"""
from __future__ import annotations

from ... import http
from ...posting import normalize_posting, remote_from_text
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "greenhouse"
BOARD_API = "https://boards-api.greenhouse.io/v1/boards/{org}/jobs"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    org = params["org"]
    payload = http.get_json(BOARD_API.format(org=org))
    postings = []
    for job in payload.get("jobs", []):
        location = (job.get("location") or {}).get("name")
        postings.append(normalize_posting(
            KEY, job.get("company_name") or org, job.get("id"), job.get("title"), job.get("absolute_url"),
            location=location,
            remote=remote_from_text(location),
            posted_at=job.get("first_published") or job.get("updated_at"),
            description=job.get("content"),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="Greenhouse (boards.greenhouse.io/{org})", fetch=fetch,
    url_patterns=(
        url_pattern(r"(?:job-boards|boards)\.greenhouse\.io/([^/?#]+)", lambda m: {"org": m.group(1)}),
        url_pattern(r"boards-api\.greenhouse\.io/v1/boards/([^/?#]+)", lambda m: {"org": m.group(1)}),
    ),
    notes="form fields: .../jobs/{id}?questions=true",
)
