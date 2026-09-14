"""Lever — jobs.lever.co/{org}. Public postings API, JSON mode."""
from __future__ import annotations

from ... import http
from ...posting import normalize_posting, salary_range
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "lever"
POSTINGS_API = "https://api.lever.co/v0/postings/{org}?mode=json"

# Lever's workplaceType is explicit, so unlike most sources we can say False.
REMOTE_BY_WORKPLACE_TYPE = {"remote": True, "onsite": False, "hybrid": False}


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    org = params["org"]
    postings = []
    for job in http.get_json(POSTINGS_API.format(org=org)):
        categories = job.get("categories") or {}
        salary = job.get("salaryRange")
        salary_text = None
        if isinstance(salary, dict):
            salary_text = salary_range(salary.get("min"), salary.get("max"), salary.get("currency"), salary.get("interval"))
        postings.append(normalize_posting(
            KEY, org, job.get("id"), job.get("text"), job.get("hostedUrl"),
            location=categories.get("location"),
            remote=REMOTE_BY_WORKPLACE_TYPE.get(job.get("workplaceType")),
            apply_url=job.get("applyUrl"),
            salary=salary_text,
            posted_at=str(job.get("createdAt") or ""),
            description=job.get("descriptionPlain"),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="Lever (jobs.lever.co/{org})", fetch=fetch,
    url_patterns=(url_pattern(r"jobs\.lever\.co/([^/?#]+)", lambda m: {"org": m.group(1)}),),
)
