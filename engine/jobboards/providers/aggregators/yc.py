"""Y Combinator jobs — ycombinator.com/jobs[/role/{r}][/location/{l}].

The public pages are Inertia-rendered: the full listing sits in a
`data-page` attribute as HTML-escaped JSON, so reading needs no login.
Postings carry salary, equity, visa, and skills. Applying goes through the
candidate's own Work at a Startup account, which is exactly the human's
job under the constitution — we only surface the link.
"""
from __future__ import annotations

import html
import json
import re

from ... import http
from ...posting import normalize_posting, remote_from_text
from ...provider import KIND_AGGREGATOR, FetchOptions, Provider, url_pattern

KEY = "yc"
SITE = "https://www.ycombinator.com"
DATA_PAGE_ATTRIBUTE = re.compile(r'data-page="([^"]+)"')
COMPANY_SLUG_IN_PATH = re.compile(r"/companies/([^/]+)/")


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    page_html = http.get_text(SITE + _jobs_path(params))
    match = DATA_PAGE_ATTRIBUTE.search(page_html)
    if not match:
        raise ValueError("yc: no embedded data-page JSON found (page layout changed?)")
    page_props = json.loads(html.unescape(match.group(1))).get("props", {})
    return [_to_posting(job) for job in page_props.get("jobPostings", [])]


def _jobs_path(params: dict) -> str:
    path = "/jobs"
    if params.get("role"):
        path += f"/role/{params['role']}"
    if params.get("location"):
        path += f"/location/{params['location']}"
    return path


def _to_posting(job: dict) -> dict:
    posting_url = job.get("url") or ""
    if posting_url.startswith("/"):
        posting_url = SITE + posting_url
    slug_match = COMPANY_SLUG_IN_PATH.search(posting_url)
    company = slug_match.group(1) if slug_match else None
    equity = job.get("equityRange")
    salary = " • ".join(part for part in (job.get("salaryRange"), f"equity {equity}" if equity else None) if part) or None
    return normalize_posting(
        KEY, company, job.get("id"), job.get("title"), posting_url,
        location=job.get("location"),
        remote=remote_from_text(job.get("location")),
        apply_url=job.get("applyUrl"),
        salary=salary,
    )


PROVIDER = Provider(
    key=KEY, kind=KIND_AGGREGATOR, label="Y Combinator jobs (ycombinator.com/jobs)", fetch=fetch,
    url_patterns=(
        url_pattern(
            r"(?:www\.)?(?:ycombinator\.com/jobs|workatastartup\.com)(?:/role/([^/?#]+))?(?:/location/([^/?#]+))?",
            lambda m: {"role": m.group(1), "location": m.group(2)},
        ),
    ),
    notes="alias yc; --role and --location narrow the page; applying needs the user's WaaS account",
)
