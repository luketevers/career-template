#!/usr/bin/env python3
"""Build a resume HTML file from profile.yaml + resume.yaml + a layout.

Truth Only enforcement point (Constitution I): every experience bullet and
project on the rendered resume is referenced *by id* from the profile. An
id that does not exist in the profile fails the build. The build never
writes prose of its own — it selects.

Usage:
  build_resume.py --profile profile.yaml --resume resume.yaml \
                  --layout engine/layouts/classic --out out/resume.html \
                  [--title "Custom Title Page Suffix"]

A layout is a directory with layout.html (containing {{TOKENS}}) and
style.css. The escape hatch for hand-written HTML resumes is simply not
using this script: render_check.py accepts any HTML file.
"""
from __future__ import annotations

import argparse
import html
import pathlib
import sys

import yaml


class BuildError(Exception):
    """Any reason the resume cannot be built truthfully."""


# ------------------------------------------------------------- loading
def esc(text: object) -> str:
    """HTML-escape any value; None becomes an empty string."""
    return html.escape(str(text or "").strip())


def load_yaml(path: pathlib.Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as error:  # noqa: BLE001 — surface any parse failure as a build error
        raise BuildError(f"cannot parse {path}: {error}") from error
    if not isinstance(data, dict):
        raise BuildError(f"{path} did not parse to a mapping")
    return data


def bullet_index(profile: dict) -> dict[str, dict]:
    """Every history bullet by id → {company, text}. Ids must be unique."""
    index: dict[str, dict] = {}
    for company_entry in profile.get("history", []) or []:
        for bullet in company_entry.get("bullets", []) or []:
            bullet_id = (bullet or {}).get("id")
            if not bullet_id:
                raise BuildError(f"profile bullet without id under company {company_entry.get('company')!r}")
            if bullet_id in index:
                raise BuildError(f"duplicate bullet id {bullet_id!r} in profile")
            index[bullet_id] = {"company": company_entry.get("company"), "text": bullet.get("text", "")}
    return index


def project_index(profile: dict) -> dict[str, dict]:
    return {
        project["id"]: project
        for project in (profile.get("projects", []) or [])
        if isinstance(project, dict) and project.get("id")
    }


# ------------------------------------------------------------ sections
def definition_list(rows: list[str]) -> str:
    """The <dl> used by skills, projects, and education; empty when no rows."""
    return f'<dl class="skills">\n{chr(10).join(rows)}\n</dl>' if rows else ""


def contact_html(identity: dict) -> str:
    parts = []
    if identity.get("location"):
        parts.append(f"<div>{esc(identity['location'])}</div>")
    if identity.get("email"):
        email = esc(identity["email"])
        parts.append(f'<div><a href="mailto:{email}">{email}</a></div>')
    for link_key in ("linkedin", "website", "github"):
        url = (identity.get("links") or {}).get(link_key)
        if url:
            label = esc(url.replace("https://", "").replace("http://", "").rstrip("/"))
            parts.append(f'<div><a href="{esc(url)}">{label}</a></div>')
    return "\n".join(parts)


def skills_html(resume: dict) -> str:
    rows = []
    for group in resume.get("skills", []) or []:
        group_name = esc(group.get("group"))
        items = esc(", ".join(group.get("items", []) or []))
        if group_name and items:
            rows.append(f"<dt>{group_name}</dt>\n<dd>{items}</dd>")
    return definition_list(rows)


def role_line(role: dict) -> str:
    """'Staff Engineer (2021 to Present)'."""
    end = role.get("end", "")
    end = "Present" if str(end).lower() == "present" else end
    span = " to ".join(str(part) for part in (role.get("start", ""), end) if part)
    return f"{esc(role.get('title'))} ({esc(span)})" if span else esc(role.get("title"))


def experience_html(profile: dict, resume: dict, bullets: dict[str, dict]) -> str:
    """One block per company in the resume's experience selection. This is
    where Truth Only bites: every included id must exist and belong to the
    company it is listed under."""
    history_by_company = {entry.get("company"): entry for entry in profile.get("history", []) or []}
    blocks = []
    for selection in resume.get("experience", []) or []:
        company = selection.get("company")
        if company not in history_by_company:
            raise BuildError(f"resume references unknown company {company!r}")
        included_ids = selection.get("include", []) or []
        if not included_ids:
            raise BuildError(f"no bullets selected for {company!r}")

        list_items = []
        for bullet_id in included_ids:
            if bullet_id not in bullets:
                raise BuildError(f"unknown bullet id {bullet_id!r} (company {company!r})")
            if bullets[bullet_id]["company"] != company:
                raise BuildError(
                    f"bullet {bullet_id!r} belongs to {bullets[bullet_id]['company']!r}, "
                    f"selected under {company!r}"
                )
            list_items.append(f"<li>{esc(bullets[bullet_id]['text'])}</li>")

        entry = history_by_company[company]
        roles = "<br />".join(role_line(role) for role in entry.get("roles", []) or [])
        blurb = f", {esc(entry.get('blurb'))}" if entry.get("blurb") else ""
        blocks.append(
            '<div class="job">\n'
            f'<p class="job--title"><strong>{esc(company)}</strong>{blurb}</p>\n'
            + (f'<p class="job--roles">{roles}</p>\n' if roles else "")
            + (f'<p class="job--meta">{esc(entry.get("location"))}</p>\n' if entry.get("location") else "")
            + "<ul>\n" + "\n".join(list_items) + "\n</ul>\n</div>"
        )
    return "\n".join(blocks)


def projects_html(resume: dict, projects: dict[str, dict]) -> str:
    rows = []
    for project_id in resume.get("projects", []) or []:
        if project_id not in projects:
            raise BuildError(f"unknown project id {project_id!r}")
        project = projects[project_id]
        rows.append(f"<dt>{esc(project.get('name'))}</dt>\n<dd>{esc(project.get('text'))}</dd>")
    return definition_list(rows)


def education_html(profile: dict, resume: dict) -> str:
    if not resume.get("show_education", True):
        return ""
    rows = []
    for entry in profile.get("education", []) or []:
        line = ", ".join(esc(part) for part in (entry.get("credential"), entry.get("school"), entry.get("years")) if part)
        if line:
            rows.append(f"<dt>Education</dt>\n<dd>{line}</dd>")
    return definition_list(rows)


# --------------------------------------------------------------- build
def build(profile_path, resume_path, layout_dir, out_path, title_suffix=None) -> pathlib.Path:
    profile = load_yaml(pathlib.Path(profile_path))
    resume = load_yaml(pathlib.Path(resume_path))
    layout_dir = pathlib.Path(layout_dir)
    layout_html = (layout_dir / "layout.html").read_text()
    stylesheet = (layout_dir / "style.css").read_text()

    identity = profile.get("identity", {}) or {}
    name = identity.get("name") or ""
    if not name:
        raise BuildError("profile identity.name is empty")

    page_title = f"{name} — Resume" + (f" — {title_suffix}" if title_suffix else "")
    token_values = {
        "{{PAGE_TITLE}}": esc(page_title),
        "{{STYLE}}": stylesheet,
        "{{NAME}}": esc(name),
        "{{TITLE}}": esc(resume.get("title", "")),
        "{{CONTACT}}": contact_html(identity),
        "{{SUMMARY}}": esc(resume.get("summary", "")),
        "{{SKILLS}}": skills_html(resume),
        "{{EXPERIENCE}}": experience_html(profile, resume, bullet_index(profile)),
        "{{PROJECTS}}": projects_html(resume, project_index(profile)),
        "{{EDUCATION}}": education_html(profile, resume),
    }
    rendered = layout_html
    for token, value in token_values.items():
        rendered = rendered.replace(token, value)
    unconsumed = [token for token in token_values if token in rendered]
    if unconsumed:
        raise BuildError(f"layout tokens not consumed: {unconsumed}")

    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered)
    return out_path


# ------------------------------------------------------------------ cli
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--resume", required=True)
    parser.add_argument("--layout", required=True, help="layout directory")
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", default=None, help="page-title suffix, e.g. company name")
    args = parser.parse_args()
    try:
        out_path = build(args.profile, args.resume, args.layout, args.out, args.title)
    except BuildError as error:
        print(f"BUILD FAILED: {error}", file=sys.stderr)
        return 1
    print(f"built {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
