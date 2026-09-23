# Operational Constraints — gophish-ics

**Pipeline step:** 3/5  
**Role:** Ops Advisor  
**Inputs:** `01_domain_brief.md`, `02_plan.md`, `PROMPT.md`

## 1. Runtime environment assumptions

**Target platform:**
- Linux or macOS workstation (operator's local machine or jump host)
- Go 1.21+ runtime (standard red team toolkit)
- No elevated privileges required (user-space only)
- SQLite3 library available (typically bundled with Go database/sql)

**Network posture:**
- Tool runs **offline-capable** — ICS generation requires no internet
- Telemetry database is local file (`telemetry.db` in working directory)
- Demo mode has zero external network calls (no DNS, no SMTP)
- If integrated with live GoPhish: operator's GoPhish instance handles actual mail relay (out of our scope)

**Filesystem expectations:**
- Write access to current working directory (for config, database, output files)
- Read access to `testdata/` and `config/` directories (relative to binary location or explicit path)
- Generated `.ics` files written to `./output/` by default (configurable via flag)

## 2. Secrets & evidence handling

**What must NEVER be committed:**
- Real target email addresses or campaign recipient lists
- Operator credentials (SMTP passwords, API keys) — even if not used in this tool, document that they don't belong here
- Actual engagement telemetry databases (`telemetry.db` → add to `.gitignore`)
- ICS files generated during live operations (`output/*.ics` → `.gitignore`)

**Safe practices:**
- All checked-in test fixtures use RFC 5737 IP ranges and RFC 2606 reserved domains:
  - example.com, example.org, example.net
  - test.invalid, localhost.localdomain
- Campaign IDs in fixtures are synthetic UUIDs with no client linkage
- Timestamps in fixtures are obviously synthetic (e.g., 2025-01-01T12:00:00Z)

**Evidence preservation (for authorized reporting):**
- Operators who DO need to archive engagement telemetry should:
  1. Copy `telemetry.db` to secure storage OUTSIDE this repo
  2. Redact/anonymize before sharing with tools developers
  3. Use separate database file per client engagement (via `--db-path` flag)

## 3. Operator workflow

**Typical engagement flow:**
1. Operator has already set up GoPhish campaign via web UI
2. Operator exports campaign data as JSON (or manually creates fixture file matching our schema)
3. Run: `./gophish-ics generate --config config/config.yaml --input campaign.json --output meeting.ics`
4. Tool checks `ics_enabled` flag:
   - If `false` (default): REFUSES with error message explaining how to override
   - If `true`: generates `.ics` file
5. Operator manually attaches `meeting.ics` to GoPhish email template OR uses GoPhish API to add attachment
6. Campaign executes via GoPhish's normal send path (not our tool)
7. RSVP simulation (lab only): `./gophish-ics simulate-rsvp --campaign-id <id> --fixture testdata/rsvp_fixture.json`
8. Generate report: `./gophish-ics report --campaign-id <id>`

**Config override for demos:**
- CLI flag: `--enable-ics` (overrides config file for current invocation only)
- Does NOT modify config file on disk (operator must consciously edit file for persistent change)
- Help text warns: "CAUTION: ICS generation disabled by default for safety"

**Error handling:**
- Config file missing or malformed: refuse to run, print example config
- Invalid campaign data (missing required fields): refuse with explicit field validation errors
- Database locked/corrupted: fail fast with troubleshooting guidance (e.g., "remove telemetry.db to reset")

## 4. Safety defaults

**Critical safeguards (architect MUST implement):**

**S1: Disabled by default**
- Checked-in `config/config.yaml` has `ics_enabled: false`
- Automated test verifies this exact file, fails CI if someone changes it to `true`
- README must have WARNING section explaining why flag exists

**S2: No silent fallback**
- If `ics_enabled: false`, tool exits with error code 1 (not warnings, not empty output)
- Error message includes: "ICS generation is disabled. To enable, edit config/config.yaml OR use --enable-ics flag"

**S3: Fixture validation**
- Before generating ICS, check all attendee emails against allowlist of safe domains:
  - Allowed (built-in): example.com, example.org, example.net, test.invalid, *.localdomain
- If ANY attendee is outside allowlist AND tool is NOT in force mode: refuse with error listing unsafe domains
- Force mode: `--force` flag bypasses check (for live engagements only, requires explicit opt-in)

**S4: Demo mode indicator**
- CLI flag: `--demo` sets DESCRIPTION field in ICS to include "[DEMO ONLY - NOT FOR OPERATIONAL USE]" prefix
- Helps operators distinguish test artifacts from live payloads

**S5: Database isolation**
- Default database path: `./telemetry.db` (local directory, not home directory or system paths)
- CLI flag: `--db-path <path>` for engagement-specific databases
- Database file has `0600` permissions (owner read/write only)

## 5. Degradation modes

**Scenario 1: SQLite database unavailable**
- Behavior: Generate ICS succeeds (database only used for RSVP tracking)
- Report command fails gracefully: "Telemetry database not found. Run simulate-rsvp first or check --db-path."

**Scenario 2: Config file missing**
- Behavior: Tool refuses to run, prints example config to stderr, exits 1
- Rationale: Forcing config file presence ensures operator has consciously set up working directory

**Scenario 3: Invalid ICS data (e.g., malformed timezone)**
- Behavior: Generator returns error, CLI exits 1 with validation details
- Rationale: Better to fail at generation time than produce calendar client garbage

**Scenario 4: Offline operation**
- Behavior: Tool works fully offline (no network dependencies)
- ICS timezone data uses embedded VTIMEZONE definitions (no external TZDB lookups)

**Scenario 5: Go library (golang-ical) unavailable**
- Behavior: Build fails (it's a required dependency)
- `go.mod` pins version to avoid supply chain drift

## 6. Plan deltas — Architect must address

**Mandatory changes to WP implementations:**

**WP2 (ICS Generator) additions:**
- [ ] Add `--force` flag to bypass email domain allowlist
- [ ] Embed VTIMEZONE definitions for common zones (US/Eastern, UTC, US/Pacific) to avoid naive local time
- [ ] Include METHOD:REQUEST in ICS (required for invites, not just events)
- [ ] Set ORGANIZER with CN (common name) matching summary or campaign name
- [ ] Attendees must have PARTSTAT:NEEDS-ACTION (initial state for invites)

**WP3 (Config & Safety) additions:**
- [ ] Implement domain allowlist check in generator (fails if unsafe domains unless --force)
- [ ] CLI help text for `generate` command must include safety warning
- [ ] Config loading error must print example YAML to stderr
- [ ] Add `--demo` flag that prefixes ICS DESCRIPTION with demo notice

**WP4 (Telemetry Store) additions:**
- [ ] Set database file permissions to `0600` on creation
- [ ] Add connection check before write operations (fail fast if DB locked)
- [ ] Telemetry database schema includes `created_at` timestamp for audit trail

**WP6 (Demo script) additions:**
- [ ] Script must use `--demo` flag for ICS generation
- [ ] Script checks `config/config.yaml` is still set to `ics_enabled: false` before starting
- [ ] Script creates temporary config override (does NOT edit checked-in file)
- [ ] Cleanup section removes `telemetry.db` and `output/*.ics` after demo

**WP7 (Documentation) additions:**
- [ ] README must have "SAFETY DEFAULTS" section before "Quick Start"
- [ ] Architecture doc must explicitly state "sidecar, not fork" and explain no GoPhish source changes
- [ ] Include failure mode table in README (what happens when DB missing, config invalid, etc.)

**WP8 (Scanners) additions:**
- [ ] .gitignore must include: `telemetry.db`, `output/`, `*.ics`
- [ ] Before running scanners, ensure no real campaign data in testdata/
- [ ] Scanner output review checklist: flag any hardcoded IPs, domains outside allowlist, insecure file permissions

**New deliverable: SAFETY_CHECKLIST.md**
- Architect must create this file with operator pre-flight checks:
  - [ ] Config file has `ics_enabled: false` (unless explicitly enabling for engagement)
  - [ ] All campaign fixtures use example.com addresses
  - [ ] telemetry.db not in git staging area
  - [ ] Output directory empty of prior engagement artifacts

---

**Impact summary:**
- Added 4 CLI flags: `--enable-ics`, `--force`, `--demo`, `--db-path`
- Added email domain allowlist validation (S3)
- Added database file permission enforcement (S5)
- Added 7 mandatory checklist items for Architect
- Zero scope creep: all constraints support existing requirements R6 (safety) and R7 (lab demo)

**Next step:** Tool Architect implements plan with these constraints baked in.
