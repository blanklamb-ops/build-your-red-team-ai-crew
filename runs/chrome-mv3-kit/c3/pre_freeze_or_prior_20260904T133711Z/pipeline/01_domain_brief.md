# Domain Brief — Chrome MV3 Lab Documentation Kit

## Goal restatement

Success is an offline-first, authorized-lab toolkit that records a deliberately narrow description of multi-origin authentication traffic, survives Manifest V3 worker restarts, and turns synthetic or exported sessions into reviewable documentation. Operators must explicitly approve every HTTP(S) origin before recording. Exports must make gaps obvious. The phishlet output is a schema-valid Evilginx 3.x scaffold containing host/path/cookie-name metadata and conspicuous placeholders, never captured credential values or ready-to-use capture/rewrite logic. The same session also drives Markdown, static-page, and commented traffic-pattern documentation.

## Constraints

- **Platform:** Chrome/Chromium Manifest V3 extension with a service worker and popup. `webRequest`, `webNavigation`, `storage`, and `downloads` are required API permissions; broad HTTP(S) access belongs only in `optional_host_permissions` and is requested from a user gesture. Chrome says `webRequest` requires both its API permission and relevant host access, and some subresources also require initiator access ([Chrome webRequest API](https://developer.chrome.com/docs/extensions/reference/api/webRequest)).
- **Lifecycle:** authoritative requested origins, permission state, recording flag, timestamps, events, and diagnostics must live in `chrome.storage`, because service-worker globals are lost on suspension ([Chrome service-worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)).
- **Capture boundary:** store URL, method, status, resource type, event source, auth-related request-header names, and Set-Cookie names only. Never store bodies, header values, passwords, tokens, or cookies. Capture ordinary requests too. Add main-frame completion fallback without claiming it is equivalent to full `webRequest` coverage.
- **Origin handling:** accept only bare HTTP(S) origins, canonicalize them to Chrome match patterns, reject userinfo and non-root paths, compare the complete requested/granted sets, and retain redirect-origin gaps in diagnostics.
- **Generation:** Node.js CLI usable offline after dependencies are installed. YAML must be parsed by a real parser and validated with JSON Schema. Evilginx documents phishlets as YAML and defines `proxy_hosts`, `auth_tokens`, `auth_urls`, credentials, and login sections ([Evilginx phishlet format](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-%282.3.0%29)); its implementation expects fields including `auto_filter` and login details ([Evilginx phishlet source](https://github.com/kgretzky/evilginx2/blob/master/core/phishlet.go)).
- **Domain grouping:** use Public Suffix List semantics through a maintained library, not last-two-label logic.
- **Safety/UI:** optional training demonstrations default off and require `lab_unsafe_modules=true`. No network exfiltration exists. Fixtures use reserved `.test`/example names only.
- **Verification:** one top-level test command covers normalization, complete permission checking, lifecycle restoration, export diagnostics, generator safety, YAML/Schema validation, snapshots, and traffic stubs. Existing Semgrep and ast-grep tools are run only after implementation; no scanners are installed.

## Prior art and interfaces

- Chrome Extensions MV3 APIs: [`chrome.permissions`](https://developer.chrome.com/docs/extensions/reference/api/permissions), [`chrome.webRequest`](https://developer.chrome.com/docs/extensions/reference/api/webRequest), [`chrome.webNavigation`](https://developer.chrome.com/docs/extensions/reference/api/webNavigation), [`chrome.storage`](https://developer.chrome.com/docs/extensions/reference/api/storage), and [`chrome.downloads`](https://developer.chrome.com/docs/extensions/reference/api/downloads).
- Evilginx 2.3+/3.x phishlet YAML vocabulary and loader, used only as a structural interoperability target; generated content remains an inert scaffold.
- JSON Schema (2020-12), Ajv, and js-yaml for machine validation; `tldts` for Public Suffix List-based registrable-domain parsing.
- Chrome match patterns (`scheme://host/path`) for runtime origin grants ([Chrome match patterns](https://developer.chrome.com/docs/extensions/develop/concepts/match-patterns)).

## Risks

- Missing host permission can silently yield zero or partial request events; the UI and export must fail/warn explicitly.
- Worker suspension can split or erase sessions unless every mutation is serialized to storage.
- Request/response/navigation callbacks can duplicate a load; careless deduplication can also erase method or status.
- Header/cookie values may leak through generic fixture fields; independent field-aware secret checks are required.
- YAML serializers can quote or alter placeholders; validation must inspect parsed values.
- Heuristics can misclassify telemetry, login host, or registrable domain; defaults must be visible and configurable.
- Static snapshots can preserve sensitive content or active code; snapshots should strip scripts and report limitations.
- Manual Chrome fidelity and scanner availability are environmental checks and must not be falsely reported as automated passes.

## Open questions and assumptions

No planning blocker remains. Assumptions: Node.js 18+ is available; dependencies can be installed before entering an air gap; synthetic fixtures represent the automated flow; manual A2/A3b checks remain explicitly documented because CI cannot drive a clean interactive Chromium profile.
