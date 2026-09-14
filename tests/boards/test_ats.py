"""One fixture-backed test per ATS provider. Fixtures are trimmed live
captures except workable, bamboohr, and recruitee (documented shapes)."""
import json

import jobboards
from helpers import assert_normalized, http_404


def test_fetch_ashby(network):
    network({"api.ashbyhq.com/posting-api/job-board/linear": "ashby.json"})
    key, postings = jobboards.fetch("https://jobs.ashbyhq.com/linear")
    assert key == "ashby"
    assert_normalized(postings, "ashby")
    assert postings[0]["company"] == "linear"
    assert postings[0]["url"].startswith("https://jobs.ashbyhq.com/linear/")
    assert postings[0]["apply_url"].endswith("/application")
    assert postings[0]["remote"] is True


def test_fetch_ashby_falls_back_to_graphql_on_404(network):
    fake = network({"api.ashbyhq.com/posting-api": http_404(), "jobs.ashbyhq.com/api/non-user-graphql": "ashby_gql.json"})
    _, postings = jobboards.fetch("https://jobs.ashbyhq.com/linear")
    assert_normalized(postings, "ashby")
    assert fake.calls[1][1] is not None  # the GraphQL POST carried a body
    assert postings[0]["url"] == f"https://jobs.ashbyhq.com/linear/{postings[0]['id']}"


def test_fetch_greenhouse(network):
    network({"boards-api.greenhouse.io/v1/boards/stripe/jobs": "greenhouse.json"})
    _, postings = jobboards.fetch("https://boards.greenhouse.io/stripe")
    assert_normalized(postings, "greenhouse")
    assert postings[0]["company"] == "Stripe"
    assert postings[0]["location"]


def test_fetch_lever(network):
    network({"api.lever.co/v0/postings/spotify": "lever.json"})
    _, postings = jobboards.fetch("https://jobs.lever.co/spotify")
    assert_normalized(postings, "lever")
    assert postings[0]["apply_url"].endswith("/apply")
    assert postings[0]["remote"] is False  # workplaceType hybrid


def test_fetch_workday(network):
    fake = network({"/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs": "workday.json"})
    _, postings = jobboards.fetch("https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite")
    assert_normalized(postings, "workday")
    assert postings[0]["url"].startswith("https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/")
    assert json.loads(fake.calls[0][1])["limit"] == 20
    assert len(fake.calls) == 1  # fixture total=2 → no second page


def test_fetch_smartrecruiters(network):
    network({"api.smartrecruiters.com/v1/companies/smartrecruiters/postings": "smartrecruiters.json"})
    _, postings = jobboards.fetch("https://jobs.smartrecruiters.com/smartrecruiters")
    assert_normalized(postings, "smartrecruiters", expected_count=1)
    assert postings[0]["remote"] is True
    assert postings[0]["company"] == "SmartRecruiters Inc"


def test_fetch_rippling(network):
    network({"api.rippling.com/platform/api/ats/v1/board/rippling/jobs": "rippling.json"})
    _, postings = jobboards.fetch("https://ats.rippling.com/rippling/jobs")
    assert_normalized(postings, "rippling")
    assert postings[0]["url"].startswith("https://ats.rippling.com/rippling/jobs/")


def test_fetch_workable(network):
    network({"apply.workable.com/api/v3/accounts/acme/jobs": "workable.json"})
    _, postings = jobboards.fetch("https://apply.workable.com/acme/")
    assert_normalized(postings, "workable")
    assert postings[0]["url"] == "https://apply.workable.com/acme/j/AB12CD/"
    assert postings[0]["location"] == "Lisbon, Portugal"
    assert postings[0]["remote"] is True and postings[1]["remote"] is False


def test_fetch_bamboohr(network):
    network({"acme.bamboohr.com/careers/list": "bamboohr.json"})
    _, postings = jobboards.fetch("https://acme.bamboohr.com/careers")
    assert_normalized(postings, "bamboohr")
    assert postings[0]["url"] == "https://acme.bamboohr.com/careers/101"
    assert postings[0]["location"] == "Denver, Colorado"


def test_fetch_personio(network):
    network({"personio.jobs.personio.de/xml": "personio.xml"})
    _, postings = jobboards.fetch("https://personio.jobs.personio.de/")
    assert_normalized(postings, "personio", expected_count=1)
    assert postings[0]["url"] == "https://personio.jobs.personio.de/job/1834171"
    assert postings[0]["location"] == "Munich"


def test_fetch_recruitee(network):
    network({"example.recruitee.com/api/offers/": "recruitee.json"})
    _, postings = jobboards.fetch("https://example.recruitee.com/")
    assert_normalized(postings, "recruitee")
    assert postings[0]["apply_url"].endswith("/c/new")
    assert postings[1]["remote"] is False
