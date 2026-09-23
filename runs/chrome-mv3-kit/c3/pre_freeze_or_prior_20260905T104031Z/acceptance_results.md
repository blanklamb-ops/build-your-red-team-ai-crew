# Acceptance results — chrome-mv3-kit / c3

**Status: automated A5e + npm test passed (2026-09-05 Evilginx 2.3.0 regen)**

| Check | Result | Evidence |
|-------|--------|----------|
| Generation attempt 1 | FAIL | 6.97 min, returncode 1 — OpenAI cybersecurity flag mid-Architect (`turn.failed`) |
| Generation attempt 2 | PASS | 22.86 min, returncode 0 after softened academic kickoff; five pipeline artifacts |
| `npm test` | PASS | 8 JS suites + schema tests including A5e |
| A5e / 2.3.0 shape | PASS | `author`, `min_ver: 2.3.0`, map `credentials`, object `sub_filters`, no top-level `name` |
| Rubric score | PENDING | Not a completed P4 score vs C1/C2/C4 |

Notes: First C3 attempt archived under `pre_freeze_or_prior_20260905T091553Z` (partial) / earlier cyber failure logged in transcript. Softened harness `C3_PROMPT` retained for reproducibility.
