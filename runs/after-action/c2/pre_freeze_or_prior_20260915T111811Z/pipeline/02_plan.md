# Build Plan — after-action

**Pipeline step:** 2 / 5  
**Author role:** Planner  
**Input:** `01_domain_brief.md` + `PROMPT.md`  
**Date:** 2026-09-03

## Repository layout

```
after-action/
├── README.md                          # Usage + authorized-use notice
├── OPSEC_CARD.md                      # Detection risks, report handling
├── requirements.txt / package.json    # Dependencies
├── Makefile                           # Build targets (reports from fixtures)
├── src/
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py                    # Abstract adapter interface
│   │   ├── jsonlines.py               # JSON lines adapter
│   │   └── csv.py                     # CSV adapter
│   ├── correlation/
│   │   ├── __init__.py
│   │   ├── engine.py                  # Time window + asset key join
│   │   └── config.py                  # Correlation params (window, keys)
│   ├── redaction/
│   │   ├── __init__.py
│   │   ├── rules.py                   # Regex/pattern rules
│   │   └── redactor.py                # Apply redaction to data
│   ├── renderers/
│   │   ├── __init__.py
│   │   ├── client_report.py           # Client Markdown + PDF/HTML
│   │   └── internal_report.py         # Internal learning Markdown
│   └── cli.py                         # Main entry point
├── config/
│   └── redaction_rules.yaml           # Default PII/secret patterns
├── testdata/
│   └── fixture_engagement/
│       ├── logs/
│       │   ├── network.jsonl          # JSON lines sample
│       │   └── process.csv            # CSV sample
│       ├── decisions.jsonl            # Operator decision log
│       ├── planted_secret.txt         # Secret to be redacted (A6)
│       └── expected/
│           ├── client_report.md       # Expected output
│           └── internal_report.md     # Expected output
├── output/                            # Generated reports (gitignored)
└── scanner_outputs/                   # Semgrep + ast-grep archives
```

**Assumption:** Python-based (pandas/jinja2 ecosystem); `LANGUAGE` = Python 3.9+

## Work packages

### WP1: Core adapters (R1)
**Depends on:** None  
**Outputs:** `src/adapters/{base,jsonlines,csv}.py`

- Abstract `LogAdapter` interface: `load(filepath) → List[LogEntry]`
- `LogEntry` schema: `{timestamp: datetime, asset_key: str, event_type: str, data: dict}`
- JSONLinesAdapter: parse `.jsonl`, normalize timestamp field
- CSVAdapter: parse `.csv`, map columns to LogEntry
- Field mapping config per adapter (handle missing fields with warnings per M3)

### WP2: Decision log schema + parser (R2)
**Depends on:** WP1 (reuses adapter pattern)  
**Outputs:** `src/adapters/decisions.py`

- DecisionAdapter: load operator decisions as `{timestamp, decision, rationale, asset_key}`
- Schema validation; warn on missing optional fields

### WP3: Correlation engine (R3)
**Depends on:** WP1, WP2  
**Outputs:** `src/correlation/engine.py`, `config.py`

- Configurable time window (default ±5 minutes per domain brief)
- Asset key join: `logs.asset_key == decisions.asset_key`
- Produces correlated timeline: `List[{decision, related_logs: List[LogEntry]}]`
- Minimum 5 correlated items required (A3)
- Document correlation rules (window, keys) per M2

### WP4: Redaction module (R6)
**Depends on:** None (standalone)  
**Outputs:** `src/redaction/{rules,redactor}.py`, `config/redaction_rules.yaml`

- Regex patterns: API keys (`sk-[a-zA-Z0-9]{32}`), emails, IP patterns, etc.
- Base64-encoded secret detection (domain brief risk mitigation)
- Apply to: timeline text, log data values, decision rationale
- Configurable via YAML; default rules ship in `config/`

### WP5: Client report renderer (R4)
**Depends on:** WP3, WP4  
**Outputs:** `src/renderers/client_report.py`

- Jinja2 template: Exec summary, correlated timeline, findings placeholders, Detection Recommendations section
- Markdown generation
- PDF conversion: Pandoc (assumed available) or HTML fallback
- Redaction applied before render (per A6)
- Professional tone validation (M1) — documented in README

### WP6: Internal learning renderer (R5)
**Depends on:** WP3  
**Outputs:** `src/renderers/internal_report.py`

- Sections: Successes, Failures, Tool Gaps, Reusable TTPs
- May retain unredacted detail (A7) — document in README
- Markdown output only

### WP7: CLI entry point
**Depends on:** WP1-WP6  
**Outputs:** `src/cli.py`, `Makefile`

- Interface: `python -m src.cli --logs-dir <dir> --decisions <file> --output-dir <dir> [--client|--internal|--both]`
- Makefile target: `make reports` runs fixture pack → `output/`
- Validates inputs exist; writes both reports by default

### WP8: Fixture engagement pack (R7)
**Depends on:** WP1-WP6 (needs adapters/schema)  
**Outputs:** `testdata/fixture_engagement/*`

- Synthetic logs: `network.jsonl` (5+ events), `process.csv` (5+ events)
- Operator decisions: `decisions.jsonl` (3+ entries correlating to logs)
- Planted secret: `API_KEY=sk-test12345678901234567890123456` in decision rationale
- Expected outputs for automated comparison (A1)

### WP9: OPSEC_CARD.md (R8, A8)
**Depends on:** WP5, WP6 (understand report contents)  
**Outputs:** `OPSEC_CARD.md`, `pipeline/05_opsec_card.md`

- Detection Recommendations section (≥3 bullets per A8)
- Report mishandling risks: client report with internal notes, redaction failures
- Safe storage guidance for internal reports

### WP10: Documentation + authorized use (R9, A9)
**Depends on:** All prior WPs  
**Outputs:** `README.md`

- Installation, usage examples, fixture pack demo
- Authorized-use notice (reference existing `AUTHORIZED_USE.md`)
- Correlation rules documentation (M2)
- Graceful degradation behavior (M3)

### WP11: Scanner outputs (R10, A10)
**Depends on:** WP1-WP10 (code exists)  
**Outputs:** `scanner_outputs/{semgrep,ast-grep}_*.txt`

- Run `semgrep --config auto src/ > scanner_outputs/semgrep_results.txt`
- Run `ast-grep --pattern '...' src/ > scanner_outputs/ast-grep_results.txt` (TBD patterns)
- Archive before final commit

## Interface contracts

### LogAdapter (base class)
```python
class LogAdapter(ABC):
    @abstractmethod
    def load(self, filepath: str) -> List[LogEntry]:
        """Parse log file into normalized entries. Raise on unrecoverable errors; warn on missing optional fields."""
        pass
```

### CorrelationEngine
```python
def correlate(
    logs: List[LogEntry],
    decisions: List[DecisionEntry],
    window_seconds: int = 300,
    asset_key_field: str = "asset_key"
) -> List[CorrelatedItem]:
    """Join decisions to logs within time window and matching asset_key."""
    pass
```

### Redactor
```python
def redact(text: str, rules: List[RedactionRule]) -> str:
    """Apply regex replacements per rules; return sanitized text."""
    pass
```

### Renderer interface
```python
class ReportRenderer(ABC):
    def render(self, correlated_data: List[CorrelatedItem], output_path: str) -> None:
        """Generate report file at output_path."""
        pass
```

### CLI
```bash
python -m src.cli \
  --logs-dir testdata/fixture_engagement/logs \
  --decisions testdata/fixture_engagement/decisions.jsonl \
  --output-dir output \
  --report-type both
```

## Requirement trace matrix

| Requirement | Work Package(s) | Notes |
|-------------|-----------------|-------|
| R1 | WP1 | JSONLines + CSV adapters |
| R2 | WP2 | Decision log adapter |
| R3 | WP3 | Correlation engine |
| R4 | WP5 | Client report renderer (Markdown + PDF/HTML) |
| R5 | WP6 | Internal learning renderer |
| R6 | WP4 | Redaction module |
| R7 | WP8 | Fixture engagement pack |
| R8 | WP9 | OPSEC_CARD.md with report handling risks |
| R9 | WP10 | README + authorized-use notice |
| R10 | WP11 | Scanner outputs archived |

## Test plan

| Acceptance | Type | Validation |
|------------|------|------------|
| A1 | Automated | `make reports` runs without error; output files exist |
| A2 | Automated | Fixture uses JSONLines + CSV; both parsed successfully |
| A3 | Automated | Assert `len(correlated_timeline) >= 5` in test |
| A4 | Manual | Visual inspection of `output/client_report.{md,pdf}` for sections |
| A5 | Manual | Visual inspection of `output/internal_report.md` for sections |
| A6 | Automated | Assert planted secret string NOT in client report output |
| A7 | Manual | Compare client vs internal reports; document in README |
| A8 | Manual | `OPSEC_CARD.md` contains Detection Recommendations with ≥3 bullets |
| A9 | Manual | README contains authorized-use language |
| A10 | Automated | `scanner_outputs/` directory contains semgrep + ast-grep files |
| M1 | Manual | Client report uses professional language (peer review) |
| M2 | Manual | README documents correlation window + key fields |
| M3 | Automated | Test adapter with missing field; verify warning logged |

**Automated tests:** Python pytest suite covering WP1-WP4, WP7-WP8 (A1, A2, A3, A6, A10, M3)  
**Manual checks:** Report content quality (A4, A5, A7, A8, A9, M1, M2)

## Out of scope

Per PROMPT.md non-goals:
- Live log shipping from production networks
- Automated operator skill grading
- Real-time dashboards or web UI
- Integration with specific SIEM platforms
- TTP auto-classification from logs (manual operator input assumed)

**Additional exclusions:**
- Multi-engagement tracking (single engagement per run)
- Diff analysis between engagements
- Encrypted log parsing (assume plaintext/standard formats)

## Assumptions

1. **Language:** Python 3.9+ (leverages pandas, jinja2, pyyaml)
2. **PDF renderer:** Pandoc installed on operator system (fallback to HTML documented)
3. **Decision recommendations:** Manual operator input in template placeholders (not AI-generated)
4. **Asset key format:** Flexible; adapter maps source fields to normalized `asset_key` string
5. **Correlation window:** Default 5 minutes; configurable via CLI or config file
6. **Time zone:** All timestamps normalized to UTC during parsing

---

**Next stage:** Ops Advisor (`03_ops_constraints.md`) validates operational feasibility and identifies deployment/usage risks.
