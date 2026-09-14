"""Workable — apply.workable.com/{account}. The v3 jobs search the hosted
careers page uses: a POST that accepts free-text `query`."""
from __future__ import annotations

from ... import http
from ...posting import join_location, normalize_posting
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "workable"
SEARCH_API = "https://apply.workable.com/api/v3/accounts/{account}/jobs"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    account = params["account"]
    payload = http.post_json(SEARCH_API.format(account=account), {"query": options.query or ""})
    postings = []
    for job in payload.get("results", []):
        location = job.get("location") or {}
        location_text = (
            join_location(location.get("city"), location.get("region"), location.get("country"))
            if isinstance(location, dict) else str(location)
        )
        shortcode = job.get("shortcode")
        postings.append(normalize_posting(
            KEY, account, shortcode, job.get("title"), f"https://apply.workable.com/{account}/j/{shortcode}/",
            location=location_text,
            remote=job.get("remote"),
            posted_at=job.get("published"),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="Workable (apply.workable.com/{account})", fetch=fetch,
    url_patterns=(url_pattern(r"apply\.workable\.com/([^/?#]+)", lambda m: {"account": m.group(1)}),),
    notes="--query searches server-side",
)
