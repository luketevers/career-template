"""SmartRecruiters — jobs.smartrecruiters.com/{Company}. Public postings API."""
from __future__ import annotations

from ... import http
from ...posting import join_location, normalize_posting
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "smartrecruiters"
POSTINGS_API = "https://api.smartrecruiters.com/v1/companies/{company}/postings?limit=100"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    company_slug = params["company"]
    payload = http.get_json(POSTINGS_API.format(company=company_slug))
    postings = []
    for job in payload.get("content", []):
        location = job.get("location") or {}
        company_name = (job.get("company") or {}).get("name") or company_slug
        postings.append(normalize_posting(
            KEY, company_name, job.get("id"), job.get("name"),
            f"https://jobs.smartrecruiters.com/{company_slug}/{job.get('id')}",
            location=join_location(location.get("city"), location.get("region"), location.get("country")),
            remote=location.get("remote"),
            posted_at=job.get("releasedDate"),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="SmartRecruiters (jobs.smartrecruiters.com/{Company})", fetch=fetch,
    url_patterns=(url_pattern(r"(?:jobs|careers)\.smartrecruiters\.com/([^/?#]+)", lambda m: {"company": m.group(1)}),),
)
