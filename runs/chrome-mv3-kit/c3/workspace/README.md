# chrome-mv3-kit

**Authorized lab use only.** This offline-capable Chrome Manifest V3 documentation kit records sanitized authentication-flow metadata, exports JSON/Markdown evidence, creates static page snapshots, emits a commented traffic-pattern skeleton, and generates a placeholder-free Evilginx 2.3.0-format phishlet scaffold from synthetic or sanitized capture evidence.

This project is not an attack playbook and does not provision a phishing domain, lure, token replay, bypass, or live-target configuration. Use it only on systems and identities you are contractually or legally authorized to test. See [AUTHORIZED_USE.md](AUTHORIZED_USE.md).

## Requirements and test

- Chrome/Chromium with Manifest V3 and developer mode
- Node.js 18+ for the offline CLI/tests
- No npm packages or network access are required

Run every automated suite with the single documented command:

```sh
npm test
```

The runner covers manifest/listener structure, shared UI origin normalization, complete-set permission comparison, storage-backed service-worker restart, mocked form metadata/no-values, diagnostics and exports, generator behavior, secret rejection, real YAML parsing plus JSON-Schema validation/mutations, safe defaults, fixture hashes, and every A5e mixed-capture assertion. Imported suites return or throw; only `tests/run.js` sets the exit code.

## Load and record in an authorized lab

1. Open `chrome://extensions`, enable Developer mode, choose **Load unpacked**, and select `extension/`.
2. Open the extension popup and press **Enable lab access**. This is the one-click default request for optional `http://*/*` and `https://*/*` access. Select **Allow** in Chrome. For tighter scope, instead list the complete authorized host set and press **Approve listed origins**; bare hosts, origins, full URLs, and canonical match patterns are accepted.
3. Follow this exact order: **Enable/Grant → Reload the extension if needed → Start → browse** the authorized lab flow.
4. Before Start, verify the popup’s requested, granted, and missing origin lists. Start fails clearly if the complete requested set is not covered.
5. Exercise the smallest useful redirect flow, then Stop and export JSON/Markdown. Review the prominent coverage result. A fallback-only capture or any observed permission gap is **incomplete**, not a full flow.

Manual A3b smoke: approve at least two synthetic/owned origins, Grant → Reload → Start, exercise a redirect across both, and confirm the export has at least five events across two origins including a `webRequest_request` or `webRequest_response` event. A lone `webNavigation_fallback` event does not pass.

The recorder retains URL, method, status when available, resource type, event source, relevant header **names**, Set-Cookie **names**, and form actions/field names/types. It never intentionally reads or stores HTTP bodies, header/cookie values, input/autofill values, passwords, or tokens. Data remains in `chrome.storage.local` until the extension/profile data is cleared and exports are local downloads; there is no remote transport.

## Permission rationale

- `webRequest`: request/response metadata and header names; `onCompleted` uses `responseHeaders` plus `extraHeaders` so Chrome exposes Set-Cookie names.
- `webNavigation`: main-frame completion fallback and form-capture timing.
- `storage`: authoritative session, origin, timestamps, events, and diagnostics across service-worker suspension/restart.
- `downloads`: local JSON, Markdown, and snapshot files via `data:` URLs.
- `scripting`: reinjects the declared form metadata script after main-frame completions when host access permits.
- `activeTab`: lets the operator explicitly snapshot the current authorized page.
- Optional `http://*/*` and `https://*/*`: never granted silently at install; requested from a popup user gesture. Broad access is the reliable one-click redirect-flow path, while a narrower complete origin list is supported.

## Headless documentation generators

```sh
node generators/cli.js phishlet testdata/session-fixture.json /tmp/lab-phishlet.yaml
node generators/cli.js validate /tmp/lab-phishlet.yaml
node generators/cli.js markdown testdata/session-fixture.json /tmp/lab-flow.md
node generators/cli.js traffic testdata/session-fixture.json /tmp/lab-traffic-patterns.txt
```

Optional generator flags are `--author NAME` and repeatable `--include-host HOST`. The latter is an explicit audit-friendly override for a conservatively excluded lab host; it does not disable secret rejection.

The scored YAML follows the Evilginx **2.3.0** phishlet shape, is loadable/placeholder-free, and fills real credential `search` expressions and hostname-rewrite `sub_filters`; operators should not hand-edit those required fields. It contains a coverage comment when credential keys were heuristic instead of DOM-evidenced. Generation fails on missing structural evidence or secret-looking values. Cookie names and canonical UUID session IDs are permitted because they are metadata, not credential values.

After generation, the authorized operator must still configure the Evilginx phishlet domain and lures and test the result inside the lab. The tool does not invent missing capture evidence and does not guarantee compatibility with a live IdP. It emits no `force_post`, `js_inject`, anti-bot removal, or evasion recipe.

The validator parses the YAML document and validates the resulting object against `schemas/phishlet-schema-2.3.0.json`; it is not a substring-only check. The unchanged study regression lives at `testdata/regression-mixed-capture.json` and is generated/validated by `npm test`.

## Static snapshots and training modules

**Save static snapshot** clones the current page and removes scripts, embedded frames/objects, event handlers, remote source attributes, form values/state, and live form actions. It saves HTML plus a short JSON report. Page text and URLs can still be sensitive evidence, so inspect and retain them under engagement policy.

The `ui_overlay_awareness` and `file_picker_awareness` training demos are separate, labeled, and unavailable by default. All three switches in `config/default.json` and `extension/config.js` default false; handlers are only attached when `lab_unsafe_modules === true`. Do not enable them outside a controlled training lab.

## Outputs and limitations

- JSON and Markdown exports include source/origin counts, requested/granted/missing origins, session times, warnings, and `coverage`.
- The traffic skeleton is a commented list of observed HTTP method/URL patterns for documentation only, not a production implant/profile.
- Event pairing preserves request method and response status while source types remain distinguishable.
- Non-HTTP(S) browser-extension noise is omitted safely from exports.
- Static scanners are a controlled post-build step; their archived output is under `../scanners/`. No scanner is installed or replaced by this project.

See [OPSEC_CARD.md](OPSEC_CARD.md) before use. Manual Chromium loading and the two-origin redirect smoke cannot be proven by the Node-only test runner and must be completed in the authorized lab profile.
