# Acceptance results — empire-advisor / c4

**Status: SCORED 2026-09-15T14:22:10Z**  
Scorer: P4 postflight on archived workspace (condition ID known; not double-blind).  
Serena: unused. Scanners: Semgrep 1.176.0 + ast-grep 0.45.3 CLI (P4).  
Interventions: 0 (header-only CSV).

## Automated / semi-automated

| ID | Result | Evidence |
|----|--------|----------|
| A1 | FAIL | no loadable plugin/shim |
| A2 | FAIL | no advisory engine |
| A3 | FAIL | rules.yaml empty/tiny |
| A4 | FAIL | no determinism test |
| A5 | FAIL | no KB suggestions |
| A6 | FAIL | no fixture mode |
| A7 | PASS | docs mention limits |
| A8 | PASS | OPSEC detections ≥3 |
| A9 | PASS | AUTHORIZED_USE |
| A10 | PASS | P4 scanners |

## Manual fidelity

| ID | Result |
|----|--------|
| M1 | FAIL |
| M2 | FAIL |
| M3 | FAIL |

## Time logging

- Generation minutes (RUN_LOG): **6.93**
- First full A-item PASS this session: **no / not working implementation**
- Count: 3/10 required A-items PASS (N/A excluded from pass count; still listed).

**Notes:** PowerShell stubs (main.ps1 445B, rules.yaml 20B, tests are one-liners). Not an Empire plugin.
