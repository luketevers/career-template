"""Every provider, in matching order.

Order matters in two places: `detect` tries URL patterns top to bottom, and
`--list` prints in this order. Keep ATS boards first, aggregators second,
portfolio platforms last.

Adding a source = one module under `providers/<kind>/` exposing `PROVIDER`,
one import line here, and one fixture-backed test under `tests/boards/`.
The test suite fails if a registered provider has no test.
"""
from __future__ import annotations

from .provider import KIND_PORTFOLIO, Provider
from .providers.aggregators import arbeitnow, himalayas, hn, jobicy, remoteok, remotive, wwr, yc
from .providers.ats import (
    ashby,
    bamboohr,
    greenhouse,
    lever,
    personio,
    recruitee,
    rippling,
    smartrecruiters,
    workable,
    workday,
)
from .providers.portfolio import consider, getro

PROVIDERS: tuple[Provider, ...] = (
    # ATS boards — company-shaped
    ashby.PROVIDER,
    greenhouse.PROVIDER,
    lever.PROVIDER,
    workday.PROVIDER,
    smartrecruiters.PROVIDER,
    rippling.PROVIDER,
    workable.PROVIDER,
    bamboohr.PROVIDER,
    personio.PROVIDER,
    recruitee.PROVIDER,
    # Aggregators — market-shaped
    yc.PROVIDER,
    hn.PROVIDER,
    remotive.PROVIDER,
    remoteok.PROVIDER,
    himalayas.PROVIDER,
    jobicy.PROVIDER,
    arbeitnow.PROVIDER,
    wwr.PROVIDER,
    # VC portfolio platforms — recognized by page signature
    consider.PROVIDER,
    getro.PROVIDER,
)

URL_PROVIDERS = tuple(p for p in PROVIDERS if p.url_patterns)
PORTFOLIO_PROVIDERS = tuple(p for p in PROVIDERS if p.kind == KIND_PORTFOLIO)
PROVIDERS_BY_KEY = {p.key: p for p in PROVIDERS}
