#!/usr/bin/env python3
"""Build a resume HTML file from profile.yaml + resume.yaml + a layout.

Truth Only enforcement point (Constitution I): every experience bullet and
project on the rendered resume is referenced by id from the profile. An id
that does not exist in the profile fails the build. The build never writes
prose of its own — it selects.

Usage:
  build_resume.py --profile profile.yaml --resume resume.yaml \
                  --layout engine/layouts/classic --out out/resume.html \
                  [--title "Custom Title Page Suffix"]

The escape hatch for hand-written HTML resumes is simply not using this
script: render_check.py accepts any HTML file.
"""
from __future__ import annotations

import argparse
import html
import pathlib
import sys

import yaml


class BuildError(Exception):
    pass


def esc(s: str) -> str:
    return html.escape(str(s or "").strip())


def load_yaml(path: pathlib.Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as e:  # noqa: BLE001
        raise BuildError(f"cannot parse {path}: {e}") from e
    if not isinstance(data, dict):
        raise BuildError(f"{path} did not parse to a mapping")
    return data


def bullet_index(profile: dict) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for company in profile.get("history", []) or []:
        for b in company.get("bullets", []) or []:
            bid = (b or {}).get("id")
            if not bid:
                raise BuildError(
                    f"profile bullet without id under company "
                    f"{company.get('company')!r}"
                )
            if bid in index:
                raise BuildError(f"duplicate bullet id {bid!r} in profile")
            index[bid] = {"company": company.get("company"), "text": b.get("text", "")}
    return index


def project_index(profile: dict) -> dict[str, dict]:
    return {
        p["id"]: p
        for p in (profile.get("projects", []) or [])
        if isinstance(p, dict) and p.get("id")
    }


def contact_html(identity: dict) -> str:
    parts = []
    if identity.get("location"):
        parts.append(f"<div>{esc(identity['location'])}</div>")
    if identity.get("email"):
        e = esc(identity["email"])
        parts.append(f'<div><a href="mailto:{e}">{e}</a></div>')
    for key in ("linkedin", "website", "github"):
        url = (identity.get("links") or {}).get(key)
        if url:
            label = esc(url.replace("https://", "").replace("http://", "").rstrip("/"))
            parts.append(f'<div><a href="{esc(url)}">{label}</a></div>')
    return "\n".join(parts)


def skills_html(resume: dict) -> str:
    rows = []
    for group in resume.get("skills", []) or []:
        name = esc(group.get("group"))
        items = esc(", ".join(group.get("items", []) or []))
        if name and items:
            rows.append(f"<dt>{name}</dt>\n<dd>{items}</dd>")
    return f'<dl class="skills">\n{chr(10).join(rows)}\n</dl>' if rows else ""


def role_line(role: dict) -> str:
    end = role.get("end", "")
    end = "Present" if str(end).lower() == "present" else end
    span = " to ".join(str(x) for x in (role.get("start", ""), end) if x)
    return f"{esc(role.get('title'))} ({esc(span)})" if span else esc(role.get("title"))


def experience_html(profile: dict, resume: dict, bullets: dict[str, dict]) -> str:
    history = {c.get("company"): c for c in profile.get("history", []) or []}
    blocks = []
    for entry in resume.get("experience", []) or []:
        company = entry.get("company")
        if company not in history:
            raise BuildError(f"resume references unknown company {company!r}")
        selected = entry.get("include", []) or []
        if not selected:
            raise BuildError(f"no bullets selected for {company!r}")
        lis = []
        for bid in selected:
            if bid not in bullets:
                raise BuildError(f"unknown bullet id {bid!r} (company {company!r})")
            if bullets[bid]["company"] != company:
                raise BuildError(
                    f"bullet {bid!r} belongs to {bullets[bid]['company']!r}, "
                    f"selected under {company!r}"
                )
            lis.append(f"<li>{esc(bullets[bid]['text'])}</li>")
        c = history[company]
        roles = "<br />".join(role_line(r) for r in c.get("roles", []) or [])
        blocks.append(
            '<div class="job">\n'
            f'<p class="job--title"><strong>{esc(company)}</strong>'
            + (f", {esc(c.get('blurb'))}" if c.get("blurb") else "")
            + "</p>\n"
            + (f'<p class="job--roles">{roles}</p>\n' if roles else "")
            + (f'<p class="job--meta">{esc(c.get("location"))}</p>\n' if c.get("location") else "")
            + "<ul>\n" + "\n".join(lis) + "\n</ul>\n</div>"
        )
    return "\n".join(blocks)


def projects_html(resume: dict, projects: dict[str, dict]) -> str:
    rows = []
    for pid in resume.get("projects", []) or []:
        if pid not in projects:
            raise BuildError(f"unknown project id {pid!r}")
        p = projects[pid]
        rows.append(f"<dt>{esc(p.get('name'))}</dt>\n<dd>{esc(p.get('text'))}</dd>")
    return f'<dl class="skills">\n{chr(10).join(rows)}\n</dl>' if rows else ""


def education_html(profile: dict, resume: dict) -> str:
    if not resume.get("show_education", True):
        return ""
    rows = []
    for e in profile.get("education", []) or []:
        line = ", ".join(
            esc(x) for x in (e.get("credential"), e.get("school"), e.get("years")) if x
        )
        if line:
            rows.append(f"<dt>Education</dt>\n<dd>{line}</dd>")
    return f'<dl class="skills">\n{chr(10).join(rows)}\n</dl>' if rows else ""


def build(profile_path, resume_path, layout_dir, out_path, title_suffix=None) -> pathlib.Path:
    profile = load_yaml(pathlib.Path(profile_path))
    resume = load_yaml(pathlib.Path(resume_path))
    layout_dir = pathlib.Path(layout_dir)
    layout = (layout_dir / "layout.html").read_text()
    style = (layout_dir / "style.css").read_text()

    bullets = bullet_index(profile)
    identity = profile.get("identity", {}) or {}
    name = identity.get("name") or ""
    if not name:
        raise BuildError("profile identity.name is empty")

    page_title = f"{name} — Resume" + (f" — {title_suffix}" if title_suffix else "")
    tokens = {
        "{{PAGE_TITLE}}": esc(page_title),
        "{{STYLE}}": style,
        "{{NAME}}": esc(name),
        "{{TITLE}}": esc(resume.get("title", "")),
        "{{CONTACT}}": contact_html(identity),
        "{{SUMMARY}}": esc(resume.get("summary", "")),
        "{{SKILLS}}": skills_html(resume),
        "{{EXPERIENCE}}": experience_html(profile, resume, bullets),
        "{{PROJECTS}}": projects_html(resume, project_index(profile)),
        "{{EDUCATION}}": education_html(profile, resume),
    }
    out = layout
    for token, value in tokens.items():
        out = out.replace(token, value)
    leftover = [t for t in tokens if t in out]
    if leftover:
        raise BuildError(f"layout tokens not consumed: {leftover}")

    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out)
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--resume", required=True)
    ap.add_argument("--layout", required=True, help="layout directory")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default=None, help="page-title suffix, e.g. company name")
    args = ap.parse_args()
    try:
        path = build(args.profile, args.resume, args.layout, args.out, args.title)
    except BuildError as e:
        print(f"BUILD FAILED: {e}", file=sys.stderr)
        return 1
    print(f"built {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
