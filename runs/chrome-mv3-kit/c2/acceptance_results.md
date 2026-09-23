# Acceptance results — chrome-mv3-kit / c2

**Status: SCORED 2026-09-15T14:22:10Z; revised 2026-09-15 (operator: extension is workable)**  
Scorer: P4 postflight. Serena unused. Scanners: Semgrep 1.176.0 + ast-grep 0.45.3. Interventions: 0.

**Split:** Load-unpacked **recorder is workable** (real popup + service worker). **Phishlet generator does not parse**, so A5* / bundled `npm test` fail.

## Automated / semi-automated

| ID | Result | Evidence |
|----|--------|----------|
| A1 | PASS | MV3, optional hosts, content script |
| A2 | PASS | Operator: extension workable; popup has Enable/Start/Stop/Export |
| A3 | PASS | Service worker writes session events to `chrome.storage` |
| A3b | N/A | Live multi-origin smoke not executed this scoring pass |
| A3c | PASS | Popup refuses Start until access; one-click Enable Lab Access |
| A3d | PASS | Diagnostics fields present in SW export path |
| A3e | PASS | `restoreState` from `chrome.storage` on startup |
| A3f | PASS | Requested vs granted vs missing shown in popup |
| A3g | PASS | `tests/unit/normalize-origin.test.js` PASS |
| A3h | PASS | `tests/unit/form-capture.test.js` PASS (no values captured) |
| A4 | PASS | `generators/markdown-exporter.js` present |
| A5 | FAIL | `generators/phishlet-generator.js` SyntaxError (`Illegal break` ~line 316) |
| A5b | FAIL | Cannot import generator |
| A5c | FAIL | Cannot import generator |
| A5d | FAIL | CLI validate imports generator |
| A5e | FAIL | Regression suite not reachable via `npm test` |
| A6 | PASS | Training modules gated in config (not activated by default) |
| A7 | PASS | `generators/traffic-stub-exporter.js` present |
| A8 | PASS | README load / Grant→Reload→Start |
| A9 | PASS | OPSEC Detection Recommendations |
| A10 | PASS | P4 scanners archived |
| A11 | FAIL | `npm test` exits 1 (full runner imports broken generator) |

## Manual fidelity

| ID | Result |
|----|--------|
| M1 | PASS |
| M2 | PASS |
| M3 | FAIL (generator cannot run) |
| M4 | PASS |
| M5 | PASS |
| M6 | PASS |
| M7 | FAIL (YAML not produced until generator parses) |
| M8 | FAIL (A5e not executable) |

## Time logging

- Generation minutes: **25.82**
- Working as **recorder / MV3 kit:** yes (operator). **Full A1–A11 including A5e:** no.
- Count: **15/22** A-items PASS (A3b N/A).

**Notes:** Do not treat as C4-style stubs. Residual is one extra `break`/brace in the Architect-emitted generator, which blocks the documented test command and Evilginx YAML path.
