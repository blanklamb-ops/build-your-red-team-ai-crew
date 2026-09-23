# Acceptance results — chrome-mv3-kit / c3

**Status: automated checks passed (operator review remaining for browser smoke)**

| Check | Result | Evidence |
|-------|--------|----------|
| Generation | PASS | `stop_reason=generated`, 16.94 min, rc=0 |
| Pipeline artifacts | PASS | `pipeline/01`–`05` present |
| `npm test` | PASS | 5/5 suites (origins, lifecycle, diagnostics/export, snapshot/safety, generators/schema/E2E) |
| Phishlet CLI | PASS | `python3 generators/cli.py phishlet --input testdata/session.json --output …` wrote Evilginx-shaped scaffold (`name`, `min_ver`, `proxy_hosts`, `auth_tokens`, placeholder `credentials`/`sub_filters`) |
| Study scanners | PASS | Semgrep 0 findings · ast-grep `[]` |
| Manual Chrome multi-origin recorder smoke | DEFERRED | Operator load unpacked extension against authorized lab target |

Model: `gpt-5.6-sol` (reasoning_effort=medium). Serena: unused.
