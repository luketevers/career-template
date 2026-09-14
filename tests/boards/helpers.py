"""Shared helpers for the jobboards tests.

`fake_network` replaces `jobboards.http.request` with a lookup table: the
first mapping key found inside the requested URL decides the response.
Values may be a fixture filename (under tests/fixtures/boards), raw bytes,
or an exception to raise. Every call is recorded on `.calls` as
(url, body) so tests can assert on what was sent.
"""
from __future__ import annotations

import pathlib
import urllib.error

from jobboards.posting import POSTING_FIELDS

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "boards"


def fake_network(responses: dict):
    calls: list[tuple[str, bytes | None]] = []

    def request(url: str, body: bytes | None = None, headers: dict | None = None) -> bytes:
        calls.append((url, body))
        for url_fragment, response in responses.items():
            if url_fragment in url:
                if isinstance(response, Exception):
                    raise response
                if isinstance(response, bytes):
                    return response
                return (FIXTURES / response).read_bytes()
        raise AssertionError(f"unexpected URL in test: {url}")

    request.calls = calls
    return request


def http_404(url: str = "https://example.test") -> urllib.error.HTTPError:
    return urllib.error.HTTPError(url, 404, "Not Found", {}, None)


def assert_normalized(postings: list[dict], source: str, expected_count: int = 2) -> None:
    """Every posting has every field, the right source, a title, and URLs."""
    assert len(postings) == expected_count
    for posting in postings:
        assert set(posting) == set(POSTING_FIELDS), posting
        assert posting["source"] == source
        assert posting["title"], posting
        assert posting["url"] and posting["url"].startswith("http"), posting
        assert posting["apply_url"], posting
        assert posting["remote"] in (True, False, None)
