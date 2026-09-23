# OPSEC Card — chrome-mv3-kit

## 1. Summary

chrome-mv3-kit is an authorized-lab Chrome Manifest V3 documentation utility. It records local HTTP-flow metadata and form field **names/types** (not values), exports JSON/Markdown, saves sanitized static snapshots, creates a commented traffic-pattern skeleton, and generates a conservative Evilginx 2.3.0 phishlet scaffold from synthetic or sanitized evidence. It does not provision domains/lures, replay credentials, or send capture data off-host.

## 2. Operator risks

- Granting the one-click optional HTTP(S) permission exposes metadata from all browsed HTTP(S) origins to the extension while recording. Use a dedicated lab profile, stop promptly, and do not mix client or personal browsing.
- URLs, status codes, cookie/header names, form field names, submit labels, and visible snapshot text can disclose application structure, identifiers, query strings, or engagement context even without secret values.
- A site may place tokens or personal data in URLs or visible DOM text. Generator secret checks reduce but cannot eliminate that risk; exported JSON, Markdown, HTML, YAML, and console output require human review.
- Missing permissions or flaky header callbacks produce incomplete evidence. Treat the explicit coverage: incomplete marker as a stop condition, not as permission to infer missing behavior.
- An unpacked extension and broad permission request are conspicuous in browser-management, endpoint, and user-observation channels. The toolkit is not designed for covert collection.
- Generated phishlet files are dual-use and can be misread as deployment-ready. They still require authorized domain/lure configuration and lab testing, and must remain within the engagement evidence boundary.
- The include-host CLI option can override conservative host exclusion. Record the reason and confirm scope before using it.
- Enabling lab_unsafe_modules exposes training-only awareness interactions. The default is false; do not enable outside a controlled training profile.

## 3. Artifacts left behind

- Chrome profile: an unpacked-extension record/ID, extension permission decisions, developer-mode indicators, service-worker registration/logs, download history, and chrome.storage.local data under the profile’s extension storage.
- Local files: lab-auth-flow JSON/Markdown, lab-page-snapshot HTML and its JSON report, generated YAML, traffic skeletons, shell history, test output, and temporary generator outputs chosen by the operator.
- Endpoint telemetry: Node.js, Semgrep, ast-grep, Chrome/Chromium process creation; reads/writes in the repository, Downloads, and /tmp; possible EDR collection of command lines or generated content.
- Network/infrastructure logs: only the operator-driven lab browsing is expected—DNS, proxy, firewall, TLS, server access, IdP/audit, and redirect-chain logs. The implementation has no fetch/XHR/WebSocket telemetry or export channel.
- Registry/mail: no tool-created registry or mail artifacts are expected. OS/browser policy systems may nevertheless log extension installation and permission changes.

## 4. Safer operating guidance

- Obtain written scope, enumerate every redirect origin, and use a disposable, dedicated Chrome profile with synthetic identities and .test/owned lab hosts.
- Follow **Enable/Grant → Reload if needed → verify requested/granted/missing → Start → browse → Stop**. Keep recording windows short and reject fallback-only or permission-gapped captures.
- Prefer the narrower complete origin set when operationally practical. If broad HTTP(S) access is used for redirect reliability, close unrelated tabs and clear the dedicated profile after evidence is retained.
- Keep training modules disabled. Do not use include-host without a written, reviewable reason.
- Review URLs, query strings, visible snapshot text, and generator inputs for client identifiers or secrets before sharing. Encrypt evidence at rest, restrict access, and apply the engagement retention/deletion schedule.
- Validate generated YAML locally, configure domain/lures separately, and test only in the authorized lab. Do not infer or add capture-unsupported bypass, injection, or replay behavior.
- Remove extension storage/profile data and downloaded/temp artifacts at closeout using approved evidence-destruction procedures; retain only the client-agreed report set.

## 5. Detection Recommendations

- Inventory browser extensions and alert on unmanaged/unpacked Chrome extensions combining webRequest, webNavigation, downloads, scripting, and optional broad HTTP(S) host access. Review Chrome enterprise/browser telemetry for new developer-mode extensions and broad runtime permission grants on non-approved research endpoints.
- Hunt endpoint file-creation events in Downloads, temporary directories, and research workspaces for names such as lab-auth-flow.json, lab-auth-flow.md, lab-page-snapshot.html, and newly created phishlet YAML files. Triage content for min_ver 2.3.0, proxy_hosts, auth_tokens, and sub_filters, while allowlisting sanctioned lab systems through change records rather than suppressing globally.
- Monitor Chrome extension storage and profile changes—particularly Local Extension Settings, extension service-worker databases, Preferences/Secure Preferences, and download-history updates—correlated with chrome://extensions developer-mode activity. Preserve the profile before cleanup when an unapproved extension is suspected.
- Correlate proxy/DNS/server logs for a workstation visiting several authentication/redirect origins in a short interval, especially sequences containing login, authorize, GetCredentialType, password POST, or SAML paths followed by local artifact creation. Validate against the approved lab origin list; do not treat the pattern alone as malicious.
- On identity and lab web servers, alert on unexpected synthetic-account authentication bursts, repeated redirect-chain testing, or access from non-designated research endpoints. Join IdP audit events with endpoint/browser-extension inventory to distinguish authorized testing from unapproved collection.
- Detect command lines invoking the generator CLI phishlet, validate, or traffic actions outside approved repositories, and review subsequent YAML/snapshot outputs. Likewise, treat Semgrep/ast-grep activity as contextual—not malicious by itself—and correlate with the extension and artifact indicators.
- If the extension is found outside scope, isolate the browser profile, export browser/EDR/proxy evidence, revoke affected synthetic or real sessions as appropriate, and inspect URLs/snapshots for accidentally retained tokens before deletion.

## 6. Residual gaps

- The review verified automated suites, source syntax, fixture hash equality, generator/validator output, and archived zero-finding local scanner runs. It did not execute Chrome’s unpacked-extension UI or the manual two-origin A3b redirect smoke in a clean profile.
- Chrome version/policy differences can affect permission prompts, response-header visibility, content-script execution, and download behavior; those require environment-specific validation.
- Snapshot sanitation cannot prove that visible text or URLs are non-sensitive, and secret-pattern rejection cannot recognize every proprietary token format.
- A custom dependency-free YAML parser validates the emitted subset and tested mutations; independent validation with the exact Evilginx 2.3.x build remains part of authorized lab testing.

