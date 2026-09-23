# Domain Brief — chrome-mv3-kit

## Goal restatement

Success is a lab-only Chrome Manifest V3 documentation kit that records capture metadata—not secrets—from authorized, multi-origin authentication flows; survives service-worker restarts; reports capture coverage honestly; and exports JSON, Markdown, a traffic-pattern documentation stub, static page snapshots, and a capture-faithful Evilginx 2.3.0 YAML file. The phishlet must use observed hosts, cookie names, auth paths, and password-form field names, exclude non-auth/telemetry/CDN hosts under the stated gold-kit rules, validate against the shipped schema, and leave unobservable body/JavaScript substitutions as structured placeholders. One documented test command must exercise all automated acceptance areas, including the unchanged mixed-capture regression fixture.

## Constraints

- Platform: unpacked Chrome/Chromium MV3 extension with an event-driven service worker, popup, content script, and local CLI generators. Required API permissions are `webRequest`, `webNavigation`, `storage`, and `downloads`; HTTP(S) hosts are declared only in `optional_host_permissions` and requested from a user gesture. Chrome documents both runtime optional host requests and the user-gesture requirement ([permissions API](https://developer.chrome.com/docs/extensions/reference/api/permissions)).
- Capture: every request may contribute URL/method/type/status metadata, but only header names and Set-Cookie names may be retained. Chrome hides `Set-Cookie` from `webRequest` unless `extraHeaders` is requested, and host visibility depends on granted host permissions ([webRequest API](https://developer.chrome.com/docs/extensions/reference/api/webRequest)).
- Lifecycle: persisted storage, not worker globals, is authoritative because MV3 workers are repeatedly terminated. Chrome explicitly recommends `chrome.storage` for state across worker sessions ([service-worker events](https://developer.chrome.com/docs/extensions/get-started/tutorial/service-worker-events), [storage API](https://developer.chrome.com/docs/extensions/reference/api/storage)).
- Form capture: declarative content script collects only form action, field name/type, and trivial submit labels; never values. It communicates metadata to the worker using extension messaging.
- Output format: Evilginx 2.3.0 phishlets are YAML with `author`, `min_ver`, `proxy_hosts`, `sub_filters`, `auth_tokens`, `credentials`, `auth_urls`, and `login`; the upstream format describes `login` as domain/path and credentials as username/password mappings ([Evilginx 2.3.0 format](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-%282.3.0%29)). Project-specific schema rules are stricter where `PROMPT.md` requires safe placeholders and forbids unsupported keys.
- Offline/air-gap: no capture exfiltration, remote runtime dependencies, live lookups, or scanner installation. Generators and validation operate locally on JSON fixtures. Static analysis is a controlled post-run command whose outputs go under `../scanners/`.
- Scope: synthetic `.test`/example fixtures and authorized lab traffic only. No live targeting, credential values, token bodies, bypasses, replay, or invented rewrite recipes.

## Prior art and interfaces

- Chrome Extensions Manifest V3 APIs: [`chrome.webRequest`](https://developer.chrome.com/docs/extensions/reference/api/webRequest), [`chrome.webNavigation`](https://developer.chrome.com/docs/extensions/reference/api/webNavigation), [`chrome.storage`](https://developer.chrome.com/docs/extensions/reference/api/storage), [`chrome.permissions`](https://developer.chrome.com/docs/extensions/reference/api/permissions), downloads, and content-script messaging.
- Evilginx upstream [Phishlet File Format 2.3.0](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-%282.3.0%29), aligned only as a serialization interface; this kit is not a deployment guide.
- JSON Schema for structural validation and a real YAML parser. The study-owned `phishlet-schema-2.3.0.json` is the conformance reference.
- Public Suffix List behavior is needed conceptually for registrable-domain grouping, but offline deterministic handling of the synthetic fixture suffixes is sufficient; no network lookup is allowed at runtime.

## Risks

- Missing/partial optional grants yield silent zero-event or fallback-only captures unless Start is gated and exports flag incomplete coverage.
- MV3 worker suspension can lose state or reorder concurrent callbacks unless every mutation is serialized through storage.
- Request/response/navigation callbacks can duplicate one load; careless deduplication can also discard method or status.
- `Set-Cookie` omission without `extraHeaders` empties auth-token evidence.
- DOM forms are dynamic, cross-frame, or absent; captured field names remain evidence, not proof. Values must never enter messages, logs, snapshots, or exports.
- Naive host inclusion or last-two-label parsing creates telemetry/CDN/junk proxy hosts. Login-path selection can incorrectly prefer OAuth/silent paths over the credential POST.
- Hand-written YAML or substring validation can accept wrong types. Secret scanning can falsely reject safe cookie names or UUID identifiers, or miss long credential-like values.
- Static snapshots may preserve page content the operator did not intend; reports and UI must state the local sensitivity and training modules must default off.

## Open questions and assumptions

No planning blocker remains. Assumptions: Node.js is available for dependency-free tests/CLI; the supplied study schema and fixture are authoritative and will be copied byte-for-byte; manual A2/A3b are documented for a human Chromium run rather than fabricated as automated results; Semgrep/ast-grep are invoked only if already installed, with absence recorded rather than installing replacements.
