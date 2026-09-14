"""One fixture-backed test per aggregator provider."""
import json

import pytest

import jobboards
from jobboards.providers.aggregators import hn
from jobboards.provider import FetchOptions
from helpers import FIXTURES, assert_normalized


def test_fetch_yc(network):
    network({"ycombinator.com/jobs/role/software-engineer": "yc.html"})
    _, postings = jobboards.fetch("https://www.ycombinator.com/jobs/role/software-engineer")
    assert_normalized(postings, "yc")
    assert postings[0]["url"].startswith("https://www.ycombinator.com/companies/")
    assert postings[0]["company"]  # slug pulled from the posting path
    assert "account.ycombinator.com" in postings[0]["apply_url"]  # the human applies via their WaaS account
    assert postings[0]["salary"]


def test_fetch_yc_page_without_embedded_json_raises(network):
    network({"ycombinator.com/jobs": b"<html><body>redesigned</body></html>"})
    with pytest.raises(ValueError):
        jobboards.fetch("yc")


def test_fetch_hn(network):
    network({"tags=story,author_whoishiring": "hn_story.json", "tags=comment,story_49522897": "hn_comments.json"})
    _, postings = jobboards.fetch("hn")
    # Only top-level comments (parent is the story) count as listings.
    fixture_comments = json.loads((FIXTURES / "hn_comments.json").read_text())["hits"]
    top_level = [comment for comment in fixture_comments if str(comment["parent_id"]) == "49522897"]
    assert_normalized(postings, "hn", expected_count=len(top_level))
    for posting in postings:
        assert posting["url"].startswith("https://news.ycombinator.com/item?id=")
        assert "<p>" not in (posting["company"] or "") and "<p>" not in posting["title"]


def test_fetch_hn_headline_split(network):
    """'Company | Role | Location' first paragraph → company + title."""
    comment = {"objectID": "1", "parent_id": "9", "created_at": "x",
               "comment_text": "Acme Corp | Senior Platform Engineer | Remote (US)<p>We build things.<p>Apply: acme.example"}
    network({"tags=comment,story_9": json.dumps({"nbPages": 1, "hits": [comment]}).encode()})
    postings = hn.fetch({"story_id": "9"}, FetchOptions())
    assert postings[0]["company"] == "Acme Corp"
    assert postings[0]["title"] == "Senior Platform Engineer | Remote (US)"
    assert postings[0]["remote"] is True


def test_fetch_remotive(network):
    network({"remotive.com/api/remote-jobs": "remotive.json"})
    _, postings = jobboards.fetch("remotive")
    assert_normalized(postings, "remotive")
    assert postings[0]["remote"] is True and postings[0]["salary"]


def test_fetch_remoteok(network):
    network({"remoteok.com/api": "remoteok.json"})
    _, postings = jobboards.fetch("remoteok")
    assert_normalized(postings, "remoteok")  # legal-notice preamble element skipped


def test_fetch_himalayas(network):
    network({"himalayas.app/jobs/api": "himalayas.json"})
    _, postings = jobboards.fetch("himalayas")
    assert_normalized(postings, "himalayas")
    assert postings[0]["salary"]


def test_fetch_jobicy(network):
    network({"jobicy.com/api/v2/remote-jobs": "jobicy.json"})
    _, postings = jobboards.fetch("jobicy")
    assert_normalized(postings, "jobicy")


def test_fetch_arbeitnow(network):
    network({"arbeitnow.com/api/job-board-api": "arbeitnow.json"})
    _, postings = jobboards.fetch("arbeitnow")
    assert_normalized(postings, "arbeitnow")
    assert postings[0]["remote"] is False


def test_fetch_wwr(network):
    network({"weworkremotely.com/categories/remote-programming-jobs.rss": "wwr.xml"})
    _, postings = jobboards.fetch("wwr")
    assert_normalized(postings, "wwr")
    assert postings[0]["company"] and ": " not in postings[0]["title"]
