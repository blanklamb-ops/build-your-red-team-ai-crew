# Build Plan — gophish-ics

**Pipeline step:** 2/5  
**Role:** Planner  
**Inputs:** `01_domain_brief.md`, `PROMPT.md`

## 1. Repository layout

```
gophish-ics/
├── README.md                    # R9: documentation + authorized-use notice
├── OPSEC_CARD.md               # R8: detection recommendations
├── config/
│   └── config.yaml             # R6: ics_enabled: false (safe default)
├── pkg/
│   └── ics/
│       ├── generator.go        # R2: ICS content generation
│       ├── generator_test.go   # R3: validation tests
│       └── types.go            # Data structures for ICS events
├── pkg/
│   └── telemetry/
│       ├── store.go            # R4: RSVP data storage
│       ├── store_test.go       # Telemetry tests
│       └── reporter.go         # R5: RSVP reporting
├── cmd/
│   ├── generate/
│   │   └── main.go             # CLI: generate ICS from fixture
│   └── report/
│       └── main.go             # CLI: show RSVP report
├── testdata/
│   ├── campaign_fixture.json   # R7: synthetic campaign data
│   └── rsvp_fixture.json       # R7: synthetic RSVP events
├── scripts/
│   ├── demo.sh                 # R7: lab demo workflow
│   └── run_scanners.sh         # R10: semgrep + ast-grep
└── docs/
    └── architecture.md         # R1: integration approach diagram
```

## 2. Work packages

### WP1: Project scaffolding
**Dependencies:** None  
**Deliverables:**
- Repository structure created
- Go module initialized (`go mod init`)
- README with placeholder sections
- config/config.yaml with `ics_enabled: false`

### WP2: ICS generator core (R2, R3)
**Dependencies:** WP1  
**Deliverables:**
- `pkg/ics/generator.go` — function signature:
  ```go
  func GenerateICS(campaign Campaign) ([]byte, error)
  ```
- Campaign struct includes: organizer, summary, dtstart, dtend, description, attendees
- Uses `github.com/arran4/golang-ical` library
- Outputs RFC 5545 compliant `.ics` with METHOD:REQUEST, VEVENT, explicit VTIMEZONE
- `generator_test.go` with ICS parser validation (satisfies R3)

### WP3: Configuration & safety gate (R6)
**Dependencies:** WP1  
**Deliverables:**
- Config struct with `ICSEnabled bool` field
- `LoadConfig()` function reads `config/config.yaml`
- Generator checks config flag; returns error if disabled
- **Critical:** Automated test `TestDefaultConfigIsDisabled` that:
  1. Loads actual `config/config.yaml` from repo
  2. Asserts `ics_enabled: false`
  3. Calls GenerateICS, expects refusal error

### WP4: RSVP telemetry store (R4)
**Dependencies:** WP1  
**Deliverables:**
- `pkg/telemetry/store.go` with interface:
  ```go
  type RSVPStore interface {
      RecordResponse(recipientID string, campaignID string, status ResponseStatus) error
      GetResponses(campaignID string) ([]RSVPEvent, error)
  }
  ```
- ResponseStatus enum: `Accept | Decline | Tentative | None`
- Sqlite3 backend (single file database for lab simplicity)
- Schema: `rsvp_events(id, recipient_id, campaign_id, status, timestamp)`

### WP5: RSVP reporter (R5)
**Dependencies:** WP4  
**Deliverables:**
- `pkg/telemetry/reporter.go`:
  ```go
  func GenerateCampaignReport(campaignID string, store RSVPStore) (*Report, error)
  ```
- Report struct includes: total_sent, accept_count, decline_count, tentative_count, no_response_count
- CLI tool `cmd/report/main.go` outputs report to stdout (JSON or table format)

### WP6: CLI tools & lab demo (R7)
**Dependencies:** WP2, WP3, WP5  
**Deliverables:**
- `cmd/generate/main.go`: reads testdata fixture, generates `.ics`, writes to stdout or file
- `testdata/campaign_fixture.json`: synthetic campaign with example.com addresses (5-10 recipients)
- `testdata/rsvp_fixture.json`: simulated RSVP events for fixture campaign
- `scripts/demo.sh`: end-to-end workflow:
  1. Generate ICS from fixture (with config override for demo)
  2. Load RSVP fixture into telemetry DB
  3. Run report showing aggregated counts
  4. Clean up demo artifacts

### WP7: Documentation (R1, R8, R9)
**Dependencies:** WP2, WP3, WP4, WP5  
**Deliverables:**
- `docs/architecture.md`: integration approach — **sidecar model** (standalone tool, not GoPhish fork)
  - Rationale: minimize maintenance, no upstream merge conflicts
  - Diagram: [Campaign JSON] → [ICS Generator] → [.ics file] → [mail send via operator's GoPhish instance]
  - RSVP webhook receiver (optional future work, use fixture simulation for now)
- README sections:
  - Quick start
  - Configuration (emphasize safe defaults)
  - Lab demo instructions
  - Authorized-use notice (link to `AUTHORIZED_USE.md`)
- `OPSEC_CARD.md` outline (filled by OPSEC Reviewer in step 5)

### WP8: Scanners & verification (R10)
**Dependencies:** All implementation WPs  
**Deliverables:**
- `scripts/run_scanners.sh`:
  ```bash
  semgrep --config=auto --json > semgrep-output.json
  ast-grep scan --json > ast-grep-output.json
  ```
- Scanner outputs archived in repo root or `scanners/` directory
- Build notes document how to re-run scanners

## 3. Interface contracts

### ICS Generator
```go
// Input
type Campaign struct {
    ID          string
    Organizer   string    // email address
    Summary     string    // event title
    Description string    // event body
    StartTime   time.Time // explicit timezone
    EndTime     time.Time
    Attendees   []string  // recipient emails
}

// Output
func GenerateICS(cfg *Config, campaign Campaign) (icsData []byte, err error)
// Returns error if cfg.ICSEnabled == false
```

### Telemetry Store
```go
type ResponseStatus int
const (
    StatusNone ResponseStatus = iota
    StatusAccept
    StatusDecline
    StatusTentative
)

type RSVPEvent struct {
    RecipientID string
    CampaignID  string
    Status      ResponseStatus
    Timestamp   time.Time
}

type RSVPStore interface {
    RecordResponse(event RSVPEvent) error
    GetResponses(campaignID string) ([]RSVPEvent, error)
}
```

### Reporter
```go
type Report struct {
    CampaignID      string
    TotalSent       int
    AcceptCount     int
    DeclineCount    int
    TentativeCount  int
    NoResponseCount int
}

func GenerateCampaignReport(campaignID string, store RSVPStore) (*Report, error)
```

## 4. Requirement trace matrix

| Req | Description | Work Package | Test Method |
|-----|-------------|--------------|-------------|
| R1  | Integration approach documented | WP7 | Manual review of docs/architecture.md |
| R2  | ICS generator implementation | WP2 | Unit tests verify VEVENT/ORGANIZER/ATTENDEE fields present |
| R3  | Valid .ics output | WP2 | generator_test.go parses output via golang-ical library |
| R4  | RSVP telemetry store | WP4 | store_test.go records accept/decline, queries by campaign |
| R5  | RSVP report generation | WP5 | Integration test with fixture data → report validates counts |
| R6  | Feature flag with safe default | WP3 | TestDefaultConfigIsDisabled loads actual config.yaml |
| R7  | Lab demo with synthetic data | WP6 | demo.sh runs without network/SMTP, uses testdata/ |
| R8  | OPSEC_CARD.md | WP7 (outline), WP9 (filled) | Manual: ≥3 detection bullets present |
| R9  | README + authorized-use | WP7 | Manual: grep README for authorized-use mention |
| R10 | Scanner outputs | WP8 | Check semgrep-output.json, ast-grep-output.json exist |

## 5. Test plan

### Automated tests (run via `go test ./...`)
- **A2 (ICS generation):** `TestGenerateICS_ValidOutput` creates ICS, asserts required fields
- **A3 (ICS validation):** `TestGenerateICS_ParsesCleanly` parses output with ical library, no errors
- **A4 (Telemetry store):** `TestRSVPStore_RecordAndQuery` writes accept/decline, queries by campaign
- **A5 (Report aggregation):** `TestReporter_AggregatesCounts` feeds fixture events, validates report struct
- **A6 (Safe default):** `TestDefaultConfigIsDisabled` loads config/config.yaml, asserts ICSEnabled==false, generator refuses

### Manual checks (documented in demo.sh comments)
- **A1 (Architecture docs):** Verify docs/architecture.md exists, describes sidecar approach
- **A7 (Lab demo):** Run scripts/demo.sh, confirm uses example.com addresses only
- **A8 (OPSEC card):** Read OPSEC_CARD.md, count Detection Recommendations bullets (≥3)
- **A9 (Authorized-use notice):** Grep README for "authorized" or "AUTHORIZED_USE.md"
- **A10 (Scanners):** Confirm semgrep-output.json and ast-grep-output.json present

### Manual fidelity checks
- **M1 (Stable recipient IDs):** Inspect testdata fixture, confirm recipient IDs consistent
- **M2 (Explicit timezones):** Read generated .ics, verify DTSTART/DTEND include TZID or Z suffix
- **M3 (Failure modes):** Check docs/architecture.md documents offline/partial failure behavior

## 6. Out of scope

**Not included in this build:**
- Actual GoPhish fork or binary modification
- Live SMTP mail sending (demo uses file output only)
- Real calendar client RSVP webhook receiver (simulated with fixture data)
- Mail/calendar gateway integration (design only, not implemented)
- Multi-campaign dashboard UI (CLI reporting only)
- Production database migration tooling (SQLite fixture DB sufficient for lab)
- Automated deployment / containerization (code only, no Docker/CI)

**Ambiguities resolved:**
- **ASSUMPTION (from domain brief):** Sidecar approach chosen over fork to minimize maintenance burden
- **ASSUMPTION:** RSVP tracking via fixture simulation rather than real calendar client responses (lab environment)
- **ASSUMPTION:** SQLite for telemetry store (simpler than MySQL for research tool)

---

**Next step:** Ops Advisor injects operational constraints before implementation begins.
