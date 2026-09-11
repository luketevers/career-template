#!/usr/bin/env bash
# Personal-data audit (spec 001, SC-004).
#
# Greps the working tree (excluding .git and this script's own blocklist)
# for every pattern in scripts/audit-blocklist.txt — the maintainer's name,
# email, employers, domains, and anything else that must never ship in the
# public template. Exits nonzero on any hit.
#
# The real blocklist is git-ignored (it is itself personal data). Copy
# scripts/audit-blocklist.example.txt to scripts/audit-blocklist.txt and
# fill it in locally. CI or a pre-publish check should fail if the file is
# missing, so an empty machine can't accidentally "pass".
set -euo pipefail

cd "$(dirname "$0")/.."
BLOCKLIST="scripts/audit-blocklist.txt"

if [[ ! -f "$BLOCKLIST" ]]; then
  echo "AUDIT: $BLOCKLIST missing — refusing to pass by default." >&2
  echo "Copy scripts/audit-blocklist.example.txt and fill it in." >&2
  exit 2
fi

status=0
while IFS= read -r pattern; do
  [[ -z "$pattern" || "$pattern" == \#* ]] && continue
  # -I skips binaries' contents; PDFs etc. still get filename matching below.
  if hits=$(grep -rIn --exclude-dir=.git --exclude="audit-blocklist.txt" -i -- "$pattern" . 2>/dev/null); then
    echo "AUDIT HIT for pattern '$pattern':"
    echo "$hits" | head -20
    status=1
  fi
  # Filenames too (a PDF named after the maintainer would slip past -I).
  if fhits=$(find . -path ./.git -prune -o -iname "*${pattern}*" -print | grep -v "^$" | grep -iv "audit-blocklist"); then
    if [[ -n "$fhits" ]]; then
      echo "AUDIT FILENAME HIT for pattern '$pattern':"
      echo "$fhits"
      status=1
    fi
  fi
done < "$BLOCKLIST"

if [[ $status -eq 0 ]]; then
  echo "AUDIT: clean."
fi
exit $status
