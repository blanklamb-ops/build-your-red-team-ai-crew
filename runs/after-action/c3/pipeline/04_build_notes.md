# Build Notes — After-Action Collector

## Delivered

- Python 3.11+ standard-library package with JSONL and CSV event adapters, CSV decision ingestion, normalized/provenanced records, sanitized warnings, and input limits.
- Explainable inclusive time-window plus exact normalized-asset correlation. Results preserve linked and unlinked records, signed/absolute deltas, and deterministic ordering.
- Configurable ordered regex redaction with fixed labels. Client Markdown is fully redacted in memory; standalone HTML is created only from that redacted value and HTML-escaped. Internal Markdown intentionally retains more operational detail.
- CLI with required output path, finite positive window validation, fixed named inputs, input/output collision refusal, and atomic `0600` report writes.
- Synthetic fixture containing six valid events across both adapters, six decisions, eight links, actual findings, three client detection recommendations, multiple secret types, one malformed row, one naive timestamp, and one missing optional field.
- Unit/integration tests, executable acceptance script and Make targets, README, authorized-use notice, local scanner rules/archive script, and archived scanner results.

## Verification performed

- `python3 -m unittest discover -s tests -v`: **7 tests passed**. Coverage includes the fixture, client secret absence, restrictive permissions, HTML/Markdown inertness, correlation boundaries/no-match behavior, naive timestamps, malformed/missing fields, invalid regex/window, and directory collision.
- `make fixture`: **success**; rendered `client_report.md`, `client_report.html`, and `internal_learning.md` from six events and six decisions with eight correlated pairs and three expected sanitized warnings.
- Direct planted-value search of both client artifacts: **no matches**. Internal report retains the fixture canary as documented.
- `python3 -m compileall -q after_action scripts tests`: **success**.
- Semgrep archive (`scanner-output/semgrep.txt`): executed offline with local rules, metrics/version checks disabled, seven Python targets scanned, zero findings, exit 0.
- ast-grep archive (`scanner-output/ast-grep.txt`): executed a Python dynamic-`eval` pattern scan; no matches, tool exit 1 (its no-match result), archived explicitly.

Run scanner archival with `make scanners`. The script installs or substitutes nothing and writes an honest `NOT_AVAILABLE` status when a named executable is absent. Run the registered checks with `make acceptance` after Role 5 creates the OPSEC card.

## Deviations from plan

- The internal detailed correlation table combines event summary and details so the richer internal/client handling distinction is visible and automatically testable.
- Scanner-local settings/log paths are placed in `scanner-output/` because the controlled environment's home configuration/cache paths are read-only. This changes no scanner implementation or rules.
- Serena was not exposed in this environment, so it was not used for navigation or editing.

## Known gaps and residual considerations

- No required feature is unimplemented. Regex redaction remains inherently incomplete for unknown secret/PII formats and therefore requires human review.
- Exact asset matching intentionally misses undocumented aliases; no fuzzy/DNS resolution is attempted.
- The client HTML is a dependency-free, escaped presentation of the Markdown report rather than a semantic Markdown conversion. It is readable, printable, offline, and script-free.
- Scanner archives attest to the commands and results available in this run; they are not a general security guarantee.
