# Acceptance results — chrome-mv3-kit / c1

**Status: SCORED 2026-09-15T14:22:10Z**  
Scorer: P4 postflight on archived workspace (condition ID known; not double-blind).  
Serena: unused. Scanners: Semgrep 1.176.0 + ast-grep 0.45.3 CLI (P4).  
Interventions: 0 (header-only CSV).

## Automated / semi-automated

| ID | Result | Evidence |
|----|--------|----------|
| A1 | PASS | extension/manifest.json MV3, optional hosts, content script |
| A2 | PASS | Real popup UI (~4KB); live Chromium load not repeated in P4 |
| A3 | PASS | Covered by automated export tests |
| A3b | N/A | Live multi-origin recorder smoke not executed this scoring pass |
| A3c | PASS | Automated UI/permission tests in suite |
| A3d | PASS | Diagnostics tests in suite |
| A3e | PASS | Lifecycle/persistence tests |
| A3f | PASS | Grant/reload tests |
| A3g | PASS | Idempotent origin tests |
| A3h | PASS | Form metadata tests |
| A4 | PASS | Markdown export tests |
| A5 | PASS | Generator+schema tests |
| A5b | PASS | 2.3.0 map credentials / object sub_filters |
| A5c | PASS | E2E fixture tests |
| A5d | PASS | Mutation validator tests |
| A5e | PASS | 12/12 regression tests |
| A6 | PASS | lab_unsafe_modules default tests |
| A7 | PASS | Traffic stub exporter tests |
| A8 | PASS | README load order + 2.3.0 |
| A9 | PASS | OPSEC Detection Recommendations ≥3 |
| A10 | PASS | P4 scanners archived |
| A11 | PASS | node tests/run-all-tests.js |

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

- Generation minutes (RUN_LOG): **16.64**
- First full A-item PASS this session: **no / not working implementation**
- Count: 20/22 required A-items PASS (N/A excluded from pass count; still listed).

**Notes:** npm test 71/71 including A5e. A3b live multi-origin smoke not re-run this session. Residual F-2026-09-05-01 is live-capture vs fixture.
