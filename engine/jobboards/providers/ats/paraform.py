"""Paraform — paraform.com/share/{company}/{role}.

Paraform is a recruiter marketplace: agencies send candidates a share link
for one role, and the candidate applies through the recruiter rather than a
public form. There is no company-level listing (paraform.com/share/{company}
is a 404), so one URL fetches exactly one posting.

The share page is a Next.js app that embeds the whole role record in its
`__NEXT_DATA__` script, so the page is fetched once and parsed without
touching any private API. The role's application questions ride along in
the description so the pipeline's form-review step sees them.
"""
from __future__ import annotations

import html
import json
import re

from ... import http
from ...posting import normalize_posting, salary_range, strip_tags
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "paraform"
SHARE_URL = "https://www.paraform.com/share/{company}/{role}"
NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)

# workplaceType as Paraform spells it → the posting's remote flag.
WORKPLACE_REMOTE = {"remote": True, "hybrid": False, "on-site": False, "onsite": False}


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    share_url = SHARE_URL.format(company=params["company"], role=params["role"])
    page_html = http.get_text(share_url)
    role = parse_share_page(page_html)
    if role is None:
        return []
    return [role_to_posting(role, share_url, params["company"])]


def parse_share_page(page_html: str) -> dict | None:
    """The role record embedded in a share page, or None when the page is
    not a role (a 404 page has no initialRoleData)."""
    match = NEXT_DATA.search(page_html)
    if not match:
        return None
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    page_props = ((payload.get("props") or {}).get("pageProps") or {})
    return page_props.get("initialRoleData") or None


def role_to_posting(role: dict, share_url: str, company_slug: str) -> dict:
    company = role.get("company") or {}
    workplace = (role.get("workplaceType") or "").strip()
    location = ", ".join(place for place in (role.get("locations") or []) if place) or None
    if workplace:
        location = f"{location} ({workplace})" if location else workplace
    return normalize_posting(
        KEY, company.get("name") or company_slug, role.get("id"), role.get("name"), share_url,
        location=location,
        remote=WORKPLACE_REMOTE.get(workplace.lower()),
        salary=_salary(role),
        posted_at=role.get("createdAt"),
        description=_description(role),
    )


def _salary(role: dict) -> str | None:
    if role.get("hide_salary"):
        return None
    summary = strip_tags(role.get("candidate_salary_info"))
    if summary:
        return re.sub(r"\s+", " ", summary)
    return salary_range(role.get("salaryLowerBound"), role.get("salaryUpperBound"), role.get("currencyType"))


def _description(role: dict) -> str | None:
    """The posting body plus the facts Paraform keeps in separate fields:
    workplace terms, experience band, tech stack, and the application
    questions the recruiter will relay."""
    parts = [role.get("description") or ""]
    if role.get("workPlaceText"):
        parts.append(f"<p><strong>Workplace:</strong> {html.escape(role['workPlaceText'])}</p>")
    years = _years(role)
    if years:
        parts.append(f"<p><strong>Experience:</strong> {html.escape(years)}</p>")
    stack = [tool for tool in (role.get("tech_stack") or []) if tool]
    if stack:
        parts.append(f"<p><strong>Tech stack:</strong> {html.escape(', '.join(stack))}</p>")
    if role.get("visa_text"):
        parts.append(f"<p><strong>Visa:</strong> {html.escape(role['visa_text'])}</p>")
    questions = [
        strip_tags(question.get("question"))
        for question in sorted(role.get("role_question") or [], key=lambda q: q.get("order") or 0)
        if question.get("active", True) and not question.get("recruiter_only")
    ]
    if questions:
        items = "".join(f"<li>{html.escape(question)}</li>" for question in questions if question)
        parts.append(f"<p><strong>Application questions:</strong></p><ol>{items}</ol>")
    body = "".join(part for part in parts if part)
    return body or None


def _years(role: dict) -> str | None:
    low, high = role.get("years_experience_min"), role.get("years_experience_max")
    if not low and not high:
        return None
    span = f"{low or '?'}–{high}" if high else f"{low}+"
    detail = (role.get("experience_info") or "").strip()
    return f"{span} years {detail}".strip()


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="Paraform (paraform.com/share/{company}/{role})", fetch=fetch,
    url_patterns=(
        url_pattern(
            r"(?:www\.)?paraform\.com/share/([^/?#]+)/([^/?#]+)",
            lambda m: {"company": m.group(1), "role": m.group(2)},
        ),
    ),
    notes="recruiter share link = one role, no company listing; apply through the recruiter; questions appended to description",
)
