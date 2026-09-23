# GoPhish-ICS

ICS/calendar invite integration for GoPhish phishing campaigns.

**⚠️ AUTHORIZED USE ONLY ⚠️**

This tool is designed for **authorized security testing, research, and education only**. See `AUTHORIZED_USE.md` for usage boundaries. Using this tool for unauthorized phishing campaigns is illegal and unethical.

## Overview

GoPhish-ICS extends GoPhish-style phishing workflows with calendar invite (ICS/iCal) delivery and RSVP telemetry tracking. This enables security teams to:

- Test how targets respond to calendar-based phishing attempts
- Track RSVP responses (accept/decline/tentative) as campaign metrics
- Demonstrate calendar phishing vectors in security awareness training

## Architecture

**Integration Approach:** Sidecar tool (standalone integration)

GoPhish-ICS operates as a standalone tool that integrates with GoPhish without requiring a fork:

```
┌─────────────┐
│   GoPhish   │
│  Campaign   │
│   Manager   │
└──────┬──────┘
       │ Export campaign data (JSON/YAML)
       ▼
┌─────────────────────┐
│   GoPhish-ICS       │
│  ┌───────────────┐  │
│  │ ICS Generator │  │
│  └───────────────┘  │
│         │           │
│         ▼           │
│    invite.ics       │
└─────────────────────┘
       │
       │ Manual/automated delivery
       ▼
┌─────────────────────┐
│  Target Recipients  │
│   (Lab/Test Users)  │
└──────┬──────────────┘
       │ RSVP response
       ▼
┌─────────────────────┐
│  RSVP Webhook       │
│  Server             │
│  ┌───────────────┐  │
│  │  Telemetry    │  │
│  │   Database    │  │
│  └───────────────┘  │
└─────────────────────┘
       │
       ▼
┌─────────────────────┐
│  Reporting CLI      │
│  Campaign Stats     │
└─────────────────────┘
```

### Components

1. **ICS Generator** (`ics_generator.py`): Creates RFC 5545 compliant ICS files from campaign data
2. **Telemetry Store** (`telemetry.py`): SQLite database for RSVP tracking
3. **Reporter** (`reporter.py`): CLI reporting for campaign statistics
4. **RSVP Server** (`server.py`): Flask webhook endpoint for receiving responses
5. **CLI** (`gophish_ics.py`): Command-line interface

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python gophish_ics.py --help
```

## Safety Defaults

**IMPORTANT:** ICS generation is **DISABLED** by default in `config.yaml`:

```yaml
ics_enabled: false  # SAFETY DEFAULT
```

This prevents accidental generation of phishing materials. To enable for authorized testing:

1. Review authorization scope
2. Edit `config.yaml` and set `ics_enabled: true`
3. Use only with lab/test infrastructure
4. Set back to `false` when done

For testing without modifying config, use `--force` flag.

## Usage

### Generate ICS File

```bash
# With ics_enabled: true in config
python gophish_ics.py generate tests/fixtures/campaign_basic.json -o invite.ics

# For testing with force flag (doesn't modify config)
python gophish_ics.py generate tests/fixtures/campaign_basic.json -o invite.ics --force
```

### Record RSVP Responses

```bash
# Manually record an RSVP
python gophish_ics.py rsvp campaign-001 recipient-123 user@lab.internal ACCEPTED
```

### View Campaign Reports

```bash
# Show report for specific campaign
python gophish_ics.py report campaign-001

# List all campaigns
python gophish_ics.py list
```

### Run RSVP Webhook Server

```bash
# Start server (configured in config.yaml)
python server.py

# Server listens for POST requests to /rsvp
# Example webhook payload:
# {
#   "campaign_id": "campaign-001",
#   "recipient_id": "recipient-123",
#   "recipient_email": "user@example.com",
#   "status": "ACCEPTED"
# }
```

## Lab Demo Instructions (A7)

**Use synthetic addresses only** - do not use real victim mailboxes.

### Setup

1. Configure test mail server or use fixture data
2. Use lab domain addresses (e.g., `*.testlab.local`, `*.lab.internal`)
3. Enable ICS generation in config (temporary)

### Demo Flow

```bash
# 1. Generate ICS from fixture
python gophish_ics.py generate tests/fixtures/campaign_basic.json -o demo.ics --force

# 2. Inspect the generated ICS file
cat demo.ics

# 3. Load fixture RSVP data
python -c "
import json
from gophish_ics import GoPhishICS
app = GoPhishICS()
with open('tests/fixtures/rsvp_data.json') as f:
    for rsvp in json.load(f):
        app.record_rsvp(
            rsvp['campaign_id'],
            rsvp['recipient_id'],
            rsvp['recipient_email'],
            rsvp['status']
        )
"

# 4. View campaign reports
python gophish_ics.py report campaign-fixture-001
python gophish_ics.py list
```

### Synthetic Test Data

Fixture files in `tests/fixtures/`:
- `campaign_basic.json` - Full campaign with multiple attendees
- `campaign_no_end.yaml` - Campaign using default duration
- `rsvp_data.json` - Sample RSVP responses

All use `.testlab.local` or `.lab.internal` domains.

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test modules
pytest tests/test_safety_defaults.py  # A6 compliance
pytest tests/test_ics_generator.py    # A2, A3
pytest tests/test_telemetry.py        # A4, M1
pytest tests/test_integration.py      # A2, A4, A5

# Verbose output
pytest -v tests/
```

### Key Tests

- **A6 Safety Default**: `test_safety_defaults.py` verifies shipped config is disabled
- **A3 ICS Validation**: Tests verify RFC 5545 compliance
- **M1 Recipient Stability**: Tests verify recipient IDs are stable across events
- **M2 Timezone Handling**: Tests verify explicit timezone in ICS output

## Campaign Data Format

### JSON Format

```json
{
  "organizer": "admin@company.com",
  "summary": "Q4 Security Review",
  "description": "Security awareness training exercise",
  "location": "Conference Room A",
  "dtstart": "2024-12-15T14:00:00",
  "dtend": "2024-12-15T15:00:00",
  "uid": "campaign-001@gophish-ics",
  "attendees": [
    "user1@testlab.local",
    "user2@testlab.local"
  ]
}
```

### YAML Format

```yaml
organizer: "admin@company.com"
summary: "Security Training"
description: "Authorized test"
dtstart: "2024-12-15T14:00:00"
attendees:
  - "user1@testlab.local"
  - "user2@testlab.local"
```

## Failure Modes (M3)

### Mail/Calendar Parts Unavailable

- **SMTP Unavailable**: ICS file is generated but cannot be delivered automatically. Use manual delivery or queue for retry.
- **Calendar Server Down**: RSVPs cannot be received. RSVP webhook server returns 500; clients should retry.
- **Invalid ICS Format**: Generator validates inputs and raises `ValueError` for missing required fields.
- **Database Locked**: SQLite handles concurrent access; very high concurrency may need connection pooling.

### Mitigation

- Generate ICS files in advance and queue for delivery
- Monitor webhook server health endpoint (`/health`)
- Implement client-side retry logic for webhook POSTs
- Test ICS files with `icalendar` library validation

## Security Considerations

See `OPSEC_CARD.md` for:
- Detection recommendations for defenders
- Artifacts left behind by calendar phishing
- Safer operating guidance
- Residual gaps

## Development

### Project Structure

```
.
├── config.yaml              # Configuration (ics_enabled: false)
├── gophish_ics.py          # Main CLI
├── ics_generator.py        # ICS generation
├── telemetry.py            # RSVP storage
├── reporter.py             # Reporting
├── server.py               # Webhook server
├── requirements.txt        # Python dependencies
├── tests/
│   ├── fixtures/           # Test data
│   ├── test_ics_generator.py
│   ├── test_telemetry.py
│   ├── test_safety_defaults.py
│   └── test_integration.py
├── README.md               # This file
├── OPSEC_CARD.md          # Detection recommendations
└── AUTHORIZED_USE.md      # Usage boundaries
```

### Adding Features

1. Follow the existing module structure
2. Add tests in `tests/`
3. Update this README
4. Maintain safety defaults

## License

Research tool for authorized security testing only. Not for production use.

## Attribution

Integrates with [GoPhish](https://github.com/gophish/gophish) - Open-Source Phishing Framework.
