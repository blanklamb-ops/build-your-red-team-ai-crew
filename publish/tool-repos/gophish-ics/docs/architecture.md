# Architecture — gophish-ics

## Integration Approach: Sidecar Model

**Decision:** `gophish-ics` is implemented as a **standalone sidecar tool**, NOT a GoPhish fork.

### Rationale

| Factor | Sidecar | Fork |
|--------|---------|------|
| Maintenance burden | Low (independent versioning) | High (upstream merge conflicts) |
| GoPhish upgrades | No impact | Requires manual rebasing |
| Deployment complexity | Simple (separate binary) | Complex (modified GoPhish build) |
| Scope isolation | Clean separation | Tightly coupled |
| Upstream contribution | Not required | Would require PR acceptance |

**Verdict:** Sidecar model minimizes technical debt while delivering required functionality.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       Operator Workflow                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   GoPhish Web UI       │
                    │   (campaign setup)     │
                    └────────────────────────┘
                                 │
                                 │ export campaign data
                                 ▼
                    ┌────────────────────────┐
                    │  campaign.json         │
                    │  (manual or API export)│
                    └────────────────────────┘
                                 │
                                 ▼
        ┌────────────────────────────────────────────────┐
        │          gophish-ics generate                  │
        │  ┌──────────────────────────────────────────┐  │
        │  │  1. Load config (ics_enabled check)      │  │
        │  │  2. Validate campaign data               │  │
        │  │  3. Check email domain allowlist         │  │
        │  │  4. Generate RFC 5545 ICS (golang-ical)  │  │
        │  └──────────────────────────────────────────┘  │
        └────────────────────────────────────────────────┘
                                 │
                                 │ output
                                 ▼
                    ┌────────────────────────┐
                    │  meeting.ics           │
                    │  (VEVENT with METHOD:  │
                    │   REQUEST)             │
                    └────────────────────────┘
                                 │
                                 │ manual attachment
                                 ▼
                    ┌────────────────────────┐
                    │  GoPhish email         │
                    │  template (with ICS    │
                    │  attached)             │
                    └────────────────────────┘
                                 │
                                 │ send via GoPhish
                                 ▼
                    ┌────────────────────────┐
                    │  Target Recipients     │
                    │  (calendar clients)    │
                    └────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
           ┌─────────────────┐      ┌─────────────────┐
           │ Real RSVP (out  │      │ Simulated RSVP  │
           │ of scope for    │      │ (lab demo only) │
           │ lab demo)       │      └─────────────────┘
           └─────────────────┘               │
                                              ▼
                                ┌─────────────────────────┐
                                │ gophish-ics             │
                                │ simulate-rsvp           │
                                │ (loads fixture JSON)    │
                                └─────────────────────────┘
                                              │
                                              ▼
                                ┌─────────────────────────┐
                                │ telemetry.db            │
                                │ (SQLite)                │
                                │                         │
                                │ rsvp_events table:      │
                                │ - recipient_id          │
                                │ - campaign_id           │
                                │ - status                │
                                │ - timestamp             │
                                └─────────────────────────┘
                                              │
                                              ▼
                                ┌─────────────────────────┐
                                │ gophish-ics report      │
                                │ (aggregate counts)      │
                                └─────────────────────────┘
                                              │
                                              ▼
                                ┌─────────────────────────┐
                                │ Campaign RSVP Report    │
                                │ - Accepted: 4           │
                                │ - Declined: 2           │
                                │ - Tentative: 1          │
                                │ - No Response: 3        │
                                └─────────────────────────┘
```

---

## Component Responsibilities

### 1. ICS Generator (`pkg/ics/generator.go`)

**Input:** Campaign struct (JSON deserialized)  
**Output:** RFC 5545-compliant `.ics` file (bytes)

**Key operations:**
- Validates campaign data (required fields, time ranges)
- Checks email domains against allowlist (unless `--force`)
- Constructs `VCALENDAR` with `METHOD:REQUEST`
- Adds `VEVENT` with:
  - `UID`: campaign ID
  - `ORGANIZER`: campaign organizer with CN
  - `ATTENDEE`: each recipient with `PARTSTAT:NEEDS-ACTION` and `RSVP:TRUE`
  - `DTSTART`/`DTEND`: explicit UTC or timezone-aware timestamps
  - `SUMMARY`: event title
  - `DESCRIPTION`: event details (with demo notice if `--demo` flag set)
  - `LOCATION`: meeting location (optional)

**Libraries used:**
- `github.com/arran4/golang-ical` — ICS construction and serialization

### 2. Telemetry Store (`pkg/telemetry/store.go`)

**Purpose:** Persist RSVP events to SQLite database

**Schema:**
```sql
CREATE TABLE rsvp_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    status INTEGER NOT NULL,  -- 0=none, 1=accept, 2=decline, 3=tentative
    timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key operations:**
- `RecordResponse()`: Insert RSVP event
- `GetResponses()`: Query all events for a campaign
- Database file created with `0600` permissions (owner only)

### 3. Reporter (`pkg/telemetry/reporter.go`)

**Purpose:** Aggregate RSVP statistics per campaign

**Algorithm:**
1. Query all RSVP events for campaign ID
2. Count events by status (accept/decline/tentative)
3. Calculate no-response count: `total_sent - (accept + decline + tentative)`
4. Return `Report` struct

### 4. CLI Tools

**`cmd/generate/main.go`**
- Loads campaign JSON from file
- Calls ICS generator with safety checks
- Writes output to file or stdout

**`cmd/simulate-rsvp/main.go`**
- Loads RSVP fixture JSON
- Writes events to telemetry database
- Lab demo only (real RSVP tracking requires calendar gateway integration)

**`cmd/report/main.go`**
- Queries telemetry database
- Calls reporter
- Outputs table or JSON format

---

## RSVP Tracking: Lab vs. Production

### Lab Demo (Implemented)

Uses **simulated RSVP responses** from fixture JSON files:

1. Operator manually creates `rsvp_fixture.json` with desired accept/decline/tentative distribution
2. Runs `simulate-rsvp` CLI to load fixture into `telemetry.db`
3. Runs `report` CLI to view aggregated statistics

**Pros:**
- No dependency on real calendar clients
- Fully offline
- Deterministic testing

**Cons:**
- Not real victim behavior
- Requires manual fixture creation

### Production Engagement (Out of Scope)

Real RSVP tracking would require:

1. **Webhook receiver:** HTTP endpoint to receive calendar RSVP responses
2. **Calendar gateway integration:** Parse `PARTSTAT` changes in iCal replies (METHOD:REPLY)
3. **Mail server cooperation:** Forward calendar response emails to webhook
4. **GoPhish event correlation:** Match RSVP recipient email to GoPhish campaign recipient ID

**Implementation sketch (not delivered):**
```
┌─────────────────┐
│ Victim calendar │
│ client accepts  │
│ invite          │
└────────┬────────┘
         │ iCal METHOD:REPLY
         ▼
┌─────────────────┐
│ Mail server     │
│ (receives RSVP) │
└────────┬────────┘
         │ forward to webhook
         ▼
┌─────────────────┐
│ gophish-ics     │
│ webhook receiver│
│ (parse PARTSTAT)│
└────────┬────────┘
         │ write to telemetry.db
         ▼
┌─────────────────┐
│ telemetry.db    │
│ (RSVP events)   │
└─────────────────┘
```

**Decision:** Lab demo simulates RSVP responses to satisfy acceptance criteria without requiring complex mail infrastructure.

---

## Failure Modes & Degradation

| Scenario | Generator Behavior | RSVP Tracking Behavior | Report Behavior |
|----------|--------------------|------------------------|-----------------|
| Config file missing | Exit 1, print example | N/A | N/A |
| `ics_enabled: false` | Exit 1, prompt for `--enable-ics` or config edit | N/A | N/A |
| Unsafe email domain | Exit 1, require `--force` flag | N/A | N/A |
| SQLite DB locked | N/A | Exit 1, suggest removing lock file | Exit 1, DB unavailable |
| Invalid campaign JSON | Exit 1, validation errors listed | N/A | N/A |
| No RSVP events for campaign | N/A | N/A | Report with 0 responses |
| Offline operation | ✓ Works (no network) | ✓ Works | ✓ Works |

---

## Security Considerations

### 1. Safe Defaults

- `ics_enabled: false` in checked-in config (enforced by automated test)
- Email domain allowlist prevents accidental targeting of real domains
- Database files created with `0600` permissions
- `.gitignore` excludes `telemetry.db` and `output/*.ics`

### 2. Operator Errors

**Risk:** Operator edits config to `ics_enabled: true` and commits it

**Mitigation:**
- CI test (`TestDefaultConfigIsDisabled`) fails if config has `ics_enabled: true`
- Pre-commit hook suggestion in SAFETY_CHECKLIST.md

**Risk:** Operator uses `--force` with real target domains during testing

**Mitigation:**
- `--force` flag name is explicit
- CLI help text warns "authorized engagements only"
- Demo script does NOT use `--force` flag

### 3. Data Leakage

**Risk:** Telemetry database contains real victim identities

**Mitigation:**
- `.gitignore` excludes `telemetry.db`
- README warns about evidence preservation
- Operator checklist includes "ensure no real data in testdata/"

---

## Testing Strategy

### Unit Tests
- `pkg/config/config_test.go`: Config loading, safe defaults verification
- `pkg/ics/generator_test.go`: ICS generation, RFC 5545 compliance, safety checks
- `pkg/telemetry/store_test.go`: Database operations, permissions
- `pkg/telemetry/reporter_test.go`: Report aggregation logic

### Integration Tests
- `scripts/demo.sh`: End-to-end workflow with fixtures

### Manual Verification
- Import generated `.ics` into calendar client (Outlook, Google Calendar, Apple Calendar)
- Verify ORGANIZER, ATTENDEE, time display correctly
- Check RSVP buttons appear (accept/decline/tentative)

---

## Dependencies

- **Go 1.21+**: Language runtime
- **github.com/arran4/golang-ical v0.3.0**: ICS generation
- **github.com/mattn/go-sqlite3 v1.14.22**: SQLite driver
- **gopkg.in/yaml.v3**: Config file parsing

All dependencies are vendorable for air-gapped deployments.

---

## Future Enhancements (Out of Scope)

- GoPhish API client for automated campaign export
- Webhook receiver for real RSVP tracking
- Dashboard UI for multi-campaign reporting
- Docker container for portable deployment
- Prometheus metrics exporter for telemetry
- Mail gateway integration (Exchange, O365) for PARTSTAT parsing

---

## References

- RFC 5545 (iCalendar): https://datatracker.ietf.org/doc/html/rfc5545
- RFC 6047 (iTIP): https://datatracker.ietf.org/doc/html/rfc6047
- GoPhish: https://github.com/gophish/gophish
- golang-ical: https://github.com/arran4/golang-ical
