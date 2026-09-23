# After-Action Report Generator

**Tool slug:** `after-action`  
**Status:** Research tool for authorized security testing only

## Overview

This tool correlates engagement logs and operator decisions into professional reports for both clients and internal learning. It processes multiple log formats, joins them on time windows and asset keys, and produces redacted outputs suitable for external delivery.

## Authorized Use Only

⚠️ **This tool is designed for authorized security testing, penetration testing, and red team engagements only.**

- Use only on systems and identities you are contractually or legally authorized to test
- Do not use against unauthorized targets
- Strip all client secrets, real victim data, and engagement identifiers before public archival
- See `AUTHORIZED_USE.md` for full boundaries and researcher obligations
- Review `OPSEC_CARD.md` for detection recommendations to share with clients

## Features

- **Multi-format log ingestion**: JSON Lines and CSV adapters included
- **Operator decision tracking**: Correlate tactical decisions with technical events
- **Dual reporting**: Client-facing professional reports + internal learning summaries
- **PII/Secret redaction**: Configurable rules to sanitize sensitive data before export
- **Reproducible builds**: Structured inputs, deterministic outputs

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate reports from fixture data
make test-run

# Or use the CLI directly
python -m after_action.cli \
  --logs testdata/fixture_engagement/logs/ \
  --decisions testdata/fixture_engagement/decisions.jsonl \
  --output reports/
```

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Project Structure

```
after_action/
├── __init__.py          # Package init
├── cli.py               # Command-line interface
├── adapters.py          # Log format adapters (JSONL, CSV)
├── correlation.py       # Event-decision correlation engine
├── redaction.py         # PII/secret redaction rules
└── renderers.py         # Report generators (client, internal)

testdata/fixture_engagement/
├── logs/                # Sample engagement logs
│   ├── phishing.jsonl
│   └── network.csv
└── decisions.jsonl      # Operator decision log

tests/
└── test_integration.py  # Integration tests
```

## Usage

### Input Formats

**Log files** (auto-detected by extension):
- `.jsonl`: JSON Lines format with `timestamp`, `event_type`, `asset`, `details`
- `.csv`: CSV with headers including `timestamp`, `event`, `target`, `result`

**Decision log** (JSONL):
```json
{"timestamp": "2024-01-15T10:30:00Z", "decision": "pivot-to-exchange", "rationale": "AD creds obtained", "asset": "DC01"}
```

### Output Reports

**Client Report** (`client_report.md`):
- Executive summary
- Engagement timeline with correlated events
- Findings placeholders
- Detection Recommendations section
- PII/secrets redacted

**Internal Report** (`internal_learning.md`):
- What worked (successes)
- What failed (failures)
- Tool gaps identified
- Reusable TTPs with framework references
- May retain more technical detail than client version

### Redaction Configuration

Edit `redaction_rules.json` to customize:
```json
{
  "patterns": [
    {"name": "api_key", "regex": "sk-[a-zA-Z0-9]{32,}"},
    {"name": "password", "regex": "password[\"']?\\s*[:=]\\s*[\"']?([^\"'\\s]+)"}
  ]
}
```

## Testing

```bash
# Run integration tests
python -m pytest tests/

# Verify redaction on planted secrets
make verify-redaction
```

## Detection Recommendations

After completing an engagement, share the Detection Recommendations from your client report with the defensive team. See `OPSEC_CARD.md` for how this tool's outputs could be detected or mishandled.

## License & Ethics

This tool is released for research purposes under the study's authorized use guidelines. Outputs are dual-use—handle responsibly and maintain clear authorization boundaries.
