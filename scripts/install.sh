#!/usr/bin/env bash
# One-shot environment setup for the career template (macOS + Linux).
#
#   bash scripts/install.sh              # venv + deps, browser check, smoke test
#   bash scripts/install.sh --dev        # also pytest (for engine development)
#   bash scripts/install.sh --with-browser   # install Chrome/Chromium if missing
#   bash scripts/install.sh --system     # skip the venv; pip install --user
#
# What it does, in order:
#   1. Finds a Python >= 3.11 (or tells you how to get one).
#   2. Creates .venv/ and installs the engine's dependencies into it
#      (pyyaml, pdfminer.six; plus pytest with --dev).
#   3. Looks for a Chromium-family browser — render_check.py needs one to
#      produce PDFs. Prints the install command, or runs it with --with-browser.
#   4. Smoke test: builds the fictional example resume and renders it to PDF
#      in a temp dir. Nothing is written into the repo.
#
# Idempotent: re-run any time. Nothing here touches your profile or data.
set -euo pipefail

cd "$(dirname "$0")/.."

DEV=0; SYSTEM=0; WITH_BROWSER=0; NO_CHECK=0
for arg in "$@"; do
  case "$arg" in
    --dev) DEV=1 ;;
    --system) SYSTEM=1 ;;
    --with-browser) WITH_BROWSER=1 ;;
    --no-check) NO_CHECK=1 ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    *) echo "unknown flag: $arg (try --help)" >&2; exit 2 ;;
  esac
done

BOLD=$'\033[1m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'; RESET=$'\033[0m'
ok()   { printf "${GREEN}  ok${RESET}  %s\n" "$1"; }
warn() { printf "${YELLOW}warn${RESET}  %s\n" "$1"; }
fail() { printf "${RED}fail${RESET}  %s\n" "$1" >&2; exit 1; }
step() { printf "\n${BOLD}%s${RESET}\n" "$1"; }

OS="$(uname -s)"
case "$OS" in
  Darwin|Linux) ;;
  *) fail "unsupported OS: $OS (macOS and Linux only)" ;;
esac

# ---------------------------------------------------------------- 1. python
step "1/4  Python"
PY=""
for cand in python3 python3.13 python3.12 python3.11; do
  if command -v "$cand" >/dev/null 2>&1 \
     && "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
    PY="$(command -v "$cand")"; break
  fi
done
if [[ -z "$PY" ]]; then
  echo "  Python 3.11+ not found." >&2
  if [[ "$OS" == "Darwin" ]]; then
    echo "  Install:  brew install python" >&2
  else
    echo "  Install:  sudo apt-get install python3 python3-venv   (Debian/Ubuntu)" >&2
    echo "            sudo dnf install python3                   (Fedora)" >&2
  fi
  exit 1
fi
ok "$("$PY" --version)  ($PY)"

# ------------------------------------------------------------ 2. dependencies
step "2/4  Dependencies"
EXTRA="checks"; [[ $DEV -eq 1 ]] && EXTRA="dev"

if [[ $SYSTEM -eq 1 ]]; then
  # No venv: install into the interpreter found above. Modern distro Pythons
  # (PEP 668) refuse this; the venv default exists for exactly that reason.
  if ! "$PY" -m pip install --quiet --user -e ".[$EXTRA]"; then
    fail "pip refused a --user install (externally managed Python?). Re-run without --system to use a venv."
  fi
  RUN_PY="$PY"
  ok "installed into $PY (--user)"
elif [[ -n "${VIRTUAL_ENV:-}" ]]; then
  RUN_PY="$VIRTUAL_ENV/bin/python"
  "$RUN_PY" -m pip install --quiet -e ".[$EXTRA]"
  ok "installed into the active venv ($VIRTUAL_ENV)"
else
  # A venv is only usable if it has pip; a failed earlier attempt (e.g. missing
  # python3-venv) leaves a stub directory behind, so rebuild in that case.
  if ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
    rm -rf .venv
    if ! "$PY" -m venv .venv; then
      rm -rf .venv
      fail "could not create .venv (Debian/Ubuntu: sudo apt-get install python3-venv)"
    fi
  fi
  RUN_PY=".venv/bin/python"
  "$RUN_PY" -m pip install --quiet --upgrade pip
  "$RUN_PY" -m pip install --quiet -e ".[$EXTRA]"
  ok "installed into .venv/ (pyyaml, pdfminer.six$([[ $DEV -eq 1 ]] && echo ', pytest'))"
fi

# ---------------------------------------------------------------- 3. browser
step "3/4  Browser (headless PDF rendering)"
find_browser() {
  "$RUN_PY" - <<'PY'
import sys
sys.path.insert(0, "engine")
import render_check as rc
b = rc.find_chrome()
print(b or "")
sys.exit(0 if b else 1)
PY
}

BROWSER="$(find_browser || true)"
if [[ -z "$BROWSER" && $WITH_BROWSER -eq 1 ]]; then
  if [[ "$OS" == "Darwin" ]]; then
    command -v brew >/dev/null || fail "Homebrew not found; install Chrome manually from https://www.google.com/chrome/"
    brew install --cask google-chrome
  else
    SUDO=""; [[ $EUID -ne 0 ]] && SUDO="sudo"
    if command -v apt-get >/dev/null; then
      $SUDO apt-get update -qq && $SUDO apt-get install -y --no-install-recommends chromium fonts-liberation
    elif command -v dnf >/dev/null; then
      $SUDO dnf install -y chromium liberation-fonts
    else
      fail "no apt-get or dnf; install Chromium with your package manager, then re-run"
    fi
  fi
  BROWSER="$(find_browser || true)"
fi

if [[ -n "$BROWSER" ]]; then
  ok "$BROWSER"
else
  warn "no Chrome/Chromium found — resume builds work, but PDF render checks won't."
  if [[ "$OS" == "Darwin" ]]; then
    echo "      brew install --cask google-chrome      (or re-run with --with-browser)"
  else
    echo "      sudo apt-get install chromium fonts-liberation   (or re-run with --with-browser)"
  fi
  echo "      Non-standard location? export CHROME_BIN=/path/to/chrome"
fi

# ------------------------------------------------------------- 4. smoke test
step "4/4  Smoke test (fictional example, temp dir)"
if [[ $NO_CHECK -eq 1 ]]; then
  warn "skipped (--no-check)"
else
  SCRATCH="$(mktemp -d)"; trap 'rm -rf "$SCRATCH"' EXIT
  "$RUN_PY" engine/build_resume.py \
    --profile examples/sam-rivera/profile.yaml \
    --resume examples/sam-rivera/resume.yaml \
    --layout engine/layouts/classic \
    --out "$SCRATCH/resume.html" >/dev/null
  ok "build_resume: example resume built (every bullet traced to the profile)"
  if [[ -n "$BROWSER" ]]; then
    # Orphan detection depends on font metrics (Georgia is macOS-only), so the
    # environment check only asserts the page count; the full check runs on
    # your own resume during setup.
    if "$RUN_PY" engine/render_check.py "$SCRATCH/resume.html" \
         --pdf "$SCRATCH/resume.pdf" --skip-orphans >/dev/null; then
      ok "render_check: one-page PDF rendered"
    else
      fail "render_check could not render a PDF — check the browser above (CHROME_BIN?)"
    fi
  else
    warn "render_check skipped (no browser)"
  fi
fi

# ------------------------------------------------------------------ next
printf "\n${BOLD}Ready.${RESET}\n"
if [[ $SYSTEM -eq 0 && -z "${VIRTUAL_ENV:-}" ]]; then
  echo "  Activate the environment in each shell before running the engine or your agent:"
  echo "      source .venv/bin/activate"
fi
echo "  Then:"
echo "      python3 engine/onboard.py        # pick titles, levels, locations, page budget"
echo "      claude                            # and say: run setup"
[[ $DEV -eq 1 ]] && echo "      pytest                            # engine test suite"
exit 0
