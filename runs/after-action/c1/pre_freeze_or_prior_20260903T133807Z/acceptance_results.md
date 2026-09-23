# Acceptance results — after-action / c1

Copy checks from `prompts/after-action/ACCEPTANCE.md`. Mark PASS/FAIL.

| ID | Result | Notes |
|----|--------|-------|
| A1 | PASS | `make build` (→ `python3 -m after_action.cli build --engagement testdata/fixture_engagement --out out`) builds both reports from `testdata/fixture_engagement/`. Verified via direct run and via the Make target. |
| A2 | PASS | Two adapters demonstrated on fixtures: `JsonlEventAdapter` (`events_scanner.jsonl`, 6 events) + `CsvEventAdapter` (`alerts.csv`, 4 events). Plus a third CSV adapter for the decision log. |
| A3 | PASS | Correlation produces 8 timeline entries, 7 linked (≥5 required), confirmed by CLI output and `tests/test_correlate.py::test_at_least_five_linked_items`. |
| A4 | PASS | `out/client_report.md`/`.html` contain "Executive Summary", "Timeline", and "Detection Recommendations" sections; also "Findings" (placeholders) per R4. Verified by `tests/test_reports.py::test_client_report_has_required_sections`. |
| A5 | PASS | `out/internal_report.md`/`.html` contain "Successes" and "Failures" sections (plus "Tool Gaps" and "Reusable TTPs"). Verified by `tests/test_reports.py::test_internal_report_has_required_sections_and_keeps_detail`. |
| A6 | PASS | Planted secrets (password, AWS-style key, email, case tag) confirmed absent from `client_report.md`/`.html` via `grep` and `tests/test_reports.py::test_client_report_redacts_planted_secrets_in_both_renders`. |
| A7 | PASS | Internal report retains full rationale/detail (e.g. `password=Sp1cyTuna!2026` verbatim, unredacted) — confirmed via `grep` and a dedicated test. Documented in `README.md` ("Client vs. internal report") and called out inline at the top of `internal_report.md` and in `OPSEC_CARD.md`. |
| A8 | PASS | `OPSEC_CARD.md` present with a "Detection Recommendations" section containing 5 bullets (≥3 required), plus the required "How report mishandling becomes an OPSEC failure" narrative. |
| A9 | PASS | `AUTHORIZED_USE.md` present at workspace root; referenced prominently at the top of `README.md`. |
| A10 | PASS | Semgrep + ast-grep installed (via pipx; neither was preinstalled) and run via `make scan` / `scripts/run_scanners.sh`; raw JSON + text output archived to `../scanners/` (`semgrep_after_action.{json,txt}`, `ast_grep_after_action.{json,txt}`). Semgrep: 0 findings/0 errors across 32 files. ast-grep: 8 findings (all `print()` calls in `cli.py`'s status output, none in report/redaction code). |

## Manual fidelity

| ID | Result | Notes |
|----|--------|-------|
| M1 | PASS | Client report reads as professional/external-appropriate: exec summary, timeline framed as operator decisions + corroborating evidence, findings marked as drafts requiring operator narrative, explicit non-guarantee language in Detection Recommendations. Timeline "Rationale" column quotes operator decision-log text verbatim (redacted) for reconstruction purposes — reasonable for this kind of closeout doc, but a human reviewer may want to paraphrase before real client delivery. |
| M2 | PASS | Correlation window size (default 30 min, symmetric, overridable via `engagement.json` or `--window-minutes`) and join keys (normalized asset string, no hostname/IP resolution) documented in `docs/CORRELATION.md`. |
| M3 | PASS | Missing/invalid fields degrade gracefully: malformed JSONL line, invalid-JSON line, CSV row missing timestamp, decision row missing rationale (kept, warned), decision row missing decision text (skipped, warned) — all exercised by the fixture and covered by `tests/test_adapters.py`. Warnings surface in the internal report's "Data Quality / Ingest Warnings" table and are summarized (count only) in the client report. |

**Working implementation?** yes

**Minutes to pass/abandon:** ~30 min (RUN_LOG `time_start_iso` 2026-09-03T06:37:11Z to final verified `make build`/`make scan` pass, based on artifact `Generated:` timestamps observed during the session, e.g. ~07:03Z for the last rebuilt report). This is an approximate wall-clock estimate from in-session artifact timestamps, not authoritative session telemetry — cross-check against the transcript/RUN_LOG for the exact figure.
