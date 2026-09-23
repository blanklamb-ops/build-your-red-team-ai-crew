#!/bin/sh
: <<'ACCEPTANCE_CHECKLIST'
# ACCEPTANCE — empire-advisor

Run this checklist directly from the repository root with: ./ACCEPTANCE.md

| ID | Check |
|----|-------|
| A1 | Plugin or shim loads via documented procedure |
| A2 | Submitting fixture command produces advisory JSON/text without executing alternatives |
| A3 | rules.yaml contains ≥10 rules with id + rationale |
| A4 | Same input twice → identical score and output |
| A5 | At least one fixture triggers a suggestion with KB citation |
| A6 | Offline fixture mode works without live Empire C2 |
| A7 | README documents Empire version compatibility and shim limits |
| A8 | OPSEC_CARD.md has Detection Recommendations (≥3 bullets) |
| A9 | Authorized-use notice is present |
| A10 | Semgrep + ast-grep run records are archived |

## Manual fidelity

| ID | Check |
|----|-------|
| M1 | Scoring rationale is understandable without reading source |
| M2 | Suggestions are concrete alternatives from the KB |
| M3 | Dangerous rules default to warn/deny advisory |

The executable exits nonzero on an automated failure. M1 and M2 also print
machine-checkable evidence but still require human wording/suitability review.
ACCEPTANCE_CHECKLIST
exec env PYTHONDONTWRITEBYTECODE=1 python3 scripts/acceptance.py "$@"
