# Domain brief — chrome-mv3-kit

## Goal restatement

Deliver an authorized-lab Chrome Manifest V3 documentation kit that records authentication-flow metadata without credential or token values, survives service-worker restarts, exports JSON and Markdown with honest coverage diagnostics, and turns those observations into a schema-valid Evilginx 3.x phishlet and a commented traffic-pattern stub. The phishlet must be capture-faithful: populate observable hosts, cookie names, auth paths, login target, and form field names; exclude irrelevant/unsafe hosts; and reserve placeholders only for `sub_filters` and `credentials.search`. Static snapshots and explicitly gated training demonstrations complete the kit. Success is the executable checklist in `ACCEPTANCE.md`, including the unchanged mixed-capture regression.

## Constraints

- Platform: Chrome/Chromium Manifest V3, an event-driven service worker, popup UI, and a declarative content script. Required API permissions are `webRequest`, `webNavigation`, `storage`, and `downloads`; broad HTTP(S) host access is optional and requested only from a user gesture. Chrome documents that host permissions enable `webRequest` visibility and that optional permissions should be requested at runtime from a user gesture ([permissions](https://developer.chrome.com/docs/extensions/reference/api/permissions), [declaration model](https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions)).
- Capture: local storage only; URL/method/status/resource type, header names, cookie names, and DOM form names/types, never values or bodies. `onCompleted` must request `responseHeaders` and `extraHeaders`; Chrome notes `Set-Cookie` is hidden without `extraHeaders` ([webRequest](https://developer.chrome.com/docs/extensions/reference/api/webRequest)).
- Lifecycle: `chrome.storage.local` is authoritative for origins, recording state, events, times, and diagnostics. Chrome service workers are intentionally short-lived and lose globals, so persistent storage is required ([service-worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)).
- Offline/air-gap: all runtime code and generation dependencies must be local; no off-host exfiltration or remotely hosted extension code. Node.js is the practical generator/test language; use a real YAML parser, JSON Schema validator, and PSL implementation.
- Output policy: synthetic `.test`/example fixtures only. Evilginx output is documentation for an authorized lab, not a working live-target recipe. The upstream format describes phishlet sections such as `proxy_hosts`, `sub_filters`, `auth_tokens`, `credentials`, and `login` ([Evilginx phishlet format](https://help.evilginx.com/community/phishlet-format)).
- Frozen process: five artifacts in order; unchanged study fixture copied byte-for-byte; static scanners run only after implementation and archived outside/alongside the workspace as specified.

## Prior art and interfaces

- Chrome Extensions MV3 manifest, service worker, `webRequest`, `webNavigation`, `permissions`, `storage`, `downloads`, and content-script APIs: https://developer.chrome.com/docs/extensions/
- Chrome match patterns, used for canonical optional origins: https://developer.chrome.com/docs/extensions/develop/concepts/match-patterns
- Evilginx community phishlet format: https://help.evilginx.com/community/phishlet-format
- YAML 1.2 and `js-yaml` for serialization/parsing: https://yaml.org/spec/1.2.2/ and https://github.com/nodeca/js-yaml
- JSON Schema Draft 2020-12 and Ajv validation: https://json-schema.org/draft/2020-12 and https://ajv.js.org/
- Public Suffix List semantics via `tldts`, needed to avoid naive last-two-label grouping: https://github.com/remusao/tldts

## Risks

- Missing/partial host grants silently produce a false-empty capture; start must compare the full requested set and exports must expose gaps.
- MV3 suspension can lose or reorder events; storage-backed, serialized updates and restart tests are essential.
- `webRequest` callbacks can duplicate request/response records, while navigation fallback lacks method/status; deduplication must merge rather than discard richer data.
- Header or DOM handling can accidentally retain values. Data shaping must use allowlists and secret-value rejection, and tests must prove input values never cross the boundary.
- Naive domain parsing and “cookie means auth host” heuristics admit Graph/admin/telemetry/CDN traps. PSL grouping plus explicit deny/ranking rules are mandatory.
- The first OAuth URL or a savestate form can outrank the actual credential POST; password-form action must win.
- YAML emitted by hand can create null arrays or structurally invalid maps; parse and schema-validate generated output.
- Snapshotting may preserve sensitive rendered content. Warn operators, keep local, and make demos separately gated/off by default.

## Open questions and assumptions

No planning blocker remains. Assumptions: a current Node.js/npm runtime is available; dependencies may be installed from the existing project environment during build but the finished extension performs no remote code loading; manual A2/A3b checks are documented and scored separately because this shell cannot exercise a GUI browser. The supplied regression fixture is authoritative where generic heuristics conflict.
