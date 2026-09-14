"""Remotive — remotive.com public remote-jobs API. Supports search and limit."""
from __future__ import annotations

import urllib.parse

from ... import http
from ...posting import normalize_posting
from ...provider import KIND_AGGREGATOR, FetchOptions, Provider, url_pattern

KEY = "remotive"
JOBS_API = "https://remotive.com/api/remote-jobs"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    query_string = urllib.parse.urlencode(
        {name: value for name, value in (("search", options.query), ("limit", options.max_items)) if value}
    )
    payload = http.get_json(JOBS_API + (f"?{query_string}" if query_string else ""))
    return [
        normalize_posting(
            KEY, job.get("company_name"), job.get("id"), job.get("title"), job.get("url"),
            location=job.get("candidate_required_location"),
            remote=True,
            salary=job.get("salary"),
            posted_at=job.get("publication_date"),
            description=job.get("description"),
        )
        for job in payload.get("jobs", [])
    ]


PROVIDER = Provider(
    key=KEY, kind=KIND_AGGREGATOR, label="Remotive (remotive.com)", fetch=fetch,
    url_patterns=(url_pattern(r"(?:www\.)?remotive\.(?:com|io)", lambda m: {}),),
    notes="alias remotive; --query and --max apply server-side",
)
