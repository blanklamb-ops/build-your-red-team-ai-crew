# Role 1 — Domain Brief

## Goal restatement

Success is an authorized-lab documentation kit whose Chrome Manifest V3 extension records a durable, local-only account of browser authentication flows without recording credential or cookie values. From synthetic or recorder-exported metadata, headless tools must create validated JSON/Markdown reports, a capture-faithful Evilginx 3.x YAML document, a commented traffic-pattern stub, and static page snapshots. The extension must make access and coverage explicit: the operator grants all required HTTP(S) origins from a user gesture, reloads if needed, starts recording, and can tell when redirects or service-worker suspension made a capture incomplete. Training demonstrations remain separately gated and off by default.

## Constraints

- **Platform/API:** Chrome Manifest V3 with a service worker, popup, content script, `webRequest`, `webNavigation`, `storage`, and `downloads`. Chrome requires both `webRequest` and host permission to observe requests; visibility is bounded by access to the requested URL and, for subresources, its initiator ([Chrome webRequest](https://developer.chrome.com/docs/extensions/reference/api/webRequest)). Host patterns therefore belong in `optional_host_permissions` and must be requested through `chrome.permissions.request` from the popup’s user gesture ([Chrome permissions](https://developer.chrome.com/docs/extensions/reference/api/permissions)).
- **Header fidelity:** `onCompleted` must request `responseHeaders` and `extraHeaders`; Chrome otherwise withholds `Set-Cookie` ([Chrome webRequest](https://developer.chrome.com/docs/extensions/reference/api/webRequest)). Store only header names and parsed Set-Cookie names, never values or bodies.
- **Lifecycle:** MV3 workers are terminated when idle, so globals cannot be authoritative; state-changing handlers must load/update `chrome.storage.local` ([service-worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)).
- **DOM boundary:** form action, control name/type, and a trivial submit label may be read by a content script, which runs in a page context while using extension messaging; values are forbidden ([Chrome content scripts](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts)).
- **Implementation/runtime assumption:** use dependency-light Node.js CommonJS for generators/tests, `js-yaml` for parsing, Ajv for JSON Schema, and `tldts` for Public Suffix List-aware registrable-domain grouping. npm dependencies may be installed during build if already available from the configured registry; final operation and fixtures must work locally.
- **Offline/air-gap:** capture and generation never send data off-host. Runtime assets and schemas are local. Browser pages themselves may be lab-network pages; tests use only `example.com`, `.test`, and synthetic data.
- **Scope:** only PROMPT.md outputs. No live IdP recipes, traffic interception, replay, `force_post`, `js_inject`, invented regexes, or scanner replacement.

## Prior art and interfaces

- Chrome’s [webRequest](https://developer.chrome.com/docs/extensions/reference/api/webRequest), [webNavigation](https://developer.chrome.com/docs/extensions/reference/api/webNavigation), [permissions](https://developer.chrome.com/docs/extensions/reference/api/permissions), and [content-script](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts) APIs define capture and permission interfaces.
- Evilginx’s upstream loader defines `proxy_hosts`, `auth_tokens`, `auth_urls`, `credentials`, and `login`; its loader enforces required sections and host consistency ([upstream source](https://github.com/kgretzky/evilginx2/blob/master/core/phishlet.go)). The older official format reference documents list-shaped cookie tokens and one landing host ([format reference](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-%282.2.0%29)). PROMPT.md deliberately fixes the required top-level contract, including `name` and string-list `sub_filters`; the shipped schema is authoritative for this kit.
- The [Public Suffix List](https://publicsuffix.org/list/) supplies boundaries needed to group hosts by registrable domain rather than by naive last-two-label splitting.
- JSON Schema plus Ajv provides structural validation; `js-yaml` supplies real YAML parsing rather than substring checks.

## Risks

- Missing or partial host grants silently suppress request events; redirect targets can remain invisible. Mitigate with full-set permission comparison, navigation fallback, origin diagnostics, and forced incomplete coverage.
- Duplicate request/response/navigation callbacks can overstate activity, while aggressive deduplication can erase method/status/cookie evidence. Merge only paired records with stable keys and retain source counts.
- Worker shutdown can race writes. Serialize storage updates and test teardown/restart.
- DOM capture can accidentally include secrets if generic serialization is used. Construct allowlisted objects from `name`, normalized `type`, action URL, and submit label only.
- Naive host filtering, suffix grouping, path selection, or username substring matching can produce invalid or misleading YAML. Use explicit exclusions, PSL logic, static/telemetry path rejection, and exact case-insensitive username priorities.
- Snapshot HTML may retain page-displayed sensitive data. Warn operators, keep capture local, and report snapshot scope; never auto-enable training modules.

## Open questions and assumptions

No planning blocker remains. Assumptions: Chromium supports the documented MV3 APIs; Node.js/npm are present for headless tooling; static manual checks (unpacked load and two-origin smoke) are documented but cannot be truthfully automated without a browser/user gesture. Scanner binaries are treated as preinstalled controlled inputs—absence is recorded, not repaired.
