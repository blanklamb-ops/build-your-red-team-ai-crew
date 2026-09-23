# Chrome MV3 Lab Kit

**AUTHORIZED LAB USE ONLY** — Academic/conference methodology study

A Chrome Manifest V3 extension kit for authorized security researchers who need to document browser authentication flows in controlled lab environments.

## ⚠️ Authorization Notice

This tool is designed for:
- **Authorized security research labs only**
- Academic methodology studies
- Controlled testing environments with explicit authorization
- Educational security analysis

**NOT for:**
- Targeting systems or identities without authorization
- Production deployments against live services
- Circumventing security controls

See `AUTHORIZED_USE.md` for complete usage restrictions.

## Features

- **MV3 Extension**: Record HTTP metadata from browser authentication flows (URLs, methods, status codes, header names, cookie names — not values)
- **Multi-origin support**: Track flows across multiple authorized domains
- **Form metadata capture**: Record input field names (never values) for credential mapping
- **Phishlet generator**: Create Evilginx 3.x-compatible phishlet YAML from captured sessions
- **Traffic pattern export**: Generate commented URL pattern skeletons for lab documentation
- **Persistence**: Survives MV3 service worker lifecycle events

## Directory Structure

```
extension/           # Chrome MV3 extension
  ├── manifest.json
  ├── service-worker.js
  ├── popup.html/js
  ├── content-script.js
  └── shared.js
generators/          # Phishlet and traffic-pattern generators
schemas/             # JSON schemas for validation
testdata/            # Synthetic fixtures
tests/               # Automated test suites
config/              # Lab configuration
```

## Installation

### 1. Install Dependencies

```bash
npm install
```

### 2. Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select the `extension/` directory

## Usage

### Recording Auth Flows

**IMPORTANT**: Follow this sequence exactly:

1. **Configure origins** — In the popup, enter authorized origins (one per line):
   ```
   https://login.example.test
   https://auth.example.test
   ```

2. **Enable Lab Access** — Click "Enable Lab Access" button
   - Grant permissions in the Chrome dialog
   - If you just granted new permissions, **reload the extension** at `chrome://extensions`

3. **Verify access** — Popup should show "Host access: Granted"

4. **Start Recording** — Click "Start Recording"
   - If access is missing, you'll see a clear error — return to step 2

5. **Exercise the flow** — Navigate through the auth flow in your browser

6. **Stop Recording** — Return to popup and click "Stop Recording"

7. **Export** — Click "Export Session (JSON)" or "Export Summary (Markdown)"

### Host Access

The extension uses **optional** host permissions (not granted at install). This means:
- No silent host access — operator must explicitly grant
- One-click enable for default `http://*/*` and `https://*/*`
- Or specify exact origins for narrower access
- Extension refuses to record without granted permissions (prevents silent 0-event sessions)

### Generating Phishlets

From a captured session JSON:

```bash
node generators/phishlet-generator.js testdata/synthetic-session.json --output phishlet.yaml
```

Options:
- `--name <phishlet-name>` — Set phishlet name (default: `lab-target`)
- `--include-host <host>` — Override telemetry exclusion for specific host
- `--output <file>` — Write to file instead of stdout

The generator will:
- ✅ Populate `proxy_hosts` from observed auth-relevant hosts
- ✅ Populate `auth_tokens` from captured Set-Cookie names
- ✅ Populate `auth_urls` from observed auth-like paths
- ✅ Populate `login.domain` and `login.path`
- ✅ Populate `credentials` and `login.username/password` when form field names were captured
- ✅ Exclude telemetry/CDN hosts by default (clarity.ms, copilot.com, etc.)
- ⚠️ Leave `sub_filters` as `{{PLACEHOLDER}}` (requires operator completion)

**Operator must still complete**:
- `sub_filters` — JavaScript proxy-rewrite recipes (cannot be derived from metadata)
- Lab testing to verify the phishlet works in your environment

**This is NOT a guaranteed working deployment** — it's a capture-faithful starting point.

### Validating Phishlets

```bash
node generators/validator.js phishlet.yaml
```

Uses YAML parser + JSON Schema validation to catch:
- Structural errors
- Forbidden properties (e.g., cookie `value` keys)
- Wrong `auth_tokens` shape
- Non-placeholder patterns without evidence

### Traffic Pattern Export

```bash
node generators/traffic-pattern.js testdata/synthetic-session.json --output pattern.md
```

Generates a commented skeleton of observed URL patterns for lab documentation.

## Permissions Justification

| Permission | Purpose |
|------------|---------|
| `webRequest` | Capture HTTP request/response metadata (methods, status codes, header names) |
| `webNavigation` | Fallback for navigation events if webRequest misses frames |
| `storage` | Persist session state across MV3 service worker restarts |
| `downloads` | Export session JSON and markdown summaries |

**Host permissions** (`http://*/*`, `https://*/*`):
- Declared as **optional** (not required at install)
- Requested at runtime from user gesture
- Required for capturing cross-origin auth flows

## Testing

Run all tests:

```bash
npm test
```

Individual test suites:
- `tests/test-normalization.js` — Origin normalization (idempotent, rejects userinfo/non-HTTP)
- `tests/test-lifecycle.js` — MV3 persistence (simulates worker restart)
- `tests/test-form-capture.js` — Form field metadata (verifies no values captured)
- `tests/test-generator.js` — Phishlet generation and secret rejection
- `tests/test-validator.js` — Schema validation

## Telemetry Exclusion

The phishlet generator **excludes telemetry/CDN hosts by default**:
- `clarity.ms`
- `bing.com`
- `browser.events.data.microsoft.com`
- `google-analytics.com`, `analytics.google.com`
- `copilot.com`, `copilot.microsoft.com`
- Paths containing `OneCollector`
- `ms-sso.copilot.*` patterns

Use `--include-host` to override for specific hosts.

## Detection Recommendations

See `OPSEC_CARD.md` for defender-oriented detection guidance.

## License

Academic research use only. See `AUTHORIZED_USE.md`.

## Support

This is a research artifact from ROOTCON 20 methodology study. No production support is provided.
