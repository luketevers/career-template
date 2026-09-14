"""Command line for `python3 engine/boards.py`.

    boards.py <url-or-source> [--titles a,b] [--titles-from profile.yaml]
              [--query TEXT] [--role R] [--location L] [--max N] [--json]
    boards.py --list

Exit codes: 0 postings printed, 1 nothing matched, 2 unknown source or a
fetch error. The pipeline skill branches on these.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import xml.etree.ElementTree as ET

from .detect import SOURCE_ALIASES, fetch, filter_by_title
from .registry import PROVIDERS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch a job board into one normalized posting shape.")
    parser.add_argument("source", nargs="?", help="board URL or aggregator name (yc, hn, remotive, ...)")
    parser.add_argument("--titles", default="", help="comma-separated keywords; keep postings whose title contains any")
    parser.add_argument("--titles-from", metavar="PROFILE", help="take keywords from profile.yaml targets.titles")
    parser.add_argument("--query", default=None, help="search text where the source supports it (workday, workable, getro, remotive, jobicy)")
    parser.add_argument("--role", default=None, help="yc only: role slug, e.g. software-engineer")
    parser.add_argument("--location", default=None, help="yc only: location slug, e.g. remote")
    parser.add_argument("--max", type=int, default=None, help="cap fetched postings where the source paginates")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    parser.add_argument("--list", action="store_true", help="list supported sources and exit")
    return parser


def print_source_list() -> None:
    for provider in PROVIDERS:
        print(f"{provider.key:16s} {provider.kind:10s} {provider.label}")
        if provider.notes:
            print(f"{'':28s}{provider.notes}")
    print("\naliases:", ", ".join(sorted(SOURCE_ALIASES)))


def resolve_source(args: argparse.Namespace) -> str:
    """Expand `yc --role X --location Y` into the matching YC page URL."""
    source = args.source
    if source.lower() in ("yc", "ycombinator") and (args.role or args.location):
        source = "https://www.ycombinator.com/jobs"
        if args.role:
            source += f"/role/{args.role}"
        if args.location:
            source += f"/location/{args.location}"
    return source


def title_keywords(args: argparse.Namespace) -> list[str]:
    keywords = [keyword for keyword in args.titles.split(",") if keyword.strip()]
    if args.titles_from:
        import yaml  # only needed for this flag; keeps the module stdlib-only otherwise

        with open(args.titles_from) as profile_file:
            profile = yaml.safe_load(profile_file) or {}
        keywords += list(((profile.get("targets") or {}).get("titles") or []))
    return keywords


def print_table(source_key: str, postings: list[dict], total: int, keywords: list[str]) -> None:
    filter_note = f" matching {keywords}" if keywords else ""
    print(f"# {source_key}: {len(postings)} of {total} postings{filter_note}")
    for posting in postings:
        remote_tag = " [remote]" if posting["remote"] else ""
        salary_tag = f"  {posting['salary']}" if posting["salary"] else ""
        location = posting["location"] or "location n/a"
        print(f"- {posting['company'] or '?'} — {posting['title']}{remote_tag}  ({location}){salary_tag}")
        print(f"  {posting['url']}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        print_source_list()
        return 0
    if not args.source:
        parser.error("source is required (or --list)")

    keywords = title_keywords(args)
    try:
        source_key, postings = fetch(resolve_source(args), query=args.query, max_items=args.max)
    except LookupError as error:
        print(f"boards: {error}", file=sys.stderr)
        return 2
    except (urllib.error.URLError, ValueError, ET.ParseError) as error:
        print(f"boards: fetch failed: {error}", file=sys.stderr)
        return 2

    total_fetched = len(postings)
    postings = filter_by_title(postings, keywords)
    if args.json:
        json.dump({"source": source_key, "total": total_fetched, "postings": postings}, sys.stdout, indent=2)
        print()
    else:
        print_table(source_key, postings, total_fetched, keywords)
    return 0 if postings else 1
