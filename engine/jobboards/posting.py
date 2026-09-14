"""The normalized posting: what every provider hands back.

A posting is a plain dict so it serializes to JSON for the agent without
ceremony. Every key is always present; a value the source does not expose
is None rather than missing, so consumers never need `.get`.

    source        provider key, e.g. "greenhouse"
    company       company name, or the board slug when that is all we have
    id            the provider's own id, as a string
    title
    location      free text as the source wrote it
    remote        True / False / None (unknown)
    url           the human-facing posting page
    apply_url     where the human submits; defaults to `url`
    salary        free-text compensation summary
    posted_at     date string as the source wrote it (formats vary)
    description   HTML or plain text; list endpoints often omit it
"""
from __future__ import annotations

import html
import re
from typing import Any

POSTING_FIELDS = (
    "source", "company", "id", "title", "location", "remote",
    "url", "apply_url", "salary", "posted_at", "description",
)


def normalize_posting(
    source: str,
    company: str | None,
    posting_id: Any,
    title: str | None,
    url: str | None,
    *,
    location: str | None = None,
    remote: bool | None = None,
    apply_url: str | None = None,
    salary: str | None = None,
    posted_at: str | None = None,
    description: str | None = None,
) -> dict:
    """Build a posting dict, blanking empty strings to None."""
    return {
        "source": source,
        "company": _clean(company),
        "id": str(posting_id) if posting_id is not None else None,
        "title": _clean(title),
        "location": _clean(location),
        "remote": remote,
        "url": url,
        "apply_url": apply_url or url,
        "salary": _clean(salary),
        "posted_at": posted_at or None,
        "description": description or None,
    }


def _clean(text: str | None) -> str | None:
    return (text or "").strip() or None


def remote_from_text(*texts: str | None) -> bool | None:
    """Infer remote-ness from location text. Only ever says True or unknown:
    absence of the word "remote" is not evidence of an on-site role."""
    combined = " ".join(text for text in texts if text).lower()
    if not combined:
        return None
    return True if "remote" in combined else None


def strip_tags(markup: str | None) -> str:
    """Drop HTML tags and unescape entities; good enough for headlines."""
    return re.sub(r"<[^>]+>", " ", html.unescape(markup or "")).strip()


def join_location(*parts: str | None) -> str | None:
    """'Lisbon', '', 'Portugal' -> 'Lisbon, Portugal'."""
    present = [part.strip() for part in parts if part and part.strip()]
    return ", ".join(present) or None


def salary_range(low: Any, high: Any, currency: str | None = None, period: str | None = None) -> str | None:
    """Format a numeric range as free text, or None when the source has none."""
    if not low and not high:
        return None
    text = f"{currency or ''} {low or '?'}–{high or '?'}".strip()
    return f"{text} / {period}" if period else text
