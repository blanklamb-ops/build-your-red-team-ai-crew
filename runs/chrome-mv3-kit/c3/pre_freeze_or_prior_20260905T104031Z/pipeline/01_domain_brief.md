# Domain Brief — chrome-mv3-kit

## Goal restatement

Deliver an offline-first Chrome Manifest V3 documentation kit for an authorized lab. An operator must deliberately grant HTTP(S) host access, record request/response and navigation metadata across all approved flow origins, capture only form field names/types (never values), and export a diagnostic-rich JSON/Markdown record. Headless generators must convert synthetic captures into a conservative Evilginx 2.3.0-format YAML documentation artifact and a commented traffic-pattern skeleton. The generated YAML must reflect observed metadata, exclude non-auth/unsafe hosts, leave unevidenced rewrite/search logic as explicit placeholders, and validate against a shipped JSON Schema. Static snapshots and clearly separated training-awareness modules complete the kit.

## Constraints

- Platform: unpacked Chrome/Chromium Manifest V3 extension with a service worker, popup, content script, `webRequest`, `webNavigation`, `storage`, and `downloads`.
- Host access: `http://*/*` and `https://*/*` are declared only in `optional_host_permissions` and requested from a popup button/user gesture. Chrome documents that optional host permissions are runtime-granted and that `permissions.request()` must be invoked from a user gesture ([Chrome permissions API](https://developer.chrome.com/docs/extensions/reference/api/permissions)).
- Visibility: `webRequest` sees only hosts for which the extension has permission. `Set-Cookie` is hidden unless `extraHeaders` is requested, so `onCompleted` must request both `responseHeaders` and `extraHeaders` ([Chrome webRequest API](https://developer.chrome.com/docs/extensions/reference/api/webRequest)).
- Persistence: service-worker globals are caches only; requested origins, recording status, events, timestamps, and diagnostics live in `chrome.storage.local` and survive worker restart.
- Data minimization: store URLs/methods/status/resource type, header names, Set-Cookie names, and DOM form field names/types; never header values, bodies, input values, passwords, tokens, or autofill content.
- Offline/air-gap: generator, YAML parser, schema validator, tests, snapshots, and fixture workflows must run locally without network calls.
- Inputs/outputs: JavaScript/Node-based tooling is assumed to minimize build complexity. Inputs are capture JSON. Outputs are JSON, Markdown, YAML, static HTML/report, and a commented documentation profile.
- Fixtures: only `.test`, `example.com`, or reserved test IP material. The harness-provided regression fixture and schema are copied byte-for-byte into `testdata/` and `schemas/` respectively.
- Scope: no live targeting, credential values, bypasses, replay, production implant, `force_post`, `js_inject`, or invented body/JavaScript rewrite recipes.

## Prior art and alignment

- Chrome Extensions Manifest V3 and its permissions model define the service-worker architecture and runtime optional-host grant flow ([Declare permissions](https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions)).
- Chrome `webRequest` supplies observable request/response metadata, subject to host permission and `extraHeaders` constraints ([webRequest reference](https://developer.chrome.com/docs/extensions/reference/api/webRequest)).
- Evilginx’s 2.3.0 format defines `proxy_hosts`, object-shaped `sub_filters`, cookie-name `auth_tokens`, `credentials`, `auth_urls`, and the replacement of deprecated `landing_path` by `login`; the tool aligns structurally while remaining a lab documentation generator ([Phishlet File Format 2.3.0](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-%282.3.0%29)).
- JSON Schema plus a real YAML parser provides structural validation; regex/substring checks alone are insufficient.

## Risks

- Missing host grants silently yield incomplete captures; prevent Start and surface exact missing origins.
- Worker suspension can lose sessions unless every state change is persisted atomically.
- Paired callbacks and navigation fallback can duplicate events or erase richer method/status data during deduplication.
- Set-Cookie names may disappear if `extraHeaders` is omitted.
- DOM inspection can accidentally collect values; content-script output must use an explicit allowlist schema.
- Naive hostname grouping can promote telemetry/CDNs or malformed edge labels into proxy hosts. Deny rules, hex-label rejection, and deterministic registrable-domain handling are mandatory.
- Naive login selection may choose OAuth authorize, silent sign-in, or static paths rather than the password form action.
- YAML serialization can corrupt placeholder quoting or emit wrong list/map shapes; schema validation must gate success.
- URLs can themselves contain sensitive query data. The prompt requires URLs, so exports need warnings and secret-value rejection before downstream generation.
- Manual A2/A3b checks cannot be fully proven headlessly and must be reported honestly.

## Planning assumptions and open questions

- **Assumption:** Node.js is available; dependencies should be vendored or limited to what the workspace can install/use offline.
- **Assumption:** the supplied `phishlet-schema-2.3.0.json` is the canonical study schema and will be copied unchanged.
- **Assumption:** a compact built-in registrable-domain implementation covering synthetic fixtures is acceptable; it must explicitly handle required edge suffix rules rather than claim full Public Suffix List coverage.
- No blocking open question remains. Manual Chromium smoke checks will be documented and scored separately from automated acceptance.
