# RUN_LOG — `after-action` / `c1`

| Field | Value |
|-------|-------|
| Freeze commit SHA | `eca82cff43faf74d327aae3a1113a433e46a9f75` (repo HEAD at run start — "Add methodology scaffold for AI scaffolding vs single-prompt study."; no commits made during the run) |
| Operator | pilot-harness |
| Host product + version | Claude Code 2.1.233 |
| Model string | claude-sonnet-5 (Claude Sonnet 5) |
| C4 Codestral pin (if c4) | n/a (condition c1) |
| MCP versions | Semgrep: 1.176.0 · ast-grep: 0.45.3 · Serena: not used. Neither Semgrep nor ast-grep were preinstalled — both installed mid-run via `pipx install` (network available) since neither is an MCP server here; both were invoked as CLI tools. |
| ACCEPTANCE.md attached to model? | no — not pasted inline in the initial prompt; it was present on disk in `workspace/` and I located + read it myself as part of exploring the task directory. |
| Pipeline mode (c2) | n/a (condition c1) |
| Air-gap (c4) | n/a (condition c1) |
| time_start_iso | 2026-09-03T06:37:11Z |
| time_first_accept_attempt_iso | ~2026-09-03T06:55:37Z (first end-to-end `build` run producing both reports against the fixture, per that run's `client_report.md` "Generated:" timestamp — 2 real bugs found and fixed afterward: an over-greedy redaction regex and duplicate findings/severity counts from overlapping decision windows) |
| time_end_iso | ~2026-09-03T07:10Z (approximate — last verified rebuild + scanner archive pass in-session) |
| time_minutes | ~33 (approximate, derived from in-session artifact timestamps above, not harness telemetry — please cross-check against the transcript for the authoritative figure) |
| stop_reason | pass |
| interventions_count | 1 — user rejected my first exploration tool calls ("STOP what you are doing and wait...") and then explicitly redirected me ("go ahead and explore the c1 directory") before work resumed. No corrections were needed after that. (Not yet reflected in `interventions.csv`, which is still empty — happy to fill that too if wanted.) |
| quality notes (optional) | All A1–A10 / M1–M3 acceptance checks PASS (see `acceptance_results.md`). 14/14 unit tests pass. Self-caught issues during build, both fixed same session: (1) `generic_password_kv` redaction regex was swallowing trailing sentence punctuation adjacent to a secret; (2) events corroborating more than one decision (overlapping correlation windows) were double-counted in Findings placeholders and severity stats. |

## Preflight checklist

- [x] Fresh workspace — only the pre-supplied scaffold (`PROMPT.md`, `ACCEPTANCE.md`, `AUTHORIZED_USE.md`, `OPSEC_CARD_TEMPLATE.md`, `.gitkeep`) was present before implementation started.
- [x] Correct condition config — worked in `runs/after-action/c1/workspace/`, single-session non-subagent condition.
- [x] MCP healthy — n/a for this run; no MCP servers were used (Semgrep/ast-grep run as local CLIs).
- [x] Prompt frozen path used (no edits) — `PROMPT.md`/`ACCEPTANCE.md`/`AUTHORIZED_USE.md`/`OPSEC_CARD_TEMPLATE.md` were read only, never modified.

## Postflight checklist

- [ ] workspace/ archived — pending (human/harness postflight step)
- [ ] transcript/ archived — pending; `transcript/pilot_c1_claude.jsonl` already exists in this directory but I have no way to confirm it's finalized/complete
- [x] scanners/ archived — `../scanners/semgrep_after_action.{json,txt}` and `../scanners/ast_grep_after_action.{json,txt}` written and verified
- [x] acceptance_results.md filled
- [ ] interventions.csv filled — still empty; see `interventions_count` note above
- [ ] pipeline/ present if c2–c4 — n/a (condition c1)
