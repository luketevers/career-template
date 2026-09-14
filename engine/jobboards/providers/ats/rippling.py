"""Rippling ATS — ats.rippling.com/{org}/jobs. Public board API, a bare list."""
from __future__ import annotations

from ... import http
from ...posting import normalize_posting, remote_from_text
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "rippling"
BOARD_API = "https://api.rippling.com/platform/api/ats/v1/board/{org}/jobs"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    org = params["org"]
    postings = []
    for job in http.get_json(BOARD_API.format(org=org)):
        work_location = job.get("workLocation") or {}
        location = work_location.get("label") or work_location.get("name") if isinstance(work_location, dict) else str(work_location)
        postings.append(normalize_posting(
            KEY, org, job.get("uuid"), job.get("name"), job.get("url"),
            location=location,
            remote=remote_from_text(location),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="Rippling ATS (ats.rippling.com/{org}/jobs)", fetch=fetch,
    url_patterns=(url_pattern(r"ats\.rippling\.com/([^/?#]+)", lambda m: {"org": m.group(1)}),),
)
