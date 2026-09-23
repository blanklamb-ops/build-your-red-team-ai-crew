# Acceptance results — empire-advisor / c1

**Status: SCORED 2026-09-15T14:22:10Z**  
Scorer: P4 postflight on archived workspace (condition ID known; not double-blind).  
Serena: unused. Scanners: Semgrep 1.176.0 + ast-grep 0.45.3 CLI (P4).  
Interventions: 0 (header-only CSV).

## Automated / semi-automated

| ID | Result | Evidence |
|----|--------|----------|
| A1 | PASS | documented shim |
| A2 | PASS |  |
| A3 | PASS | rules.yaml ≥10 |
| A4 | PASS | determinism |
| A5 | PASS | KB citation |
| A6 | PASS | offline fixtures |
| A7 | PASS |  |
| A8 | PASS |  |
| A9 | PASS |  |
| A10 | PASS |  |

## Manual fidelity

| ID | Result |
|----|--------|
| M1 | PASS |
| M2 | PASS |
| M3 | PASS |

## Time logging

- Generation minutes (RUN_LOG): **11.94**
- First full A-item PASS this session: **yes**
- Count: 10/10 required A-items PASS (N/A excluded from pass count; still listed).

**Notes:** test_advisor.py 12 passed. Shim not live Empire. Some pass in unused paths.
