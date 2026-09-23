 # After-Action Collector Build Plan

## Repository Layout

```
/
├── src/
│   ├── ingest/
│   │   ├── json_ingest.py
│   │   └── csv_ingest.py
│   ├── correlation/
│   │   └── correlate.py
│   ├── report/
│   │   ├── client_report.py
│   │   └── internal_report.py
│   ├── utils/
│   │   ├── pii_redaction.py
│   │   └── render.py
│   └── main.py
├── testdata/
│   ├── sample_logs/
│   │   ├── json_logs/
│   │   └── csv_logs/
│   ├── operator_decisions.json
│   └── pii_redaction_rules.json
├── OPSEC_CARD.md
├── README.md
├── AUTHORIZED_USE.md
└── requirements.txt
```

## Work Packages

1. **WP1: Log Ingestion**
   - WP1.1: Implement JSON log ingestion (`src/ingest/json_ingest.py`)
   - WP1.2: Implement CSV log ingestion (`src/ingest/csv_ingest.py`)
2. **WP2: Event Correlation**
   - WP2.1: Implement event correlation based on time window and asset key (`src/correlation/correlate.py`)
3. **WP3: Report Generation**
   - WP3.1: Implement client report generation in Markdown and PDF/HTML (`src/report/client_report.py`)
   - WP3.2: Implement internal learning summary generation (`src/report/internal_report.py`)
4. **WP4: Utilities**
   - WP4.1: Implement PII/secret redaction (`src/utils/pii_redaction.py`)
   - WP4.2: Implement report rendering (`src/utils/render.py`)
5. **WP5: Main Application**
   - WP5.1: Implement main application (`src/main.py`)
6. **WP6: Documentation**
   - WP6.1: Create fixture engagement pack under `testdata/`
   - WP6.2: Create `OPSEC_CARD.md`
   - WP6.3: Create `README.md`
   - WP6.4: Create `AUTHORIZED_USE.md`

## Interface Contracts

- `src/ingest/json_ingest.py` and `src/ingest/csv_ingest.py` will have a function `ingest(file_path)` that takes a file path as input and returns a list of ingested events.
- `src/correlation/correlate.py` will have a function `correlate(events, decisions)` that takes a list of events and a list of decisions as input and returns a list of correlated events.
- `src/report/client_report.py` and `src/report/internal_report.py` will have a function `generate_report(correlated_events)` that takes a list of correlated events as input and returns a report object.
- `src/utils/pii_redaction.py` will have a function `redact(report, rules)` that takes a report object and a list of redaction rules as input and returns a redacted report object.
- `src/utils/render.py` will have a function `render(report, format)` that takes a report object and a format as input and returns a rendered report in the specified format.
- `src/main.py` will have a function `main()` that orchestrates the entire process.

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PR-01                 | WP1.1, WP1.2  |
| PR-02                 | WP1.1, WP1.2  |
| PR-03                 | WP1          |
| PR-04                 | WP2          |
| PR-05                 | WP3.1        |
| PR-06                 | WP3.2        |
| PR-07                 | WP4.1        |
| PR-08                 | WP3.1, WP4.2  |
| PR-09                 | WP6.1        |
| PR-10                 | WP6.2        |
| PR-11                 | WP6.3, WP6.4  |

## Test Plan

- All work packages will be unit tested.
- The fixture engagement pack will be used to test the end-to-end functionality.
- The test plan will include automated tests for the ingestion, correlation, report generation, and redaction modules.
- The test plan will include manual tests for the rendering module.

## Out of Scope

- Real-time log shipping during the study (PR-12)
- Automated grading of operator skill (PR-13)

## Assumptions

- The operator decision log will be in JSON format.
- The PII/secret redaction rules will be in JSON format.
- The tool will handle large volumes of log data by processing the data in chunks.
- The expected format of the operator decision log and the PII/secret redaction rules is subject to further clarification.