"""Personio — {company}.jobs.personio.de (or .com). Public XML feed."""
from __future__ import annotations

import xml.etree.ElementTree as ET

from ... import http
from ...posting import normalize_posting, remote_from_text
from ...provider import KIND_ATS, FetchOptions, Provider, url_pattern

KEY = "personio"
FEED_URL = "https://{host}/xml"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    host = params["host"]
    feed = ET.fromstring(http.get_text(FEED_URL.format(host=host)))
    postings = []
    for position in feed.findall(".//position"):
        def text_of(tag: str) -> str | None:
            return (position.findtext(tag) or "").strip() or None

        description = " ".join(
            (block.findtext("value") or "") for block in position.findall(".//jobDescription")
        ) or None
        postings.append(normalize_posting(
            KEY, text_of("subcompany") or host.split(".")[0], text_of("id"), text_of("name"),
            f"https://{host}/job/{text_of('id')}",
            location=text_of("office"),
            remote=remote_from_text(text_of("office")),
            posted_at=text_of("createdAt"),
            description=description,
        ))
    return postings


PROVIDER = Provider(
    key=KEY, kind=KIND_ATS, label="Personio ({company}.jobs.personio.de)", fetch=fetch,
    url_patterns=(url_pattern(r"([a-z0-9-]+\.jobs\.personio\.(?:de|com))", lambda m: {"host": m.group(1)}),),
)
