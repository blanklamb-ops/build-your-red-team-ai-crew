# PROMPT — chrome-mv3-kit

**Tool slug:** `chrome-mv3-kit`  
**Context:** Academic / conference methodology study (authorized lab only).
**Authorized use only** — see `AUTHORIZED_USE.md` in this workspace.

## Operator goal

Build a Chrome **Manifest V3** **lab documentation kit** for authorized security researchers who need to:

- record **metadata about browser authentication HTTP flows** in a local lab (URLs, methods, status codes, **header names only** — not secrets by default)
- generate an **Evilginx 3.x-compatible phishlet `.yaml` that is as complete as the capture allows** — fully populate every field that session metadata can evidence (`proxy_hosts`, `auth_tokens` cookie names, `auth_urls`, `login`, and `credentials` when the recorder captured login-form field names via DOM content-script); leave only `sub_filters` (JS proxy-rewrite recipes) as enforced placeholders, since those require operator judgment the metadata recorder cannot observe
- save **static HTML snapshots** of lab pages for offline review, with optional **training demos** (UI-overlay awareness; file-picker UX awareness) that stay **off unless explicitly enabled**
- export a **commented HTTP traffic-pattern skeleton** (profile stub) derived from observed URL patterns, for lab documentation — not a production implant

This prompt specifies **software deliverables and acceptance tests** for synthetic fixtures. It is **not** a request for attack recipes, bypasses, live targeting, or a guaranteed working Evilginx deployment against any live IdP. Output is **capture-faithful** config plus operator completion for body/JS rules the metadata recorder cannot observe.

## Requirement IDs

| ID | Requirement |
|----|-------------|
| R1 | MV3 extension scaffold with service worker; minimal permissions justified in README. Include `webRequest`, `storage`, `downloads`, and `webNavigation`. Use **optional** host permissions (`http(s)://*/*`) requested at runtime — not granted silently at install. |
| R2 | Auth-flow recorder (local only, **no off-host exfiltration**): while recording is ON, capture request **metadata** for observed navigations/requests — URL, method, status (when available), resource type, and auth-related **header names** / Set-Cookie **names** (never values/bodies/tokens). **Do not** only log events that already carry auth headers — a plain HTTPS page load must still produce events. |
| R2a | **Host-access gate:** popup must expose a **one-click** “Enable lab access” (or equivalent) that requests the declared optional host permissions (typically `http://*/*` and `https://*/*`) from a user gesture — the operator must **not** be forced to type origins for the default path. Optionally also support a narrower host list. Show whether access is granted; **refuse to start recording** (clear error) if access is missing — otherwise operators get silent **0-event** sessions. Shared helpers such as `normalizeOrigin` must be loaded into the popup via `<script src=…>` (popup pages cannot use `importScripts`). README must document: Enable → Allow → Reload extension if needed → Start → then browse. |
| R2b | **Navigation fallback:** also record `webNavigation` main-frame completions while recording, so loads are not lost if `webRequest` header listeners are flaky. |
| R2c | **Multi-origin coverage:** before recording, let the operator enter or approve the complete authorized host set for the flow and request those optional origins from a user gesture. The UI accepts bare HTTP(S) origins such as `https://example.test`, host-only entries, full URLs (derive the origin), and already-canonical Chrome match patterns such as `https://example.test/*`. Canonicalization must be **idempotent**: applying it twice to the same value must not fail (popup and service worker may both normalize). Always store/request/compare as `https://example.test/*`. Reject userinfo and non-HTTP(S) schemes. Show requested, granted, and missing origins. During capture, record redirect/navigation origins and warn in the export when an observed origin lacked permission. Do not silently represent a one-navigation fallback as a complete auth flow. |
| R2d | **Capture diagnostics:** exports must distinguish `webRequest` request events, response events, and `webNavigation` fallback events; report event counts by source and origin, permission gaps, session start/stop times, and a prominent `coverage: incomplete` marker when only fallback events were captured or any observed origin lacked access. Deduplicate paired callbacks without discarding method/status data. |
| R2e | **MV3 lifecycle persistence:** do not keep authoritative recording/session state only in service-worker globals. Persist requested origins, recording state, captured events, timestamps, and diagnostics in `chrome.storage` and restore them after worker suspension/restart. Extension reload after granting access must retain the requested-origin set. Include automated tests with mocked Chrome APIs that simulate worker restart and verify restored state. |
| R2f | **Login-form metadata capture (names only, never values):** while recording is ON, on each main-frame navigation completion to an auth-relevant page (login form, OAuth/SAML authorize, credential entry), inject a **content script** that reads the page DOM and records: (1) each `<form>` `action` URL (resolved to absolute), (2) each `<input>`/`<button>` `name` attribute and its `type` (e.g. `type=password` → password field, `type=email`/`text` → username candidate), and (3) the form's visible submit control label if trivially available. **Never record input values, autofill values, or anything the user typed.** Store these as a `form_fields` array on the event: `{ url, form_action, fields: [{ name, type }] }`. This is what lets the phishlet generator fill `credentials` and `login.*` from capture instead of leaving placeholders. Pages with no `<form>` simply yield an empty `form_fields` array. **Username detection must consider field NAME, not only `type`** — many IdPs (e.g. Microsoft) carry the username in a `type=hidden` input named `login`/`loginfmt`/`user`/`username`/`email`/`account`; the generator must treat such name-matched fields as username candidates even when `type=hidden`. |
| R3 | Export captured flows to JSON + human-readable markdown summary (extension UI and/or CLI). Both formats must include the R2d diagnostics. |
| R4 | **Capture-complete phishlet generator:** from a captured session JSON or filled form, emit an Evilginx **3.x-compatible** phishlet `.yaml` that is **as complete as the capture allows**. Authorized lab use only. Top-level keys exactly: `name`, `min_ver`, `proxy_hosts`, `auth_tokens`, `auth_urls`, `login`, `credentials`, `sub_filters` (plus optional documented comments/metadata). **Must be fully filled from the session (no placeholders):** (1) `name`, `min_ver: "3.0.0"`; (2) `proxy_hosts` — one entry per **auth-relevant** host using Public Suffix List registrable-domain grouping; each entry has `phish_sub`, `orig_sub`, `domain`, and boolean `session` / `is_landing` / `auto_filter`; `session: true` iff Set-Cookie names were observed on that host; exactly one `is_landing: true` on the documented primary login host; `phish_sub` / `orig_sub` are single DNS labels (never multi-dot junk such as `content.lifecycle` or CDN edge IDs); (3) `auth_tokens` — a **YAML list** of objects `{ domain: <host>, keys: [<cookie names>] }` (never a map of domain→`[{name:…}]`, never cookie values, never a `value` key); (4) `auth_urls` — deduplicated observed paths that look like login/OAuth/SAML/token/authorize/callback endpoints; **exclude** static assets (`.js`/`.css`/`.png`/`.svg`/fonts/images) and telemetry paths; if no auth-like paths exist, emit `[]` and note that in coverage comments — never invent paths; (5) `login` — `{ domain, path }` for the primary login host + best auth HTML or credential XHR path (never a static JS/CSS asset). **Auth-relevant host filter (mandatory):** default-exclude telemetry/CDN/analytics hosts and document the list (at least: `clarity.ms`, `bing.com`, `browser.events.data.microsoft.com`, paths containing `OneCollector`, `google-analytics`, Skype config hosts, pure static CDN hosts that set no auth cookies, `copilot.com`, `copilot.microsoft.com`, `ms-sso.copilot.*`). Operator may pass `--include-host` to override. **Fill from capture when available:** when the session export contains a `form_fields` array (from R2f DOM capture), the generator MUST populate `credentials` and `login.*` from it — `credentials` entries use the captured input `name` attributes as `key`, with `password` typed fields mapped to the password credential and `email`/`text` typed fields mapped to username candidates; **also match username by field NAME** (`login`, `loginfmt`, `user`, `username`, `email`, `account`) even when `type=hidden` (Microsoft uses hidden inputs for the username); `login.path` uses the captured `form_action` (path only) when it is more specific than the URL path. `login.username`/`login.password` reference the captured field names. **Empty arrays must be `[]`, never null/blank:** when no Set-Cookie names were observed, `auth_tokens` MUST be `[]` (an empty YAML list), not a null/blank value — the schema requires an array type. Same for `auth_urls: []` and `credentials: []` when empty. **Placeholders ONLY where capture genuinely cannot know:** `sub_filters` (JS proxy-rewrite recipes) remain `{{PLACEHOLDER}}` — these require operator judgment about which scripts/URLs to rewrite and cannot be reliably derived from metadata capture alone. `credentials.search` remains placeholder unless the operator supplied a regex via CLI. Do **not** invent Microsoft/Okta/Google capture regexes, JS rewrite recipes, `force_post`, or `js_inject` blocks beyond what the captured form fields evidence. **Schema / safety:** ship a JSON Schema, executable validator (real YAML parser + JSON Schema engine such as `js-yaml`+Ajv — not substring checks), fixture, and docs. Validator fails nonzero on parse errors, missing required properties, forbidden properties, wrong types, wrong `auth_tokens` shape, cookie `value` keys, or non-placeholder credential/sub_filter patterns when no form-name evidence exists. Secret detection targets credential **values** only — UUIDs (incl. `session_id`), ISO timestamps, hostnames, URL paths, and **cookie names** (incl. names containing `token`/`auth`/`jwt`/`secret`) are never secrets. Bookkeeping fields must not block generation. Tolerate missing/partial diagnostics; derive coverage from events when needed. Accept recorder export as primary input (snake_case and camelCase event fields); never gate on optional fields — derive origin from `url` when `origin` is absent. **Hard requirement:** cookie names MUST be read from `set_cookie_names` (recorder spelling) and also accept `setCookieNames` / legacy `cookieNames`; a generator that only reads `cookieNames` FAILS. The shipped session fixture MUST emit `set_cookie_names` and MUST NOT use `cookieNames` alone — CI must fail if the fixture uses a field the recorder never writes. E2E CLI test against the shipped fixture must assert ≥1 `proxy_hosts`, **non-empty `auth_tokens` whenever any event has `set_cookie_names`**, non-empty `auth_urls` when auth-like paths exist, and `login.path` is not a static asset. Explicit non-goal: a guaranteed working Evilginx deployment against any live IdP. |
| R5 | Page-snapshot lab utility: save static snapshot + short report; optional training modules (`ui_overlay_awareness`, `file_picker_awareness`) are separate, labeled, **disabled by default**, require `lab_unsafe_modules=true`. |
| R6 | Traffic-pattern stub exporter: draft commented skeleton from observed URL patterns (documentation aid only; not a guaranteed production profile). |
| R7 | CLI and/or extension action to run generators headlessly on fixtures. |
| R8 | `OPSEC_CARD.md` with Detection Recommendations (defender-oriented). |
| R9 | README: build, load unpacked, **host-access + recording order**, lab-only warnings, authorized-use notice; document what the operator must still complete (`credentials` / `sub_filters` / lab testing). |
| R10 | Run Semgrep + ast-grep on what you write; archive outputs under `../scanners/`. |
| R11 | Provide one documented test command that runs every test suite. Test modules imported by a parent runner must return or throw rather than call `process.exit`; only the top-level runner may set the process exit code. Tests for origin normalization, permission comparison, persistence, and YAML validation must execute shared production functions rather than reimplementing the same logic inside the test. |

## Non-goals

- Targeting systems or identities without authorization
- Capturing or replaying passwords / session tokens against third parties
- Inventing IdP-specific credential-capture regexes, JS/response rewrite recipes, `force_post`, or `js_inject` that were not evidenced by session metadata or explicit operator input
- A guaranteed working Evilginx deployment against any live IdP
- Guaranteed bypass of any security control, or guaranteed compatibility with any IdP's current login flow
- Step-by-step attack playbooks

## Deliverable layout (suggested)

```
README.md
OPSEC_CARD.md
AUTHORIZED_USE.md
extension/          # MV3 (popup + service worker recorder)
generators/         # capture-complete phishlet + traffic-pattern stub generators
schemas/            # JSON schemas for exports and the phishlet
testdata/           # synthetic fixtures only (example.com / .test / RFC5737 IPs)
config/             # lab_unsafe_modules default false
```

## Success

Passes `ACCEPTANCE.md` using **synthetic fixtures** for generators. The manual
recorder smoke must exercise an authorized redirect flow spanning at least two
origins, capture multiple request/response events (not only a navigation
fallback), and report coverage honestly. A single captured main-frame event is
an incomplete capture and does not pass. The emitted phishlet must validate
against the shipped schema, fully populate capture-derived fields (including
`credentials` and `login.*` when the recorder captured form-field names),
exclude telemetry by default, and retain placeholders only for `sub_filters`
where metadata cannot supply values.
