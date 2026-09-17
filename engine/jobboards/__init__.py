"""jobboards — fetch job postings from any supported board, one shape out.

The application pipeline's discover step (FR-003) calls this instead of
reciting ATS endpoints. Give it a board URL or an aggregator name and get
back a list of normalized postings (see `posting.py` for the shape).

Package layout:

    http.py        the single network call; tests stub `http.request`
    posting.py     the normalized posting dict and small text helpers
    provider.py    the Provider contract every source implements
    providers/     one module per source, grouped by kind:
                     ats/          company boards (Ashby, Greenhouse, ...)
                     aggregators/  market boards (Y Combinator, HN, ...)
                     portfolio/    VC portfolio boards (Consider, Getro)
    registry.py    collects every provider into ordered lists
    detect.py      URL → provider; careers-page sniffing; title filter
    cli.py         `python3 engine/boards.py` argument handling

Public API (re-exported here):

    fetch(url_or_name, query=None, max_items=None) -> (provider_key, postings)
    detect(url_or_name) -> Detection | None
    filter_by_title(postings, keywords) -> postings   (spelling-insensitive)
"""
from .detect import (  # noqa: F401
    SOURCE_ALIASES,
    Detection,
    detect,
    detect_embedded_board,
    detect_portfolio_platform,
    fetch,
    filter_by_title,
    normalize_title,
)
from .posting import normalize_posting  # noqa: F401
from .provider import FetchOptions, Provider  # noqa: F401
from .registry import PORTFOLIO_PROVIDERS, PROVIDERS, URL_PROVIDERS  # noqa: F401
