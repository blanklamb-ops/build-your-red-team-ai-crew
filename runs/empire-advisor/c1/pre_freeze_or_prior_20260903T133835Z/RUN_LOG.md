# RUN_LOG — `empire-advisor` / `c1`

| Field | Value |
|-------|-------|
| Freeze commit SHA | |
| Operator | |
| Host product + version | |
| Model string | |
| C4 Codestral pin (if c4) | |
| MCP versions | Semgrep: · ast-grep: · Serena: |
| ACCEPTANCE.md attached to model? | yes/no |
| Pipeline mode (c2) | subagents / staged-single-session / n/a |
| Air-gap (c4) | yes/no/partial |
| time_start_iso | |
| time_first_accept_attempt_iso | |
| time_end_iso | |
| time_minutes | |
| stop_reason | pass / intervention_cap / timeout / hard_fail |
| interventions_count | |
| quality notes (optional) | |

## Preflight checklist

- [ ] Fresh workspace
- [ ] Correct condition config
- [ ] MCP healthy
- [ ] Prompt frozen path used (no edits)

## Postflight checklist

- [ ] workspace/ archived
- [ ] transcript/ archived
- [ ] scanners/ archived
- [ ] acceptance_results.md filled
- [ ] interventions.csv filled
- [ ] pipeline/ present if c2–c4
