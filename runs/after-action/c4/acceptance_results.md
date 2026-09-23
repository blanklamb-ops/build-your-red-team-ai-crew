# Acceptance results — after-action / c4

**Status: SCORED 2026-09-15T14:22:10Z**  
Scorer: P4 postflight on archived workspace (condition ID known; not double-blind).  
Serena: unused. Scanners: Semgrep 1.176.0 + ast-grep 0.45.3 CLI (P4).  
Interventions: 0 (header-only CSV).

## Automated / semi-automated

| ID | Result | Evidence |
|----|--------|----------|
| A1 | FAIL | CLI cannot run |
| A2 | FAIL | adapters import missing models |
| A3 | FAIL | no fixture correlation |
| A4 | FAIL | no client report |
| A5 | FAIL | no internal report |
| A6 | FAIL | no planted-secret fixture |
| A7 | FAIL | undocumented |
| A8 | PASS | OPSEC_CARD.md exists (thin detections) |
| A9 | FAIL | README lacks authorized-use |
| A10 | PASS | P4 scanners |

## Manual fidelity

| ID | Result |
|----|--------|
| M1 | FAIL |
| M2 | FAIL |
| M3 | FAIL |

## Time logging

- Generation minutes (RUN_LOG): **2.91**
- First full A-item PASS this session: **no / not working implementation**
- Count: 2/10 required A-items PASS (N/A excluded from pass count; still listed).

**Notes:** pytest cannot collect: missing src.models; main.py uses List without import; no testdata/fixture_engagement.
