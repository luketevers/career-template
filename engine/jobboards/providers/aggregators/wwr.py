"""We Work Remotely — weworkremotely.com/categories/{category}.rss.

Public RSS per category; programming is the default. Item titles are
"Company: Role", which we split back apart.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from ... import http
from ...posting import normalize_posting
from ...provider import KIND_AGGREGATOR, FetchOptions, Provider, url_pattern

KEY = "wwr"
FEED_URL = "https://weworkremotely.com/categories/{category}.rss"
DEFAULT_CATEGORY = "remote-programming-jobs"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    category = params.get("category") or DEFAULT_CATEGORY
    feed = ET.fromstring(http.get_text(FEED_URL.format(category=category)))
    postings = []
    for item in feed.findall(".//item"):
        raw_title = (item.findtext("title") or "").strip()
        company, separator, role_title = raw_title.partition(": ")
        if not separator:
            company, role_title = None, raw_title
        postings.append(normalize_posting(
            KEY, company, item.findtext("guid") or item.findtext("link"), role_title, item.findtext("link"),
            location=(item.findtext("region") or "").strip() or None,
            remote=True,
            posted_at=item.findtext("pubDate"),
            description=item.findtext("description"),
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_AGGREGATOR, label="We Work Remotely (weworkremotely.com/categories/{category})", fetch=fetch,
    url_patterns=(url_pattern(r"(?:www\.)?weworkremotely\.com(?:/categories/([^/?#.]+))?", lambda m: {"category": m.group(1)}),),
    notes="alias wwr = programming category; pass a category URL for others",
)
