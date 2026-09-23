# Domain Brief — after-action

## Goal restatement

Success is a repeatable, offline closeout workflow: an operator points a CLI at an engagement directory containing JSON Lines events, CSV events, and a structured decision log; the tool normalizes and correlates them by asset and time; then it emits a redacted, professional client report and a more detailed internal learning report. The fixture engagement must yield at least five decision-linked timeline entries, and a planted secret must never appear in the client export.

## Constraints and assumptions

- **ASSUMPTION — platform:** Python 3.10+ on Linux/macOS, using only the standard library so an air-gapped lab can run it without package installation. No elevated privileges or network access are needed.
- **Inputs:** UTF-8 local files. JSON Lines is one valid JSON value per line and is suited to record-at-a-time processing ([JSON Lines documentation](https://jsonlines.org/)). CSV handling should follow the broadly used record/header and quoting conventions documented by [RFC 4180](https://www.rfc-editor.org/info/rfc4180/), while accepting normal line-ending variation.
- **Canonical time:** ISO 8601 timestamps with timezone offsets; timestamps without an offset are invalid records and produce warnings rather than guessed times.
- **Correlation:** exact normalized asset-key equality plus an inclusive, configurable absolute time window. One event may link to its nearest qualifying decision; stable tie-breaking makes renders reproducible.
- **Outputs:** Markdown plus self-contained HTML satisfies R4 without a PDF toolchain. Client redaction happens before client content is assembled or written. Internal output may preserve authorized operational detail and must be protected accordingly.
- **Configuration:** a local JSON configuration defines the window and ordered regex redaction rules. Inputs remain read-only; outputs go to an explicit directory.

## Prior art and interfaces

- **JSON Lines** provides a simple streaming interchange format for heterogeneous events and requires UTF-8, one JSON value per line ([format documentation](https://jsonlines.org/)).
- **CSV / `text/csv`** is a ubiquitous tabular exchange interface. RFC 4180 documents headers, one record per line, quoting, and embedded comma/newline behavior ([RFC 4180](https://www.rfc-editor.org/rfc/rfc4180.html)). Python's standard [`csv` module](https://docs.python.org/3/library/csv.html) supplies dialect-aware readers and dictionary rows, avoiding unsafe ad-hoc splitting.
- **OWASP Logging Cheat Sheet** identifies access tokens, passwords, connection strings, encryption keys, session identifiers, and sensitive PII as data that should usually be removed, masked, hashed, or encrypted; it also recommends restricted access and retention-aware disposal ([OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)). This informs default redaction and handling guidance, not automated compliance claims.
- **Markdown and self-contained HTML** are portable handoff formats readable without a report server. No external renderer or hosted API is required.

## Risks

- Timestamp parse errors, timezone ambiguity, clock skew, or a poorly chosen window can cause false or missed joins.
- Asset aliases (`host-a`, FQDN, IP) will not correlate under exact-key matching unless inputs are normalized beforehand; fuzzy matching would risk misleading reports.
- Malformed rows or missing fields can silently bias findings unless every skipped/defaulted row generates a visible warning.
- Regex-only redaction cannot recognize every secret or contextual PII. Misconfigured rules, encoded secrets, split tokens, and generated prose can leak data.
- Rendering untrusted event text into HTML creates injection risk unless values are escaped. Spreadsheet formula prefixes in CSV are data on ingest but become risky if later opened in spreadsheet software.
- Client/internal report confusion, permissive output permissions, copied working files, terminal history, scanner logs, and backups can expose engagement data.
- Determinism can be lost through locale-dependent dates, input enumeration, or unstable tie-breaking.

## Open questions resolved for planning

No blocking questions remain. **ASSUMPTION:** decisions use JSON Lines with required `timestamp`, `decision`, `rationale`, and `asset` fields. **ASSUMPTION:** malformed individual records warn and are skipped; missing optional fields render as `Unknown`; an unreadable required file is a fatal error. **ASSUMPTION:** the default correlation window is 10 minutes and can be changed in configuration. **ASSUMPTION:** scanner binaries may be absent in the controlled environment; the build must execute each when present and always archive command/version/status output without installing replacements.
