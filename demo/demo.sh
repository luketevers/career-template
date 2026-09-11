#!/usr/bin/env bash
# The career-template demo, starring the fictional Sam Rivera.
# Everything here runs for real against the repo's example data —
# run it yourself from the repo root:  bash demo/demo.sh
set -uo pipefail

DIM=$'\033[2m'; BOLD=$'\033[1m'; GREEN=$'\033[32m'; RED=$'\033[31m'; RESET=$'\033[0m'
say()  { printf "\n${DIM}# %s${RESET}\n" "$1"; sleep "${2:-1.6}"; }
run()  { printf "${BOLD}$ %s${RESET}\n" "$1"; sleep 0.7; eval "$1"; sleep "${2:-1.4}"; }

REPO="$(pwd)"
SCRATCH="$(mktemp -d)"
trap 'rm -rf "$SCRATCH"' EXIT

clear
printf "${BOLD}career-template${RESET} — the resume that compounds\n"
say "Meet Sam Rivera. Fictional engineer, real pipeline." 2
run "grep -A3 'identity:' examples/sam-rivera/profile.yaml | head -4"

say "1. Point it at a live job board (Linear's, via the Ashby API):" 2
run "curl -s 'https://jobs.ashbyhq.com/api/non-user-graphql' -H 'Content-Type: application/json' --data '{\"operationName\":\"ApiJobBoardWithTeams\",\"variables\":{\"organizationHostedJobsPageName\":\"linear\"},\"query\":\"query ApiJobBoardWithTeams(\$organizationHostedJobsPageName: String!) { jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: \$organizationHostedJobsPageName) { jobPostings { title locationName } } }\"}' | python3 -c 'import json,sys; [print(\" •\", p[\"title\"], \"—\", p.get(\"locationName\",\"\")) for p in json.load(sys.stdin)[\"data\"][\"jobBoard\"][\"jobPostings\"][:6]]' || echo ' (offline — see examples/sam-rivera/snapshots/)'" 2

say "2. The agent ranks fit against Sam's profile — strengths AND named gaps." 2
printf "${DIM}   (excerpt from the recorded pipeline run)${RESET}\n"
cat <<'RANK'
   Senior/Staff Product Engineer, AI — ~75%
   + LLM feature shipped behind a 500-case offline eval set
   + internal tooling with 200+ daily users
   – gap they'll probe: no model training (API-level work only)
RANK
sleep 3

say "3. Tailor a variant. Every bullet is selected from Sam's verified profile:" 2
run "python3 engine/build_resume.py --profile examples/sam-rivera/profile.yaml --resume examples/sam-rivera/resume.yaml --layout engine/layouts/classic --out $SCRATCH/resume.html --title Linear"

say "4. Check it: exactly one page, no orphan lines." 1.5
run "python3 engine/render_check.py $SCRATCH/resume.html --pdf '$SCRATCH/Sam Rivera Resume - Linear.pdf'" 2

say "5. Try to make it lie. (You can't — unknown claims fail the build.)" 2
run "python3 - <<'EOF'
import yaml, pathlib
r = yaml.safe_load(open('examples/sam-rivera/resume.yaml'))
r['experience'][0]['include'].append('corvid-kubernetes-at-scale')  # invented
pathlib.Path('$SCRATCH/lying-resume.yaml').write_text(yaml.safe_dump(r))
EOF
python3 engine/build_resume.py --profile examples/sam-rivera/profile.yaml --resume $SCRATCH/lying-resume.yaml --layout engine/layouts/classic --out $SCRATCH/nope.html" 2.5

say "6. Every application is tracked with its fit prediction. Closing a season audits you:" 2
run "mkdir -p $SCRATCH/home && cp -r examples/sam-rivera/searches $SCRATCH/home/ && cd $SCRATCH/home && python3 - <<'EOF'
# reopen the example season so the demo can close it live
import pathlib, re
p = pathlib.Path('searches/2026/applications.md')
p.write_text(re.sub(r'^Status: CLOSED [0-9-]+\.', 'Status: OPEN.', p.read_text(), flags=re.M))
pathlib.Path('searches/2026/retro.md').unlink()
EOF
python3 \"$REPO\"/engine/season.py close 2026 && head -13 searches/2026/retro.md && cd \"$REPO\" >/dev/null" 3

say "The retro is the product: predicted fit vs what actually happened," 1.2
say "so the NEXT search starts from evidence, not vibes." 2
printf "\n${GREEN}It prepares. ${BOLD}You review, you submit.${RESET}\n\n"
sleep 2
