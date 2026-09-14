"""VC portfolio platforms: recognized by page signature, not URL."""
import json

import pytest

import jobboards
from helpers import FIXTURES, assert_normalized


def test_fetch_consider(network):
    fake = network({"jobs.sequoiacap.com/jobs": "consider_page.html",
                    "jobs.sequoiacap.com/api-boards/search-jobs": "consider.json"})
    key, postings = jobboards.fetch("https://jobs.sequoiacap.com/jobs", max_items=2)
    assert key == "consider"
    assert_normalized(postings, "consider")
    # The POST carried the page's CSRF token and the board id the page embedded.
    search_url, search_body = fake.calls[1]
    assert search_url.endswith("/api-boards/search-jobs")
    assert json.loads(search_body)["board"]["id"] == "sequoia-capital"
    assert postings[0]["url"].startswith("https://jobs.ashbyhq.com/")  # the portfolio company's own ATS
    assert postings[0]["salary"]
    assert postings[0]["remote"] is False


def test_fetch_consider_paginates_by_cursor(network):
    fake = network({"jobs.sequoiacap.com/jobs": "consider_page.html", "search-jobs": "consider.json"})
    # The fixture reports total=10033 and hands back a cursor, so a second page is requested.
    _, postings = jobboards.fetch("https://jobs.sequoiacap.com/jobs", max_items=4)
    assert len(postings) == 4
    assert json.loads(fake.calls[2][1])["meta"]["sequence"] == "CURSOR2"


def test_fetch_consider_login_gated_raises(network):
    network({"jobs.example.com/jobs": b'<html>/api-boards/ <a href="/talent-network">Join</a></html>'})
    with pytest.raises(ValueError):
        jobboards.fetch("https://jobs.example.com/jobs")


def test_fetch_getro(network):
    fake = network({"jobs.accel.com/jobs": "getro_page.html"})
    key, postings = jobboards.fetch("https://jobs.accel.com/jobs", max_items=2)
    assert key == "getro"
    assert_normalized(postings, "getro")
    assert postings[0]["company"] == "Xero"
    assert postings[0]["remote"] is False  # workMode on_site
    assert len(fake.calls) == 1  # page 1 reused from the sniff fetch


def test_fetch_getro_query_hits_server_filter(network):
    fake = network({"jobs.accel.com/jobs": "getro_page.html"})
    jobboards.fetch("https://jobs.accel.com/jobs", query="staff engineer", max_items=2)
    assert any("q=staff+engineer" in url for url, _ in fake.calls)


def test_platform_detected_before_embedded_ats(network):
    """A Getro page is full of Greenhouse links; it must still be read as Getro."""
    page = (FIXTURES / "getro_page.html").read_text() + '<a href="https://boards.greenhouse.io/acme">x</a>'
    network({"jobs.accel.com/jobs": page.encode()})
    key, _ = jobboards.fetch("https://jobs.accel.com/jobs", max_items=2)
    assert key == "getro"
