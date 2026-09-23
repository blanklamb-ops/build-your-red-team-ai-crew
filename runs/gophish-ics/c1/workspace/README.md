# GoPhish ICS Integration

**AUTHORIZED USE ONLY** — This tool is for authorized security testing, research, and education only. See [AUTHORIZED_USE.md](AUTHORIZED_USE.md) for usage boundaries.

## Overview

GoPhish ICS Integration is a sidecar tool that adds calendar invite (ICS/iCal) functionality to [GoPhish](https://github.com/gophish/gophish) phishing campaigns. It enables authorized operators to:

- Generate RFC 5545-compliant `.ics` calendar invites from campaign data
- Track RSVP responses (accept/decline/tentative/none) 
- Report aggregated RSVP telemetry per campaign
- Maintain lab safety with explicit enable flags and synthetic test data

## Architecture (A1)

### Integration Approach: Sidecar

This tool uses a **sidecar integration** pattern rather than forking GoPhish:

```
┌─────────────────────┐
│   GoPhish Server    │
│  (upstream/stock)   │
└──────────┬──────────┘
           │
           │ Campaign data (JSON/API)
           ▼
┌─────────────────────┐
│  GoPhish ICS Tool   │◄─── config.yaml (ics_enabled: false by default)
│    (this repo)      │
├─────────────────────┤
│  • ICS Generator    │──► .ics files (RFC 5545)
│  • Telemetry Store  │──► SQLite database (RSVPs)
│  • Reporter         │──► Campaign reports
└─────────────────────┘
```

**Rationale:**
- No GoPhish source modifications required
- Easy to version-control and distribute
- Can be integrated via GoPhish's webhook/API system
- Simpler to audit and review as a standalone component

### Components

1. **ICS Generator** (`gophish_ics.ICSGenerator`)
   - Generates RFC 5545-compliant calendar invites
   - Explicit UTC timezone handling (no naive datetimes)
   - Configurable via `config.yaml`

2. **Telemetry Store** (`gophish_ics.TelemetryStore`)
   - SQLite-backed RSVP tracking
   - Stable recipient IDs across events
   - Records accept/decline/tentative/none responses

3. **Reporter** (`gophish_ics.Reporter`)
   - Aggregates RSVP statistics per campaign
   - Text-based summary reports

4. **Configuration** (`gophish_ics.Config`)
   - YAML-based configuration
   - Safety validation on load
   - **Ships with `ics_enabled: false` by default**

## Installation

```bash
# Clone repository
git clone <repo-url>
cd gophish-ics

# Install dependencies
pip install -r requirements.txt

# Verify safety defaults
python gophish_ics.py check-config
```

## Usage

### Safety Check (Required First Step)

```bash
# Verify ICS generation is disabled by default
python gophish_ics.py check-config
```

Expected output:
```
✓ Safe: ICS generation is disabled by default
```

### Generate ICS File (A2, A3)

```bash
# Create campaign data JSON (see testdata/campaign_fixture.json for example)
cat > campaign.json << EOF
{
  "organizer": "sender@example.com",
  "organizer_name": "Security Team",
  "summary": "Security Awareness Training",
  "dtstart": "2026-11-01T14:00:00Z",
  "dtend": "2026-11-01T15:00:00Z",
  "location": "Room 101",
  "description": "Mandatory training session",
  "attendees": [
    {"email": "user1@example.com", "name": "User One"},
    {"email": "user2@example.com", "name": "User Two"}
  ]
}
EOF

# Enable ICS in config (ONLY with proper authorization)
# Edit config.yaml: ics_enabled: true

# Generate ICS
python gophish_ics.py generate campaign.json -o invite.ics
```

### Record RSVP Responses (A4)

```bash
# Record accept response
python gophish_ics.py rsvp rec-001 accept

# Record decline response
python gophish_ics.py rsvp rec-002 decline

# Record tentative response
python gophish_ics.py rsvp rec-003 tentative
```

### Generate Campaign Report (A5)

```bash
# Show RSVP statistics for campaign
python gophish_ics.py report test-campaign-001
```

Example output:
```
Campaign RSVP Summary: test-campaign-001
============================================================
Total Recipients: 4

  ✓ Accepted:        1 ( 25.0%)
  ✗ Declined:        1 ( 25.0%)
  ? Tentative:       1 ( 25.0%)
  ∅ No Action:       0 (  0.0%)
  - No Response:     1 ( 25.0%)
```

## Lab Demo Instructions (A7)

**Use synthetic addresses only** — all fixtures use safe domains:
- `example.com` (RFC 2606 reserved)
- `test.local` (non-routable)
- `demo.lab` (non-routable)

### Demo Workflow

```bash
# 1. Verify safety defaults
python gophish_ics.py check-config

# 2. Initialize demo campaign (uses fixture data)
python test_gophish_ics.py -v -k test_generates_ics_from_fixture

# 3. Generate demo ICS (requires temporary config override)
cp config.yaml config.yaml.backup
sed -i 's/ics_enabled: false/ics_enabled: true/' config.yaml
python gophish_ics.py generate testdata/campaign_fixture.json -o demo.ics

# 4. Inspect generated ICS
cat demo.ics

# 5. Validate ICS
python -c "from icalendar import Calendar; cal = Calendar.from_ical(open('demo.ics', 'rb').read()); print('Valid ICS:', cal['PRODID'])"

# 6. Restore safety defaults
mv config.yaml.backup config.yaml

# 7. Populate demo telemetry
python -c "
from gophish_ics import Config, TelemetryStore
import json

config = Config('config.yaml')
store = TelemetryStore(config)

# Load campaign fixture
with open('testdata/campaign_fixture.json') as f:
    data = json.load(f)

# Create campaign
store.create_campaign(data['campaign_id'], data['campaign_name'])

# Add recipients
for att in data['attendees']:
    store.add_recipient(data['campaign_id'], att['recipient_id'], att['email'], att['name'])

# Record demo RSVPs
store.record_rsvp('rec-001', 'accept')
store.record_rsvp('rec-002', 'decline')
store.record_rsvp('rec-003', 'tentative')
print('Demo telemetry populated')
"

# 8. Generate report
python gophish_ics.py report test-campaign-001
```

## Testing (A3, A6)

Run the test suite to verify all acceptance criteria:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest test_gophish_ics.py -v

# Run specific test categories
pytest test_gophish_ics.py::TestSafetyDefaults -v  # A6: Safety defaults
pytest test_gophish_ics.py::TestICSGeneration -v   # A2, A3: ICS generation
pytest test_gophish_ics.py::TestTelemetry -v       # A4: Telemetry
pytest test_gophish_ics.py::TestReporting -v       # A5: Reporting
pytest test_gophish_ics.py::TestLabSafety -v       # A7: Synthetic addresses
```

**Critical Test (A6):** The test suite verifies that the shipped `config.yaml` has `ics_enabled: false` and that generation is refused until explicitly enabled:

```bash
pytest test_gophish_ics.py::TestSafetyDefaults::test_shipped_config_has_ics_disabled -v
```

## Integration with GoPhish

### Option 1: Manual Workflow

1. Export campaign data from GoPhish (via UI or API)
2. Format as JSON (see `testdata/campaign_fixture.json`)
3. Generate ICS: `python gophish_ics.py generate campaign.json`
4. Attach ICS to campaign emails
5. Track RSVPs via webhook or manual recording

### Option 2: Webhook Integration

Configure GoPhish webhook to call:
```bash
curl -X POST http://localhost:5000/rsvp \
  -H "Content-Type: application/json" \
  -d '{"recipient_id": "rec-001", "response": "accept"}'
```

See `docs/webhook_integration.md` (future) for complete setup.

### Option 3: API Client

Use `gophish_ics` as a library:

```python
from gophish_ics import Config, ICSGenerator, TelemetryStore

config = Config('config.yaml')
generator = ICSGenerator(config)
telemetry = TelemetryStore(config)

# Generate ICS
campaign_data = {...}
ics_content = generator.generate(campaign_data)

# Record RSVP
telemetry.record_rsvp('rec-001', 'accept')
```

## Failure Modes (M3)

| Scenario | Behavior |
|----------|----------|
| ICS disabled in config | `ConfigError` raised, generation refused |
| Invalid datetime format | `ValueError` with clear message |
| Missing organizer | Uses default `noreply@example.com` |
| Missing attendees | Generates valid ICS with no attendees |
| Database locked | SQLite retry logic (3 attempts) |
| Corrupt ICS | icalendar library validation catches on load |

## Security Considerations

See [OPSEC_CARD.md](OPSEC_CARD.md) for:
- Detection recommendations (A8)
- Operator risks
- Artifacts left behind
- Safer operating guidance

## Configuration Reference

`config.yaml` settings:

```yaml
# REQUIRED: Feature flag (must be false by default)
ics_enabled: false

# Telemetry database path
telemetry_db: "telemetry.db"

# ICS generation settings
ics_settings:
  default_timezone: "UTC"
  prodid: "-//GoPhish ICS Integration//EN"
  default_duration: 60  # minutes

# Demo mode
demo_mode:
  use_fixtures: true
  test_domains: ["example.com", "test.local", "demo.lab"]
```

## Files

- `gophish_ics.py` — Main tool implementation
- `config.yaml` — Configuration (ships with `ics_enabled: false`)
- `test_gophish_ics.py` — Test suite
- `testdata/` — Synthetic fixtures
  - `campaign_fixture.json` — Example campaign data
  - `rsvp_fixture.json` — Example RSVP responses
- `OPSEC_CARD.md` — Detection recommendations
- `AUTHORIZED_USE.md` — Usage boundaries

## Requirements

- Python 3.8+
- PyYAML >= 6.0
- icalendar >= 5.0 (for validation)
- pytest >= 7.0 (for testing)

## License

See LICENSE file.

## Authors

Research tool for security methodology comparison study.

## Contributing

This is a research artifact. If adapting for production use:
1. Review AUTHORIZED_USE.md
2. Conduct security audit
3. Add your own detection/monitoring
4. Include OPSEC card in client deliverables
