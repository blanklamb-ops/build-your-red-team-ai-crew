# OPSEC Card — chrome-mv3-kit

## 1. Summary

`chrome-mv3-kit` is an authorized-lab documentation kit. Its unpacked Chrome Manifest V3 extension passively records authentication-flow metadata—URLs, methods, status codes, resource types, selected header names, Set-Cookie names, and form action/control names and types—to local extension storage. Headless tools turn that evidence into JSON/Markdown reports, an explicitly incomplete-until-reviewed Evilginx 3.x YAML document, a static HTML snapshot, and a commented traffic-pattern skeleton. It does not store credential/cookie values, modify traffic, replay sessions, or transmit data to a backend.

## 2. Operator risks

- The one-click default grants the extension visibility across all HTTP(S) pages. Browsing out-of-scope sites while recording can capture URLs and metadata even though values/bodies are excluded.
- Authentication URLs, query strings, form-field names, cookie names, hostnames, and timestamps can still be sensitive engagement evidence. URL query parameters may themselves contain identifiers or short-lived codes supplied by a site.
- Static snapshots contain page-rendered HTML and may retain names, identifiers, or other displayed data; script removal does not sanitize text or attributes.
- Unpacked-extension installation, Developer mode, broad host permission prompts, persistent Chrome storage, downloads, and generator command history are conspicuous on an operator endpoint.
- A permission gap, fallback-only capture, cached request, or worker/storage failure can yield incomplete evidence. Treating `coverage: incomplete` as complete creates a fidelity and reporting risk.
- `--include-host` and operator-supplied credential regexes can override safe derivation constraints. Poor review may introduce irrelevant infrastructure or sensitive patterns into the output.
- The YAML is documentation generated from metadata, not proof of a safe or functional live deployment. Completing `sub_filters` outside a controlled lab materially changes risk and is outside this review.

## 3. Artifacts left behind

- **Browser:** unpacked extension registration/ID, Developer-mode state, optional host grants, service-worker console records, and `chrome.storage.local` state containing requested/granted origins, session ID, timestamps, events, and diagnostics. Profile paths commonly expose per-extension local storage.
- **Filesystem/downloads:** exported `chrome-mv3-kit-<session>.json` and `.md`; generated YAML, normalized JSON, Markdown, snapshot HTML/report, traffic skeleton, source tree, safe config, dependency metadata, test temporaries while running, and scanner JSON/stdout/stderr/status files.
- **Process and shell telemetry:** Chrome/Chromium, Node test runner, Python generator/validator/export utilities, Semgrep, ast-grep, and commands/arguments naming input/output evidence paths. Shell history may retain those paths and explicit include/regex overrides.
- **Network:** the extension and generators create no independent outbound connection. The operator's authorized page browsing still produces normal authentication/redirect traffic to every visited lab origin. Dependency installation, if performed, uses the operator's configured package sources and is separate from runtime.
- **Registry/mail:** no Windows registry or email artifact is intentionally created. Browser/OS management and endpoint products may still log extension installation, downloads, and processes.

## 4. Safer operating guidance

- Use a dedicated, disposable, non-synchronized Chromium profile and synthetic accounts on isolated lab origins. Close unrelated tabs and verify the written host scope before granting access.
- Prefer the complete narrow-origin list. If the required broad one-click grant is used, perform only the lab flow, Stop immediately, export, then remove the extension or revoke its site access.
- Follow **Grant → Reload → Start → browse → Stop → inspect coverage**. Refuse handoff when any origin is missing, only navigation fallback exists, or the event/origin counts do not match the exercised flow.
- Keep `lab_unsafe_modules=false` unless an approved training exercise explicitly needs a named inert awareness module. Never use client pages for snapshot acceptance.
- Store exports in the engagement evidence boundary, restrict access, hash or inventory deliverables as required, sanitize before publication, and delete the disposable browser profile/artifacts under the retention plan.
- Review every URL/query, cookie/form name, `--include-host` override, and operator regex. Complete `sub_filters` only under separate authorization in an isolated lab, then revalidate and document the change.

## 5. Detection Recommendations

- Inventory Chrome/Chromium extensions and alert on unpacked/Developer-mode extensions that combine `webRequest`, `webNavigation`, `downloads`, and broad optional `http://*/*` or `https://*/*` access. Correlate installation time, extension ID, host-permission changes, and the responsible user/device.
- On managed endpoints, monitor Chrome profile extension-storage locations for newly created records containing keys such as `labRecorderState`, `requested_origins`, `set_cookie_names`, `event_counts_by_source`, or `coverage_reasons`. Scope collection to policy and privacy requirements; these strings distinguish this kit from ordinary browsing history.
- Hunt endpoint file telemetry and DLP indexes for paired `chrome-mv3-kit-*.json`/`.md` downloads or YAML containing the combination `proxy_hosts`, `auth_tokens`, `auth_urls`, `credentials`, and `sub_filters`. Treat matches as sensitive security-testing artifacts and validate authorization before escalation.
- Correlate browser process telemetry with short bursts of navigation across multiple authentication origins and paths containing `/login`, `/oauth/authorize`, `/saml`, `/token`, or `/callback`, followed by local JSON/Markdown downloads. Use allowlisted lab hosts and engagement windows to reduce false positives.
- Monitor process creation for `phishlet_generator.py`, `validate_phishlet.py`, `traffic_pattern_generator.py`, `snapshot.py`, Semgrep, or ast-grep launched from the same working tree. Capture command-line output paths and `--include-host`/credential-search switches for audit without collecting credential values.
- Baseline network destinations for the extension host and generator processes. This implementation requires no runtime egress beyond operator-driven page browsing; DNS/HTTP connections initiated by Python/Node generator processes or an extension service worker are unexpected and should be investigated for modification or dependency compromise.
- Review downloads and snapshots for retention-policy compliance. Alert when these artifact types move to email, consumer cloud storage, source-control remotes, or removable media without an approved evidence-handling workflow.

## 6. Residual gaps

- This review did not run a clean interactive Chromium load or the user-gesture two-origin redirect smoke, so browser console cleanliness, rendered popup behavior, and real callback fidelity remain manual acceptance items.
- Semgrep and ast-grep completed with zero findings under local safety-focused rules, but managed/remote rulesets were unavailable in the restricted environment. Scanner evidence is in `workspace/scanners/` because the required sibling `../scanners/` mount was read-only.
- No client data, live identity provider, enterprise browser policy, EDR, SIEM, DLP, or retention system was available; the detection ideas require local field/path adaptation and baselining.
- Metadata-only capture cannot prove that all relevant origins, cookie names, form steps, or body/JavaScript rewrite requirements were observed. `sub_filters` and any explicit regex remain operator-reviewed lab work.
