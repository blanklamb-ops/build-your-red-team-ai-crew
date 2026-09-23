# Chrome MV3 Auth Flow Lab Kit

**⚠️ AUTHORIZED LAB USE ONLY ⚠️**

Chrome Manifest V3 extension for authorized security researchers to document browser authentication flows in controlled lab environments. Generates operator-ready Evilginx 2.3.0 phishlets with minimal hand-editing required.

See `AUTHORIZED_USE.md` for usage boundaries and `OPSEC_CARD.md` for defender recommendations.

## Features

- **MV3 Extension Recorder**: Captures auth flow metadata (URLs, methods, status codes, header/cookie names only — never values)
- **Evilginx 2.3.0 Phishlet Generator**: Creates **placeholder-free, loadable YAML** with capture-derived fields:
  - `proxy_hosts` with PSL-based domain grouping and exclusion filters
  - `auth_tokens` from observed Set-Cookie names
  - `credentials` map with DOM-evidenced field keys (e.g., `loginfmt`, `passwd`)
  - `sub_filters` using Evilginx auto-fill variables (`{hostname}`)
  - Real `search` patterns (default `'(.*)'` for POST) — **no `{{PLACEHOLDER}}` tokens**
- **Lab Documentation Tools**: Traffic pattern skeletons, markdown exports
- **MV3 Lifecycle Safety**: Persists recording state across service worker restarts

## Installation

### Prerequisites

- Node.js 18+ (for generators and tests)
- Chromium-based browser (Chrome, Edge, Brave)

### Setup

```bash
# Install dependencies
npm install

# Run tests
npm test
```

## Extension Usage

### 1. Load Unpacked Extension

1. Open `chrome://extensions/` in your browser
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `extension/` directory
5. Note the extension ID

### 2. Grant Host Access → Reload → Start → Browse

**⚠️ CRITICAL ORDER:**

#### Step 1: Enable Lab Access

1. Click the extension icon to open popup
2. Click **"Enable Lab Access (All HTTP/HTTPS)"** for one-click `http://*/*` + `https://*/*` access
   - OR enter specific origins (e.g., `https://login.example.test, https://auth.example.test`) and click **"Request Custom Origins"**
3. Click **"Allow"** in the Chrome permission dialog
4. **Important**: If you just granted new origins, **reload the extension** (`chrome://extensions/` → click reload icon)

#### Step 2: Verify and Start Recording

1. Reopen the popup — verify "Lab access granted" is shown
2. Confirm requested origins are listed
3. Click **"Start Recording"**
   - ❌ **Error if access missing**: If you see "Missing permission for X", go back to Step 1
4. Browse to your authorized lab flow (login, OAuth, SAML, etc.)
5. Complete the full authentication flow across all required origins

#### Step 3: Stop and Export

1. Click **"Stop Recording"**
2. Use **"Export JSON"** to download the session file

### Permissions Explained

**Required at install:**
- `webRequest` — Capture request/response metadata
- `webNavigation` — Fallback for main-frame navigation events
- `storage` — Persist session state across service worker restarts
- `downloads` — Export JSON/markdown from popup

**Optional (runtime-requested):**
- `http://*/*`, `https://*/*` — Host access for the lab domains you're documenting

Why optional? Chrome MV3 requires explicit user consent for host access. The extension **cannot** record flows without permission for those origins.

## Generators

### Phishlet Generator

Converts captured session JSON to Evilginx 2.3.0 YAML:

```bash
node generators/phishlet-generator.js session.json \
  --output phishlet.yaml \
  --schema schemas/phishlet-schema-2.3.0.json \
  --author "your-name"
```

**Output Characteristics:**
- ✅ **Placeholder-free**: No `{{PLACEHOLDER}}` anywhere — the YAML is loadable as-is
- ✅ Capture-derived `credentials.username.key` / `credentials.password.key` when form fields were captured
- ✅ Heuristic fallback keys (`login` / `passwd`) when no password form seen (documented in comments)
- ✅ Real `search` patterns (e.g., `'(.*)'` for `type: post`)
- ✅ `sub_filters` derived from `proxy_hosts` with `{hostname}` rewrite patterns
- ✅ Excludes telemetry/CDN/analytics hosts by default (graph, admin, copilot, clarity, etc.)
- ⚠️ **Operator must still**: Configure phishlet domain/lures in Evilginx, lab-test against live IdP

**What This Does NOT Guarantee:**
- Working deployment against any specific live IdP after domain/lure setup
- Bypasses for anti-bot controls or IdP-specific mitigations
- That the generated `sub_filters` are sufficient for all IdP JS behaviors

### Traffic Pattern Generator

```bash
node generators/traffic-pattern-generator.js session.json --output pattern.md
```

### Markdown Exporter

```bash
node generators/markdown-exporter.js session.json --output report.md
```

## Testing

**Single command runs all tests (A11):**

```bash
npm test
```

**Includes:**
- ✅ A3e: MV3 lifecycle persistence (service worker restart simulation)
- ✅ A3f: Requested origins persist after grant/reload
- ✅ A3g: Idempotent origin normalization
- ✅ A3h: Form metadata capture (names only, never values)
- ✅ A5, A5b, A5c: Phishlet structure, secret rejection, schema validation
- ✅ **A5e: Regression test against `testdata/regression-mixed-capture.json`**
- ✅ A5d: JSON Schema validation with mutation tests

All tests import production functions (not test-only reimplementations).

## Project Structure

```
├── extension/
│   ├── manifest.json           # MV3 manifest
│   ├── service-worker.js       # Background recorder
│   ├── content-script.js       # Form field metadata capture
│   ├── popup/
│   │   ├── popup.html
│   │   └── popup.js
│   └── shared/
│       └── utils.js            # Origin normalization, UUID generation
├── generators/
│   ├── phishlet-generator.js   # Evilginx 2.3.0 generator
│   ├── traffic-pattern-generator.js
│   └── markdown-exporter.js
├── schemas/
│   └── phishlet-schema-2.3.0.json
├── testdata/
│   ├── regression-mixed-capture.json  # A5e fixture (DO NOT MODIFY)
│   └── example-simple.json
├── tests/
│   ├── test-runner.js          # A11 single-command runner
│   ├── utils-test.js
│   ├── lifecycle-test.js
│   ├── form-capture-test.js
│   ├── phishlet-generator-test.js
│   └── schema-validator-test.js
├── config/
├── AUTHORIZED_USE.md
├── OPSEC_CARD.md
├── README.md
└── package.json
```

## Evilginx 2.3.0 Format Notes

Generated phishlets conform to [Evilginx Phishlet File Format (2.3.0)](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-(2.3.0)):

- **No top-level `name`** (2.3.0 removes it)
- **`credentials` is a map** with `username` and `password` objects (not a list)
- **No `login.username` / `login.password`** (only `login.domain` and `login.path`)
- **`auth_tokens` is a list** of `{ domain, keys: [...] }` (no `value` keys)
- **`sub_filters` is a list of objects** (not bare strings)
- **`min_ver: "2.3.0"`**

The generator validates against the bundled JSON Schema before output.

## Workflow Summary

1. **Grant** → Allow → **Reload** (if new origins granted)
2. **Start** → Browse authorized lab flow
3. **Stop** → **Export JSON**
4. Run generator: `node generators/phishlet-generator.js session.json --output phishlet.yaml --schema schemas/phishlet-schema-2.3.0.json`
5. Operator configures Evilginx domain/lures and lab-tests the phishlet

## Troubleshooting

**"Missing permission" error when starting?**
- Verify popup shows "Lab access granted"
- Check that requested origins list includes the domains you plan to visit
- After granting new origins, **reload the extension** before starting

**Only 1 navigation event captured?**
- Likely missing host permission for redirect/POST targets
- Re-check granted origins cover all domains in the flow
- Export will mark `coverage: incomplete` and list missing permissions

**No Set-Cookie names in export?**
- Service worker uses `['responseHeaders', 'extraHeaders']` — check Chrome version supports MV3 extraHeaders
- Verify recording was active when navigating (not started mid-flow)

**Phishlet has heuristic `login`/`passwd` keys instead of DOM-evidenced?**
- No password-bearing form was captured
- Ensure content script ran on the login page (check for auth-related keywords in URL)
- Export's `form_fields` array should show captured field names

## References

- [Evilginx 2.3.0 Phishlet Format](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-(2.3.0))
- [Chrome MV3 Migration Guide](https://developer.chrome.com/docs/extensions/mv3/intro/)
- `AUTHORIZED_USE.md` — Usage boundaries
- `OPSEC_CARD.md` — Detection recommendations (defender handoff)

## License

Authorized lab use only. See `AUTHORIZED_USE.md`.
