# Launch check — spec 001 (T036)

**Run**: 2026-09-11. **Verdict: READY except two named holds** (bottom).

## Functional requirements

| FR | Requirement | Status | Evidence |
|---|---|---|---|
| FR-001 | Zero personal data; fictional examples in `examples/` | PASS | Audit script clean over tree; Sam marked FICTIONAL in every file; `tests/test_fixtures.py::test_fixture_is_fictional` |
| FR-002 | Skills derive user facts solely from profile.yaml | PASS | setup / application-pipeline / interview-prep / AGENTS.md all read `profile.yaml`; `voice` reads `writing-feedback.md` and `season` reads the tracker by design (neither states user facts) |
| FR-003 | Ashby/Greenhouse/Lever/Workday + manual fallback | PASS | application-pipeline §1 (incl. Ashby posting-API-disabled fallback and "never skip form review") |
| FR-004 | One-page render + orphan check, fail loudly | PASS | `engine/render_check.py` (exit 1 with named violation); tests cover pass/fail; demo shows it live |
| FR-005 | Voice rules gate + bootstrap on empty log | PASS (fixed in this check) | voice SKILL; gate wired in application-pipeline §5 AND interview-prep §2 — the latter was missed at T022 and added during this launch check |
| FR-006 | Tracker fields incl. predicted fit + first response | PASS | `templates/tracker.md`; season.py parses them; `tests/test_season.py` |
| FR-007 | Close → retro + freeze | PASS | `season.py close`; refuses unresolved rows and double-close; tested |
| FR-008 | No submit/send/sensitive-autofill anywhere | PASS | engine grep clean (Chrome subprocess only); every skill ends at checklist/proposal; constitution governance rejects future requests |
| FR-009 | Documented agent-runnable setup, clone → first variant | PASS | setup SKILL (privacy check first); AGENTS.md setup section |
| FR-010 | YAML canonical, 2 layouts, shared check, HTML accepted | PASS | build_resume + classic/compact; render_check takes any HTML (escape hatch is check-only, a documented deviation from T013's flag wording) |
| FR-011 | Claude skills + generic AGENTS.md; connector features marked | PASS | AGENTS.md; season SKILL sweep flagged Claude Code-only |
| FR-012 | MIT license from first public commit | PASS | LICENSE present since Phase 1 (`959e859`) |

## Success criteria

| SC | Status | Notes |
|---|---|---|
| SC-001 | **HOLD — not verified** | Needs one non-author user to go clone → variant in <60 min. Recommend one friendly tester before or immediately after launch. |
| SC-002 | PASS | Provenance enforced in code (`test_unknown_bullet_id_fails` etc.); Sam spot-audit clean |
| SC-003 | PASS | `demo/demo.sh` reproduces the full loop live; walkthrough.md documents it |
| SC-004 | PASS with a stated nuance | Working tree + all tracked files clean against the maintainer blocklist; machine paths scrubbed from demo.cast during this check. Nuance: git AUTHOR metadata and commit trailers identify the maintainer — expected and acceptable (SC-004 protects career data, not maintainer identity); the maintainer's name appearing as repo owner is inherent to publishing. |

## Fixed during this check

1. `demo/demo.cast` contained absolute local paths (`/Users/<user>/...`) — scrubbed to `~/career-template` / `/tmp/demo-scratch`.
2. Voice-gate wiring missing from interview-prep (T022 gap) — added.

## Holds before T037 (flip public)

1. **SC-001 stranger test** — one person who isn't the maintainer runs setup. (Judgment call: launching without it is survivable; the README quickstart doubles as the script.)
2. **Maintainer decision on the repo's public name/owner** — publishing under the personal account publicly ties the product to the maintainer (fine, expected — but decide deliberately, since the maintainer is mid-job-search and this repo reveals sophisticated application tooling. Consider whether recruiters finding it helps or hurts; the constitution's anti-spam stance is the defense).

Everything else is green: 16/16 tests, audit clean, demo runs end to end.
