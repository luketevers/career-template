"""Ask HN: Who is hiring — the monthly thread, via the HN Algolia API.

Each top-level comment is one employer's listing, conventionally headed
"Company | Role | Location | ...". Replies are discussion, not listings,
so only comments whose parent is the story itself count.

Story id 0 (what the `hn` alias resolves to) means "find the latest
thread"; a news.ycombinator.com/item?id=N URL pins a specific month.
"""
from __future__ import annotations

import re
import urllib.parse

from ... import http
from ...posting import normalize_posting, remote_from_text, strip_tags
from ...provider import KIND_AGGREGATOR, FetchOptions, Provider, url_pattern

KEY = "hn"
SEARCH_API = "https://hn.algolia.com/api/v1/search_by_date"
LATEST_THREAD_URL = (
    f"{SEARCH_API}?query=" + urllib.parse.quote('"Ask HN: Who is hiring"')
    + "&tags=story,author_whoishiring&hitsPerPage=1"
)
COMMENTS_URL = SEARCH_API + "?tags=comment,story_{story_id}&hitsPerPage=1000&page={page}"
PARAGRAPH_BREAK = re.compile(r"<p>|<br\s*/?>|\n")
LATEST_THREAD_SENTINEL = "0"


def fetch(params: dict, options: FetchOptions) -> list[dict]:
    story_id = params.get("story_id")
    if not story_id or story_id == LATEST_THREAD_SENTINEL:
        story_id = _latest_thread_id()
        if not story_id:
            return []
    postings: list[dict] = []
    page = 0
    while True:
        payload = http.get_json(COMMENTS_URL.format(story_id=story_id, page=page))
        for comment in payload.get("hits", []):
            if str(comment.get("parent_id")) != str(story_id):
                continue  # a reply, not a listing
            postings.append(_to_posting(comment))
        page += 1
        if page >= int(payload.get("nbPages") or 1):
            return postings


def _latest_thread_id() -> str | None:
    hits = http.get_json(LATEST_THREAD_URL).get("hits", [])
    return hits[0]["objectID"] if hits else None


def _to_posting(comment: dict) -> dict:
    raw_text = comment.get("comment_text") or ""
    first_paragraph = PARAGRAPH_BREAK.split(raw_text, maxsplit=1)[0]
    headline = strip_tags(first_paragraph)[:200]
    segments = [segment.strip() for segment in headline.split("|")]
    company = segments[0] if segments else None
    title = " | ".join(segments[1:]) if len(segments) > 1 else headline
    comment_id = comment.get("objectID")
    return normalize_posting(
        KEY, company, comment_id, title, f"https://news.ycombinator.com/item?id={comment_id}",
        remote=remote_from_text(headline),
        posted_at=comment.get("created_at"),
        description=raw_text,
    )


PROVIDER = Provider(
    key=KEY, kind=KIND_AGGREGATOR, label="Ask HN: Who is hiring (news.ycombinator.com/item?id=N)", fetch=fetch,
    url_patterns=(url_pattern(r"news\.ycombinator\.com/item\?id=(\d+)", lambda m: {"story_id": m.group(1)}),),
    notes="alias hn = latest monthly thread; free-text posts, read description",
)
