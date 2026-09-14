#!/usr/bin/env python3
"""Interactive onboarding: the enumerable half of setup.

Fills profile.yaml's structured fields — identity basics, target job titles
(searchable picker over a bundled list, custom entries welcome), levels,
locations, remote/onsite, compensation floor, and resume style (page
budget) — then hands off to the setup skill for the conversational half
(history bullets, strengths, gaps).

Comment-preserving on purpose: profile.yaml is created from
templates/profile.yaml by textual substitution so every schema comment
survives, and re-runs update known keys in place the same way. A YAML
round-trip would drop the comments the user relies on.

Usage: python3 engine/onboard.py   (interactive; safe to re-run)
"""
from __future__ import annotations

import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
TITLES_FILE = pathlib.Path(__file__).resolve().parent / "data" / "job_titles.txt"
PROFILE_TEMPLATE = REPO_ROOT / "templates" / "profile.yaml"
PROFILE_PATH = pathlib.Path("profile.yaml")  # relative: runs from the repo root

LEVEL_CHOICES = ["Junior", "Mid-level", "Senior", "Staff", "Principal", "Lead", "Manager", "Director", "VP", "Executive"]
SEARCH_RESULT_LIMIT = 8


# -------------------------------------------------------- title picker
def load_titles() -> list[str]:
    return [
        line.strip()
        for line in TITLES_FILE.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def search_titles(query: str, titles: list[str], limit: int = SEARCH_RESULT_LIMIT) -> list[str]:
    """Case-insensitive substring search; word-prefix matches rank first."""
    needle = query.lower().strip()
    if not needle:
        return []
    prefix_matches, substring_matches = [], []
    for title in titles:
        lowered = title.lower()
        if any(word.startswith(needle) for word in lowered.split()):
            prefix_matches.append(title)
        elif needle in lowered:
            substring_matches.append(title)
    return (prefix_matches + substring_matches)[:limit]


def pick_titles(titles: list[str]) -> list[str]:
    """Loop: search → numbered results → pick; quotes add a custom title."""
    print("\n— Target job titles —")
    print("Type to search the list (e.g. 'product', 'nurse', 'engineer').")
    print("Enter a number to pick, type a custom title in quotes to add it")
    print("verbatim, or press Enter on an empty line when done.\n")
    chosen: list[str] = []
    while True:
        query = input(f"search ({len(chosen)} picked) > ").strip()
        if not query:
            if chosen:
                return chosen
            print("pick at least one title (or type one in quotes).")
            continue
        is_quoted = query.startswith(('"', "'")) and query.endswith(('"', "'")) and len(query) > 2
        if is_quoted:
            chosen.append(query.strip("\"'"))
            print(f"  added custom: {chosen[-1]}")
            continue
        if query.isdigit():
            print("  search first, then pick by number from the results.")
            continue
        results = search_titles(query, titles)
        if not results:
            print("  no matches — type it in quotes to add a custom title.")
            continue
        for number, title in enumerate(results, 1):
            print(f"  {number}. {title}")
        picks = input("pick number(s), comma-separated (or Enter to search again) > ").strip()
        for pick in picks.split(","):
            pick = pick.strip()
            if pick.isdigit() and 1 <= int(pick) <= len(results):
                title = results[int(pick) - 1]
                if title not in chosen:
                    chosen.append(title)
                    print(f"  added: {title}")


# ------------------------------------------------------------- prompts
def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix} > ").strip()
    return answer or default


def ask_int(prompt: str, default: int) -> int:
    """Accepts '150k', '$150,000', '150000'."""
    while True:
        raw = ask(prompt, str(default))
        normalized = raw.replace(",", "").replace("$", "").replace("k", "000").replace("K", "000")
        try:
            return int(normalized)
        except ValueError:
            print("  enter a number")


def ask_list(prompt: str) -> list[str]:
    raw = ask(prompt + " (comma-separated)")
    return [item.strip() for item in raw.split(",") if item.strip()]


# --------------------------------------------------- writing the file
def yaml_list(items: list[str]) -> str:
    return "[" + ", ".join(f'"{item}"' for item in items) + "]"


def apply_answers(profile_text: str, answers: dict) -> str:
    """Substitute answers into the (template-shaped) profile text.

    Each pattern matches the key whether it still holds the template's
    empty value or a previously filled one, so re-running updates in place
    and every comment survives. Only the first occurrence is touched.
    """
    substitutions = [
        (r'(^identity:\n  name: )"[^"]*"', rf'\g<1>"{answers["name"]}"'),
        (r'(\n  email: )"[^"]*"', rf'\g<1>"{answers["email"]}"'),
        (r'(\n  location: ) *"[^"]*"', rf'\g<1>"{answers["location"]}"'),
        (r"(\ntargets:\n  locations: )\[[^\]]*\]", rf"\g<1>{yaml_list(answers['locations'])}"),
        (r"(\n  remote_ok: )\w+", rf"\g<1>{str(answers['remote_ok']).lower()}"),
        (r"(\n  onsite_days_max: )\d+", rf"\g<1>{answers['onsite_days_max']}"),
        (r"(\n  levels: )\[[^\]]*\]", rf"\g<1>{yaml_list(answers['levels'])}"),
        (r"(\n  titles: )\[[^\]]*\]", rf"\g<1>{yaml_list(answers['titles'])}"),
        (r"(\n  comp_floor_usd: )\d+", rf"\g<1>{answers['comp_floor']}"),
        (r"(\nresume_style:\n  max_pages: )\d+", rf"\g<1>{answers['max_pages']}"),
    ]
    for pattern, replacement in substitutions:
        profile_text = re.sub(pattern, replacement, profile_text, count=1, flags=re.M)
    return profile_text


# ------------------------------------------------------------------ cli
def interview() -> dict:
    """Ask every structured question and return the answers."""
    titles = load_titles()
    answers: dict = {}
    answers["name"] = ask("Full name")
    answers["email"] = ask("Email")
    answers["location"] = ask("Location as a recruiter should read it (e.g. 'Denver, CO')")
    answers["titles"] = pick_titles(titles)
    print("\n— Seniority levels you're targeting —")
    print("  " + ", ".join(LEVEL_CHOICES))
    answers["levels"] = ask_list("Levels")
    answers["locations"] = ask_list("Work locations you'd accept (e.g. Denver, Remote (US))")
    answers["remote_ok"] = ask("Remote OK? (y/n)", "y").lower().startswith("y")
    answers["onsite_days_max"] = ask_int("Max in-office days per week you'll accept", 5)
    answers["comp_floor"] = ask_int("Compensation floor, USD base (postings below get flagged)", 0)
    print("\n— Resume style —")
    print("One page is the default and right for most industries; academic")
    print("CVs, federal resumes, and some senior roles legitimately run longer.")
    answers["max_pages"] = ask_int("Max resume pages", 1)
    return answers


def main() -> int:
    print("career onboarding — the structured fields. Re-run any time;")
    print("the conversational parts (history, strengths, gaps) happen with")
    print("your agent afterward.\n")
    answers = interview()
    source_path = PROFILE_PATH if PROFILE_PATH.exists() else PROFILE_TEMPLATE
    PROFILE_PATH.write_text(apply_answers(source_path.read_text(), answers))
    print(f"\nwrote {PROFILE_PATH.resolve()}")
    print("next: tell your agent to 'run setup' to fill history, strengths,")
    print("and gaps — then build your first resume.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
