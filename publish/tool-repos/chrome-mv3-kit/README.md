# Chrome MV3 Lab Kit

A Chrome **Manifest V3** lab documentation toolkit for authorized security researchers. Captures browser authentication flow metadata, generates operator-ready Evilginx 2.3.0 phishlet YAML, and provides lab documentation exports.

**Authorized lab use only.** See [AUTHORIZED_USE.md](AUTHORIZED_USE.md).

## Features

- **MV3 Auth Flow Recorder**: Captures request metadata (URLs, methods, status codes, header/cookie **names only** - never values)
- **Host Access Management**: Runtime permission workflow for multi-origin lab flows
- **Form Metadata Capture**: Records form structure (field names/types) - **never captures input values**
- **Evilginx 2.3.0 Phishlet Generator**: Emits **placeholder-free**, schema-valid YAML with:
  - Capture-derived `proxy_hosts`, `auth_tokens`, `credentials` keys, `login.path`
  - Real `search` patterns (default `(.*)` for `post` type)
  - Object-shaped `sub_filters` derived from `proxy_hosts` using `{hostname}` variables
  - Telemetry/CDN/analytics host filtering (R4g gold-kit rules)
- **Markdown & Traffic Pattern Exports**: Human-readable reports and URL skeleton stubs
- **MV3 Persistence**: Survives service worker suspension via `chrome.storage`

## Build & Load

### Prerequisites

- Node.js 18+ (for generators/tests)
- Chromium-based browser (Chrome, Edge, Brave, etc.)

### Install Dependencies

```bash
npm install
```

### Load Extension (Unpacked)

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `extension/` directory from this repository

The extension icon should appear in your toolbar.

## Usage Workflow

**Critical:** Follow this exact sequence to avoid silent 0-event captures:

### 1. Grant Host Access

1. Click the extension icon to open the popup
2. Click **"Enable Lab Access (http/https)"** for default wildcard access
   - OR use **"Custom Origins"** to specify exact authorized origins
3. **Allow** the permission request when Chrome prompts
4. **Reload the extension** if Chrome suggests it (visit `chrome://extensions/`, toggle off/on)
5. Re-open the popup and verify **"Access granted"** appears

### 2. Start Recording

1. In the popup, click **"Start Recording"**
2. If host access is missing, you'll see a clear error - go back to step 1
3. When recording starts, the status shows **"🔴 Recording: N events"**

### 3. Browse Your Lab Flow

Navigate through your authorized authentication flow in the browser:
- Login pages
- OAuth/SAML redirects
- Post-authentication landing pages

The extension captures:
- `webRequest` events with Set-Cookie names (via `extraHeaders`)
- `webNavigation` fallback for main-frame loads
- Form metadata when pages contain `<form>` elements

### 4. Stop & Export

1. Click **"Stop Recording"** in the popup
2. Export captured data:
   - **Export JSON**: Full capture with diagnostics (for phishlet generation)
   - **Export Markdown**: Human-readable report

### 5. Generate Phishlet

Run the CLI generator on your exported JSON:

```bash
node generators/cli.js generate path/to/lab-capture-<session-id>.json
```

**Outputs:**
- `<basename>-phishlet.yaml` - Evilginx 2.3.0 phishlet (placeholder-free, schema-valid)
- `<basename>-report.md` - Markdown summary
- `<basename>-traffic-pattern.txt` - URL skeleton (documentation aid)

### Validate Phishlet

```bash
node generators/cli.js validate path/to/phishlet.yaml
```

## Evilginx 2.3.0 Output

Generated phishlets follow the [Phishlet File Format (2.3.0)](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-(2.3.0)) specification:

- **No `{{PLACEHOLDER}}` tokens**: All fields populated with real values or documented heuristics
- **Map-shaped `credentials`**: `username` and `password` objects with `key`, `search`, `type`
- **Object `sub_filters`**: Hostname-rewrite filters derived from `proxy_hosts` using `{hostname}` variables
- **Telemetry filtering**: Excludes `copilot`, `graph`, `admin`, `monitor`, CDN hosts by default
- **Capture-derived keys**: When password form is captured, `credentials.*.key` uses actual field names (`loginfmt`, `passwd`)
- **Loadable YAML**: Passes JSON Schema validation and Evilginx 2.3.x YAML parser

**What the operator still does:**
- Configure phishlet domain/lure in Evilginx
- Lab-test live behavior against authorized targets
- Refine filters/tokens for IdP-specific edge cases

This tool generates **loadable scaffolds** - not guaranteed live-IdP phishlets.

## Permissions Justification

| Permission | Why |
|-----------|-----|
| `webRequest` | Capture HTTP metadata (method, status, header/cookie names) |
| `webNavigation` | Fallback recording for main-frame navigations |
| `storage` | Persist session state across MV3 service worker suspension |
| `downloads` | Export captured data as JSON/Markdown from popup |

**Host access (`http://*/*`, `https://*/*`):**
- **Optional** (requested at runtime, not granted at install)
- Required to observe auth flows spanning multiple origins
- Operator explicitly grants via popup before recording

## Testing

Run all test suites (origin normalization, lifecycle persistence, form capture, phishlet generation, schema validation, A5e regression):

```bash
npm test
```

Individual test files are in `tests/`:
- `test-origin-normalization.js` - Idempotent normalization, userinfo/scheme rejection
- `test-lifecycle-persistence.js` - MV3 service worker state survival
- `test-form-capture.js` - Form metadata capture (NO input values)
- `test-phishlet-generator.js` - Generator correctness, secret rejection, structure
- `test-schema-validation.js` - Schema mutation tests
- `test-regression-a5e.js` - **Critical**: Regression test against `testdata/regression-mixed-capture.json`

All tests must pass for acceptance.

## Lab Safety

- **No off-host exfiltration**: All data stays local (no API calls, no telemetry)
- **Never captures secrets**: Only header/cookie/field **names**, never values/bodies/tokens
- **Authorized use only**: See [AUTHORIZED_USE.md](AUTHORIZED_USE.md)
- **Detection surface**: See [OPSEC_CARD.md](OPSEC_CARD.md) for defender recommendations

## Project Structure

```
extension/
  manifest.json           # MV3 manifest
  background/             # Service worker (recorder)
  popup/                  # UI (host access + recording controls)
  content/                # Form metadata content script
  shared/                 # Origin normalization utilities
generators/
  phishlet-generator.js   # Evilginx 2.3.0 YAML generator
  host-classifier.js      # R4g filtering rules
  markdown-exporter.js    # Human-readable reports
  traffic-pattern-exporter.js  # URL skeleton
  phishlet-validator.js   # JSON Schema validator
  cli.js                  # CLI interface
testdata/
  regression-mixed-capture.json  # Regression fixture (A5e)
  phishlet-schema-2.3.0.json     # Evilginx 2.3.0 schema
tests/
  run-all-tests.js        # Master test runner
  test-*.js               # Test suites
```

## Limitations

- **Not a bypasser**: Does not guarantee evasion of any security control
- **Not a live phishlet**: Operator must configure domain/lures and lab-test
- **Lab-only**: Not for targeting unauthorized systems
- **No training modules by default**: `ui_overlay_awareness` and `file_picker_awareness` require `lab_unsafe_modules=true` in config (currently disabled)

## References

- [Evilginx 2.3.0 Phishlet Format](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-(2.3.0))
- [Chrome Manifest V3](https://developer.chrome.com/docs/extensions/mv3/intro/)
- [webRequest API](https://developer.chrome.com/docs/extensions/reference/webRequest/)
- [Authorized Use Policy](AUTHORIZED_USE.md)

## License

MIT - Authorized research/education use only.
