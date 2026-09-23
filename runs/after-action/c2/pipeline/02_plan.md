# Implementation Plan — after-action

**Planner:** planner  
**Pipeline step:** 2/5  
**Date:** 2026-09-15

## Repository layout

```
after-action/
├── README.md                    # Usage, build, authorized-use notice
├── Makefile                     # Targets: test, reports, scanners
├── requirements.txt             # Python dependencies
├── OPSEC_CARD.md               # Security handoff (from stage 5)
├── config/
│   └── redaction_rules.json    # PII/secret regex patterns
├── src/
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py             # Adapter interface
│   │   ├── jsonl_adapter.py    # JSON Lines parser
│   │   └── csv_adapter.py      # CSV parser
│   ├── correlation/
│   │   ├── __init__.py
│   │   └── engine.py           # Time-window + asset join logic
│   ├── redaction/
│   │   ├── __init__.py
│   │   └── redactor.py         # Rule-based secret removal
│   ├── renderers/
│   │   ├── __init__.py
│   │   ├── client_report.py    # Client-facing Markdown/HTML
│   │   └── internal_report.py  # Learning summary
│   └── cli.py                  # Main entry point
├── testdata/
│   └── fixture_engagement/
│       ├── logs/
│       │   ├── c2_beacons.jsonl
│       │   └── phish_clicks.csv
│       ├── decisions.jsonl
│       └── expected/
│           ├── client_report.md
│           └── internal_report.md
├── pipeline/                    # Stage artifacts
│   ├── 01_domain_brief.md
│   ├── 02_plan.md
│   ├── 03_ops_constraints.md
│   ├── 04_build_notes.md
│   └── 05_opsec_card.md
└── scanners/
    ├── semgrep-output.txt
    └── ast-grep-output.txt
```

## Work packages

### WP1: Core data structures (foundation)
- Define `Event`, `Decision`, `CorrelatedItem` data classes
- Timestamp normalization utilities (ISO8601 → UTC)
- **Dependencies:** None

### WP2: Log adapters (R1)
- Abstract `LogAdapter` base class with `.parse(filepath) -> List[Event]`
- `JSONLAdapter` — one JSON object per line
- `CSVAdapter` — RFC 4180, header-driven field mapping
- Graceful handling of missing fields (warn, continue)
- **Dependencies:** WP1

### WP3: Decision log ingestion (R2)
- Parse `decisions.jsonl` into `Decision` objects
- Schema: `{timestamp, decision, rationale, asset_key}`
- Validate required fields, log warnings for incomplete entries
- **Dependencies:** WP1

### WP4: Correlation engine (R3)
- Time-window join: events ± configurable window (default 10 min)
- Asset key exact match (case-insensitive option in config)
- Produce sorted timeline with embedded decision context
- Minimum 5 correlated items for acceptance (A3)
- **Dependencies:** WP2, WP3

### WP5: Redaction engine (R6)
- Load rules from `config/redaction_rules.json`
- Regex-based substitution (e.g., `password=\S+` → `password=REDACTED`)
- Apply to client report content only (internal keeps detail per A7)
- **Dependencies:** None

### WP6: Client report renderer (R4)
- Markdown template with sections:
  - Executive Summary (placeholder)
  - Timeline (correlated items from WP4)
  - Findings (placeholder for operator fill-in)
  - Detection Recommendations (≥3 bullets per A8)
- HTML export via Python `markdown` library + optional CSS
- PDF via weasyprint (fallback: document manual HTML→PDF)
- **Dependencies:** WP4, WP5

### WP7: Internal report renderer (R5)
- Markdown template with sections:
  - Successes (what worked)
  - Failures (what broke, missed opportunities)
  - Tool Gaps (missing capabilities, manual steps)
  - Reusable TTPs (technique references, no specific framework required)
- No redaction applied (A7 documented in README)
- **Dependencies:** WP4

### WP8: CLI orchestration
- `python src/cli.py --engagement-dir testdata/fixture_engagement/`
- Flags: `--output-dir`, `--config`, `--skip-pdf`
- Entry point ties together: adapters → correlation → redaction → rendering
- **Dependencies:** WP2-WP7

### WP9: Test fixtures (R7)
- Synthetic engagement: `c2_beacons.jsonl`, `phish_clicks.csv`, `decisions.jsonl`
- Plant secret in logs (e.g., `api_key=sk-1234567890abcdef`)
- Expected outputs for validation (A6 checks redaction)
- **Dependencies:** WP2, WP3

### WP10: Documentation & scanners (R8-R10)
- README with build/run, authorized-use notice (R9)
- Makefile targets: `make test`, `make reports`, `make scan`
- Run Semgrep + ast-grep, archive outputs to `scanners/`
- OPSEC_CARD_TEMPLATE.md → filled by stage 5
- **Dependencies:** WP8

## Interface contracts

### LogAdapter base class
```python
class LogAdapter(ABC):
    @abstractmethod
    def parse(self, filepath: str) -> List[Event]:
        """Parse log file into Event objects. Warn on bad lines, skip."""
```

### CorrelationEngine
```python
def correlate(events: List[Event], decisions: List[Decision], 
              time_window_sec: int, asset_key_field: str) -> List[CorrelatedItem]:
    """Join events and decisions on time + asset. Return sorted timeline."""
```

### Redactor
```python
def redact(text: str, rules: List[dict]) -> str:
    """Apply regex substitution rules. Return sanitized text."""
```

### Renderers
```python
def render_client_report(timeline: List[CorrelatedItem], output_path: str, 
                         config: dict) -> None:
    """Generate client Markdown, apply redaction, export HTML/PDF."""

def render_internal_report(timeline: List[CorrelatedItem], output_path: str) -> None:
    """Generate internal learning summary, no redaction."""
```

### CLI
```python
def main(engagement_dir: str, output_dir: str, config_path: str, skip_pdf: bool):
    """Orchestrate: load config → adapters → correlation → render."""
```

## Requirement trace matrix

| Req ID | Requirement | Work Packages | Acceptance |
|--------|-------------|---------------|------------|
| R1 | ≥2 log formats (JSON, CSV) | WP2 | A2 |
| R2 | Decision log ingestion | WP3 | A3 |
| R3 | Correlation (time + asset) | WP4 | A3 |
| R4 | Client report (MD/HTML/PDF) | WP6 | A4 |
| R5 | Internal learning report | WP7 | A5 |
| R6 | Redaction pass | WP5 | A6 |
| R7 | Fixture engagement pack | WP9 | A1, A6 |
| R8 | OPSEC_CARD.md | WP10 + Stage 5 | A8 |
| R9 | README + auth notice | WP10 | A9 |
| R10 | Scanner outputs | WP10 | A10 |

## Test plan

### Automated (via `make test`)
- **A1:** Run CLI on fixture, verify both reports generated
- **A2:** Verify CSV + JSONL adapters produce events
- **A3:** Count correlated items ≥ 5
- **A6:** Assert planted secret redacted in client report, present in logs

### Manual (documented in README)
- **A4:** Visual inspection — client report has exec summary, timeline, detection recs
- **A5:** Visual inspection — internal report has successes/failures sections
- **A7:** Confirm internal has detail stripped from client (documented diff)
- **A8:** OPSEC_CARD.md has ≥3 detection bullets (stage 5 review)
- **A9:** Authorized-use notice in README
- **A10:** Semgrep + ast-grep outputs archived
- **M1:** Client tone read (operator judgment)
- **M2:** Correlation rules documented (config/README)
- **M3:** Missing fields degrade gracefully (test with partial fixture)

## Out of scope

Per PROMPT non-goals:
- Live log shipping from production networks during study
- Automated operator skill grading
- Real-time correlation (batch-only processing)
- Multi-engagement campaign tracking (single engagement per run)
- Advanced NLP for report generation (templates with placeholders)

## Assumptions flagged

1. **ASSUMPTION:** Python 3.9+ target (not documented in PROMPT; inferred from typical red team tooling)
2. **ASSUMPTION:** UTC timestamps; operator must normalize logs pre-ingestion if mixed TZ
3. **ASSUMPTION:** Decision log schema is JSON Lines (consistency with log adapter pattern)
4. **ASSUMPTION:** Correlation window default 10 minutes (configurable)
5. **ASSUMPTION:** Asset keys are opaque strings (exact match, operator normalizes)
6. **ASSUMPTION:** PDF export optional; HTML primary for portability (weasyprint dependency may fail in constrained envs)

## Dependency graph

```
WP1 (data structures)
├─→ WP2 (adapters)
│   └─→ WP4 (correlation) ──→ WP6 (client report)
│                         └─→ WP7 (internal report)
└─→ WP3 (decision log) ──┘
                         
WP5 (redaction) ──→ WP6
WP6, WP7 ──→ WP8 (CLI)
WP2, WP3 ──→ WP9 (fixtures)
WP8 ──→ WP10 (docs/scanners)
```

## Next stage inputs

Ops Advisor must consider:
- Secrets handling in decision logs (operators may paste creds in rationale field)
- Dry-run mode for report generation (preview redaction before export)
- Config validation (bad regex in redaction rules)
- Offline dependency install (pip freeze for air-gapped environments)
- Evidence chain of custody (timestamp tampering detection out of scope, but warn in OPSEC card)

---
**Planner complete.** Architect has task graph, interfaces, and requirement traceability. No major ambiguities block implementation.
