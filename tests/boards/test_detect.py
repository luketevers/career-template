"""URL and alias detection, careers-page sniffing, and the title filter."""
import pytest

import jobboards


@pytest.mark.parametrize("url,key,params", [
    ("https://jobs.ashbyhq.com/linear", "ashby", {"org": "linear"}),
    ("https://jobs.ashbyhq.com/linear/1234?x=1", "ashby", {"org": "linear"}),
    ("https://boards.greenhouse.io/stripe", "greenhouse", {"org": "stripe"}),
    ("https://job-boards.greenhouse.io/stripe/jobs/1", "greenhouse", {"org": "stripe"}),
    ("https://jobs.lever.co/spotify", "lever", {"org": "spotify"}),
    ("https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite", "workday",
     {"host": "nvidia.wd5.myworkdayjobs.com", "tenant": "nvidia", "locale": "en-US", "site": "NVIDIAExternalCareerSite"}),
    ("https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/x", "workday",
     {"host": "nvidia.wd5.myworkdayjobs.com", "tenant": "nvidia", "locale": None, "site": "NVIDIAExternalCareerSite"}),
    ("https://jobs.smartrecruiters.com/SmartRecruiters", "smartrecruiters", {"company": "SmartRecruiters"}),
    ("https://ats.rippling.com/rippling/jobs", "rippling", {"org": "rippling"}),
    ("https://apply.workable.com/acme/", "workable", {"account": "acme"}),
    ("https://acme.bamboohr.com/careers", "bamboohr", {"company": "acme"}),
    ("https://acme.jobs.personio.de/", "personio", {"host": "acme.jobs.personio.de"}),
    ("https://acme.recruitee.com/", "recruitee", {"company": "acme"}),
    ("https://www.ycombinator.com/jobs", "yc", {"role": None, "location": None}),
    ("https://www.ycombinator.com/jobs/role/software-engineer/location/remote", "yc",
     {"role": "software-engineer", "location": "remote"}),
    ("https://www.workatastartup.com/jobs", "yc", {"role": None, "location": None}),
    ("https://news.ycombinator.com/item?id=49522897", "hn", {"story_id": "49522897"}),
    ("https://weworkremotely.com/categories/remote-devops-sysadmin-jobs", "wwr", {"category": "remote-devops-sysadmin-jobs"}),
])
def test_detect_urls(url, key, params):
    detection = jobboards.detect(url)
    assert detection is not None, url
    assert detection.provider.key == key
    assert detection.params == params


@pytest.mark.parametrize("alias", ["yc", "hn", "remotive", "remoteok", "himalayas", "jobicy", "arbeitnow", "wwr"])
def test_detect_aliases(alias):
    detection = jobboards.detect(alias)
    assert detection and detection.provider.key == alias


def test_hn_alias_means_latest_thread():
    assert jobboards.detect("hn").params["story_id"] == "0"


def test_detect_unknown():
    assert jobboards.detect("https://example.com/careers") is None
    assert jobboards.detect("linkedin") is None


def test_embedded_board_link_stops_at_slug():
    page = '<html><iframe src="https://boards.greenhouse.io/acme?for=embed"></iframe></html>'
    assert jobboards.detect_embedded_board(page) == "https://boards.greenhouse.io/acme"
    assert jobboards.detect_embedded_board("<html>nothing here</html>") is None


def test_unknown_page_sniffs_embedded_board(network):
    page = b'<html><a href="https://jobs.lever.co/spotify">Careers</a></html>'
    network({"example.com/careers": page, "api.lever.co/v0/postings/spotify": "lever.json"})
    key, postings = jobboards.fetch("https://example.com/careers")
    assert key == "lever" and len(postings) == 2


def test_unknown_page_with_nothing_embedded_raises(network):
    network({"example.com": b"<html>custom ATS</html>"})
    with pytest.raises(LookupError):
        jobboards.fetch("https://example.com/careers")


def test_filter_by_title():
    postings = [{"title": "Senior Platform Engineer"}, {"title": "Account Manager"}, {"title": None}]
    assert jobboards.filter_by_title(postings, ["platform", "staff"]) == [postings[0]]
    assert jobboards.filter_by_title(postings, []) == postings


@pytest.mark.parametrize("board_title", [
    "Senior / Staff Fullstack Engineer",
    "Full Stack Engineer, Growth",
    "FULL-STACK ENGINEER",
    "Software Engineer (Full-stack)",
])
def test_filter_by_title_ignores_spelling_variants(board_title):
    """A profile that says 'Full-Stack Engineer' must catch every way boards write it."""
    postings = [{"title": board_title}, {"title": "Backend Engineer"}]
    assert jobboards.filter_by_title(postings, ["Full-Stack Engineer"]) == [postings[0]]


def test_normalize_title():
    assert jobboards.normalize_title("Full-Stack Engineer") == jobboards.normalize_title("fullstack engineer") == "fullstackengineer"
    assert jobboards.normalize_title("Member of Technical Staff") == "memberoftechnicalstaff"
