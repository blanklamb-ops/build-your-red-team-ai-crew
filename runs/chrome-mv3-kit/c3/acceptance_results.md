# Acceptance results — chrome-mv3-kit / c3

**Status: SCORED 2026-09-15T14:22:10Z**  
Scorer: P4 postflight on archived workspace (condition ID known; not double-blind).  
Serena: unused. Scanners: Semgrep 1.176.0 + ast-grep 0.45.3 CLI (P4).  
Interventions: 0 (header-only CSV).

## Automated / semi-automated

| ID | Result | Evidence |
|----|--------|----------|
| A1 | PASS | MV3 optional hosts + content script |
| A2 | PASS | Real popup; live Chromium not repeated |
| A3 | PASS | Export tests |
| A3b | N/A | Live multi-origin smoke not executed this pass |
| A3c | PASS | Permission/UI tests |
| A3d | PASS | Coverage diagnostics tests |
| A3e | PASS | Lifecycle tests |
| A3f | PASS | Origin set tests |
| A3g | PASS | Normalization tests |
| A3h | PASS | Form tests |
| A4 | PASS | Export tests |
| A5 | PASS | Generator tests |
| A5b | PASS | 2.3.0 shape tests |
| A5c | PASS | Validation tests |
| A5d | PASS | Schema mutation tests |
| A5e | PASS | regression suite PASS |
| A6 | PASS | safety suite |
| A7 | PASS | generator/traffic tests |
| A8 | PASS | README |
| A9 | PASS | OPSEC detections |
| A10 | PASS | P4 scanners archived |
| A11 | PASS | node tests/run.js |

## Manual fidelity

| ID | Result |
|----|--------|
| M1 | PASS |
| M2 | PASS |
| M3 | PASS |
| M4 | PASS |
| M5 | PASS |
| M6 | PASS |
| M7 | PASS |
| M8 | PASS |

## Time logging

- Generation minutes (RUN_LOG): **18.02**
- First full A-item PASS this session: **no / not working implementation**
- Count: 20/22 required A-items PASS (N/A excluded from pass count; still listed).

**Notes:** node tests/run.js: 9/9 suites PASS including regression. Extra permissions scripting/activeTab vs prompt minimum.
