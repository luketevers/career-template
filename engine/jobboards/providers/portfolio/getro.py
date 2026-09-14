"""Getro-hosted VC portfolio boards — Accel and others on their own domains.

Server-rendered Next.js: every /jobs page embeds twenty jobs in the
`__NEXT_DATA__` script as `initialState.jobs.found`, with the total count
alongside. `?q=` filters server-side and `?page=N` paginates, so --query
is cheap here. Postings link to each portfolio company's own ATS.
"""
from __future__ import annotations

import json
import re
import urllib.parse

from ... import http
from ...posting import normalize_posting
from ...provider import KIND_PORTFOLIO, FetchOptions, Provider

KEY = "getro"
NEXT_DATA_SCRIPT = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
PAGE_SIGNATURE = re.compile(r'cdn\.getro\.com.*?id="__NEXT_DATA__"', re.S)
DEFAULT_MAX_ITEMS = 200
# Getro's workMode is explicit, so on-site and hybrid can be reported as not remote.
REMOTE_BY_WORK_MODE = {"remote": True, "on_site": False, "hybrid": False}


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    host = params["host"]
    limit = options.limit(DEFAULT_MAX_ITEMS)
    postings: list[dict] = []
    page_number = 1
    while len(postings) < limit:
        page_html = _page_html(host, params, options.query, page_number)
        script_match = NEXT_DATA_SCRIPT.search(page_html)
        if not script_match:
            raise ValueError(f"getro: no __NEXT_DATA__ on {host}/jobs (layout changed?)")
        next_data = json.loads(script_match.group(1))
        jobs_state = (((next_data.get("props") or {}).get("pageProps") or {}).get("initialState") or {}).get("jobs") or {}
        page = jobs_state.get("found") or []
        postings.extend(_to_posting(job) for job in page)
        total_available = int(jobs_state.get("total") or 0)
        if not page or len(postings) >= total_available:
            break
        page_number += 1
    return postings


def _page_html(host: str, params: dict, query: str | None, page_number: int) -> str:
    # The sniff that recognized this board already fetched page 1; reuse it
    # unless a query changes what page 1 contains.
    if page_number == 1 and not query and params.get("page_html"):
        return params["page_html"]
    query_params = {name: value for name, value in (("q", query), ("page", page_number if page_number > 1 else None)) if value}
    query_string = urllib.parse.urlencode(query_params)
    return http.get_text(f"https://{host}/jobs" + (f"?{query_string}" if query_string else ""))


def _to_posting(job: dict) -> dict:
    organization = job.get("organization") or {}
    salary_low_cents, salary_high_cents = job.get("compensationAmountMinCents"), job.get("compensationAmountMaxCents")
    salary = f"${salary_low_cents // 100:,}–${salary_high_cents // 100:,}" if salary_low_cents and salary_high_cents else None
    locations = job.get("searchableLocations") or []
    return normalize_posting(
        KEY, organization.get("name") or organization.get("slug"), job.get("id"), job.get("title"), job.get("url"),
        location=", ".join(locations[:2]) if isinstance(locations, list) else str(locations),
        remote=REMOTE_BY_WORK_MODE.get(job.get("workMode")),
        salary=salary,
        posted_at=str(job.get("createdAt") or ""),
    )


PROVIDER = Provider(
    key=KEY, kind=KIND_PORTFOLIO, label="Getro-hosted VC boards (jobs.accel.com, ...)",
    fetch=fetch, page_signature=PAGE_SIGNATURE,
    notes="pass the board's /jobs URL; --query filters server-side",
)
