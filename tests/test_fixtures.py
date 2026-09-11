"""T010: the Sam Rivera fixture loads, satisfies the schema, and is clean."""
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAM = ROOT / "examples" / "sam-rivera"


def load(name):
    return yaml.safe_load((SAM / name).read_text())


def test_profile_loads_and_has_required_sections():
    p = load("profile.yaml")
    assert p["identity"]["name"] == "Sam Rivera"
    assert p["identity"]["email"].endswith("@example.com")
    assert p["targets"]["comp_floor_usd"] > 0
    assert p["strengths"] and p["gaps"], "fit rubric needs both"
    assert p["history"], "provenance pool must exist"


def test_bullet_ids_unique_and_present():
    p = load("profile.yaml")
    ids = [b["id"] for c in p["history"] for b in c["bullets"]]
    assert ids and len(ids) == len(set(ids))
    for c in p["history"]:
        for b in c["bullets"]:
            assert b["text"].strip()
            assert "metrics" in b


def test_resume_selects_only_existing_ids():
    p, r = load("profile.yaml"), load("resume.yaml")
    pool = {b["id"] for c in p["history"] for b in c["bullets"]}
    companies = {c["company"] for c in p["history"]}
    for entry in r["experience"]:
        assert entry["company"] in companies
        for bid in entry["include"]:
            assert bid in pool, f"resume selects unknown bullet {bid}"
    projects = {pr["id"] for pr in p.get("projects", [])}
    for pid in r.get("projects", []):
        assert pid in projects


def test_fixture_is_fictional():
    text = (SAM / "profile.yaml").read_text().lower()
    assert "fictional" in text
    assert "example.com" in text
