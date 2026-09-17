"""Turn a URL or source name into a provider, then fetch through it.

Resolution order in `fetch`:

1. Aliases: bare names like "yc" or "hn" map to a canonical URL.
2. URL patterns: each provider's regexes, in registry order.
3. Page sniff (unknown URL only): fetch the page once, then
   a. portfolio platforms by page signature — checked first, because a
      Sequoia or Accel board page is full of Greenhouse and Ashby links;
   b. an embedded ATS board link inside a company's own careers page.

Nothing matched → LookupError. The pipeline skill treats that as "ask the
user to paste the posting" and never skips the form-review step.
"""
from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass

from . import http
from .provider import FetchOptions, Provider
from .registry import PORTFOLIO_PROVIDERS, URL_PROVIDERS

# Aggregators have no company in the URL, so a bare name is the natural way
# to ask for them. "hn" resolves to the latest monthly thread (story id 0 is
# the sentinel the HN provider understands as "look it up").
SOURCE_ALIASES = {
    "yc": "https://www.ycombinator.com/jobs",
    "ycombinator": "https://www.ycombinator.com/jobs",
    "hn": "https://news.ycombinator.com/item?id=0",
    "remotive": "https://remotive.com/",
    "remoteok": "https://remoteok.com/",
    "himalayas": "https://himalayas.app/",
    "jobicy": "https://jobicy.com/",
    "arbeitnow": "https://www.arbeitnow.com/",
    "wwr": "https://weworkremotely.com/",
}

# Links to hosted boards that a company careers page might embed or link.
# Each stops at the org slug so `detect` can re-match the captured URL.
_SLUG = r"[^/\"'\s?#]+"
EMBEDDED_BOARD_PATTERNS = [
    re.compile(rf"https?://jobs\.ashbyhq\.com/{_SLUG}"),
    re.compile(rf"https?://(?:job-boards|boards)\.greenhouse\.io/{_SLUG}"),
    re.compile(rf"https?://boards-api\.greenhouse\.io/v1/boards/{_SLUG}"),
    re.compile(rf"https?://jobs\.lever\.co/{_SLUG}"),
    re.compile(r"https?://[a-z0-9-]+\.wd\d+\.myworkdayjobs\.com/[^\"'\s]+"),
    re.compile(rf"https?://(?:jobs|careers)\.smartrecruiters\.com/{_SLUG}"),
    re.compile(rf"https?://ats\.rippling\.com/{_SLUG}"),
    re.compile(rf"https?://apply\.workable\.com/{_SLUG}"),
    re.compile(r"https?://[a-z0-9-]+\.bamboohr\.com/careers"),
    re.compile(r"https?://[a-z0-9-]+\.jobs\.personio\.(?:de|com)"),
    re.compile(r"https?://[a-z0-9-]+\.recruitee\.com"),
]


@dataclass(frozen=True)
class Detection:
    provider: Provider
    params: dict


def detect(url_or_name: str) -> Detection | None:
    """Match an alias or URL against every URL-pattern provider."""
    url = SOURCE_ALIASES.get(url_or_name.strip().lower(), url_or_name.strip())
    for provider in URL_PROVIDERS:
        params = provider.match_url(url)
        if params is not None:
            return Detection(provider, params)
    return None


def detect_embedded_board(page_html: str) -> str | None:
    """First hosted-ATS board URL found inside a careers page, if any."""
    for pattern in EMBEDDED_BOARD_PATTERNS:
        match = pattern.search(page_html)
        if match:
            return match.group(0)
    return None


def detect_portfolio_platform(page_html: str, page_url: str) -> Detection | None:
    """Recognize a VC portfolio board (Consider, Getro) from its page."""
    for provider in PORTFOLIO_PROVIDERS:
        if provider.match_page(page_html):
            host = urllib.parse.urlsplit(page_url).netloc
            # Hand the already-fetched page along so the provider need not
            # refetch it (Consider also needs the cookies that GET set).
            return Detection(provider, {"host": host, "page_html": page_html})
    return None


def fetch(
    url_or_name: str,
    *,
    query: str | None = None,
    max_items: int | None = None,
    sniff_unknown_pages: bool = True,
) -> tuple[str, list[dict]]:
    """Resolve a source and fetch its postings: (provider key, postings)."""
    detection = detect(url_or_name)
    if detection is None and sniff_unknown_pages and url_or_name.startswith("http"):
        detection = _sniff_page(url_or_name)
    if detection is None:
        raise LookupError(f"no known job board at {url_or_name!r} (see --list)")
    options = FetchOptions(query=query, max_items=max_items)
    return detection.provider.key, detection.provider.fetch(detection.params, options)


def _sniff_page(url: str) -> Detection | None:
    page_html = http.get_text(url)
    platform = detect_portfolio_platform(page_html, url)
    if platform:
        return platform
    embedded_url = detect_embedded_board(page_html)
    return detect(embedded_url) if embedded_url else None


def normalize_title(text: str) -> str:
    """Lowercase alphanumerics only, so spelling variants collide:
    'Full-Stack Engineer', 'Fullstack Engineer', 'Full Stack engineer' → 'fullstackengineer'."""
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def filter_by_title(postings: list[dict], keywords: list[str]) -> list[dict]:
    """Keep postings whose title contains any keyword, after normalizing
    both sides (see normalize_title). No keywords → everything, so an empty
    profile target list is harmless."""
    needles = [normalize_title(keyword) for keyword in keywords if normalize_title(keyword)]
    if not needles:
        return postings
    return [
        posting for posting in postings
        if posting.get("title") and any(needle in normalize_title(posting["title"]) for needle in needles)
    ]
