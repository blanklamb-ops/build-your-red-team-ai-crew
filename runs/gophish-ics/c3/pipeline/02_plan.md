# Build Plan — gophish-ics

## Assumptions

- **ASSUMPTION:** “Make ACCEPTANCE.md executable” means provide one local command that executes all acceptance checks while keeping `ACCEPTANCE.md` as the authoritative checklist.
- **ASSUMPTION:** The required RSVP path is a sidecar CLI boundary backed by SQLite; parsing inbound SMTP/iTIP replies and modifying GoPhish are outside the stated local-fixture success condition.
- **ASSUMPTION:** Scanner binaries may be absent by design. Archive truthful outputs from controlled post-build invocations (including an explicit unavailable status) without installing substitutes.

## Repository layout

```text
README.md                         architecture, lab demo, failures, acceptance
OPSEC_CARD.md                     final safety/detection guidance
AUTHORIZED_USE.md                 existing notice
ethics/AUTHORIZED_USE.md          canonical notice referenced by PROMPT
config/default.yaml               shipped `ics_enabled: false`
fixtures/campaign.json            synthetic campaign/attendee data
fixtures/rsvps.json               accept + decline fixture events
gophish_ics/__init__.py
gophish_ics/config.py             strict feature configuration
gophish_ics/ics.py                RFC 5545 serializer/validator
gophish_ics/store.py              SQLite RSVP persistence/reporting
gophish_ics/cli.py                operator interface
tests/test_config.py
tests/test_ics.py
tests/test_store_cli.py
scripts/acceptance.sh              executable acceptance entry point
scans/semgrep.txt
scans/ast-grep.txt
pipeline/01_domain_brief.md
pipeline/02_plan.md
pipeline/03_ops_constraints.md
pipeline/04_build_notes.md
pipeline/05_opsec_card.md
```

## Work packages

1. **WP1 — Safety/config foundation** (no dependencies): add canonical ethics notice, false shipped configuration, strict loader, package skeleton, and synthetic-only fixture policy.
2. **WP2 — Invite generator** (depends on WP1): parse campaign JSON, validate stable identifiers/emails/explicit timestamps, serialize escaped and folded RFC 5545 `METHOD:REQUEST`/`VEVENT` content with CRLF, and expose a lightweight structural validator.
3. **WP3 — Telemetry and reporting** (depends on WP1): create SQLite event/current-state schema, validate allowed states, upsert latest recipient status while retaining events, seed fixture responses, and aggregate all four response categories.
4. **WP4 — CLI integration** (depends on WP2, WP3): implement generate, validate, record, seed, and report commands; default every generate operation to `config/default.yaml`; allow explicit alternate config only.
5. **WP5 — Documentation/demo** (depends on WP4): document sidecar architecture, GoPhish attachment/result-ID handoff, offline synthetic demo, shipped-default safety proof, unavailable-component failure modes, and authorized use.
6. **WP6 — Automated verification** (depends on WP4, WP5): unit/integration tests for configuration, RFC structure/timezones, injection resistance, stable identities, RSVP aggregation, CLI behavior, and byte-preservation of shipped config; add executable acceptance runner.
7. **WP7 — Controlled static analysis archive** (depends on WP6): run existing Semgrep and ast-grep if available, archive exact command/version/result or truthful unavailable status, and do not install or replace tools.
8. **WP8 — Build handoff** (depends on WP7): execute acceptance, map evidence to A1–A10/M1–M3, and record implementation and verification notes.

## Interface contracts

```python
# gophish_ics/config.py
load_config(path: Path) -> AppConfig
require_ics_enabled(config: AppConfig) -> None

# gophish_ics/ics.py
load_campaign(path: Path) -> Campaign
generate_invite(campaign: Campaign, recipient_id: str) -> bytes
validate_invite(data: bytes) -> list[str]

# gophish_ics/store.py
initialize(db_path: Path) -> None
record_response(db_path: Path, campaign_id: str, recipient_id: str,
                response: str, occurred_at: str) -> None
seed_responses(db_path: Path, fixture_path: Path) -> int
campaign_report(db_path: Path, campaign_id: str) -> dict[str, int]

# gophish_ics/cli.py
main(argv: list[str] | None = None) -> int
```

CLI contracts:

```text
python -m gophish_ics.cli generate --campaign FILE --recipient-id ID --output FILE [--config FILE]
python -m gophish_ics.cli validate FILE
python -m gophish_ics.cli record --db FILE --campaign-id ID --recipient-id ID --response STATE --occurred-at RFC3339
python -m gophish_ics.cli seed --db FILE --fixture FILE
python -m gophish_ics.cli report --db FILE --campaign-id ID [--json]
```

Failures return nonzero with a concise stderr message; report output always includes accept, decline, tentative, none, and total. `recipient_id` is opaque and never derived from email.

## Requirement trace matrix

| Requirement | Work packages |
|---|---|
| R1 integration approach/diagram | WP5 |
| R2 field-driven ICS generator | WP2, WP4 |
| R3 valid ICS/linter tests | WP2, WP6 |
| R4 keyed RSVP telemetry | WP3, WP4, WP6 |
| R5 per-campaign report | WP3, WP4, WP6 |
| R6 disabled shipped flag + proof | WP1, WP4, WP6 |
| R7 seed data/local lab demo | WP1, WP3, WP5 |
| R8 OPSEC detection recommendations | WP5, Role 5 review |
| R9 README/authorized-use notice | WP1, WP5 |
| R10 archived scanners | WP7 |

## Test plan

| Check | Mode and evidence |
|---|---|
| A1, A7, A8, A9, M3 | Automated documentation assertions plus reviewer inspection |
| A2, A3, M2 | Generate from fixture under temporary enabled config; validate bytes, CRLF, required fields, escaping/folding, and UTC values |
| A4, A5, M1 | Seed SQLite fixture; assert stable composite keys, event history, latest state, and exact aggregate report |
| A6 | Load exact shipped config, assert refusal; hash bytes before/after enabled temporary-config demo |
| A10 | Assert both nonempty scanner archives name command, version/status, and result |

`scripts/acceptance.sh` runs the standard-library test suite, a CLI demo in a temporary directory, documentation/config/archive assertions, and exits nonzero on any failed acceptance item.

## Out of scope

- Sending email, operating an SMTP receiver, connecting to real victim mailboxes, or capturing credentials.
- Mail-security bypass, calendar-client bypass, persistence, evasion, or automatic external targeting.
- A GoPhish fork/dashboard modification; live API credentials and live campaign mutation.
- Full MIME/iMIP transport, inbound iTIP email parsing, recurring events, cancellations, or arbitrary YAML support.
- Installing/replacing static scanners during generation.
