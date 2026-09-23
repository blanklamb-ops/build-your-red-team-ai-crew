# OPSEC Card — chrome-mv3-kit

## 1. Summary

Chrome MV3 Kit is an authorized-lab documentation tool. Its unpacked Manifest V3 extension records local authentication-flow metadata—URLs, methods, status, resource type, selected header names, Set-Cookie names, and form field names/types—then exports local JSON/Markdown, static HTML snapshots, a commented traffic-pattern stub, and capture-faithful Evilginx 3.x-format YAML. It deliberately does not retain header/cookie/input values or bodies, performs no application-originated exfiltration, requests broad HTTP(S) access only after an operator gesture, and keeps training demonstrations disabled by default.

## 2. Operator risks

- Broad optional host access can expose metadata from unrelated tabs if the operator grants all HTTP(S) origins and browses outside the authorized lab while recording. Prefer the complete narrow origin set.
- Full URLs are evidence and may contain authorization codes, state parameters, account identifiers, or internal topology even though the recorder never captures body/header/cookie values and the generator intentionally does not classify URL queries as secrets.
- Static snapshots can preserve visible page text, links, DOM structure, internal names, and referenced resource URLs. Sanitizing scripts and form values does not make a snapshot non-sensitive.
- Chrome storage persists across service-worker suspension, extension reload, and ordinary cache/history clearing. Failure to stop, export, and remove retained evidence can extend the collection/retention window.
- Generated YAML can be misleading if coverage is incomplete, host permission was missing, the operator overrides a deny-listed host, or capture-derived rankings are accepted without review. It is not proof of a deployable live-IdP phishlet.
- Editing both training gates to true enables conspicuous page overlays or a file-picker control. These demonstrations can confuse users, trigger endpoint/browser telemetry, or exceed scope if used outside a labeled exercise.
- Unpacked developer-mode extensions, CLI invocations, generated filenames, and scanner/test activity are visible to endpoint controls and can disclose the methodology.

## 3. Artifacts left behind

- Browser profile: the unpacked extension registration and ID, granted optional-origin permissions, developer-mode state, and `chrome.storage.local` LevelDB data (commonly under the profile's `Local Extension Settings/<extension-id>/`) containing requested/granted/missing origins, URLs, timestamps, event sources/counts, header/cookie names, and form metadata.
- Browser/runtime logs: extension service-worker and popup console errors, extension install/reload/activity records where the managed-browser product exposes them, and normal browser history/cache created by the exercised flow.
- Downloads/files: `chrome-mv3-session-*.json`, `chrome-mv3-session-*.md`, `chrome-mv3-snapshot-*.html`, matching snapshot reports, generated `.yaml`, Markdown summaries, and traffic-pattern text files.
- Development host: workspace sources, `build/` outputs, Python bytecode/cache if not cleaned, npm metadata, scanner output, terminal/shell history, and process telemetry for `python3 generators/cli.py`, `npm test`, Semgrep, and ast-grep.
- Network: the extension itself makes no off-host requests. The operator's ordinary browser requests to every exercised origin remain visible in proxy, DNS, TLS, firewall, IdP, application, WAF, and browser telemetry. Snapshotting does not fetch extra resources.
- No registry keys, mail, persistence service, scheduled task, or external server-side storage are created by the kit itself.

## 4. Safer operating guidance

- Obtain written scope, use synthetic/owned identities, and enumerate every redirect origin before capture. Prefer a narrow origin set; if broad access is necessary, use a dedicated browser profile and do nothing unrelated in it.
- Follow **Grant → Reload → Start → browse → Stop**. Before browsing, confirm requested equals granted and missing is empty. Reject a one-event or fallback-only export and any export marked `coverage: incomplete`.
- Stop immediately after the authorized flow. Review URLs—including query strings—before sharing; handle JSON, Markdown, HTML, YAML, and traffic stubs as engagement evidence even when no credential values are present.
- Keep `lab_unsafe_modules=false` and both module flags false unless the exercise explicitly includes a labeled demonstration. Never enable demos merely to take a snapshot.
- Validate generated YAML, inspect every host/path/cookie/field choice, and treat exact `--include-host` overrides as review events. Complete only `credentials.search` and `sub_filters` from authorized lab knowledge; do not infer live-target rules.
- Store artifacts in an access-controlled engagement directory, set a retention deadline, securely remove the dedicated profile and exports when permitted, and record the removal in engagement notes.
- Unload the extension and revoke its host permissions after the exercise. Do not reuse the capture profile for personal or production browsing.

## 5. Detection Recommendations

- **Managed-browser extension inventory:** alert on unmanaged/unpacked extensions whose manifest combines `webRequest`, `webNavigation`, `storage`, and `downloads` with optional `http://*/*` and `https://*/*` access. Correlate developer-mode installation/reload with new broad host grants; allowlist the approved lab extension ID only for the exercise window.
- **Endpoint process telemetry:** query process creation for Chrome/Chromium launched with `--load-extension` or an isolated test profile, and for command lines containing `generators/cli.py phishlet`, `generators/cli.py validate`, `npm test`, `semgrep scan`, or `ast-grep scan`. Correlate to the authorized operator, host, and change ticket rather than treating the string alone as malicious.
- **Filesystem and DLP hunting:** monitor browser download and engagement directories for `chrome-mv3-session-*.json`, `chrome-mv3-snapshot-*.html`, traffic-pattern stubs, or YAML containing both the header `AUTHORIZED LAB USE ONLY` and keys `proxy_hosts`, `auth_tokens`, `auth_urls`, and `sub_filters`. Flag copies outside approved encrypted evidence storage.
- **Browser-profile artifacts:** where policy and privacy rules allow, hunt `Local Extension Settings/<extension-id>` and extension preference records for broad optional-origin grants plus stored keys such as `capture_state_v1`, `requested_origins`, `counts_by_source`, and `set_cookie_names`. Use this to confirm collection scope and retention, not to recover credential values the tool does not store.
- **Identity/proxy correlation:** during the authorized window, compare the session's origin list and timestamps with IdP/WAF/proxy/DNS logs. Alert when the research profile reaches origins outside the approved set or when authentication-like traffic continues after the recorded stop time. There is no distinctive kit-generated network beacon, so network-only signatures should not claim attribution.
- **Training-module control:** file-integrity monitor `extension/config.js` and `config/default.json` for `lab_unsafe_modules: true`. If enabled, correlate with browser DOM/extension activity and require an approved awareness-exercise ticket.
- **Evidence-retention control:** create a scheduled compliance query for stale session/snapshot/YAML artifacts and residual dedicated Chrome profiles after the engagement retention deadline; verify deletion or documented legal hold.

## 6. Residual gaps

This review verified source, automated tests, schema mutations, the unchanged A5e fixture, and local static scans. It could not load the extension in a clean GUI profile, observe Chrome's permission UI/enterprise audit events, execute the required two-origin redirect smoke, validate snapshot sanitization against a real complex DOM, or test organization-specific EDR/DLP queries. Chrome policy and profile paths vary by OS/version. Semgrep and ast-grep used small local rulesets and are evidence of the required run, not a comprehensive security audit. The manual A2/A3b procedure and environment-specific detection tuning remain required before client handoff.

