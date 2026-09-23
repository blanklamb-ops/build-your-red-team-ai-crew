#!/bin/sh
: <<'ACCEPTANCE_CHECKLIST'
# ACCEPTANCE — gophish-ics

| ID | Check |
|----|-------|
| A1 | Architecture/integration approach documented in README |
| A2 | ICS generator produces `.ics` from fixture JSON/YAML |
| A3 | ICS validates via automated test or documented linter command |
| A4 | Telemetry store records at least accept + decline for fixture recipients |
| A5 | Report shows aggregated RSVP counts for a fixture campaign |
| A6 | The checked-in configuration has `ics_enabled: false`; an automated test loads that exact file and verifies generation is refused until explicitly enabled. Demo tests use a temporary override and leave the shipped config unchanged. |
| A7 | Lab demo instructions use synthetic addresses only |
| A8 | `OPSEC_CARD.md` includes Detection Recommendations (≥3 bullets) |
| A9 | Authorized-use notice in README |
| A10 | Semgrep + ast-grep outputs archived |

## Manual fidelity

| ID | Check |
|----|-------|
| M1 | Recipient identity keys stable across RSVP events |
| M2 | Timezones in ICS are explicit (not naive local ambiguity) |
| M3 | Failure modes documented when mail/calendar parts unavailable |
ACCEPTANCE_CHECKLIST

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$repo_dir/scripts/acceptance.sh"
