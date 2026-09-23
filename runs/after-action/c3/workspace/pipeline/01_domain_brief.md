# Domain Brief — After-Action Collector

## Goal restatement

Success is a deterministic, local closeout workflow: an authorized operator points a CLI or Make target at one engagement directory containing JSON Lines events, CSV events, and a structured decision log. The tool normalizes the records, correlates decisions to events by asset and a documented time window, warns rather than crashes on optional missing fields, and renders (1) a professional client Markdown plus HTML report and (2) a more detailed internal Markdown learning summary. The fixture must yield at least five linked timeline items, and every planted secret must be replaced before client content is written.

## Constraints and assumptions

- **Platform/language:** Assume Python 3.11+ on Linux/macOS and use only the standard library so the fixture can run offline without dependency installation. A portable `Makefile` may wrap the Python CLI.
- **Inputs:** UTF-8 text. JSON Lines is one valid JSON value per line and conventionally uses `.jsonl`; blank lines are not values ([JSON Lines](https://jsonlines.org/)). CSV follows the widely implemented header/record conventions documented in informational RFC 4180, while tolerant parsing and explicit validation handle real-world variation ([RFC 4180](https://www.rfc-editor.org/rfc/rfc4180.html)).
- **Canonical fields:** events need timestamp, asset, event type, and summary/details; decisions need timestamp, decision, rationale, and related asset. Missing non-key fields receive defaults and warnings. Missing/invalid timestamps or asset keys cannot correlate but should remain visible where safe.
- **Time:** Assume ISO 8601 timestamps. Naive timestamps are treated as UTC with a warning; output is normalized to UTC. Default correlation window: ±10 minutes, same normalized asset key.
- **Offline/air-gap:** No APIs, telemetry, remote templates, or live production log shipping. Reports and warnings are reproducible from the engagement pack alone.
- **Output boundary:** Client-facing data passes through configurable regex redaction before any client file is persisted. Internal output may retain operational detail; this difference must be explicit.
- **Scope:** Reports provide findings placeholders rather than automated operator grading or vulnerability conclusions.
- **Scanner evidence:** The build does not install scanners. Controlled post-run Semgrep and ast-grep outputs are archived at stable paths; availability/failure must be recorded honestly.

## Prior art and interfaces

- **JSON Lines:** A natural append/log interchange because records are independently parseable ([format definition](https://jsonlines.org/)).
- **CSV / `text/csv`:** Common tabular interchange with quoting rules and an optional header described by RFC 4180 ([RFC Editor](https://www.rfc-editor.org/info/rfc4180/)). Python's `csv.DictReader` exposes header-keyed records and avoids hand-rolled quoting logic ([Python `csv` documentation](https://docs.python.org/3/library/csv.html)).
- **Python CLI and serialization:** `argparse`, `json`, `csv`, `datetime`, `re`, `html`, and `pathlib` provide an offline standard-library implementation. Markdown is the canonical readable artifact; standalone escaped HTML satisfies the second client format without a PDF engine.
- **Correlation model:** A small normalized event/decision model with adapter provenance, stable IDs, UTC timestamps, exact normalized asset matching, and absolute time-distance comparison keeps joins explainable and testable.

## Risks

- Timestamp timezone ambiguity, clock drift, and malformed values can create false or missed links.
- Asset aliases (hostname versus IP, case, trailing dot) can defeat exact matching; conservative normalization avoids dangerous fuzzy joins but may miss valid matches.
- Multiple events within the window can over-associate one decision. Every match must expose why it linked and its time delta.
- Regex redaction can miss novel secret shapes or over-redact useful text. Configurable rules, safe defaults, and fixture assertions are required; logs/warnings must not echo secret values.
- HTML injection is possible unless all report-sourced content is escaped.
- Client/internal artifacts can be swapped, copied, or stored with weak permissions, turning closeout reporting into an OPSEC disclosure.
- Spreadsheet consumers may interpret cells as formulas; this tool reads CSV and does not export it, but untrusted input must remain inert text in reports.

## Open questions

No question blocks planning. Assumptions above fix the runtime, schemas, ±10-minute window, conservative asset matching, and Markdown/HTML choice. Operators can override the window and redaction configuration through documented CLI inputs without changing the core model.
