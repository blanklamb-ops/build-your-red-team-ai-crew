 # After-Action Collector Build Plan

## Repository Layout

```
/after-action-collector
    /ingestion
        log_parser.py
        decision_log_parser.py
    /correlation
        correlation_engine.py
    /reporting
        client_report.py
        internal_report.py
    /utils
        renderer.py
        redaction.py
    /tests
        test_ingestion.py
        test_correlation.py
        test_reporting.py
    /docs
        README.md
        ASSUMPTIONS.md
    requirements.txt
    main.py
```

## Work Packages

1. WP1: Log Ingestion
   - Depends on: None
   - Tasks: Implement log parsers for two log formats and operator decision logs.
2. WP2: Event Correlation
   - Depends on: WP1
   - Tasks: Implement a correlation engine to correlate events with decisions.
3. WP3: Client Reporting
   - Depends on: WP2
   - Tasks: Implement a client-facing report generator with executive summary, timeline, findings placeholders, and detection recommendations.
4. WP4: Internal Learning Summary
   - Depends on: WP2
   - Tasks: Implement an internal learning summary generator highlighting successes, failures, tool gaps, and reusable TTPs.
5. WP5: Utilities
   - Depends on: None
   - Tasks: Implement a rendering utility for Markdown/HTML and a redaction utility for PII/secret redaction.
6. WP6: Testing
   - Depends on: WP1-WP5
   - Tasks: Implement automated tests for ingestion, correlation, and reporting.

## Interface Contracts

- `log_parser.py`: `parse(log_file_path)`
- `decision_log_parser.py`: `parse(decision_log_file_path)`
- `correlation_engine.py`: `correlate(events, decisions)`
- `client_report.py`: `generate(correlated_data)`
- `internal_report.py`: `generate(correlated_data)`
- `renderer.py`: `render(data, format)`
- `redaction.py`: `redact(data, rules)`

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PROMPT-1.1           | WP1, WP3     |
| PROMPT-1.2           | WP2, WP3, WP4 |
| PROMPT-1.3           | WP3, WP4     |
| PROMPT-2.1           | WP1-WP6      |
| PROMPT-2.2           | WP6          |
| PROMPT-3.1           | WP5          |
| PROMPT-3.2           | WP5          |

## Test Plan

- Automated tests: Ingestion, correlation, and reporting.
- Manual tests: PII/secret redaction, operator decision log format, tool architecture and data flow.

## Out of Scope

- Real-time log analysis and visualization.
- Live log shipping during the study.
- Specific log formats other than the two mentioned and operator decision logs.
- Operator decision log format validation.
- Tool architecture and data flow design.