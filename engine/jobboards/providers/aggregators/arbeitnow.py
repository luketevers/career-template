"""Arbeitnow — arbeitnow.com/api/job-board-api. European and remote roles."""
from __future__ import annotations

from ... import http
from ...posting import normalize_posting
from ...provider import KIND_AGGREGATOR, FetchOptions, Provider, url_pattern

KEY = "arbeitnow"
JOBS_API = "https://www.arbeitnow.com/api/job-board-api"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    payload = http.get_json(JOBS_API)
    return [
        normalize_posting(
            KEY, job.get("company_name"), job.get("slug"), job.get("title"), job.get("url"),
            location=job.get("location"),
            remote=job.get("remote"),
            posted_at=str(job.get("created_at") or ""),
            description=job.get("description"),
        )
        for job in payload.get("data", [])
    ]


PROVIDER = Provider(
    key=KEY, kind=KIND_AGGREGATOR, label="Arbeitnow (arbeitnow.com)", fetch=fetch,
    url_patterns=(url_pattern(r"(?:www\.)?arbeitnow\.com", lambda m: {}),),
    notes="alias arbeitnow",
)
