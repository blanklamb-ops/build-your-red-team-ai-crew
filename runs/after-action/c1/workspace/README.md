# after-action — Post-Engagement Report Generator

**Authorized use only** — Security testing, research, and education purposes.

## Overview

The `after-action` tool correlates engagement logs and operator decisions into professional reports for security assessments. It generates:

1. **Client-facing report** — Professional, non-technical where possible, with executive summary, timeline, and Detection Recommendations
2. **Internal learning report** — What worked, what failed, tool gaps, and reusable TTPs

## Features

- **Multi-format log ingestion** — Adapters for JSON Lines, CSV, and custom decision logs
- **Event-Decision correlation** — Joins events with operator decisions using configurable time windows and asset matching
- **Automated redaction** — Strips PII, credentials, and secrets before client export
- **Structured outputs** — Markdown reports ready for review and PDF conversion
- **Reproducible** — Runs on fixture data for validation and testing

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only)

## Installation

```bash
# Clone or extract the tool
cd after-action

# Make executable
chmod +x after_action.py
```

## Usage

### Basic Report Generation

```bash
./after_action.py testdata/fixture_engagement/
```

This reads all logs from the specified directory and generates reports in `./output/`:
- `client_report.md` — Redacted, client-facing report
- `internal_report.md` — Full internal learning report
- `metadata.json` — Report generation metadata

### Custom Output Directory

```bash
./after_action.py testdata/fixture_engagement/ -o my_reports/
```

### Custom Redaction Rules

Create a `redaction_config.json`:

```json
{
  "additional_rules": [
    {
      "pattern": "CompanyName",
      "replacement": "[REDACTED_ORG]"
    },
    {
      "pattern": "\\d{3}-\\d{2}-\\d{4}",
      "replacement": "[REDACTED_SSN]"
    }
  ]
}
```

Then run:

```bash
./after_action.py testdata/fixture_engagement/ -c redaction_config.json
```

## Log Format Requirements

### Event Logs

**JSON Lines (.jsonl):**
```json
{"timestamp": "2026-09-01T10:15:00Z", "asset": "target-host", "action": "port_scan", "details": "..."}
```

**CSV:**
```csv
timestamp,asset,action,details
2026-09-01 10:15:00,target-host,port_scan,Scanned ports 1-1000
```

Required fields:
- `timestamp` — ISO format or parseable datetime
- `asset` — Target system/host identifier
- `action` — Activity type

Optional fields:
- `details` — Additional context
- `protocol` — Network protocol used
- Any other custom fields

### Decision Logs

JSON Lines format with operator decisions:

```json
{"timestamp": "2026-09-01T10:14:00Z", "decision": "Begin recon", "rationale": "Client authorized", "asset": "target-host", "tags": ["recon"], "outcome": "success"}
```

Required fields:
- `timestamp`
- `decision` — What the operator decided
- `rationale` — Why the decision was made
- `asset` — Related target (for correlation)

Optional fields:
- `tags` — Categories (e.g., "recon", "exploit")
- `outcome` — Result (e.g., "success", "failed", "blocked")

## Correlation Rules

The correlation engine joins events with decisions based on:

1. **Time window** — Events within ±5 minutes (300 seconds) of decision timestamp
2. **Asset matching** — Asset identifiers must match or contain each other
3. **Closest match** — When multiple decisions match, selects the one closest in time

These parameters are configurable in `correlate.py`:

```python
correlation = CorrelationEngine(
    time_window_seconds=300,  # 5 minutes
    asset_match=True          # Require asset match
)
```

Missing fields degrade gracefully with warnings logged to console.

## Redaction Rules

Default redaction patterns:
- API keys (OpenAI, GitHub, AWS, etc.)
- Passwords and secrets
- Email addresses
- Private IP addresses
- SSH private keys
- Generic secret/token patterns

See `redaction.py` for full list and customization options.

## Testing

Run the acceptance test suite:

```bash
make test
```

Or manually:

```bash
./after_action.py testdata/fixture_engagement/ -o output/
# Verify output files exist and planted secrets are redacted
grep -i "sk-proj-" output/client_report.md  # Should return nothing
grep -i "redacted" output/client_report.md  # Should find redactions
```

## Project Structure

```
after-action/
├── after_action.py          # Main CLI tool
├── adapters/                # Log format adapters
│   ├── __init__.py
│   ├── jsonlines_adapter.py
│   ├── csv_adapter.py
│   └── decision_adapter.py
├── renderers/               # Report renderers
│   ├── __init__.py
│   ├── client_renderer.py
│   └── internal_renderer.py
├── correlate.py             # Event-decision correlation
├── redaction.py             # PII/secret redaction
├── testdata/                # Test fixtures
│   └── fixture_engagement/
│       ├── events.jsonl
│       ├── network_activity.csv
│       └── operator_decisions.jsonl
├── README.md
├── OPSEC_CARD.md
├── AUTHORIZED_USE.md
└── Makefile
```

## OPSEC Considerations

See `OPSEC_CARD.md` for:
- Operator risks when generating reports
- Artifacts and residual data
- Safe handling guidance
- Detection recommendations for clients

**Critical:** Reports may contain sensitive engagement data. Handle as confidential client material. Verify redaction before external distribution.

## Authorized Use

This tool is designed for:
- Authorized penetration testing engagements
- Red team exercises with written authorization
- Security research in controlled environments
- Educational demonstrations

**Do NOT use** on unauthorized systems or networks. See `AUTHORIZED_USE.md` for full boundaries.

## Extensibility

### Adding Log Adapters

Create a new adapter in `adapters/`:

```python
class CustomAdapter:
    def load(self, path: Path) -> List[Dict[str, Any]]:
        # Parse your format
        # Return list of normalized events
        pass
```

Register in `after_action.py`:

```python
self.adapters['custom'] = CustomAdapter()
```

### Customizing Reports

Modify renderers in `renderers/`:
- `client_renderer.py` — Client-facing report structure
- `internal_renderer.py` — Internal learning report

Each renderer has modular section methods for easy customization.

## Client vs Internal Reports

**Client Report:**
- Professional tone suitable for external stakeholders
- Redacted to remove PII, credentials, internal IPs
- Includes executive summary and detection recommendations
- Contains findings placeholder for manual insertion
- Suitable for compliance documentation

**Internal Report:**
- Technical detail for operator learning
- Full data retained (no redaction)
- Successes and failures analysis
- Tool gaps and capability needs
- Reusable TTP references
- Correlation quality metrics

Both reports are generated from the same data source to ensure consistency.

## License

Research tool for authorized security testing methodology comparison.

## Contact

For methodology questions, see the parent research project documentation.

---

**Remember:** Always verify authorization before testing. Handle reports as confidential. Redact before sharing.
