# Operational Constraints — chrome-mv3-kit

## Runtime environment

- Target a current desktop Chrome/Chromium profile with developer mode and unpacked-extension loading. The extension runs without elevated OS privileges.
- The CLI/test path assumes Node.js 18+ and local filesystem access. Generation and validation must work offline; no runtime CDN, telemetry, remote API, or package fetch is permitted.
- Browser networking is operator-driven and limited to expressly authorized lab origins. The kit neither navigates to targets nor provisions Evilginx infrastructure.
- Treat A2 and A3b as manual browser checks. Everything else should be deterministic and runnable with `npm test` in an air-gapped workspace.

## Secrets and evidence handling

- Never persist request/response bodies, header values, cookie values, DOM input values, autofill data, passwords, bearer strings, session tokens, real identities, engagement IDs, or real client hostnames.
- Keep only header names and parsed Set-Cookie names. Content-script messages must be constructed from `name`, normalized `type`, resolved form action, and a trivial visible submit label; the production code must never read `.value`.
- Generated captures, Markdown, snapshots, and YAML are evidence artifacts. Store locally, apply engagement retention policy, and review before sharing. Static snapshots can retain page text and URLs even after form values are stripped.
- The generator must reject secret-looking values in free-text/capture fields while allowing cookie names and canonical UUID session identifiers. Rejection is fail-closed with a useful field location.
- Repository fixtures remain synthetic (`.test`/reserved examples); study fixtures are copied unchanged and must not be “cleaned up.”

## Operator workflow

1. Confirm written authorization and enumerate every origin in the lab redirect chain.
2. Load the unpacked extension. In the popup choose **Enable lab access**, approve the optional HTTP(S) host permission, and optionally enter the narrower complete origin set.
3. Reload the extension if Chrome requires it. Confirm requested, granted, and missing origins are visible.
4. Press Start only after the complete requested set passes the permission gate, then browse the authorized flow. Stop after the smallest useful capture.
5. Inspect coverage diagnostics before export. A fallback-only session or any observed permission gap is incomplete and must not be represented as a full auth flow.
6. Export JSON/Markdown locally, then run the headless generator/validator and traffic stub against the sanitized capture. Configure domain/lures separately and lab-test any phishlet; generator success is not live-target assurance.
7. Enable awareness demos only in a controlled training environment after explicitly setting `lab_unsafe_modules=true`.

## Safety defaults

- Recording defaults OFF after install. Training modules default OFF and require the exact explicit configuration flag.
- Optional global HTTP(S) host access is requested only from the popup user gesture; installation grants none. Start fails if requested permission is missing.
- Exports are local downloads using data URLs. No fetch/XHR/WebSocket or off-host exfiltration code.
- Host selection is deny-by-default for telemetry, admin, API, object storage, generic CDN, edge, and suspicious long-label hosts. `--include-host` is the only explicit, auditable override and does not bypass secret rejection.
- Unsupported or insufficient captures fail clearly. Heuristic `login`/`passwd` keys are allowed only when no password form exists and must be disclosed in coverage comments.
- Snapshot output is inert static documentation: strip scripts, event-handler attributes, form values, active form submission behavior, and remote-loading elements where practical. Awareness demonstrations are separately labeled.

## Degradation modes

- Service-worker restart: restore the complete versioned state from storage before handling events; storage errors stop recording and surface an error rather than continuing ephemerally.
- Missing host access: refuse Start. A newly observed redirect origin creates a permission-gap warning and incomplete export.
- Hidden/unavailable response headers: retain request/navigation metadata, report source counts, and mark fallback-only coverage incomplete. Never infer cookies.
- Non-HTTP(S) events: omit them from capture export and diagnostics origin normalization without throwing.
- No forms/no password form: emit an empty `form_fields` list; generator uses disclosed heuristic credential keys, never OTP names as passwords.
- No cookie/path evidence: produce empty `auth_tokens`/`auth_urls` lists where structurally allowed; fail if no workable proxy/login host exists.
- Offline operation: all core functions remain available. Links in documentation may be inaccessible, but no build/test/generation path depends on them.
- Scanner unavailable: do not install or substitute it; archive a timestamped “not available” result and continue other verification. Do not claim the scan passed.

## Non-negotiable plan deltas for the Architect

- **WP1:** preserve both study fixture files byte-for-byte and record hash equality in tests.
- **WP2:** make state transitions storage-first/awaited; store diagnostics with state; merge paired callbacks without losing method/status; filter schemes before origin parsing.
- **WP3:** keep globals non-authoritative; require full-set permission before Start; show all requested/granted/missing origins; include the exact `onCompleted` extra-info spec; use local scripts only and data-URL downloads.
- **WP3/WP5:** prohibit reading form values; sanitize snapshots into inert files; keep awareness UI and handlers gated and visibly labeled.
- **WP4:** implement explicit allow/deny evidence and login ranking from R4g; reject secrets before YAML serialization; emit no attack tuning beyond capture-derived 2.3.0 scaffolding.
- **WP6:** inspect production functions, listener registration, and no-value behavior. Mock restart with a new module/controller instance over the same storage object. Exercise every schema mutation and every A5e bullet.
- **WP7:** state the exact grant/reload/start workflow, evidence-retention caution, incomplete-coverage semantics, and remaining domain/lure/lab-test work.
- **WP8:** never modify tooling during the run; distinguish scanner success, findings, and absence.
- **WP9:** document local storage keys, downloaded artifacts, extension ID/profile traces, permission prompts, `webRequest`/navigation patterns, and generated phishlet/profile files as detection-relevant artifacts.
