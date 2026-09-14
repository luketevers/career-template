"""Ashby — jobs.ashbyhq.com/{org}.

Primary: the public posting API, which includes descriptions and the
compensation summary. Some orgs disable it (404); then the hosted board's
GraphQL endpoint still lists titles, locations, and compensation.
"""
from __future__ import annotations

import urllib.error

from ... import http
from ...posting import normalize_posting, remote_from_text
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "ashby"
POSTING_API = "https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true"
HOSTED_GRAPHQL = "https://jobs.ashbyhq.com/api/non-user-graphql"
BOARD_QUERY = (
    "query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {"
    " jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) {"
    " jobPostings { id title locationName employmentType compensationTierSummary } } }"
)


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    org = params["org"]
    try:
        return _from_posting_api(org)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
    return _from_hosted_graphql(org)


def _from_posting_api(org: str) -> list[dict]:
    payload = http.get_json(POSTING_API.format(org=org))
    postings = []
    for job in payload.get("jobs", []):
        compensation = (job.get("compensation") or {}).get("compensationTierSummary")
        postings.append(normalize_posting(
            KEY, org, job.get("id"), job.get("title"), job.get("jobUrl"),
            location=job.get("location"),
            remote=job.get("isRemote"),
            apply_url=job.get("applyUrl"),
            salary=compensation,
            posted_at=job.get("publishedAt"),
            description=job.get("descriptionHtml"),
        ))
    return postings


def _from_hosted_graphql(org: str) -> list[dict]:
    payload = http.post_json(HOSTED_GRAPHQL, {
        "operationName": "ApiJobBoardWithTeams",
        "variables": {"organizationHostedJobsPageName": org},
        "query": BOARD_QUERY,
    })
    board = (payload.get("data") or {}).get("jobBoard") or {}
    postings = []
    for job in board.get("jobPostings", []):
        posting_url = f"https://jobs.ashbyhq.com/{org}/{job.get('id')}"
        postings.append(normalize_posting(
            KEY, org, job.get("id"), job.get("title"), posting_url,
            location=job.get("locationName"),
            remote=remote_from_text(job.get("locationName")),
            apply_url=f"{posting_url}/application",
            salary=job.get("compensationTierSummary"),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="Ashby (jobs.ashbyhq.com/{org})", fetch=fetch,
    url_patterns=(url_pattern(r"jobs\.ashbyhq\.com/([^/?#]+)", lambda m: {"org": m.group(1)}),),
    notes="posting API with hosted-board GraphQL fallback; form fields via ApiJobPosting GraphQL",
)
