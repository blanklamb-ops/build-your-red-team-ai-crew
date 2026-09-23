# chrome-mv3-kit

A Chrome **Manifest V3** lab documentation kit for authorized security
researchers. It records auth-flow HTTP **metadata**, generates
placeholder-filled config templates for engagement notes, saves static page
snapshots for offline review, and drafts a commented traffic-pattern
skeleton — all against **synthetic fixtures** or infrastructure you are
explicitly authorized to test.

**⚠️ Authorized lab use only.** See `AUTHORIZED_USE.md`. This is not a
working credential harvester, phishing proxy, or C2 implant — several
generators intentionally emit incomplete templates that require an operator
to fill in details under their own authorization before use.

## What's in here

```
extension/          MV3 browser extension (auth-flow recorder + export UI)
generators/          Node CLI + library: templates, page-clone, traffic-pattern stub
generators/lab_modules/  Gated, off-by-default "unsafe" structural-review modules (R5)
schemas/             JSON Schemas for all generator inputs/outputs
testdata/fixtures/    Synthetic fixtures only (example.com-style, no real targets)
config/lab.config.json  Default config — lab_unsafe_modules is false
out/                  Sample generator output (from testdata fixtures)
```

## Requirement → implementation map

| Req | Where |
|-----|-------|
| R1 | `extension/manifest.json` (MV3, minimal permissions — see below) |
| R2 | `extension/lib/background.js` (webRequest metadata recorder, local-only) |
| R3 | `extension/popup.js` (Export JSON / Export Markdown), `generators/lib/session_export.js` |
| R4 | `generators/lib/phishlet_template.js`, `schemas/phishlet_input.schema.json` |
| R5 | `generators/lib/page_clone.js` + `generators/lab_modules/` (gated) |
| R6 | `generators/lib/profile_stub.js`, `schemas/profile_stub_input.schema.json` |
| R7 | `generators/cli.js` (headless CLI over all generators) |
| R8 | `OPSEC_CARD.md` |
| R9 | this file |
| R10 | `../scanners/` (semgrep + ast-grep output archived by run harness) |

## Extension: build & load unpacked

**Recording order (required — skipping host access yields 0 events):**

1. Load unpacked → open popup → **Grant lab host access** → Allow.
2. On `chrome://extensions`, **Reload** the extension.
3. Popup status must show host access **granted**.
4. **Start recording**, *then* browse the lab page, then **Stop** → Export.

While recording is ON the service worker must log navigations/requests (not only
requests that already carry auth headers) and should include a `webNavigation`
main-frame fallback (see `extension/lib/background.js`).

No build step — the extension is plain ES modules loadable directly by
Chrome/Chromium.

1. Open `chrome://extensions`.
2. Enable **Developer mode** (top right).
3. Click **Load unpacked** and select the `extension/` directory.
4. Click the extension icon to open the popup.
5. Click **Grant lab host access** to request the optional
   `http://*/*` / `https://*/*` host permission (see *Permissions* below) —
   only needed once per profile, and only if you want the recorder to
   observe real page traffic instead of just being loaded.
6. Enter a target label (free text, **no secrets**), click **Start
   recording**, browse your **authorized lab target**, then **Stop
   recording**.
7. Use **Export JSON** / **Export Markdown** to save the session via
   `chrome.downloads`. Nothing is sent anywhere else — check
   `extension/lib/background.js`, there is no `fetch()`/`XMLHttpRequest`
   call in the service worker.

### Permissions (R1 / M1)

| Permission | Why |
|---|---|
| `storage` | Persist the current recording session locally (`chrome.storage.local`) so the popup can be closed/reopened without losing data. |
| `webRequest` | Observe request/response header **names** and status codes for the recorder. Non-blocking — this kit never modifies requests. |
| `downloads` | Let the popup save JSON/Markdown exports via `chrome.downloads.download()` instead of requiring clipboard copy-paste. |
| `optional_host_permissions: http(s)://*/*` | **Not granted by default.** Only requested at runtime, on demand, when the operator clicks "Grant lab host access" — `webRequest` cannot observe a request's headers without a matching host permission. Scope this down to your actual lab hosts in `manifest.json` if you know them ahead of time. |

No `<all_urls>` permission is present in the manifest's `permissions` list
at install time — it is optional and requested at runtime, so a reviewer
inspecting the unpacked extension before granting access sees an extension
that cannot observe any traffic yet.

## CLI: run generators headlessly on fixtures (R7)

```sh
node generators/cli.js session:export-json testdata/fixtures/session.sample.json out/session_export.json
node generators/cli.js session:export-md   testdata/fixtures/session.sample.json out/session_summary.md
node generators/cli.js phishlet:generate    testdata/fixtures/phishlet_input.sample.json out/phishlet_template.yaml
node generators/cli.js profile:generate     testdata/fixtures/profile_stub_input.sample.json out/profile_stub.txt
node generators/cli.js clone:run            testdata/fixtures/sample_page.html out/clone
```

All commands validate their input and exit non-zero with a clear stderr
message on missing/invalid input (ACCEPTANCE M3) rather than emitting
silent garbage.

### Gated "unsafe" lab modules (R5 / A6)

`clone:run` can additionally run two off-by-default structural-review
modules (clickjacking-susceptibility review, file-prompt pretext review —
see `generators/lab_modules/README.md`). Both of the following are required
to activate them:

```sh
# 1. config/lab.config.json must set:
{ "lab_unsafe_modules": true }

# 2. AND the CLI must be invoked with --lab-unsafe:
node generators/cli.js clone:run testdata/fixtures/sample_page.html out/clone --lab-unsafe --config config/lab.config.json
```

The shipped `config/lab.config.json` defaults to `lab_unsafe_modules: false`.
Passing `--lab-unsafe` alone, or flipping the config alone, is not enough —
see `generators/lab_modules/index.js`.

## Data handling

- The recorder (`extension/lib/background.js`) stores header/cookie
  **names**, never values, bodies, tokens, or passwords. See
  `schemas/session.schema.json`.
- All generator output is written to local files only. No generator or
  extension component in this repo makes an outbound network call other
  than the operator-directed `fetch()` in `generators/lib/page_clone.js`
  used to snapshot a page the operator supplies.
- Templates (`phishlet_template.js`, `profile_stub.js`) are intentionally
  incomplete skeletons with `__REPLACE_*__` / `{{PLACEHOLDER}}` markers —
  they contain no working proxy, C2, or credential-capture logic.

## Testing against fixtures

`testdata/fixtures/` contains only synthetic data (`example.com`-style
hostnames, fabricated session IDs). Do not add real client hostnames,
tokens, or engagement identifiers to this repo — see `AUTHORIZED_USE.md`
and ACCEPTANCE check M2.
