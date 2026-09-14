"""The `python3 engine/boards.py` command: listing, JSON output, exit codes."""
import json
import subprocess
import sys

import jobboards
from jobboards import cli
from helpers import REPO_ROOT


def test_list_names_every_provider(capsys):
    assert cli.main(["--list"]) == 0
    output = capsys.readouterr().out
    for provider in jobboards.PROVIDERS:
        assert provider.key in output


def test_json_output_and_title_filter(network, capsys):
    network({"api.lever.co/v0/postings/spotify": "lever.json"})
    exit_code = cli.main(["https://jobs.lever.co/spotify", "--json", "--titles", "android"])
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0 and output["source"] == "lever" and output["total"] == 2
    assert all("android" in posting["title"].lower() for posting in output["postings"])


def test_nothing_matched_exits_1(network, capsys):
    network({"api.lever.co/v0/postings/spotify": "lever.json"})
    assert cli.main(["https://jobs.lever.co/spotify", "--titles", "zzz-no-such-role"]) == 1


def test_unknown_source_exits_2(capsys):
    assert cli.main(["not-a-board"]) == 2
    assert "no known job board" in capsys.readouterr().err


def test_yc_role_flag_builds_the_page_url(network):
    fake = network({"ycombinator.com/jobs/role/data-scientist/location/remote": "yc.html"})
    cli.main(["yc", "--role", "data-scientist", "--location", "remote", "--json"])
    assert fake.calls[0][0] == "https://www.ycombinator.com/jobs/role/data-scientist/location/remote"


def test_entry_script_runs_from_repo_root():
    """engine/boards.py is what the skills invoke; it must work as a script."""
    result = subprocess.run([sys.executable, str(REPO_ROOT / "engine" / "boards.py"), "--list"],
                            capture_output=True, text=True, cwd=REPO_ROOT)
    assert result.returncode == 0, result.stderr
    assert "greenhouse" in result.stdout
