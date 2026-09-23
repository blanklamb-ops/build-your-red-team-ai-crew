# RUN_LOG — `after-action` / `c4`

| Field | Value |
|-------|-------|
| Freeze commit SHA | n/a — pre-freeze |
| Operator | pilot-harness |
| Host product + version | CrewAI 1.15.18 + Ollama host `192.168.224.1` |
| Model string | `ollama/codestral` |
| C4 Codestral pin (if c4) | `codestral:latest` digest `0898a8b286d5…` Q4_0 22.2B |
| MCP versions | Semgrep CLI (OOM on auto) · ast-grep CLI · Serena: n/a |
| ACCEPTANCE.md attached to model? | yes |
| Pipeline mode (c2) | n/a (c4) |
| Air-gap (c4) | partial — host Ollama over VMnet |
| time_start_iso | 2026-09-03T13:13:46Z |
| time_first_accept_attempt_iso | 2026-09-03T13:16Z (unassisted FAIL); 13:19Z (post-repair) |
| time_end_iso | 2026-09-03T13:15:35Z crew; repair ~13:21Z |
| time_minutes | ~2 crew + ~5 repair |
| stop_reason | **intervention_cap** — model stubs; agent completed working tool |
| interventions_count | 4 |
| quality notes (optional) | Unassisted: stub scaffold. Repair: stdlib after-action in `src/main.py`, fixtures from harness MVP, tests PASS. **RQ3 score = FAIL (unassisted).** Functional demo tree exists post-intervention. |

## Preflight checklist

- [x] Fresh workspace (stub archive kept)
- [x] Host Codestral reachable
- [x] Prompt frozen path used

## Postflight checklist

- [x] workspace/ has working sources + testdata
- [x] pipeline/ mirrored
- [x] scanners/ archived (ast-grep OK; semgrep partial/OOM)
- [x] acceptance_results.md filled (dual scoring)
- [x] interventions.csv filled
