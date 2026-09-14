"""Workday — {tenant}.wd{N}.myworkdayjobs.com/{locale}/{site}.

Every tenant exposes the same "cxs" search endpoint the careers page
itself calls: a POST with search text and offset. Tenants vary in what
they return, so this is best effort. The list endpoint carries no
description; the posting URL does.
"""
from __future__ import annotations

from ... import http
from ...posting import normalize_posting, remote_from_text
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "workday"
SEARCH_API = "https://{host}/wday/cxs/{tenant}/{site}/jobs"
PAGE_SIZE = 20
DEFAULT_MAX_ITEMS = 200


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    host, tenant, site = params["host"], params["tenant"], params["site"]
    locale = params.get("locale") or "en-US"
    limit = options.limit(DEFAULT_MAX_ITEMS)
    postings: list[dict] = []
    offset = 0
    while True:
        payload = http.post_json(
            SEARCH_API.format(host=host, tenant=tenant, site=site),
            {"searchText": options.query or "", "limit": PAGE_SIZE, "offset": offset, "appliedFacets": {}},
        )
        page = payload.get("jobPostings", [])
        for job in page:
            external_path = job.get("externalPath") or ""
            # externalPath ends in "_<requisition id>"; that suffix is the stable id.
            requisition_id = external_path.rsplit("_", 1)[-1] or external_path
            postings.append(normalize_posting(
                KEY, tenant, requisition_id, job.get("title"),
                f"https://{host}/{locale}/{site}{external_path}",
                location=job.get("locationsText"),
                remote=remote_from_text(job.get("locationsText")),
                posted_at=job.get("postedOn"),
            ))
        offset += PAGE_SIZE
        total_available = int(payload.get("total") or 0)
        if not page or offset >= total_available or offset >= limit:
            return postings


def _params(match) -> dict:
    return {"host": match.group(1), "tenant": match.group(2), "locale": match.group(3), "site": match.group(4)}


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="Workday ({tenant}.wd5.myworkdayjobs.com/{site})", fetch=fetch,
    url_patterns=(
        url_pattern(r"(([a-z0-9-]+)\.wd\d+\.myworkdayjobs\.com)/(?:([a-z]{2}-[A-Za-z]{2})/)?([^/?#]+)", _params),
    ),
    notes="best effort, tenants vary; --query searches server-side",
)
