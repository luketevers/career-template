#!/usr/bin/env python3
"""Interactive onboarding: the enumerable half of setup.

Fills profile.yaml's structured fields — identity basics, target job titles
(searchable picker over a bundled list, custom entries welcome), levels,
locations, remote/onsite, compensation floor, and resume style (page
budget) — then hands off to the setup skill for the conversational half
(history bullets, strengths, gaps).

Comment-preserving: when profile.yaml doesn't exist, it is created from
templates/profile.yaml by textual substitution so every schema comment
survives. When it exists, values are updated in place by the same textual
method for known keys.

Usage: python3 engine/onboard.py   (interactive; safe to re-run)
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TITLES_FILE = pathlib.Path(__file__).resolve().parent / "data" / "job_titles.txt"
TEMPLATE = ROOT / "templates" / "profile.yaml"
PROFILE = pathlib.Path("profile.yaml")

LEVEL_CHOICES = ["Junior", "Mid-level", "Senior", "Staff", "Principal", "Lead", "Manager", "Director", "VP", "Executive"]


def load_titles() -> list[str]:
    return [
        ln.strip()
        for ln in TITLES_FILE.read_text().splitlines()
        if ln.strip() and not ln.startswith("#")
    ]


def search_titles(query: str, titles: list[str], limit: int = 8) -> list[str]:
    """Case-insensitive substring search; word-prefix matches rank first."""
    q = query.lower().strip()
    if not q:
        return []
    prefix, contains = [], []
    for t in titles:
        tl = t.lower()
        if any(w.startswith(q) for w in tl.split()):
            prefix.append(t)
        elif q in tl:
            contains.append(t)
    return (prefix + contains)[:limit]


def pick_titles(titles: list[str]) -> list[str]:
    print("\n— Target job titles —")
    print("Type to search the list (e.g. 'product', 'nurse', 'engineer').")
    print("Enter a number to pick, type a custom title in quotes to add it")
    print("verbatim, or press Enter on an empty line when done.\n")
    chosen: list[str] = []
    while True:
        q = input(f"search ({len(chosen)} picked) > ").strip()
        if not q:
            if chosen:
                return chosen
            print("pick at least one title (or type one in quotes).")
            continue
        if q.startswith(('"', "'")) and q.endswith(('"', "'")) and len(q) > 2:
            chosen.append(q.strip("\"'"))
            print(f"  added custom: {chosen[-1]}")
            continue
        if q.isdigit():
            print("  search first, then pick by number from the results.")
            continue
        results = search_titles(q, titles)
        if not results:
            print("  no matches — type it in quotes to add a custom title.")
            continue
        for i, t in enumerate(results, 1):
            print(f"  {i}. {t}")
        sel = input("pick number(s), comma-separated (or Enter to search again) > ").strip()
        for part in sel.split(","):
            part = part.strip()
            if part.isdigit() and 1 <= int(part) <= len(results):
                t = results[int(part) - 1]
                if t not in chosen:
                    chosen.append(t)
                    print(f"  added: {t}")


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix} > ").strip()
    return val or default


def ask_int(prompt: str, default: int) -> int:
    while True:
        raw = ask(prompt, str(default))
        try:
            return int(raw.replace(",", "").replace("$", "").replace("k", "000").replace("K", "000"))
        except ValueError:
            print("  enter a number")


def ask_list(prompt: str) -> list[str]:
    raw = ask(prompt + " (comma-separated)")
    return [x.strip() for x in raw.split(",") if x.strip()]


def yaml_list(items: list[str]) -> str:
    return "[" + ", ".join(f'"{i}"' for i in items) + "]"


def apply_answers(text: str, a: dict) -> str:
    """Textual substitution into the (template-shaped) profile, preserving
    comments. Each key is replaced only on its first schema occurrence."""
    # Each pattern matches the key whether it holds the template's empty
    # value or a previously-filled one, so re-running onboarding updates
    # in place while every comment survives.
    subs = [
        (r'(^identity:\n  name: )"[^"]*"', rf'\g<1>"{a["name"]}"'),
        (r'(\n  email: )"[^"]*"', rf'\g<1>"{a["email"]}"'),
        (r'(\n  location: ) *"[^"]*"', rf'\g<1>"{a["location"]}"'),
        (r"(\ntargets:\n  locations: )\[[^\]]*\]", rf"\g<1>{yaml_list(a['locations'])}"),
        (r"(\n  remote_ok: )\w+", rf"\g<1>{str(a['remote_ok']).lower()}"),
        (r"(\n  onsite_days_max: )\d+", rf"\g<1>{a['onsite_days_max']}"),
        (r"(\n  levels: )\[[^\]]*\]", rf"\g<1>{yaml_list(a['levels'])}"),
        (r"(\n  titles: )\[[^\]]*\]", rf"\g<1>{yaml_list(a['titles'])}"),
        (r"(\n  comp_floor_usd: )\d+", rf"\g<1>{a['comp_floor']}"),
        (r"(\nresume_style:\n  max_pages: )\d+", rf"\g<1>{a['max_pages']}"),
    ]
    for pattern, repl in subs:
        text = re.sub(pattern, repl, text, count=1, flags=re.M)
    return text


def main() -> int:
    titles = load_titles()
    print("career onboarding — the structured fields. Re-run any time;")
    print("the conversational parts (history, strengths, gaps) happen with")
    print("your agent afterward.\n")

    a: dict = {}
    a["name"] = ask("Full name")
    a["email"] = ask("Email")
    a["location"] = ask("Location as a recruiter should read it (e.g. 'Denver, CO')")
    a["titles"] = pick_titles(titles)
    print("\n— Seniority levels you're targeting —")
    print("  " + ", ".join(LEVEL_CHOICES))
    a["levels"] = ask_list("Levels")
    a["locations"] = ask_list("Work locations you'd accept (e.g. Denver, Remote (US))")
    a["remote_ok"] = ask("Remote OK? (y/n)", "y").lower().startswith("y")
    a["onsite_days_max"] = ask_int("Max in-office days per week you'll accept", 5)
    a["comp_floor"] = ask_int("Compensation floor, USD base (postings below get flagged)", 0)
    print("\n— Resume style —")
    print("One page is the default and right for most industries; academic")
    print("CVs, federal resumes, and some senior roles legitimately run longer.")
    a["max_pages"] = ask_int("Max resume pages", 1)

    source = PROFILE if PROFILE.exists() else TEMPLATE
    text = apply_answers(source.read_text(), a)
    PROFILE.write_text(text)
    print(f"\nwrote {PROFILE.resolve()}")
    print("next: tell your agent to 'run setup' to fill history, strengths,")
    print("and gaps — then build your first resume.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
