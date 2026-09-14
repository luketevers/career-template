#!/usr/bin/env python3
"""Fetch job postings from any supported board — the command the skills run.

    python3 engine/boards.py https://jobs.ashbyhq.com/linear --titles-from profile.yaml
    python3 engine/boards.py yc --role software-engineer --json
    python3 engine/boards.py --list

The implementation lives in the `jobboards` package next to this file:
one module per source, a shared posting shape, and URL/page detection.
This file only exists so the documented command keeps working.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from jobboards.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
