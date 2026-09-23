# ACCEPTANCE — after-action

| ID | Check |
|----|-------|
| A1 | CLI/Make target builds reports from `testdata/fixture_engagement/` |
| A2 | ≥2 log adapters demonstrated on fixtures |
| A3 | Decision log joins produce a correlated timeline with ≥5 linked items |
| A4 | Client report contains exec summary, timeline, Detection Recommendations |
| A5 | Internal learning report contains successes + failures sections |
| A6 | Planted secret in fixture is redacted in client export |
| A7 | Internal report may retain more detail than client report (documented) |
| A8 | `OPSEC_CARD.md` with Detection Recommendations (≥3 bullets) |
| A9 | Authorized-use notice present |
| A10 | Semgrep + ast-grep outputs archived |

## Manual fidelity

| ID | Check |
|----|-------|
| M1 | Client tone appropriate for external read |
| M2 | Correlation rules documented (window size, keys) |
| M3 | Missing fields degrade gracefully with warnings |
