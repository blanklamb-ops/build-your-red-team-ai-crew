 # After-Action Collector Build Plan

## Repository Layout

```
/after-action-collector
    /src
        /ingest
            ingest.py
            json_ingest.py
            csv_ingest.py
        /correlate
            correlate.py
        /report
            report.py
            markdown_report.py
            pdf_report.py
        /utils
            utils.py
    /tests
        /unit
        /integration
        /acceptance
    /docs
    /reports
    requirements.txt
    README.md
```

## Work Packages

1. **WP1: Ingestion Module**
   - WP1.1: JSON Ingestion (json_ingest.py)
   - WP1.2: CSV Ingestion (csv_ingest.py)
   - Depends on: WP4
2. **WP2: Correlation Module**
   - WP2.1: Event-Decision Correlation (correlate.py)
   - Depends on: WP1
3. **WP3: Reporting Module**
   - WP3.1: Markdown Reporting (markdown_report.py)
   - WP3.2: PDF Reporting (pdf_report.py)
   - Depends on: WP2, WP5
4. **WP4: Utilities Module**
   - WP4.1: Data Validation (utils.py)
   - WP4.2: PII/Secrets Redaction (utils.py)
   - Depends on: None
5. **WP5: Operator Decision Capture Module**
   - WP5.1: Decision Logging Mechanism (decision_log.py)
   - Depends on: None

## Interface Contracts

- `ingest.py`: `ingest(file_path: str) -> DataFrame`
- `correlate.py`: `correlate(data: DataFrame, decisions: DataFrame, time_window: int, asset_key: str) -> DataFrame`
- `report.py`: `generate_report(data: DataFrame, format: str) -> str`
- `utils.py`: `validate_data(data: DataFrame) -> DataFrame`, `redact_data(data: DataFrame) -> DataFrame`
- `decision_log.py`: `log_decision(decision: dict) -> None`

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PROMPT-1             | WP1           |
| PROMPT-2             | WP1, WP4      |
| PROMPT-3             | WP1           |
| PROMPT-4             | WP2           |
| PROMPT-5             | WP3, WP4      |
| PROMPT-6             | WP3           |
| PROMPT-7             | WP5           |
| PROMPT-8 (Assumption)| WP1           |
| PROMPT-9 (Assumption)| WP4           |
| PROMPT-10 (Assumption)| WP5           |

## Test Plan

- Unit tests: WP1, WP2, WP3, WP4, WP5
- Integration tests: WP1-WP3, WP1-WP4, WP2-WP3, WP2-WP4, WP3-WP4, WP3-WP5
- Acceptance tests: PROMPT-1 to PROMPT-7

## Out of Scope

- Real-time data processing
- Multi-threading/parallel processing
- GUI/web interface
- Cloud integration
- Containerization/orchestration
- CI/CD pipeline
- Version control (assumed to be handled externally)