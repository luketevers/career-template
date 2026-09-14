"""Recruitee — {company}.recruitee.com. Public careers-site offers API."""
from __future__ import annotations

from ... import http
from ...posting import normalize_posting, remote_from_text
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "recruitee"
OFFERS_API = "https://{company}.recruitee.com/api/offers/"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    company = params["company"]
    payload = http.get_json(OFFERS_API.format(company=company))
    postings = []
    for offer in payload.get("offers", []):
        location = offer.get("location")
        remote_flag = offer.get("remote")
        postings.append(normalize_posting(
            KEY, company, offer.get("id"), offer.get("title"), offer.get("careers_url"),
            location=location,
            remote=remote_flag if isinstance(remote_flag, bool) else remote_from_text(location),
            apply_url=offer.get("careers_apply_url"),
            posted_at=offer.get("published_at"),
            description=offer.get("description"),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="Recruitee ({company}.recruitee.com)", fetch=fetch,
    url_patterns=(url_pattern(r"([a-z0-9-]+)\.recruitee\.com", lambda m: {"company": m.group(1)}),),
)
