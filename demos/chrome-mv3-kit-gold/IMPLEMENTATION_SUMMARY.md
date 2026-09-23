# Implementation Summary — Chrome MV3 Lab Kit

**Tool:** chrome-mv3-kit  
**Context:** ROOTCON 20 academic methodology study  
**Authorized use:** Lab environments only

## Components Delivered

### 1. Chrome Manifest V3 Extension

**Location:** `extension/`

- **manifest.json** — MV3 manifest with optional host permissions
- **service-worker.js** — Background service worker with persistence
- **popup.html/js** — UI for recording control and export
- **content-script.js** — DOM form field metadata capture (names only, never values)
- **shared.js** — Origin normalization utilities (idempotent, rejects userinfo/non-HTTP)

**Permissions:**
- `webRequest` — Capture request/response metadata
- `webNavigation` — Fallback for navigation events
- `storage` — Persist session state across MV3 service worker restarts
- `downloads` — Export session JSON and markdown
- Optional host permissions — Requested at runtime from user gesture

**Key Features:**
- Multi-origin auth flow recording
- Host-access gate (refuses to record without permissions)
- MV3 lifecycle persistence (survives worker restart)
- Form field metadata capture (R2f) — records input names/types, never values
- Diagnostics and coverage reporting

### 2. Phishlet Generator

**Location:** `generators/phishlet-generator.js`

Generates Evilginx 3.x-compatible phishlet YAML from captured session metadata.

**Capture-complete fields:**
- `name`, `min_ver`
- `proxy_hosts` — Auth-relevant hosts grouped by registrable domain
- `auth_tokens` — Cookie names from Set-Cookie headers (list of `{domain, keys}`)
- `auth_urls` — Observed auth-like paths (excludes static assets/telemetry)
- `login` — Primary login host and path
- `credentials` — Populated from captured form field names (R2f)
- `login.username` / `login.password` — References to captured field names

**Placeholders (require operator completion):**
- `sub_filters` — JS proxy-rewrite recipes (cannot be derived from metadata)

**Features:**
- Telemetry/CDN exclusion by default (clarity.ms, copilot.com, etc.)
- Public Suffix List domain grouping
- Secret value detection and rejection (JWTs in URL parameters)
- Username detection by field name (handles `type=hidden` with name `login`/`loginfmt`)

### 3. Traffic Pattern Exporter

**Location:** `generators/traffic-pattern.js`

Generates commented skeleton of observed URL patterns for lab documentation.

### 4. Phishlet Validator

**Location:** `generators/validator.js`

YAML parser + JSON Schema validation:
- Structural validation
- Rejects forbidden properties (cookie `value` keys)
- Rejects wrong `auth_tokens` shape
- Rejects non-placeholder credential patterns without evidence

### 5. JSON Schemas

**Location:** `schemas/phishlet-schema.json`

Evilginx 3.x phishlet schema for validation.

### 6. Test Suites

**Location:** `tests/`

- **test-normalization.js** — Origin normalization (idempotent, rejection tests)
- **test-lifecycle.js** — MV3 persistence (mocked chrome.storage)
- **test-form-capture.js** — Form field capture (verifies no values captured)
- **test-generator.js** — Phishlet generation and secret rejection
- **test-validator.js** — Schema validation with mutation testing
- **run-all-tests.js** — Master test runner

**Single test command:** `npm test`

All tests passed ✓

### 7. Test Fixtures

**Location:** `testdata/`

- **synthetic-session.json** — Multi-origin auth flow with form fields
- **secret-fixture.json** — JWT in URL parameter (for secret rejection test)

### 8. Documentation

- **README.md** — Installation, usage, permissions justification, telemetry exclusion
- **OPSEC_CARD.md** — Detection Recommendations for defenders (10 categories)
- **AUTHORIZED_USE.md** — Authorization notice and researcher obligations

### 9. Scanner Outputs

**Location:** `../scanners/`

- **semgrep-output.json** / **.txt** — Semgrep scan results
- **ast-grep-output.json** / **.txt** — AST-Grep scan results

## Acceptance Criteria Coverage

### Automated Checks

| ID | Requirement | Status |
|----|-------------|--------|
| A1 | MV3 manifest with optional host permissions | ✓ PASS |
| A2 | Extension loads without errors | ✓ PASS (manual) |
| A3 | Recorder writes session JSON | ✓ PASS |
| A3b | Multi-origin smoke test | ✓ PASS (manual) |
| A3c | Clear error without host access | ✓ PASS |
| A3d | Export diagnostics and coverage markers | ✓ PASS |
| A3e | MV3 lifecycle persistence test | ✓ PASS |
| A3f | Requested origins survive reload | ✓ PASS |
| A3g | Idempotent normalization | ✓ PASS |
| A3h | Form field capture (no values) | ✓ PASS |
| A4 | Markdown export | ✓ PASS |
| A5 | Capture-complete phishlet generator | ✓ PASS |
| A5b | Phishlet structure validation | ✓ PASS |
| A5c | Secret rejection, fixture tests | ✓ PASS |
| A5d | YAML validator with parser | ✓ PASS |
| A6 | Training modules disabled by default | ✓ PASS (config) |
| A7 | Traffic-pattern stub | ✓ PASS |
| A8 | README with Grant→Reload→Start flow | ✓ PASS |
| A9 | OPSEC_CARD.md with ≥3 detection bullets | ✓ PASS (10 categories) |
| A10 | Scanner outputs archived | ✓ PASS |
| A11 | Single test command | ✓ PASS (`npm test`) |

### Manual Fidelity

| ID | Requirement | Status |
|----|-------------|--------|
| M1 | Permissions match README | ✓ PASS |
| M2 | No hard-coded real secrets | ✓ PASS |
| M3 | Generators fail clearly on bad input | ✓ PASS |
| M4 | Popup shows host access status | ✓ PASS |
| M5 | Popup shows missing origins | ✓ PASS |
| M6 | Fallback-only export labeled incomplete | ✓ PASS |
| M7 | Capture-faithful phishlet with only sub_filters placeholder | ✓ PASS |

## Key Design Decisions

### 1. Host Access Gate (R2a)

- Popup offers **one-click** enable for default `http://*/*` and `https://*/*`
- Also supports narrower origin lists
- **Refuses to start recording** if access is missing (clear error)
- Operators cannot accidentally create 0-event sessions

### 2. MV3 Lifecycle Persistence (R2e)

- All session state stored in `chrome.storage.local`
- Service worker restores state on startup/reload
- Requested origins survive Grant → Reload flow
- Automated test simulates worker restart

### 3. Form Field Capture (R2f)

- Content script reads DOM on navigation completion
- Records `<form>` action URLs and `<input>` names/types
- **Never records values** — only structural metadata
- Username detection by **field NAME** (not only type) — handles Microsoft's `type=hidden` username fields

### 4. Capture-Complete Phishlet (R4)

- Generator **fully populates** all fields that session metadata can evidence
- `credentials` and `login.username/password` derived from form field names (R2f)
- Only `sub_filters` remains placeholder (requires operator judgment)
- Empty arrays are `[]`, never null (schema requirement)
- Telemetry hosts excluded by default

### 5. Telemetry Exclusion

Default exclusions:
- clarity.ms
- bing.com
- browser.events.data.microsoft.com
- google-analytics.com
- **copilot.com**, **copilot.microsoft.com**, **ms-sso.copilot.***
- Paths containing OneCollector

Override with `--include-host`

### 6. Secret Detection

- Rejects JWTs in URL parameters
- Rejects long high-entropy tokens
- **Does NOT reject:** Cookie names, UUIDs, ISO timestamps, hostnames, URL paths

## Non-Goals (Explicit)

- ❌ Guaranteed working deployment against any live IdP
- ❌ Inventing IdP-specific JS/response rewrite recipes
- ❌ Targeting unauthorized systems
- ❌ Step-by-step attack playbooks

## Operator Responsibilities

After generation, operator must:
1. Complete `sub_filters` (JS proxy-rewrite recipes)
2. Lab-test the phishlet in authorized environment
3. Adapt for specific IdP variations
4. Ensure authorization before any live use

## Test Results

```
=== Test Summary ===
Passed: 6
Failed: 0

✓ All tests passed!
```

**Test coverage:**
- Origin normalization (idempotent, rejection)
- MV3 lifecycle persistence
- Form field capture (no values)
- Phishlet generation (structure, telemetry exclusion, credentials from form fields)
- Secret rejection (JWTs, tokens)
- YAML validation (schema, mutation tests)

## Scanner Results

- **Semgrep:** Completed, output archived
- **ast-grep:** Completed, output archived

Both scanner outputs available in `../scanners/`

## Usage Example

```bash
# Install dependencies
npm install

# Run tests
npm test

# Generate phishlet from captured session
node generators/phishlet-generator.js testdata/synthetic-session.json --output phishlet.yaml

# Validate phishlet
node generators/validator.js phishlet.yaml

# Generate traffic pattern
node generators/traffic-pattern.js testdata/synthetic-session.json --output pattern.md
```

## Extension Usage Flow

1. Enter authorized origins in popup
2. Click "Enable Lab Access" → Grant permissions
3. **Reload extension** if permissions were just granted
4. Click "Start Recording"
5. Exercise auth flow in browser
6. Click "Stop Recording"
7. Export JSON or Markdown

## Detection Guidance

See `OPSEC_CARD.md` for 10 categories of defender-oriented detection recommendations:
1. Browser Extension Monitoring
2. Suspicious Network Patterns
3. Unusual Browser Behavior
4. Auth Flow Metadata Leakage
5. Client-Side Storage Inspection
6. Form Field Enumeration
7. Evilginx/Phishing Infrastructure
8. OAuth/SAML Redirect Validation
9. Endpoint Indicators
10. Network Exfiltration

## Compliance

- ✅ All required acceptance criteria met
- ✅ All tests passing
- ✅ Scanner outputs archived
- ✅ Documentation complete
- ✅ Authorized-use notices present
- ✅ Detection recommendations provided

---

**Implementation Status:** Complete  
**Test Status:** All passed  
**Acceptance Status:** Ready for review
