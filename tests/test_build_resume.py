"""T011: YAML->HTML build, with Truth Only enforced at the build step."""
import pathlib

import pytest
import yaml

import build_resume as br

ROOT = pathlib.Path(__file__).resolve().parent.parent
SAM = ROOT / "examples" / "sam-rivera"
CLASSIC = ROOT / "engine" / "layouts" / "classic"
COMPACT = ROOT / "engine" / "layouts" / "compact"


def build_sam(tmp_path, layout=CLASSIC, resume_path=None):
    return br.build(
        SAM / "profile.yaml",
        resume_path or (SAM / "resume.yaml"),
        layout,
        tmp_path / "out.html",
    )


def test_builds_from_fixture_both_layouts(tmp_path):
    for layout in (CLASSIC, COMPACT):
        out = build_sam(tmp_path, layout)
        html = out.read_text()
        assert "Sam Rivera" in html
        assert "41 minutes to 12" in html or "41 to 12" in html
        assert "{{" not in html, "unconsumed layout tokens"


def test_every_rendered_bullet_exists_in_profile(tmp_path):
    out = build_sam(tmp_path)
    html = out.read_text()
    profile = yaml.safe_load((SAM / "profile.yaml").read_text())
    resume = yaml.safe_load((SAM / "resume.yaml").read_text())
    pool = {b["id"]: b["text"].strip() for c in profile["history"] for b in c["bullets"]}
    for entry in resume["experience"]:
        for bid in entry["include"]:
            # First few words of the bullet text must appear in the output.
            head = " ".join(pool[bid].split()[:4])
            assert head in html, f"bullet {bid} not rendered verbatim"


def test_unknown_bullet_id_fails(tmp_path):
    resume = yaml.safe_load((SAM / "resume.yaml").read_text())
    resume["experience"][0]["include"].append("corvid-invented-claim")
    bad = tmp_path / "resume.yaml"
    bad.write_text(yaml.safe_dump(resume))
    with pytest.raises(br.BuildError, match="unknown bullet id"):
        build_sam(tmp_path, resume_path=bad)


def test_bullet_from_wrong_company_fails(tmp_path):
    resume = yaml.safe_load((SAM / "resume.yaml").read_text())
    # bluejay bullet selected under Corvid
    resume["experience"][0]["include"].append("bluejay-scheduling")
    bad = tmp_path / "resume.yaml"
    bad.write_text(yaml.safe_dump(resume))
    with pytest.raises(br.BuildError, match="belongs to"):
        build_sam(tmp_path, resume_path=bad)


def test_unknown_project_id_fails(tmp_path):
    resume = yaml.safe_load((SAM / "resume.yaml").read_text())
    resume["projects"] = ["proj-does-not-exist"]
    bad = tmp_path / "resume.yaml"
    bad.write_text(yaml.safe_dump(resume))
    with pytest.raises(br.BuildError, match="unknown project id"):
        build_sam(tmp_path, resume_path=bad)
