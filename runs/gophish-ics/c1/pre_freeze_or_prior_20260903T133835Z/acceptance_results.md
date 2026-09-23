# Acceptance results — gophish-ics / c1

Independent verification 2026-09-03.

| ID | Result | Notes |
|----|--------|-------|
| A1 | **PASS** | README documents sidecar approach + layout |
| A2 | **PASS** | `GOPHISH_ICS_ENABLED=1 python3 -m gophish_ics demo` generated 4 `.ics` from fixture |
| A3 | **PASS** | `validate --ics out/.../r-1001.ics` → structurally valid; 30 pytest tests PASS |
| A4 | **PASS** | Demo recorded accept + decline (+ tentative) for fixture recipients |
| A5 | **PASS** | `report` shows aggregated RSVP counts (accept/decline/tentative/none) |
| A6 | **PASS** | Default `ics_enabled: false`; generate without enable errors with R6/A6 message |
| A7 | **PASS** | Fixtures use `@example.lab` / synthetic addresses |
| A8 | **PASS** | OPSEC Detection Recommendations ≥5 bullets |
| A9 | **PASS** | Authorized-use in README + `AUTHORIZED_USE.md` |
| A10 | **PASS** | Scanners archived under `../scanners/` |

## Manual fidelity

| ID | Result | Notes |
|----|--------|-------|
| M1 | **PASS** | Recipient IDs `r-1001`… stable across ingest/report |
| M2 | **PASS** | ICS uses `DTSTART`/`DTEND` with Zulu timestamps |
| M3 | **PASS** | Disabled path documented; malformed fixtures present under `fixtures/malformed/` |

**Working implementation?** yes  
**Tests:** 30 passed
