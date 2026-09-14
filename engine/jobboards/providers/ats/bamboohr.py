"""BambooHR — {company}.bamboohr.com/careers. The careers page's own JSON list."""
from __future__ import annotations

from ... import http
from ...posting import join_location, normalize_posting, remote_from_text
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "bamboohr"
LIST_API = "https://{company}.bamboohr.com/careers/list"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    company = params["company"]
    payload = http.get_json(LIST_API.format(company=company))
    postings = []
    for job in payload.get("result", []):
        location = job.get("location") or {}
        location_text = join_location(location.get("city"), location.get("state")) if isinstance(location, dict) else str(location)
        postings.append(normalize_posting(
            KEY, company, job.get("id"), job.get("jobOpeningName"),
            f"https://{company}.bamboohr.com/careers/{job.get('id')}",
            location=location_text,
            remote=True if job.get("isRemote") else remote_from_text(location_text),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="BambooHR ({company}.bamboohr.com/careers)", fetch=fetch,
    url_patterns=(url_pattern(r"([a-z0-9-]+)\.bamboohr\.com/", lambda m: {"company": m.group(1)}),),
)
