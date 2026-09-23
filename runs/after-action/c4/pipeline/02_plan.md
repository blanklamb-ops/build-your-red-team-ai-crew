 # Plan for After-Action Collector

## Repository Layout

- `src/`
  - `adapters/`
    - `json_adapter.py`
    - `csv_adapter.py`
  - `correlator.py`
  - `renderers/`
    - `client_report_renderer.py`
    - `learning_summary_renderer.py`
  - `main.py`
- `tests/`
  - `test_adapters.py`
  - `test_correlator.py`
  - `test_renderers.py`
- `docs/`
  - `log_formats.md`
  - `operator_decision_log_format.md`
- `reports/`
- `README.md`
- `requirements.txt`

## Work Packages

1. **WP1: Log Ingestion Adapters**
   - Dependencies: None
2. **WP2: Correlation Engine**
   - Dependencies: WP1
3. **WP3: Client Report Renderer**
   - Dependencies: WP2
4. **WP4: Internal Learning Summary Renderer**
   - Dependencies: WP2
5. **WP5: Main Module**
   - Dependencies: WP1, WP2, WP3, WP4

## Interface Contracts

- `adapters/json_adapter.py` and `adapters/csv_adapter.py`:
  - `ingest(log_path: str) -> List[LogEvent]`
- `correlator.py`:
  - `correlate(log_events: List[LogEvent], decision_logs: List[DecisionLog]) -> List[CorrelatedEvent]`
- `renderers/client_report_renderer.py` and `renderers/learning_summary_renderer.py`:
  - `render(correlated_events: List[CorrelatedEvent]) -> str`
- `main.py`:
  - `main(log_paths: List[str], decision_log_path: str, output_dir: str)`

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PR1                  | WP1          |
| PR2                  | WP1          |
| PR3                  | WP1          |
| PR4                  | WP2          |
| PR5                  | WP3          |
| PR6                  | WP4          |
| PR7                  | WP5          |
| PR8                  | WP5          |

## Test Plan

- `test_adapters.py`: Automated tests for log ingestion adapters
- `test_correlator.py`: Automated tests for correlation engine
- `test_renderers.py`: Automated tests for report renderers
- Manual testing for offline/air-gap needs and OPSEC card

## Out of Scope

- Live log shipping from production client networks during the study
- Detailed specification of log formats and operator decision log format
- Specific requirements for client report renderer and internal learning summary renderer
- Correlation engine's time window and asset key definition

## Assumptions

- The specific log formats and operator decision log format are known and documented.
- The correlation engine's time window is 5 minutes and the asset key is unique.
- The client report renderer should be professional and non-jargony, and the internal learning summary renderer should be structured.