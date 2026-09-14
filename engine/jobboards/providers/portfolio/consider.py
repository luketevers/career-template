"""Consider-hosted VC portfolio boards — Sequoia, Kleiner Perkins, Bessemer,
Lightspeed, First Round, and others on their own jobs.* domains.

How the site works, and therefore how we do:

1. GET /jobs sets a session cookie and embeds a matching `csrfToken` and
   the `board` descriptor in the page. (The shared cookie jar in http.py
   keeps that session for the POST.)
2. POST /api-boards/search-jobs with the token as a header. Results page
   by an opaque `sequence` cursor returned in `meta`.

The endpoint ignores every text-search key we tried, so filtering is
client-side: the caller caps with --max and filters by title. Postings
link to each portfolio company's own ATS, where the form step continues.
A board that redirects /jobs to a login-walled talent network has no token
in the page, which raises a clear error instead of a confusing empty list.
"""
from __future__ import annotations

import json
import re

from ... import http
from ...posting import normalize_posting
from ...provider import KIND_PORTFOLIO, FetchOptions, Provider

KEY = "consider"
CSRF_TOKEN_IN_PAGE = re.compile(r'"csrfToken":"([^"]+)"')
BOARD_IN_PAGE = re.compile(r'"board":(\{[^{}]*\})')
PAGE_SIGNATURE = re.compile(r'/api-boards/|"csrfToken":"[^"]+".{0,400}"board":\{', re.S)
PAGE_SIZE = 100
DEFAULT_MAX_ITEMS = 500


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    host = params["host"]
    page_html = params.get("page_html") or http.get_text(f"https://{host}/jobs")
    token_match = CSRF_TOKEN_IN_PAGE.search(page_html)
    board_match = BOARD_IN_PAGE.search(page_html)
    if not (token_match and board_match):
        raise ValueError(f"consider: no csrfToken/board in {host} page (login-gated board?)")
    board = json.loads(board_match.group(1))
    headers = {
        "x-csrf-token": token_match.group(1),
        "Origin": f"https://{host}",
        "Referer": f"https://{host}/jobs",
    }
    limit = options.limit(DEFAULT_MAX_ITEMS)
    postings: list[dict] = []
    cursor = None
    while len(postings) < limit:
        page_meta = {"size": min(PAGE_SIZE, limit - len(postings))}
        if cursor:
            page_meta["sequence"] = cursor
        payload = http.post_json(
            f"https://{host}/api-boards/search-jobs",
            {"meta": page_meta, "board": board, "query": {"promoteFeatured": True}},
            headers,
        )
        page = payload.get("jobs") or []
        postings.extend(_to_posting(job) for job in page)
        cursor = (payload.get("meta") or {}).get("sequence")
        total_available = int(payload.get("total") or 0)
        if not page or not cursor or len(postings) >= total_available:
            break
    return postings


def _to_posting(job: dict) -> dict:
    locations = job.get("locations") or []
    remote_flag = job.get("remote")
    return normalize_posting(
        KEY, job.get("companyName") or job.get("companySlug"), job.get("jobId"), job.get("title"), job.get("url"),
        location=", ".join(locations[:2]) if isinstance(locations, list) else str(locations),
        remote=remote_flag if isinstance(remote_flag, bool) else None,
        apply_url=job.get("applyUrl"),
        salary=_salary_text(job.get("salary")),
        posted_at=job.get("timeStamp"),
    )


def _salary_text(salary: dict | None) -> str | None:
    """Consider nests currency and period as {label, value} objects."""
    if not isinstance(salary, dict) or not salary.get("minValue"):
        return None

    def label_of(field: object) -> str:
        return (field.get("value") or field.get("label") or "") if isinstance(field, dict) else str(field or "")

    return f"{label_of(salary.get('currency'))} {salary['minValue']}–{salary.get('maxValue', '')} / {label_of(salary.get('period'))}".strip(" /")


PROVIDER = Provider(
    key=KEY, kind=KIND_PORTFOLIO, label="Consider-hosted VC boards (jobs.sequoiacap.com, Kleiner Perkins, Bessemer, ...)",
    fetch=fetch, page_signature=PAGE_SIGNATURE,
    notes="pass the board's /jobs URL; no server search — use --titles/--titles-from with --max",
)
