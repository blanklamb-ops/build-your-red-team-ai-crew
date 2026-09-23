# ACCEPTANCE — empire-advisor

| ID | Check |
|----|-------|
| A1 | Plugin or shim loads via documented procedure |
| A2 | Submitting fixture command produces advisory JSON/text without executing alternatives |
| A3 | `rules.yaml` (or equiv) contains ≥10 rules with id + rationale |
| A4 | Same input twice → identical score (determinism test) |
| A5 | At least one fixture triggers a suggestion with KB citation |
| A6 | Offline fixture mode works without live Empire C2 |
| A7 | README documents Empire version compatibility or shim limits |
| A8 | `OPSEC_CARD.md` with Detection Recommendations (≥3 bullets) |
| A9 | Authorized-use notice present |
| A10 | Semgrep + ast-grep outputs archived |

## Manual fidelity

| ID | Check |
|----|-------|
| M1 | Scoring rationale understandable to an operator without reading source |
| M2 | Suggestions are alternatives in the KB, not vague advice only |
| M3 | Dangerous rules default to warn/block advisory, not silent ignore |
