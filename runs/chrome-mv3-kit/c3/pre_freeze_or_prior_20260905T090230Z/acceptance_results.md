# Acceptance results — chrome-mv3-kit / c3

**Status: automated A5e + npm test passed (2026-09-05 Choice-1 regen)**

| Check | Result | Evidence |
|-------|--------|----------|
| Generation | PASS | 33.35 min, returncode 0, five pipeline artifacts written |
| `npm test` | PASS | 4 JS suites + 4 Python tests including `test_a5e_production_generator` |
| A5e mixed-capture | PASS | `proxy_hosts` = idp/wallet/authcdn/corp.test; `login.path=/ppsecure/post.srf`; credentials loginfmt+passwd; no junk PSL |
| extraHeaders | PASS | `webRequest.onCompleted` uses `['responseHeaders', 'extraHeaders']` |
| R12 fixture | PASS | `testdata/regression-mixed-capture.json` byte-identical to `study-fixtures/` |
| Rubric score | PENDING | Not a completed P4 score vs C1/C2/C4 |

Notes: generator is Python (`publicsuffix2`). `credentials` is Evilginx map shape, not a YAML list. Manual unpacked-extension smoke not run in this pass.
