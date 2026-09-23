# Operational Constraints — chrome-mv3-kit

**Author:** Ops Advisor  
**Stage:** 3/5  
**Date:** 2026-09-15  
**Input:** `01_domain_brief.md`, `02_plan.md`, `PROMPT.md`

## 1. Runtime Environment Assumptions

### Platform
- **Chrome/Chromium 88+** (Manifest V3 support; `extraHeaders` in `webRequest`)
- **Node.js 18+** for CLI generators and tests (for `node:test` built-in)
- **Operating system:** Linux, macOS, Windows (extension + CLI must be cross-platform)
- **Privileges:** Standard user account; **no** elevated/root required
- **Network:** Local-only operation; **no** outbound connections from extension or generators (except browser-initiated navigation to authorized lab targets)

### Lab Environment
- Authorized security research lab **only**
- Isolated test environment (not production networks)
- Operator has explicit written authorization to test target flows
- Test fixtures use `example.com`, `.test` TLDs, RFC5737 IPs only

## 2. Secrets & Evidence Handling

### Never Commit to Repository
- Real credential **values** (usernames, passwords, PINs, OTP codes)
- Session tokens, cookies, JWTs, bearer tokens (any value, not names)
- Request/response bodies containing secrets
- Real organization hostnames, client IDs, tenant IDs
- API keys, private keys, certificates
- Actual lab target URLs or identities

### Allowed in Repository
- Cookie **names** and header **names** (no values)
- Synthetic test fixtures with `example.com`, `.test` domains
- Canonical patterns: `session_id`, `csrf_token` (names only)
- Public documentation references (Evilginx wiki URL, Chrome API docs)

### Evidence Lifecycle
- Captured sessions remain **local** to operator workstation
- Export files (JSON, YAML, Markdown) stored in operator-controlled directories (not auto-uploaded)
- Extension uses `chrome.storage.local` (synced to Chrome profile, not cloud-synced by default, but operator should use isolated profile)
- Generated phishlets contain **no secrets** (only metadata and patterns)
- Deletion: operator manually deletes session exports and generated files; extension provides "Clear session" button

### WP Impact
- **WP4, WP5, WP6:** Must filter and validate **before** storage — reject or truncate secret-looking values in free-text fields
- **WP8:** Secret rejection must fail clearly (not silently truncate and produce broken phishlet)
- **WP18:** README must warn: "Use isolated Chrome profile; do not enable Chrome Sync on that profile"

## 3. Operator Workflow

### Pre-Engagement
1. Obtain written authorization for target authentication flow
2. Set up isolated Chrome profile (no Sync enabled)
3. Install extension unpacked (`chrome://extensions` → Developer mode → Load unpacked)
4. Prepare authorized origin list (hostnames involved in auth flow)

### Capture Session
1. Open extension popup
2. Enter/approve authorized origins (e.g., `https://login.idp.test`, `https://wallet.idp.test`)
3. Click "Enable lab access" → Chrome prompts for host permissions → **Grant**
4. **Reload extension** (critical: `chrome://extensions` → reload icon)
5. Open popup again → verify origins shown as granted
6. Click "Start recording"
7. Navigate to target auth flow in a browser tab (login page → enter credentials → complete flow)
8. Return to popup → "Stop recording"
9. "Export session" → save JSON locally
10. Close browser, clear profile if needed

### Generate Artifacts
```bash
# From JSON export
node cli/generate.js \
  --input captures/session-20260915.json \
  --output-phishlet phishlets/target-idp.yaml \
  --output-markdown reports/target-idp.md

# Review generated phishlet for completeness
node cli/validate-phishlet.js phishlets/target-idp.yaml

# Load into Evilginx (operator's responsibility; not this tool's scope)
# Configure phishlet domain, lures, test in lab
```

### Post-Capture
- Review diagnostics in JSON export: `coverage: incomplete` → re-capture with all origins granted
- Inspect `proxy_hosts` for junk entries (telemetry, CDNs) → verify deny-list worked
- Confirm `credentials.username.key` / `credentials.password.key` match observed form field names
- Test phishlet in Evilginx lab instance (separate tool, separate authorization)

### WP Impact
- **WP2:** Popup must show clear status: "Origins requested: X | Granted: Y | Missing: Z"
- **WP4:** Pre-flight check must **block** recording start if `missingOrigins.length > 0`
- **WP6:** Export must include timestamp, session ID, coverage diagnostic
- **WP18:** README must document this exact sequence (especially Grant → Reload → Start)

## 4. Safety Defaults

### Fail-Safe Configuration
- **Host permissions:** Default to **optional** (not granted at install)
- **Training modules:** `config/lab_unsafe_modules.json` defaults to `{lab_unsafe_modules: false}`
- **Recording state:** Default OFF; requires explicit "Start recording" click
- **Export scope:** No auto-export; operator must click "Export session"
- **Phishlet generation:** No auto-submit to Evilginx; generates local YAML file only

### Explicit Confirmations
- **Before recording start:** Check host permissions; show error if incomplete
- **Before phishlet generation:** Warn if `coverage: incomplete` in input JSON
- **On secret detection:** Fail phishlet generation clearly; show offending value pattern (truncated) in error message
- **On missing structural data:** Fail generation if no events captured; do not emit empty phishlet

### Allowlists & Denylists
- **R4g deny-list:** Telemetry, CDNs, object storage **excluded by default** from `proxy_hosts`
- **Origin normalization:** Only `http://` and `https://` allowed; reject `file://`, `ftp://`, `chrome-extension://`
- **CLI override:** `--include-host graph.example.com` to override deny-list (for edge cases)

### WP Impact
- **WP1:** Manifest must use `optional_host_permissions`, not `permissions`
- **WP4:** Service worker must check permissions before registering recording session
- **WP8:** Generator must fail loudly (non-zero exit, clear message) on invalid input
- **WP17:** Training modules must read config file; default disabled

## 5. Degradation Modes

### Partial Capture (Graceful)
- **Only navigation events:** Mark `coverage: incomplete`, still export JSON, warn in phishlet generation
- **Some origins missing permission:** Record accessible origins, flag missing in diagnostics, mark incomplete
- **No password form captured:** Emit phishlet with heuristic `credentials` keys (`login`/`passwd`), add comment `# WARNING: No password form observed; keys are heuristic`

### Hard Failures (Abort Early)
- **No host permissions granted:** Do not start recording; show popup error "Cannot record: host access not granted"
- **No events captured:** Do not export/generate; show "Session is empty" error
- **Secret detected in phishlet generator input:** Fail with error "Input contains secret-looking value: [first 8 chars]..."; do not emit YAML
- **Malformed capture JSON:** Fail generation with clear parse error

### Offline Operation
- **Extension:** Works fully offline (no external requests)
- **Generators:** Work offline (all dependencies bundled)
- **Validator:** Works offline (local schema file)

### Service-Worker Suspension
- **State persisted to `chrome.storage.local`:** Session survives worker restart
- **Loss scenario:** Worker evicted mid-request → event might be lost → coverage diagnostic detects gap
- **Mitigation:** Restore state on every listener invocation if needed

### WP Impact
- **WP4, WP6:** Diagnostics must expose gaps honestly
- **WP8:** Generator must have multiple failure paths with distinct error messages
- **WP9:** Validator must distinguish malformed YAML vs. schema violations

## 6. Plan Deltas (Non-Negotiable Changes)

The Tool Architect **must** implement the following constraints. Reference plan WP numbers:

### WP1: Extension Scaffold
- ✅ Manifest `optional_host_permissions` instead of `permissions` for host access
- ✅ No hard-coded real hostnames in `manifest.json` examples

### WP2: Origin Normalization
- ✅ Reject `file://`, `chrome://`, `chrome-extension://`, `ftp://` schemes
- ✅ Reject URLs with `userinfo` component (`https://user:pass@example.com`)
- ✅ Popup must show three counts: Requested, Granted, Missing
- ✅ "Enable lab access" button must be one-click (default `http://*/*` + `https://*/*`)

### WP4: Event Capture
- ✅ Pre-flight check: `if (missingOrigins.length > 0) { showError('Cannot start: missing host access'); return; }`
- ✅ Filter `chrome-extension://` URLs **before** passing to `normalizeOrigin` (don't throw on noise)
- ✅ Hard-code `extraInfoSpec: ['responseHeaders', 'extraHeaders']` for `onCompleted` (no user override)

### WP5: Form Capture
- ✅ **Never** read `input.value`, `input.defaultValue`, `input.autofill`
- ✅ Content script must be scoped: `"matches": ["http://*/*", "https://*/*"], "run_at": "document_idle"`
- ✅ Username detection: case-insensitive exact match against: `login`, `loginfmt`, `user`, `username`, `usernameEntry`, `email`, `account`

### WP6: Export & Diagnostics
- ✅ Download via `data:application/json;charset=utf-8,...` URL (not popup-scoped `blob:`)
- ✅ Include session metadata: `{sessionId, sessionStart, sessionEnd, requestedOrigins, grantedOrigins, diagnostics}`
- ✅ Diagnostics must expose: `eventCountsBySource`, `eventCountsByOrigin`, `missingOrigins`, `coverage`

### WP8: Phishlet Generator
- ✅ Fail (throw exception, exit non-zero) if input contains secret-like value in free-text
- ✅ Secret regex (preliminary): `/[A-Za-z0-9_-]{32,}\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/` (JWT), or long base64 runs in credential context
- ✅ Allow: cookie names, canonical IDs (`session_id`, `csrf_token`, UUID patterns)
- ✅ Default `credentials.*.search` to `'(.*)'` (never `{{PLACEHOLDER}}`)
- ✅ Default `sub_filters` to hostname-rewrite objects derived from `proxy_hosts` (never empty, never strings)
- ✅ Add phishlet header comment: `# Generated by chrome-mv3-kit | Authorized lab use only`
- ✅ Add coverage comment when heuristic keys used: `# WARNING: No password form observed; credentials.username.key and credentials.password.key are heuristic defaults`

### WP9: Validator
- ✅ Use `js-yaml` in **safe mode** (no custom tags)
- ✅ Substring check: `if (yamlText.includes('{{PLACEHOLDER}}')) { fail('YAML contains placeholder tokens'); }`
- ✅ Schema check: `ajv.validate(schema, parsed)` must pass

### WP11: CLI Runner
- ✅ Exit non-zero on validation failure
- ✅ Print error messages to stderr, success to stdout
- ✅ Support `--help` flag with usage

### WP17: Page Snapshot
- ✅ Check `config/lab_unsafe_modules.json` exists; default `{lab_unsafe_modules: false}` if missing
- ✅ Training modules do **not** activate unless `lab_unsafe_modules: true`

### WP18: Documentation
- ✅ README must include "Authorized Use" section referencing `AUTHORIZED_USE.md`
- ✅ README must document Grant → Reload → Start → Browse sequence with emphasis
- ✅ README must state: "Generated phishlets are placeholder-free and loadable, but the operator must configure Evilginx phishlet domain and lures, and lab-test the deployment. This tool does not guarantee bypass of any security control."
- ✅ OPSEC_CARD.md must include detection artifacts: browser extension install events, optional permission requests, chrome.storage writes, downloads of JSON/YAML files

### WP19: Static Analysis
- ✅ Archive full Semgrep + ast-grep outputs (not just summaries)
- ✅ Do not fail build on linter warnings (informational only)

## 7. Detection-Relevant Artifacts (for OPSEC Reviewer)

The following behaviors are **observable by defenders** and must be documented in `OPSEC_CARD.md`:

1. **Browser extension installation:** `chrome://extensions` developer mode enabled, unpacked extension loaded
2. **Permission requests:** User grants broad host access (`http://*/*`, `https://*/*`) to an extension
3. **Chrome storage writes:** Extension writes session data to `chrome.storage.local` (persists in Chrome profile)
4. **Downloads:** Operator downloads JSON, YAML, Markdown files from extension popup
5. **Content script injection:** Scripts injected into login pages to read DOM metadata
6. **WebRequest listeners:** Extension registers listeners for all HTTP(S) traffic while recording
7. **File artifacts:** Exported JSON/YAML/Markdown files on operator disk
8. **Evilginx deployment (out of scope for this tool):** Generated phishlet loaded into Evilginx instance (separate opsec surface)

---

**Handoff to Stage 4 (Tool Architect):** Operational constraints defined. Proceed to implementation with these non-negotiable guardrails.
