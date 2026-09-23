# Domain Brief — chrome-mv3-kit

## Goal restatement

Success is an offline-capable, authorized-lab documentation kit that records browser-authentication **metadata only**, survives Manifest V3 worker restarts, and turns synthetic or sanitized captures into: JSON and Markdown reports, a schema-valid and placeholder-free Evilginx 2.3.0 phishlet scaffold, static page snapshots, and a commented traffic-pattern profile stub. The extension must make host authorization and incomplete coverage obvious. The generated phishlet is documentation scaffolding; operators still bind a lab domain/lure and test it within scope.

## Constraints

- Platform: Chrome/Chromium Manifest V3. The background component is a service worker, so authoritative state must live in `chrome.storage`, not globals. Host access is declared under `optional_host_permissions` and requested from a popup user gesture. Chrome documents both MV3 service workers and runtime permission requests [1][2].
- Required extension APIs: `webRequest`, `webNavigation`, `storage`, and `downloads`. `webRequest.onCompleted` must request `responseHeaders` plus `extraHeaders` so Set-Cookie names can be observed without retaining values.
- Data minimization: collect URLs, methods, status, resource/source type, header names, cookie names, and form field names/types. Never collect bodies, header/cookie values, typed/autofill values, or tokens. No off-host transmission.
- Coverage: record ordinary HTTP(S) requests as well as auth-marked traffic; preserve source diagnostics; omit non-HTTP(S) export noise; mark fallback-only or permission-gapped sessions incomplete.
- Forms: inject the declared content script only for main-frame auth-relevant completion handling and return actions, names, types, and a trivial submit label—never values.
- Generator format: Evilginx phishlet 2.3.0 structure and auto-fill variables must follow the published 2.3.0 format [3]. YAML is parsed and validated against the supplied JSON Schema; no `{{PLACEHOLDER}}` text is allowed.
- Host selection: apply the prompt’s explicit auth relevance, deny-list, registrable-domain, representative-host, and login-path rules. Never synthesize live-target recipes or unsupported `force_post`/`js_inject` behavior.
- Tooling: keep the implementation dependency-light and runnable offline after dependency installation. One top-level command must execute every test. Static scanners are a post-build controlled step and their output belongs under `../scanners/`.
- Fixtures: only synthetic `.test`/reserved data. Copy both files from `study-fixtures/` into `testdata/` byte-for-byte; A5e exercises the unchanged mixed capture.

## Prior art and interfaces

- Chrome Extensions Manifest V3 service workers: lifecycle and event-driven background execution [1].
- Chrome optional permissions API: `chrome.permissions.request()` must be called from a user gesture [2].
- Chrome `webRequest` API: request/response observation and `extraHeaders` behavior [4].
- Chrome `webNavigation` API: navigation completion fallback [5].
- Evilginx 2.3.0 phishlet file format: canonical keys and hostname auto-fill behavior [3].
- JSON Schema provides machine-checkable structural validation [6]; a real YAML parser is also required so malformed YAML cannot pass textual checks.

## Risks

- Service-worker suspension can lose sessions unless every mutation is persisted and initialization is awaited.
- Permission normalization mismatches can create silent zero-event sessions; wildcard grants must cover canonical per-origin entries during comparison.
- Callback deduplication can accidentally discard method/status fields. Merge complementary events conservatively and retain source counts.
- Chrome may suppress sensitive response headers unless the exact listener options are used; navigation fallback alone provides incomplete evidence.
- A naive host or public-suffix heuristic can promote telemetry/CDN hosts or junk experiment labels. The fixed regression fixture is the guardrail.
- YAML string escaping, schema drift, or wrong map/list shapes can create superficially plausible but unloadable output.
- Broad permissions and dual-use terminology can be misunderstood. Runtime consent, lab-only warnings, disabled training modules, and defender recommendations are required controls.
- Static snapshots can accidentally retain secrets present in DOM. Snapshot logic must sanitize active/value-bearing elements and clearly document residual review risk.

## Planning assumptions and open questions

No blocking questions remain. Assumptions: Node.js is available for a dependency-light CLI/test runner; bundled schema version `2.3.0` is authoritative for this study; public-suffix handling only needs to satisfy the supplied synthetic fixtures plus conservative rejection rules; browser-load fidelity A2/A3b remains a documented manual check where Chromium UI automation is unavailable.

## Sources

1. https://developer.chrome.com/docs/extensions/develop/concepts/service-workers
2. https://developer.chrome.com/docs/extensions/reference/api/permissions
3. https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-(2.3.0)
4. https://developer.chrome.com/docs/extensions/reference/api/webRequest
5. https://developer.chrome.com/docs/extensions/reference/api/webNavigation
6. https://json-schema.org/specification
