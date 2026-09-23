 # After-Action Collector Build Plan

## Repository Layout

- `/src`
  - `/adapters`
    - `json_adapter.py`
    - `csv_adapter.py`
  - `/correlator`
    - `correlator.py`
  - `/reporter`
    - `markdown_reporter.py`
    - `pdf_reporter.py`
    - `html_reporter.py`
  - `/redactor`
    - `redactor.py`
  - `main.py`
- `/config`
  - `redaction_config.json`
- `/logs`
- `/reports`
- `/tests`
- `requirements.txt`
- `README.md`

## Work Packages

1. **WP1: Log Adapters**
   - Tasks: Implement JSON and CSV log adapters.
2. **WP2: Correlator**
   - Depends on: WP1
   - Tasks: Implement log correlation engine.
3. **WP3: Redactor**
   - Tasks: Implement PII/secret redaction pass.
4. **WP4: Markdown Reporter**
   - Depends on: WP2, WP3
   - Tasks: Implement Markdown report generation.
5. **WP5: PDF and HTML Reporters**
   - Depends on: WP4
   - Tasks: Implement PDF and HTML report generation.
6. **WP6: Main Application**
   - Depends on: WP1-WP5
   - Tasks: Implement main application logic.

## Interface Contracts

- `json_adapter.py` and `csv_adapter.py`:
  - `parse(log_file: str) -> List[LogEvent]`
- `correlator.py`:
  - `correlate(log_events: List[LogEvent], decisions: List[Decision]) -> List[CorrelatedEvent]`
- `redactor.py`:
  - `redact(data: str, config: RedactionConfig) -> str`
- `markdown_reporter.py`, `pdf_reporter.py`, and `html_reporter.py`:
  - `generate_report(correlated_events: List[CorrelatedEvent]) -> str`
- `main.py`:
  - `main(log_files: List[str], decision_log: str, output_format: str) -> None`

## Requirement Trace Matrix

| Requirement ID | Work Package |
|----------------|--------------|
| R1             | WP1           |
| R2             | WP3           |
| R3             | WP4, WP5      |
| R4             | N/A (Assumed offline compatibility) |
| R5             | N/A (Assumed log files are provided) |

## Test Plan

- **Automated Acceptance Tests:** Unit tests for each module.
- **Manual Acceptance Tests:** Visual inspection of generated reports.

## Out of Scope

- Live log shipping from production client networks during the study.
- Exact format specification for operator decision log, client-facing report, and internal learning summary.
- Detailed requirements for the PII/secret redaction pass.

## Assumptions

- Operator decision log format: CSV with columns for timestamp, decision, rationale, and related asset.
- PII/secret redaction pass configuration: JSON file with regex patterns for redaction.
- Client-facing report format: Standard format with sections for an executive summary, timeline, findings, and detection recommendations.
- Internal learning summary format: Format that highlights successes, failures, tool gaps, and reusable TTPs as references.