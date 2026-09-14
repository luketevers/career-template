"""RemoteOK — remoteok.com/api. A bare JSON list whose first element is a
legal notice (link back when displaying), not a job."""
from __future__ import annotations

from ... import http
from ...posting import normalize_posting
from ...provider import KIND_AGGREGATOR, FetchOptions, Provider, url_pattern

KEY = "remoteok"
JOBS_API = "https://remoteok.com/api"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    postings = []
    for entry in http.get_json(JOBS_API):
        if "position" not in entry:
            continue  # the legal-notice preamble element
        salary_low, salary_high = entry.get("salary_min"), entry.get("salary_max")
        has_salary = salary_low and salary_high and str(salary_low) != "0"
        postings.append(normalize_posting(
            KEY, entry.get("company"), entry.get("id"), entry.get("position"), entry.get("url"),
            location=entry.get("location"),
            remote=True,
            apply_url=entry.get("apply_url"),
            salary=f"${salary_low}–${salary_high}" if has_salary else None,
            posted_at=entry.get("date"),
            description=entry.get("description"),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_AGGREGATOR, label="RemoteOK (remoteok.com)", fetch=fetch,
    url_patterns=(url_pattern(r"(?:www\.)?remoteok\.(?:com|io)", lambda m: {}),),
    notes="alias remoteok; their terms ask for a link back when displaying",
)
