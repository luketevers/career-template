"""Jobicy — jobicy.com/api/v2/remote-jobs. Remote roles; `tag` filters server-side."""
from __future__ import annotations

import urllib.parse

from ... import http
from ...posting import normalize_posting, salary_range
from ...provider import KIND_AGGREGATOR, FetchOptions, Provider, url_pattern

KEY = "jobicy"
JOBS_API = "https://jobicy.com/api/v2/remote-jobs"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    query_string = urllib.parse.urlencode(
        {name: value for name, value in (("tag", options.query), ("count", options.max_items)) if value}
    )
    payload = http.get_json(JOBS_API + (f"?{query_string}" if query_string else ""))
    return [
        normalize_posting(
            KEY, job.get("companyName"), job.get("id"), job.get("jobTitle"), job.get("url"),
            location=job.get("jobGeo"),
            remote=True,
            salary=salary_range(job.get("salaryMin"), job.get("salaryMax"), job.get("salaryCurrency"), job.get("salaryPeriod")),
            posted_at=job.get("pubDate"),
            description=job.get("jobDescription"),
        )
        for job in payload.get("jobs", [])
    ]


PROVIDER = Provider(
    key=KEY, kind=KIND_AGGREGATOR, label="Jobicy (jobicy.com)", fetch=fetch,
    url_patterns=(url_pattern(r"(?:www\.)?jobicy\.com", lambda m: {}),),
    notes="alias jobicy; --query becomes their tag filter",
)
