"""T048: onboarding — title search and comment-preserving profile writes."""
import pathlib

import yaml

import onboard

ROOT = pathlib.Path(__file__).resolve().parent.parent

ANSWERS = {
    "name": "Sam Rivera",
    "email": "sam.rivera@example.com",
    "location": "Chicago, IL",
    "titles": ["Product Manager", "Program Manager"],
    "levels": ["Senior"],
    "locations": ["Chicago", "Remote (US)"],
    "remote_ok": True,
    "onsite_days_max": 3,
    "comp_floor": 165000,
    "max_pages": 2,
}


def test_titles_list_loads_and_is_broad():
    titles = onboard.load_titles()
    assert len(titles) > 150
    # generalization check: well beyond engineering
    for t in ("Registered Nurse", "Account Executive", "Financial Analyst",
              "Teacher", "Product Marketing Manager", "Paralegal"):
        assert t in titles


def test_search_prefix_beats_contains():
    titles = onboard.load_titles()
    res = onboard.search_titles("nurse", titles)
    assert res[0] == "Registered Nurse" or "Nurse" in res[0]
    res = onboard.search_titles("market", titles)
    assert any("Marketing" in t for t in res)
    assert onboard.search_titles("zzzz", titles) == []


def test_apply_answers_fills_template_and_keeps_comments():
    template = (ROOT / "templates" / "profile.yaml").read_text()
    out = onboard.apply_answers(template, ANSWERS)
    data = yaml.safe_load(out)
    assert data["identity"]["name"] == "Sam Rivera"
    assert data["targets"]["titles"] == ["Product Manager", "Program Manager"]
    assert data["targets"]["comp_floor_usd"] == 165000
    assert data["targets"]["onsite_days_max"] == 3
    assert data["resume_style"]["max_pages"] == 2
    # comments survive the fill
    assert "Truth Only" in out
    assert "searchable list" in out


def test_apply_answers_rerun_updates_existing_values():
    template = (ROOT / "templates" / "profile.yaml").read_text()
    first = onboard.apply_answers(template, ANSWERS)
    changed = dict(ANSWERS, titles=["Data Analyst"], comp_floor=190000)
    second = onboard.apply_answers(first, changed)
    data = yaml.safe_load(second)
    assert data["targets"]["titles"] == ["Data Analyst"]
    assert data["targets"]["comp_floor_usd"] == 190000
