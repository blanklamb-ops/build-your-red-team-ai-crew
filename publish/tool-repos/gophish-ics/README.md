# gophish-ics

Calendar invite (ICS) payload generation and RSVP telemetry tracking for authorized phishing campaigns.

## ⚠️ Authorized Use Only

This tool is designed for **authorized security testing and red team engagements only**. See [`AUTHORIZED_USE.md`](AUTHORIZED_USE.md) for usage guidelines and ethical constraints.

**Do not use this tool against systems you do not have explicit written authorization to test.**

---

## 🛡️ Safety Defaults

**ICS generation is DISABLED by default** to prevent accidental deployment during testing.

- The checked-in configuration file (`config/config.yaml`) has `ics_enabled: false`
- All test fixtures use RFC-reserved domains (`example.com`, `test.invalid`)
- Email domain allowlist prevents generation for non-test addresses unless explicitly bypassed with `--force`
- Database files are created with `0600` permissions (owner read/write only)

To enable ICS generation:
- **For demos:** Use `--enable-ics` CLI flag (does not modify config file)
- **For live engagements:** Edit `config/config.yaml` and set `ics_enabled: true` (requires conscious action)

---

## Overview

`gophish-ics` is a **sidecar tool** (not a GoPhish fork) that generates RFC 5545-compliant iCalendar invites for phishing campaigns and tracks simulated RSVP responses.

### Key capabilities

- **ICS generation:** Create `.ics` calendar invites from campaign JSON data
- **RSVP telemetry:** Record recipient responses (accept/decline/tentative) in local SQLite database
- **Campaign reporting:** Aggregate RSVP statistics per campaign
- **Lab-safe defaults:** All features require explicit enablement and use synthetic test data

### Integration approach

See [`docs/architecture.md`](docs/architecture.md) for detailed integration design.

**TL;DR:** This tool operates as a standalone utility. It does NOT modify GoPhish source code. Operators:
1. Export campaign data from GoPhish (or manually create campaign JSON)
2. Run `gophish-ics generate` to create `.ics` file
3. Manually attach ICS to GoPhish email template
4. Simulate RSVP responses using fixture data (real RSVP tracking requires calendar gateway integration, out of scope)
5. View aggregated RSVP reports

---

## Quick Start

### Prerequisites

- Go 1.21 or later
- SQLite3 (bundled with Go `database/sql`)

### Build

```bash
# Install dependencies
go mod download

# Build CLI tools
go build -o bin/generate ./cmd/generate
go build -o bin/simulate-rsvp ./cmd/simulate-rsvp
go build -o bin/report ./cmd/report
```

### Run demo

```bash
# Execute end-to-end demo with synthetic data
./scripts/demo.sh
```

This will:
1. Verify safe config defaults
2. Generate an ICS file from `testdata/campaign_fixture.json`
3. Load simulated RSVP events
4. Display aggregated campaign report

### Clean up demo artifacts

```bash
rm -f telemetry.db output/*.ics
```

---

## Usage

### Generate ICS file

```bash
./bin/generate \
  --config config/config.yaml \
  --input campaign.json \
  --output output/meeting.ics \
  --enable-ics \
  --demo
```

**Flags:**
- `--config`: Path to configuration file (default: `config/config.yaml`)
- `--input`: Campaign JSON file (required)
- `--output`: Output `.ics` path (stdout if omitted)
- `--enable-ics`: Override config to enable generation (for demos/testing)
- `--force`: Bypass domain safety checks (authorized engagements only)
- `--demo`: Add `[DEMO ONLY]` notice to event description

**Campaign JSON schema:**

```json
{
  "id": "campaign-001",
  "organizer": "sender@example.com",
  "summary": "Meeting Title",
  "description": "Meeting agenda details",
  "start_time": "2025-06-15T14:00:00Z",
  "end_time": "2025-06-15T15:00:00Z",
  "location": "Conference Room A",
  "attendees": [
    "recipient1@example.com",
    "recipient2@example.com"
  ]
}
```

### Simulate RSVP responses

```bash
./bin/simulate-rsvp \
  --db-path telemetry.db \
  --fixture testdata/rsvp_fixture.json
```

**RSVP fixture JSON schema:**

```json
[
  {
    "recipient_id": "user1@example.com",
    "campaign_id": "campaign-001",
    "status": "accept"
  },
  {
    "recipient_id": "user2@example.com",
    "campaign_id": "campaign-001",
    "status": "decline"
  }
]
```

**Valid status values:** `accept`, `decline`, `tentative`, `none`

### Generate RSVP report

```bash
./bin/report \
  --db-path telemetry.db \
  --campaign-id campaign-001 \
  --total-sent 10
```

**Output (table format):**

```
Campaign RSVP Report
====================
Campaign ID:  campaign-001
Total Sent:   10

Accepted:     4
Declined:     2
Tentative:    1
No Response:  3
```

Add `--json` flag for JSON output.

---

## Configuration

Edit `config/config.yaml`:

```yaml
# Feature flag: enable ICS generation
# WARNING: Only set to true during authorized engagements
ics_enabled: false

# Safe domain allowlist (for --force bypass validation)
safe_domains:
  - example.com
  - example.org
  - example.net
  - test.invalid
  - localhost.localdomain

# Default timezone for ICS generation
default_timezone: UTC

# Database path (relative to working directory)
database_path: ./telemetry.db
```

---

## Testing

Run automated test suite:

```bash
go test ./...
```

**Critical tests:**
- `TestDefaultConfigIsDisabled`: Verifies checked-in config has `ics_enabled: false`
- `TestGenerateICS_ParsesCleanly`: Validates RFC 5545 compliance via ICS parser
- `TestRSVPStore_RecordAndQuery`: Verifies telemetry database operations
- `TestReporter_AggregatesCounts`: Validates RSVP report aggregation logic

---

## Failure Modes

| Scenario | Behavior |
|----------|----------|
| Config file missing | Tool exits with error, prints example config |
| `ics_enabled: false` (default) | Generation refused, operator must use `--enable-ics` or edit config |
| Unsafe email domains | Blocked unless `--force` flag used |
| SQLite database unavailable | ICS generation succeeds (DB only needed for RSVP tracking); report command fails gracefully |
| Invalid campaign data | Validation errors printed, tool exits before generation |
| Offline operation | Fully supported (no network dependencies) |

---

## OPSEC Considerations

See [`OPSEC_CARD.md`](OPSEC_CARD.md) for detailed operational security guidance, including:
- Artifacts left behind by calendar invites
- Detection recommendations for blue teams
- Safer operating procedures for engagements

**Quick tips:**
- Never commit `telemetry.db` or live engagement `.ics` files (`.gitignore` configured)
- Use separate database files per client engagement (`--db-path` flag)
- Calendar invites create forensic artifacts: ORGANIZER identity, timezone data, embedded URLs
- Mail/calendar gateways may log ICS MIME parts differently than plain emails

---

## Project Structure

```
gophish-ics/
├── cmd/
│   ├── generate/         # ICS generation CLI
│   ├── simulate-rsvp/    # RSVP fixture loader
│   └── report/           # Campaign report generator
├── pkg/
│   ├── config/           # Configuration loading
│   ├── ics/              # ICS generation logic
│   └── telemetry/        # RSVP storage and reporting
├── testdata/             # Synthetic test fixtures
├── scripts/
│   └── demo.sh           # End-to-end lab demo
├── docs/
│   └── architecture.md   # Integration approach
├── config/
│   └── config.yaml       # Default configuration
├── OPSEC_CARD.md         # Operational security guidance
├── SAFETY_CHECKLIST.md   # Operator pre-flight checks
└── AUTHORIZED_USE.md     # Usage authorization notice
```

---

## License & Attribution

Research tool developed for authorized security testing. See `AUTHORIZED_USE.md` for usage constraints.

---

## Support

For issues or questions about authorized research use, contact your engagement lead or security team.

**Remember:** This tool generates content designed to appear legitimate. Only use it in authorized testing contexts with proper legal agreements in place.
