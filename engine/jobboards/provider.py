"""The contract every job-board source implements.

A provider module (see `providers/`) exposes one `PROVIDER` constant built
from this dataclass. The registry collects them; `detect` matches URLs
against their patterns; the CLI prints them for `--list`.

Two ways a provider gets recognized:

- URL patterns (`url_patterns`): the board lives on the provider's own
  domain, so a regex over the URL both identifies the provider and pulls
  out the org slug. This covers every ATS and aggregator.
- Page signature (`page_signature`): VC portfolio boards live on custom
  domains (jobs.sequoiacap.com), so the page HTML is fetched once and
  matched against a regex that only that platform's pages contain.

Fetch functions take the params the matcher extracted plus the caller's
options and return normalized postings (`posting.normalize_posting`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

# Extracts provider params (org slug, host, ...) from a URL regex match.
ParamBuilder = Callable[[re.Match], dict]
# The fetch entry point: (params, options) -> list of posting dicts.
FetchFunction = Callable[[dict, "FetchOptions"], list[dict]]

KIND_ATS = "ats"                # one URL = one company's open roles
KIND_AGGREGATOR = "aggregator"  # many companies; caller filters by title
KIND_PORTFOLIO = "portfolio"    # a VC's portfolio companies, custom domain


@dataclass(frozen=True)
class FetchOptions:
    """What the caller can ask for beyond 'everything on the board'."""
    query: str | None = None       # search text, where the source supports it
    max_items: int | None = None   # stop paginating past this many postings

    def limit(self, default: int) -> int:
        return self.max_items or default


@dataclass(frozen=True)
class Provider:
    key: str                          # short id used in --list and posting["source"]
    kind: str                         # KIND_ATS / KIND_AGGREGATOR / KIND_PORTFOLIO
    label: str                        # human name for docs and --list
    fetch: FetchFunction
    url_patterns: tuple[tuple[re.Pattern, ParamBuilder], ...] = field(default_factory=tuple)
    page_signature: re.Pattern | None = None
    notes: str = ""                   # one line for --list: quirks, flags, caveats

    def match_url(self, url: str) -> dict | None:
        """Params for this provider if `url` belongs to it, else None."""
        for pattern, build_params in self.url_patterns:
            match = pattern.match(url)
            if match:
                return build_params(match)
        return None

    def match_page(self, page_html: str) -> bool:
        return bool(self.page_signature and self.page_signature.search(page_html))


HTTP_PREFIX = r"https?://"


def url_pattern(regex: str, build_params: ParamBuilder) -> tuple[re.Pattern, ParamBuilder]:
    """Small helper so provider modules read as a table of patterns."""
    return re.compile(HTTP_PREFIX + regex), build_params
