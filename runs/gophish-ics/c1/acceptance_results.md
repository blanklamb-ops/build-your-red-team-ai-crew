# Acceptance results — gophish-ics / c1

**Status: SCORED 2026-09-15T14:22:10Z**  
Scorer: P4 postflight on archived workspace (condition ID known; not double-blind).  
Serena: unused. Scanners: Semgrep 1.176.0 + ast-grep 0.45.3 CLI (P4).  
Interventions: 0 (header-only CSV).

## Automated / semi-automated

| ID | Result | Evidence |
|----|--------|----------|
| A1 | PASS | README architecture |
| A2 | PASS | ICS from fixture |
| A3 | PASS | icalendar validation tests |
| A4 | PASS | accept+decline telemetry tests |
| A5 | PASS | aggregate RSVP report tests |
| A6 | PASS | ics_enabled false in shipped config + tests |
| A7 | PASS | synthetic testdata |
| A8 | PASS | OPSEC detections |
| A9 | PASS | authorized-use in README |
| A10 | PASS | P4 scanners |

## Manual fidelity

| ID | Result |
|----|--------|
| M1 | PASS |
| M2 | PASS |
| M3 | PASS |

## Time logging

- Generation minutes (RUN_LOG): **7.2**
- First full A-item PASS this session: **yes**
- Count: 10/10 required A-items PASS (N/A excluded from pass count; still listed).

**Notes:** pytest 12 passed (icalendar). Sidecar Python rather than GoPhish fork.
