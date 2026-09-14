"""The one place jobboards touches the network.

Every provider goes through `request`, so a test can replace that single
function with a fixture server and never open a socket. Keep it that way:
no provider should import urllib directly.

A process-wide cookie jar is deliberate. Consider-hosted portfolio boards
tie their CSRF token to a session cookie set by the first page load, so the
follow-up POST must carry the same cookies.
"""
from __future__ import annotations

import json
import urllib.request
from typing import Any

# Generic on purpose: the personal-data audit forbids maintainer identifiers,
# and a job board has no reason to know who forked the template.
USER_AGENT = "career-template/0.1 (job-board fetcher; open source, no tracking)"
TIMEOUT_SECONDS = 25

_cookie_aware_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())


def request(url: str, body: bytes | None = None, headers: dict | None = None) -> bytes:
    """GET (or POST when `body` is given) and return the raw response bytes.

    Tests monkeypatch this function; everything else in the package calls it
    indirectly through the helpers below.
    """
    merged_headers = {"User-Agent": USER_AGENT, **(headers or {})}
    http_request = urllib.request.Request(url, data=body, headers=merged_headers)
    with _cookie_aware_opener.open(http_request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def get_json(url: str) -> Any:
    return json.loads(request(url))


def post_json(url: str, payload: dict, headers: dict | None = None) -> Any:
    body = json.dumps(payload).encode()
    json_headers = {"Content-Type": "application/json", **(headers or {})}
    return json.loads(request(url, body=body, headers=json_headers))


def get_text(url: str) -> str:
    return request(url).decode("utf-8", errors="replace")
