# ACCEPTANCE — chrome-mv3-kit

Score each item `PASS` / `FAIL` / `N/A`. All required items must PASS for “working implementation.”

## Automated / semi-automated

| ID | Check |
|----|-------|
| A1 | `extension/manifest.json` is MV3 (`manifest_version: 3`) and lists `webRequest`, `webNavigation`, `storage`, `downloads`; host access is **optional** (not required at install). A content script is declared for form-metadata capture (R2f) on main-frame auth-relevant pages. |
| A2 | Extension loads unpacked without console errors on a clean Chromium profile (manual) |
| A3 | Recorder writes at least one synthetic session JSON matching `schemas/` (fixture path) |
| A3b | **Manual multi-origin recorder smoke:** approve at least two authorized origins, then Grant → Reload → Start → exercise a redirect flow. Export contains at least 5 events across at least 2 origins, including at least one non-fallback `webRequest` event. A lone `webNavigation` event fails. |
| A3c | Starting recording **without** host access shows a clear error and does not pretend to record successfully. Default popup path offers one-click enable of optional `http(s)://*/*` (typing origins is optional). |
| A3d | Export reports counts by event source and origin, requested/granted/missing origins, and marks `coverage: incomplete` when only fallback events were seen or an observed redirect origin lacked permission |
| A3e | Automated Chrome-API mock test starts a session, simulates MV3 service-worker teardown/restart, and verifies requested origins, recording state, events, timestamps, and diagnostics are restored from `chrome.storage` |
| A3f | Requested origins remain visible after the documented Grant → Reload sequence; Start verifies permission for the complete requested set, not merely that any origin is granted |
| A3g | Production UI normalization is **idempotent**: bare `https://example.test`, full URLs, and already-canonical `https://example.test/*` all become `https://example.test/*` before `chrome.permissions.request` / storage; an automated test imports that same production function and rejects userinfo and non-HTTP(S) schemes |
| A3h | Content-script form-metadata capture (R2f): an automated test with a mocked DOM verifies the content script records `<form>` `action` URLs and `<input>` `name`+`type` attributes into a `form_fields` array, and that **no input values** are recorded. A fixture containing `form_fields` flows through to `credentials` in the generated phishlet. |
| A4 | Markdown export generated from fixture session |
| A5 | Capture-complete phishlet generator emits schema-valid Evilginx 3.x-format `.yaml` from both fixture input and a captured-session JSON; capture-derived fields are populated; coverage metadata is present |
| A5b | Generated phishlet contains `name`, `min_ver`, `proxy_hosts` (≥1 entry, each with single-label `phish_sub` / `orig_sub`, `domain`, and boolean `session` / `is_landing` / `auto_filter`; exactly one landing host), `login.domain` + `login.path` (path is **not** a static asset), `auth_tokens` as a **list** of `{ domain, keys: [cookie names…] }` (no map-of-`name` objects, no `value` keys), and `auth_urls` drawn only from auth-like paths (no `.js`/`.css`/image/telemetry paths). Telemetry/CDN/analytics hosts are excluded by default and the exclusion list is documented (includes `copilot.com`, `copilot.microsoft.com`, `ms-sso.copilot.*`); `--include-host` can override. When the fixture has Set-Cookie names, `auth_tokens` is non-empty; when it has auth-like paths, `auth_urls` is non-empty. **Empty `auth_tokens`/`auth_urls`/`credentials` MUST be `[]` (empty YAML list), never null/blank — the schema requires array type.** **When the fixture contains a `form_fields` array (R2f DOM capture), `credentials` MUST be populated from the captured input `name` attributes and `login.username`/`login.password` reference those captured field names — not `{{PLACEHOLDER}}`. Username detection must match by field NAME (`login`, `loginfmt`, `user`, `username`, `email`, `account`) even when `type=hidden` (Microsoft uses hidden inputs for username).** Only `sub_filters` remains `{{PLACEHOLDER}}` (JS proxy-rewrite recipes require operator judgment). Authorized-lab-use header comment is present. |
| A5c | Generator rejects secret-looking **values** (JWTs, long tokens in free-text fields) and fails clearly when required structural input is absent; test includes a secret-looking value in an otherwise valid `example.com` fixture to prevent a fixture-host bypass. Companion tests confirm cookie **names** (including `csrf_token` and `__Host-…`-style IdP names) and a canonical-UUID `session_id` never block generation, while a JWT as a captured value is rejected; a session export missing its diagnostics block still generates with coverage metadata derived from the events. All bundled fixtures must pass generation and validation in CI. An end-to-end test runs the documented single generation command against the shipped session fixture (recorder export field spellings exactly — no fields the recorder never emits) and validates the output, asserting ≥1 `proxy_hosts`, correct `auth_tokens` list shape, and that `login.path` is not a static asset; event processing must not be gated on optional fields (origin derived from `url` when absent); a fixture containing `set_cookie_names` (recorder spelling — not only camelCase `cookieNames`) must yield non-empty `auth_tokens`, and the shipped fixture file itself must contain `set_cookie_names` keys; a fixture with auth-like paths must yield non-empty `auth_urls`; a fixture mixing auth hosts with `clarity.ms` / `browser.events.data.microsoft.com`-style telemetry must **omit** those telemetry hosts from `proxy_hosts` by default; hosts are grouped by registrable domain (PSL — `login.live.com` → `live.com`); **a fixture containing a `form_fields` array with input names (e.g. `[{name:"login",type:"hidden"},{name:"passwd",type:"password"}]` — Microsoft-style hidden username) must yield `credentials` populated with those field names and `login.username`/`login.password` referencing them — a generator that emits `{{PLACEHOLDER}}` for `credentials` when `form_fields` is present FAILS; a generator that only matches `type=email/text` and misses `type=hidden` username fields named `login`/`loginfmt` FAILS**; **a fixture with no `set_cookie_names` must yield `auth_tokens: []` (empty array), not null/blank — schema validation must catch a null `auth_tokens`**; telemetry exclusion must cover `copilot.com` / `copilot.microsoft.com` / `ms-sso.copilot.*` |
| A5d | Documented validator command uses a YAML parser and JSON Schema implementation against the shipped phishlet schema. Tests rename `name` to `removed_name`, add a forbidden top-level property, add a cookie `value` key, replace `auth_tokens` with a domain→`[{name:…}]` map, replace a `credentials` placeholder with a live regex such as `(.*)`, and provide malformed YAML; every mutation must fail nonzero. Substring/regex-only validators fail this check. |
| A6 | Optional training modules do not activate unless `lab_unsafe_modules=true` |
| A7 | Traffic-pattern stub exporter emits non-empty skeleton from fixture |
| A8 | README contains build/load steps, **Grant → Reload → Start → browse** order, authorized-use notice, and what the operator must still complete before lab use |
| A9 | `OPSEC_CARD.md` has Detection Recommendations section with ≥3 defender-oriented bullets |
| A10 | Semgrep and ast-grep outputs archived under `../scanners/` (or `scanners/` at run root) |
| A11 | The documented single test command demonstrably executes lifecycle, UI-normalization, generator, secret-rejection, and schema-validation tests without an imported child suite terminating the runner |

## Manual fidelity

| ID | Check |
|----|-------|
| M1 | Permissions list matches README justification (including why host access is optional/runtime) |
| M2 | No hard-coded real client hostnames or secrets in repo |
| M3 | Generators fail clearly on incomplete input rather than silent garbage |
| M4 | Popup status shows whether host access is granted |
| M5 | Popup displays the authorized origin set and identifies missing permission before recording |
| M6 | A one-event fallback-only export is visibly labeled incomplete and cannot be reported as a successful full-flow capture |
| M7 | Capture-derived fields (`proxy_hosts`, `auth_tokens`, `auth_urls`, `login`, and `credentials` when `form_fields` was captured) look faithful to the session; the only remaining placeholder is `sub_filters` (JS proxy-rewrite recipes); README states that `sub_filters` still requires operator completion and that output is not a guaranteed live-IdP phishlet |

## Time logging

Record wall-clock minutes to first full PASS on A1–A10 (+ A3b/A3c when scored) or abandon.
