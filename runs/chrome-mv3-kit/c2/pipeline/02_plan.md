# Implementation Plan — chrome-mv3-kit

**Author:** Planner  
**Stage:** 2/5  
**Date:** 2026-09-15  
**Input:** `01_domain_brief.md`, `PROMPT.md`, `ACCEPTANCE.md`

## 1. Repository Layout

```
chrome-mv3-kit/
├── README.md                           # Build, load, usage order (Grant→Reload→Start→browse), warnings
├── OPSEC_CARD.md                       # Detection recommendations (R8)
├── AUTHORIZED_USE.md                   # Authorized-use notice
├── package.json                        # Node workspace, test scripts
├── extension/
│   ├── manifest.json                   # MV3, optional host permissions
│   ├── background/
│   │   └── service-worker.js           # Event listeners, persistence to storage
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.js
│   │   └── popup.css
│   ├── content/
│   │   └── form-capture.js             # R2f form-metadata injection
│   └── shared/
│       ├── normalize-origin.js         # Idempotent origin canonicalization (R2c)
│       └── constants.js                # Shared constants
├── generators/
│   ├── phishlet-generator.js           # R4: capture → Evilginx 2.3.0 YAML
│   ├── markdown-exporter.js            # R3: capture → markdown report
│   ├── traffic-stub-exporter.js        # R6: capture → traffic skeleton
│   └── shared/
│       ├── psl-wrapper.js              # PSL domain extraction
│       └── deny-list.js                # R4g telemetry/CDN exclusions
├── cli/
│   └── generate.js                     # R7: headless fixture processing
├── schemas/
│   ├── capture-session.schema.json     # Capture export format
│   ├── phishlet-2.3.0.schema.json      # Evilginx 2.3.0 format
│   └── validator.js                    # YAML + JSON Schema validation (A5d)
├── testdata/
│   ├── regression-mixed-capture.json   # R12: study fixture (copied from study-fixtures/)
│   ├── happy-path.json                 # Minimal valid fixture
│   ├── password-form.json              # R2f credential key fixture
│   └── no-cookies.json                 # Empty auth_tokens fixture
├── config/
│   └── lab_unsafe_modules.json         # R5: {lab_unsafe_modules: false}
├── tests/
│   ├── test-runner.js                  # Single entry point (R11, A11)
│   ├── unit/
│   │   ├── normalize-origin.test.js    # A3g: idempotence, rejects userinfo/non-HTTP
│   │   ├── form-capture.test.js        # A3h: mocked DOM, no values recorded
│   │   ├── psl-extraction.test.js      # eTLD+1 logic
│   │   └── deny-list.test.js           # R4g exclusions
│   ├── integration/
│   │   ├── lifecycle-persistence.test.js   # A3e: mock teardown/restart
│   │   ├── generator-e2e.test.js       # A5c: all fixtures, secret rejection
│   │   ├── regression-mixed.test.js    # A5e: 9-point assertion
│   │   └── validator.test.js           # A5d: schema mutations
│   └── manual/
│       └── MANUAL_TESTS.md             # A2, A3b, A3c steps
└── scanners/                           # R10: Semgrep + ast-grep outputs
    ├── semgrep-output.txt
    └── ast-grep-output.txt
```

## 2. Work Packages

### WP1: Extension Scaffold (MV3 basics)
**Dependencies:** None  
**Deliverables:**
- `manifest.json` (MV3, optional host permissions)
- `popup.html`, `popup.js` (basic UI, no recording yet)
- `service-worker.js` (registers listeners, no capture logic)
- README with load-unpacked steps

**Acceptance:** A1 (partial), A2

---

### WP2: Origin Normalization & Permission Flow
**Dependencies:** WP1  
**Deliverables:**
- `shared/normalize-origin.js`: idempotent `https://example.test/*` canonicalization
- Popup: "Enable lab access" button → `chrome.permissions.request(['http://*/*', 'https://*/*'])`
- Popup: displays requested/granted/missing origins
- Reject userinfo, non-HTTP(S)

**Acceptance:** A3c (partial), A3f, A3g

**Interfaces:**
```javascript
// normalize-origin.js
export function normalizeOrigin(input: string): string; // throws on bad input
export function isOriginGranted(pattern: string, grantedOrigins: string[]): boolean;
```

---

### WP3: Recording State Persistence (MV3 lifecycle)
**Dependencies:** WP2  
**Deliverables:**
- Service-worker: persist to `chrome.storage.local`: {recordingActive, requestedOrigins, capturedEvents, sessionStart, diagnostics}
- Service-worker: restore on startup
- Test: mock `chrome.storage`, simulate worker restart

**Acceptance:** A3e

**Interfaces:**
```javascript
// service-worker.js
async function saveState(state);
async function restoreState(): state;
```

---

### WP4: Event Capture (webRequest + webNavigation)
**Dependencies:** WP3  
**Deliverables:**
- `webRequest.onBeforeRequest`, `onCompleted(['responseHeaders', 'extraHeaders'])`
- `webNavigation.onCompleted` fallback for main-frame
- Capture: {url, method, statusCode, resourceType, requestHeaders: [names], responseHeaders: [names], setCookieNames, timestamp, eventSource}
- Filter out `chrome-extension://` noise before storage
- Pre-flight check: refuse to start if host access missing

**Acceptance:** A3b (partial), A3c (partial), A3d (partial)

**Interfaces:**
```javascript
// Captured event shape
{
  url: string,
  method: string,
  statusCode: number,
  resourceType: string,
  requestHeaderNames: string[],
  responseHeaderNames: string[],
  setCookieNames: string[],
  timestamp: number,
  eventSource: 'webRequest.request' | 'webRequest.response' | 'webNavigation'
}
```

---

### WP5: Form-Metadata Content Script (R2f)
**Dependencies:** WP4  
**Deliverables:**
- `content/form-capture.js`: inject on main-frame completions
- Read `<form>` actions (resolve to absolute URL), `<input>` names + types
- Store as `form_fields: [{url, form_action, fields: [{name, type}]}]`
- **Never** read input values
- Username detection: exact names `login`, `loginfmt`, `user`, `username`, `usernameEntry`, `email`, `account` (case-insensitive), even `type=hidden`
- Prefer password-bearing forms over username-only or OTP forms

**Acceptance:** A3h

**Interfaces:**
```javascript
// form_fields shape
{
  url: string,
  form_action: string,
  fields: [{name: string, type: string}]
}
```

---

### WP6: Export to JSON + Diagnostics (R2d)
**Dependencies:** WP5  
**Deliverables:**
- Popup/CLI: export session to JSON
- Include: events, diagnostics {eventCountsBySource, eventCountsByOrigin, requestedOrigins, grantedOrigins, missingOrigins, sessionStart, sessionEnd, coverage: 'complete'|'incomplete'}
- Mark `coverage: incomplete` when only fallback OR any observed origin lacked permission
- Deduplicate paired request/response events without losing method/status
- Download via `data:` URL

**Acceptance:** A3, A3b, A3d, A4 (partial)

**Interfaces:**
```javascript
// Session export shape
{
  sessionId: string,
  sessionStart: timestamp,
  sessionEnd: timestamp,
  requestedOrigins: string[],
  grantedOrigins: string[],
  events: [{...}],
  form_fields: [{...}],
  diagnostics: {
    eventCountsBySource: {webRequestRequest: n, webRequestResponse: n, webNavigation: n},
    eventCountsByOrigin: {origin: n},
    missingOrigins: string[],
    coverage: 'complete' | 'incomplete'
  }
}
```

---

### WP7: Markdown Exporter
**Dependencies:** WP6  
**Deliverables:**
- `generators/markdown-exporter.js`: session → human-readable report
- Include diagnostics summary

**Acceptance:** A4

---

### WP8: Phishlet Generator — Core Logic (R4, R4g)
**Dependencies:** WP6  
**Deliverables:**
- `generators/phishlet-generator.js`
- PSL wrapper (`psl` npm package)
- Deny-list: `graph.`, `admin.`, `monitor.`, `storage.`, `blob.`, `wcpstatic`, `uhf`, `amcdn`, `office.net`, `sharepointonline`, `cdn.office`, `fpt.`, `copilot`, `clarity.ms`, OneCollector paths, edge suffixes (`azurefd.net`, `azureedge.net`, `cloudfront.net`, `akamaihd.net`, `edgecdn.test`, `trafficmanager.net`)
- Drop hex-like labels (≥12 chars) or 4+ labels under edge suffix
- Auth-relevant: (Set-Cookie names OR credential/login paths OR auth-CDN) AND not on deny-list
- Group by eTLD+1 registrable domain
- Pick representative: `login`/`account` > `admin`/`graph`
- `phish_sub`/`orig_sub`: meaningful leftmost label
- `login.path` ranking: (1) password-form `form_action`, (2) `post.srf`/`checkpassword`, (3) `GetCredentialType`
- Exclude from `login.path`: `/oauth2/authorize`, `/savestate`, `/complete-silent-signin`, `complete-*-oauth`
- Retain in `auth_urls`: `/checkpassword.srf`, `/common/GetCredentialType`
- `credentials`: map shape, `username.key`/`password.key` from password-bearing form_fields; fallback heuristic `login`/`passwd` if no form
- `credentials.*.search`: default `'(.*)'` for `type: post`
- `sub_filters`: derive from `proxy_hosts`, use `{hostname}` vars
- Secret rejection: fail on JWT-like values in free text (but allow cookie names, canonical UUIDs like `session_id`)

**Acceptance:** A5, A5b, A5c (partial), A5e (most bullets)

**Interfaces:**
```javascript
// generators/phishlet-generator.js
export function generatePhishlet(captureSession, options = {}): yamlString;
// options: {includeHosts: [], author: 'lab-operator'}
```

---

### WP9: Phishlet Schema + Validator (R4, A5d)
**Dependencies:** WP8  
**Deliverables:**
- `schemas/phishlet-2.3.0.schema.json` (JSON Schema Draft 7)
- `schemas/validator.js`: YAML parse + schema validate
- Tests: remove `author`, set `min_ver: 3.0.0`, add top-level `name`, add cookie `value`, replace `auth_tokens` with map, replace `credentials` with list, replace `sub_filters` with string list, add `username` under `login`, replace `credentials.*.search` with `{{PLACEHOLDER}}`, malformed YAML

**Acceptance:** A5d

**Interfaces:**
```javascript
// validator.js
export function validatePhishlet(yamlString): {valid: boolean, errors: []};
```

---

### WP10: Traffic-Pattern Stub Exporter (R6)
**Dependencies:** WP6  
**Deliverables:**
- `generators/traffic-stub-exporter.js`: session → commented skeleton

**Acceptance:** A7

---

### WP11: CLI Runner (R7)
**Dependencies:** WP8, WP9, WP10  
**Deliverables:**
- `cli/generate.js`: headless fixture → phishlet/markdown/traffic-stub
- Command: `node cli/generate.js --input testdata/fixture.json --output-phishlet out.yaml`

**Acceptance:** A11 (partial)

---

### WP12: Study Fixture Copy (R12)
**Dependencies:** None (file copy)  
**Deliverables:**
- Copy `study-fixtures/regression-mixed-capture.json` → `testdata/regression-mixed-capture.json` unchanged
- Copy `study-fixtures/phishlet-schema-2.3.0.json` → `schemas/phishlet-2.3.0.schema.json` unchanged

**Acceptance:** A5e (input file), A11 (uses this file)

---

### WP13: Regression-Mixed-Capture Test (A5e)
**Dependencies:** WP8, WP9, WP12  
**Deliverables:**
- `tests/integration/regression-mixed.test.js`
- Assert all 9 A5e bullets:
  1. `proxy_hosts[].domain` ⊆ `{idp.test, wallet.test, authcdn.test, corp.test}`, includes `idp.test`, `wallet.test`, `corp.test`
  2. No junk hosts
  3. `auth_tokens[].domain` registrable
  4. `login.domain` is `wallet.test`, `login.path` is `/ppsecure/post.srf`, no `username`/`password` keys
  5. `credentials` is map, `username.key: loginfmt`, `password.key: passwd`, `type: post`, `search` non-placeholder
  6. `auth_urls` includes `/checkpassword.srf`, `/common/GetCredentialType`
  7. `sub_filters` non-empty object list, no placeholders
  8. `min_ver: "2.3.0"`, `author` non-empty
  9. Full YAML text has no `{{PLACEHOLDER}}` substring
- Schema validation must pass

**Acceptance:** A5e, A11 (partial)

---

### WP14: Unit Tests
**Dependencies:** WP2, WP5, WP8  
**Deliverables:**
- `tests/unit/normalize-origin.test.js` (A3g)
- `tests/unit/form-capture.test.js` (A3h)
- `tests/unit/psl-extraction.test.js`
- `tests/unit/deny-list.test.js`

**Acceptance:** A3g, A3h, A11 (partial)

---

### WP15: Integration Tests
**Dependencies:** WP3, WP8, WP9  
**Deliverables:**
- `tests/integration/lifecycle-persistence.test.js` (A3e)
- `tests/integration/generator-e2e.test.js` (A5c: all fixtures, secret rejection)
- `tests/integration/validator.test.js` (A5d mutations)

**Acceptance:** A3e, A5c, A5d, A11 (partial)

---

### WP16: Test Runner (R11, A11)
**Dependencies:** WP14, WP15, WP13  
**Deliverables:**
- `tests/test-runner.js`: single command runs all suites
- Import child test modules; they return/throw, don't call `process.exit`
- Only top-level runner sets exit code
- Document: `npm test` or `node tests/test-runner.js`

**Acceptance:** A11

---

### WP17: Page Snapshot Utility (R5)
**Dependencies:** WP1  
**Deliverables:**
- Extension/CLI: save HTML snapshot + report
- Optional training modules (`ui_overlay_awareness`, `file_picker_awareness`) check `config/lab_unsafe_modules.json` `{lab_unsafe_modules: false}`

**Acceptance:** A6

---

### WP18: Documentation (R8, R9)
**Dependencies:** All functional WPs  
**Deliverables:**
- README.md: build, load unpacked, **Grant → Reload → Start → browse** order, authorized-use notice, Evilginx 2.3.0 format, placeholder-free guarantee, operator must configure domain/lures and lab-test
- OPSEC_CARD.md: ≥3 Detection Recommendations (defender-oriented)

**Acceptance:** A8, A9

---

### WP19: Static Analysis (R10)
**Dependencies:** WP18  
**Deliverables:**
- Run Semgrep + ast-grep
- Archive outputs to `scanners/`

**Acceptance:** A10

---

### WP20: Manual Testing (A2, A3b, A3c)
**Dependencies:** All functional WPs  
**Deliverables:**
- `tests/manual/MANUAL_TESTS.md`: step-by-step for A2 (load unpacked), A3b (multi-origin smoke), A3c (pre-flight error)

**Acceptance:** A2, A3b, A3c

## 3. Interface Contracts

### Extension ↔ Service Worker
- Popup sends messages: `{action: 'startRecording'}`, `{action: 'stopRecording'}`, `{action: 'exportSession'}`
- Service worker responds: `{status: 'ok', data: {...}}` or `{status: 'error', message: '...'}`

### Generators
```javascript
// phishlet-generator.js
export function generatePhishlet(captureSession, options): string; // YAML

// markdown-exporter.js
export function exportMarkdown(captureSession): string;

// traffic-stub-exporter.js
export function exportTrafficStub(captureSession): string;
```

### Validator
```javascript
// validator.js
export function validatePhishlet(yamlString): {valid: boolean, errors: string[]};
```

### CLI
```
node cli/generate.js --input <capture.json> --output-phishlet <out.yaml> [--output-markdown <out.md>] [--output-traffic <out.txt>]
```

## 4. Requirement Trace Matrix

| Requirement | Work Package(s) |
|-------------|-----------------|
| R1 | WP1 |
| R2 | WP4 |
| R2a | WP2 |
| R2b | WP4 |
| R2c | WP2, WP4 |
| R2d | WP4, WP6 |
| R2e | WP3 |
| R2f | WP5 |
| R3 | WP6, WP7 |
| R4 | WP8, WP9 |
| R4g | WP8 |
| R5 | WP17 |
| R6 | WP10 |
| R7 | WP11 |
| R8 | WP18 |
| R9 | WP18 |
| R10 | WP19 |
| R11 | WP16 |
| R12 | WP12, WP13 |

| Acceptance | Work Package(s) |
|------------|-----------------|
| A1 | WP1 |
| A2 | WP1, WP20 |
| A3 | WP6 |
| A3b | WP4, WP6, WP20 |
| A3c | WP2, WP4, WP20 |
| A3d | WP6 |
| A3e | WP3, WP15 |
| A3f | WP2 |
| A3g | WP2, WP14 |
| A3h | WP5, WP14 |
| A4 | WP7 |
| A5 | WP8, WP9 |
| A5b | WP8 |
| A5c | WP8, WP15 |
| A5d | WP9, WP15 |
| A5e | WP12, WP13 |
| A6 | WP17 |
| A7 | WP10 |
| A8 | WP18 |
| A9 | WP18 |
| A10 | WP19 |
| A11 | WP11, WP14, WP15, WP16 |

## 5. Test Plan

### Automated Tests
- **A3e:** Lifecycle persistence (mock Chrome APIs, simulate restart)
- **A3g:** Origin normalization (idempotence, reject userinfo/non-HTTP)
- **A3h:** Form capture (mocked DOM, no values)
- **A5c:** Generator E2E (all fixtures, secret rejection)
- **A5d:** Schema validator mutations
- **A5e:** Regression-mixed-capture (9-point assertion)
- **A11:** Single test runner executes all suites

### Manual Tests (documented in `tests/manual/MANUAL_TESTS.md`)
- **A2:** Load unpacked, no console errors
- **A3b:** Multi-origin smoke (≥2 origins, ≥5 events, ≥1 non-fallback)
- **A3c:** Start recording without host access → clear error
- **A3f:** Grant → Reload → verify origins remain

### Schema-Only Tests
- **A1:** Manifest inspection (MV3, permissions list, content script declared)
- **A3:** Fixture session JSON exists
- **A4:** Markdown export exists
- **A6:** Config file `lab_unsafe_modules: false`
- **A7:** Traffic-stub export exists
- **A8:** README content check
- **A9:** OPSEC_CARD ≥3 bullets
- **A10:** Semgrep + ast-grep outputs exist

### Manual Fidelity (M1–M8)
- Spot checks during manual tests
- README review for M7 guidance

## 6. Out of Scope

- Targeting live systems without authorization (explicitly forbidden)
- Capturing or storing credential **values**, session tokens, request/response bodies
- Inventing IdP-specific anti-bot JS removal, `force_post`, or `js_inject` beyond hostname-rewrite `sub_filters`
- Guaranteed working Evilginx deployment against any live IdP (phishlet is loadable and placeholder-free, but operator must configure domain/lures and lab-test)
- Step-by-step attack playbooks
- Support for Manifest V2
- Support for Firefox/Safari (Chrome MV3 only)
- Real-time streaming export (captures are start → browse → stop → export)
- Automatic phishlet testing against live IdPs
- GUI phishlet editor

## 7. Assumptions

1. **PSL library:** Use `psl` npm package for eTLD+1 extraction.
2. **YAML library:** Use `js-yaml` (strict mode) for generation and parsing.
3. **JSON Schema library:** Use `ajv` for validation.
4. **Test framework:** Use Node.js built-in `node:test` (Node 18+) or simple assertion runner.
5. **Username field priority:** Exact match order (case-insensitive): `loginfmt` > `login` > `user` > `username` > `usernameEntry` > `email` > `account`.
6. **Credential key fallback:** If no password form captured, use heuristic keys `login` / `passwd` and document in phishlet comment that keys are not DOM-evidenced.
7. **Coverage threshold:** At least one `webRequest` event required; only navigation fallback = incomplete.

---

**Handoff to Stage 3 (Ops Advisor):** Plan complete. Proceed to operational constraints and opsec review.
