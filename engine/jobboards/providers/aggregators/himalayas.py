"""Himalayas — himalayas.app/jobs/api. Remote roles; cursor-paginated feed
(we take the first page up to --max)."""
from __future__ import annotations

from ... import http
from ...posting import normalize_posting, salary_range
from ...provider import KIND_AGGREGATOR, FetchOptions, Provider, url_pattern

KEY = "himalayas"
JOBS_API = "https://himalayas.app/jobs/api?limit={limit}"
DEFAULT_MAX_ITEMS = 100


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    payload = http.get_json(JOBS_API.format(limit=options.limit(DEFAULT_MAX_ITEMS)))
    postings = []
    for job in payload.get("jobs", []):
        postings.append(normalize_posting(
            KEY, job.get("companyName"), job.get("guid"), job.get("title"),
            job.get("applicationLink") or job.get("guid"),
            location=", ".join(job.get("locationRestrictions") or []) or None,
            remote=True,
            salary=salary_range(job.get("minSalary"), job.get("maxSalary"), job.get("currency"), job.get("salaryPeriod")),
            posted_at=str(job.get("pubDate") or ""),
            description=job.get("description"),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_AGGREGATOR, label="Himalayas (himalayas.app)", fetch=fetch,
    url_patterns=(url_pattern(r"(?:www\.)?himalayas\.app", lambda m: {}),),
    notes="alias himalayas",
)
