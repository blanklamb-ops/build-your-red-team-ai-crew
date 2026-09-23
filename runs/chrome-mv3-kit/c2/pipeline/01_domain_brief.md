# Domain Brief — chrome-mv3-kit

**Author:** Domain Researcher  
**Stage:** 1/5  
**Date:** 2026-09-15

## 1. Goal Restatement

Build a **Chrome Manifest V3 extension** and accompanying CLI tools that enable authorized security researchers in a controlled lab environment to:

- **Record metadata** about browser authentication flows (HTTP metadata: URLs, methods, status codes, header/cookie **names** only — never values/secrets)
- **Generate operator-ready Evilginx 2.3.0-format phishlet YAML** that is **placeholder-free** and loadable, minimizing post-generation hand-editing by populating all capture-derived fields (`proxy_hosts`, `auth_tokens`, `auth_urls`, `login`, `credentials`, `sub_filters`)
- **Save static HTML snapshots** with optional training modules (disabled by default)
- **Export HTTP traffic-pattern documentation** skeletons for lab reference

Success means: extension loads without errors, captures multi-origin redirect flows with real `webRequest` events (not only navigation fallback), generates schema-valid phishlets with **no `{{PLACEHOLDER}}` tokens**, passes all acceptance tests including the critical **A5e regression-mixed-capture** test, and explicitly fails when host permissions or input data are insufficient rather than producing silent garbage.

## 2. Constraints

### Platform & APIs
- **Chrome Manifest V3** (manifest_version: 3) with service-worker background context
- Required permissions: `webRequest`, `webNavigation`, `storage`, `downloads`
- Host permissions must be **optional** (`optional_host_permissions` for `http://*/*`, `https://*/*`) and requested at runtime via user gesture (`chrome.permissions.request`), not granted silently at install
- **`webRequest.onCompleted` must use `['responseHeaders', 'extraHeaders']`** extraInfoSpec to capture `Set-Cookie` headers (Chrome MV3 hides them without `extraHeaders`)
- Content scripts for login-form DOM metadata capture (form actions, field names/types — **never values**)
- MV3 service-worker lifecycle: state must persist to `chrome.storage` and survive worker suspension/restart

### Language & Environment
- JavaScript (ES modules in service worker, standard scripts in popup HTML)
- Node.js for CLI generators and tests
- YAML output for phishlets; JSON for capture exports
- No off-host exfiltration (local-only tool)
- Synthetic test fixtures only (`example.com`, `.test` TLDs, RFC5737 IPs)

### Critical Format Dependency
- **Evilginx 2.3.0 Phishlet File Format** (https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-(2.3.0))
  - Required top-level keys: `author`, `min_ver`, `proxy_hosts`, `auth_tokens`, `auth_urls`, `login`, `credentials`, `sub_filters`
  - **No** top-level `name` key
  - `credentials` must be a **map** (not list): `{username: {key, search, type}, password: {key, search, type}}`
  - `auth_tokens` is a **list** of `{domain, keys: [cookie_names]}` (not map, no `value` keys)
  - `sub_filters` is a **list of objects** with `{triggers_on, orig_sub, domain, search, replace, mimes}` — never bare strings
  - `login` contains only `domain` and `path` (no `username`/`password` keys)
  - Must ship with JSON Schema validator

## 3. Prior Art

### Evilginx 2
- Open-source MITM phishing framework (https://github.com/kgretzky/evilginx2)
- Uses reverse-proxy phishlets to capture credentials and session cookies
- Phishlet YAML format version 2.3.0 is the target (not 3.x)
- Auto-fill variables: `{hostname}`, `{domain}` used in `sub_filters` for hostname rewrites
- PSL (Public Suffix List) for registrable domain extraction (eTLD+1)

### Chrome Extension APIs
- `chrome.webRequest` for HTTP event monitoring (https://developer.chrome.com/docs/extensions/reference/api/webRequest)
- `chrome.webNavigation` for navigation events as fallback
- `chrome.permissions` for runtime permission requests (https://developer.chrome.com/docs/extensions/reference/api/permissions)
- `chrome.storage` for persistent state across service-worker restarts
- MV3 service-worker lifecycle documentation: workers suspend after ~30 seconds idle

### JSON Schema & YAML
- JSON Schema Draft 7+ for phishlet validation
- `js-yaml` for YAML parsing/generation (strict mode to catch bad input)

## 4. Risks

### Technical Failure Modes
1. **Silent 0-event sessions:** If operator starts recording without host permissions, `webRequest` listeners fire for no events. Mitigation: explicit pre-flight permission check, clear error if missing.
2. **Missing `Set-Cookie` headers:** Without `extraHeaders` in `extraInfoSpec`, Chrome MV3 hides cookies → empty `auth_tokens`. Mitigation: hardcoded `['responseHeaders', 'extraHeaders']`.
3. **Service-worker state loss:** MV3 workers suspend unpredictably. Session state in globals only → data loss. Mitigation: persist everything to `chrome.storage.local`.
4. **Placeholder phishlets pass schema but fail to load:** Generated YAML with `{{PLACEHOLDER}}` in `credentials.search` or `sub_filters` is structurally valid but operationally useless. Mitigation: substring check for `{{PLACEHOLDER}}` as hard-fail condition; default `'(.*)'` for `search`.
5. **Telemetry/CDN pollution:** Naively including `graph.microsoft.com`, `clarity.ms`, `wcpstatic.`, edge CDNs (`azurefd.net`, `cloudfront.net`) in `proxy_hosts` produces garbage phishlets. Mitigation: R4g deny-list exclusion.
6. **Hex-ID / experiment-label domains:** CDN URLs like `uhf-exp-fd-a1b2c3d4e5f6.b02.edgecdn.test` yield junk eTLD+1 parsing. Mitigation: drop hosts with ≥12-char hex labels or 4+ labels under edge suffixes.
7. **Idempotence failures in normalization:** Applying `normalizeOrigin` twice to same input fails → double-reload breaks. Mitigation: canonicalize to `https://example.test/*` once; test for idempotence.

### Operational Failure Modes
1. **No password form captured:** Generator must still emit usable heuristic `credentials` keys (`login`/`passwd`) and document they're not DOM-evidenced.
2. **Incomplete capture reported as success:** Single navigation event should not pass acceptance. Mitigation: coverage diagnostics, `incomplete` marker.
3. **Operator edits required for loadability:** If `sub_filters` or `credentials.search` are placeholders, operator must hand-edit before Evilginx can parse the phishlet. Non-goal: guaranteed IdP bypass. Goal: **loadable, placeholder-free YAML**.

## 5. Open Questions & Assumptions

### Assumptions
- **PSL implementation:** We will use the `psl` npm package for eTLD+1 extraction (registrable domain parsing).
- **Username field detection:** Match exact field names (case-insensitive): `login`, `loginfmt`, `user`, `username`, `usernameEntry`, `email`, `account` — even when `type=hidden`. Rationale: Microsoft/Azure login flows use hidden `loginfmt`.
- **`login.path` ranking:** Prefer (1) password-form `form_action`, (2) paths matching `post.srf`/`checkpassword`, (3) `GetCredentialType` or login HTML — **never** `/oauth2/authorize` or `/savestate` or silent-signin paths.
- **Coverage threshold:** "Incomplete" if **only** navigation fallback events, **or** any observed origin lacked permission. At least one `webRequest` event required.

### Blocked Questions (marked for Planner)
- **None at this stage.** Requirements are prescriptive; generators have well-defined defaults for missing data.

## Word Count
~780 words

---

**Handoff to Stage 2 (Planner):** Domain is mapped. Proceed to task decomposition and dependency graph.
