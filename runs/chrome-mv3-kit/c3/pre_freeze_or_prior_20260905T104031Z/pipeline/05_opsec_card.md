# OPSEC Card — chrome-mv3-kit

## 1. Summary

`chrome-mv3-kit` is an authorized-lab, offline-first Chrome Manifest V3 documentation kit. It records minimized authentication-flow metadata from explicitly approved HTTP(S) origins, persists sessions locally, exports JSON/Markdown diagnostics, and derives a conservative Evilginx 2.3.0-format YAML documentation scaffold, static HTML snapshots, and a commented traffic-pattern skeleton. It stores header and cookie names—not values—and form field names/types—not user-entered content. Generated credential searches and substitution rules remain placeholders requiring separate operator review and isolated lab testing.

## 2. Operator risks

- Broad optional `http://*/*` and `https://*/*` access makes scope mistakes possible after the operator grants it. Recording while unrelated tabs are active can collect out-of-scope URLs and metadata even though values/bodies are excluded.
- URLs, page snapshots, form actions, field names, cookie names, timestamps, and hostnames can reveal account identifiers, query data, application structure, or engagement context. “Metadata only” is not the same as non-sensitive.
- `chrome.storage.local` retains the current session and requested-origin set across service-worker restart and extension reload. Closing the popup or stopping recording does not erase that stored evidence.
- Downloaded JSON, Markdown, YAML, HTML, reports, traffic skeletons, shell history, temporary files, scanner logs, and filesystem metadata can identify the study and its timing.
- A fallback-only or permission-gap capture can create false confidence if its `coverage: incomplete` marker is ignored. Generated placeholders can likewise be mistaken for deployment-ready configuration.
- Explicit `--include-host` use can add an operator-reviewed denied host to documentation. Misuse may enlarge scope or include telemetry/API infrastructure.
- Static snapshots have scripts/inline handlers removed but retain supplied page content and attributes. An input snapshot can therefore contain sensitive material that the browser recorder itself would never collect.
- Enabling awareness modules changes snapshot content and may confuse recipients unless the `lab_unsafe_modules=true` decision and training purpose are recorded.

## 3. Artifacts left behind

- **Browser:** unpacked-extension entry/ID, developer-mode indicators, permission prompts and grants, dedicated-profile history/cache, downloads history, extension console/error records, and the persisted `chromeMv3KitSession` object in extension `chrome.storage.local`.
- **Filesystem:** source tree, real or synthetic capture JSON, Markdown summaries, phishlet YAML, traffic-pattern text, static HTML and reports, Node/Python cache or temporary metadata, and `scanners/` JSON/log/config artifacts. Deleted evidence may remain in backups, snapshots, indexing databases, or endpoint telemetry.
- **Process/command telemetry:** Chrome/Chromium developer-mode activity, `node generators/cli.js`, `npm test`, `python3 generators/validate_yaml.py`, Semgrep, and ast-grep executions plus corresponding command-line arguments and recent-file records.
- **Network:** no application off-host exfiltration is implemented. While recording, the browser still makes the operator-driven requests to approved lab origins; DNS, proxy, firewall, TLS inspection, server, and identity-service logs will show those flows and may show repeated authentication navigation during testing.
- **Registry/preferences:** on Windows, Chrome profile and extension preferences may be reflected in user-profile files and related registry/enterprise-policy telemetry. Other platforms retain equivalent browser preference/profile artifacts.
- **Mail/collaboration:** the kit sends no mail or messages. Any manual sharing of exports creates copies in mail, chat, ticketing, cloud storage, DLP, and recipient systems outside the kit’s control.

## 4. Safer operating guidance

- Maintain written authorization and a complete expected-origin allowlist. Prefer the narrower grant path; use the broad one-click grant only in a dedicated lab profile with unrelated tabs closed.
- Follow **Enable → Allow → Reload if needed → verify Requested/Granted/Missing → Start → browse → Stop**. Refuse or repeat any run with missing origins, fallback-only evidence, fewer than the expected events, or an incomplete coverage marker.
- Use synthetic identities and `.test` lab hosts. Never enter real credentials into a recorded flow and never use the extension in a personal/client production browser profile.
- Stop immediately after the intended flow. Review exports locally for sensitive URLs/query data before sharing, and transfer evidence only through the engagement’s approved encrypted channel and retention process.
- Treat `chrome.storage.local`, downloads, snapshots, and temporary outputs as evidence. Remove the extension/profile and securely dispose of evidence according to client policy after retention obligations are met; verify backups and sync destinations separately.
- Keep `lab_unsafe_modules`, `ui_overlay_awareness`, and `file_picker_awareness` false unless a documented training exercise explicitly requires them.
- Leave credential searches and `sub_filters` as placeholders until separately reviewed. Revalidate the YAML and test only in isolated lab infrastructure. Do not interpret schema validity as live operational readiness.
- Record every `--include-host` override with the authorization basis and reviewer. Never use it merely to suppress an exclusion warning.

## 5. Detection Recommendations

- **Browser/endpoint inventory:** alert or review when unmanaged unpacked Chrome extensions run in Developer mode or request broad runtime HTTP(S) access together with `webRequest`, `webNavigation`, `storage`, and `downloads`. Correlate extension-install/grant events with the approved research window and device owner; allowlist only documented lab extension IDs/hashes.
- **Extension storage and downloads:** on managed test endpoints, inventory extension local-storage keys for `chromeMv3KitSession` and monitor creation of closely timed `.json`, `.md`, `.yaml`, and snapshot `.html` files containing markers such as `AUTHORIZED LAB USE ONLY`, `Capture coverage`, `proxy_hosts`, `auth_tokens`, and `sub_filters`. Scope content inspection through legal/privacy policy and hash approved study outputs to reduce noise.
- **Process telemetry:** query EDR for `node` running `generators/cli.js`, Python running `generators/validate_yaml.py`, and Semgrep/ast-grep executions from the same workspace. Correlate parent processes, working directory, user, extension grant time, and output-file creation; investigate activity outside authorized researcher hosts or time windows.
- **Network correlation:** identify short browser sessions that contact multiple authentication-like lab origins in sequence (authorize/login, credential-type, password-post, redirect/account) from a workstation that just granted an unpacked extension broad host access. Validate destinations against the engagement allowlist; do not treat a path name alone as malicious.
- **Identity/web logs:** build detections for repeated synthetic-account login flows, rapid retries, unusual redirect chains, or lab-only hostnames originating from non-lab endpoints. Join reverse-proxy/WAF/IdP events by source device and time, and distinguish sanctioned test accounts from production identities.
- **Data-loss controls:** monitor uploads or outbound sharing of capture JSON, HTML snapshots, or YAML containing authentication hostnames/cookie names. Enforce approved encrypted repositories and retention labels; alert when such artifacts move to personal mail, consumer storage, or unapproved chat/ticket systems.
- **Coverage abuse signal:** if the tool is institutionally deployed, collect a minimal operator audit record (not captured secrets) when runs are exported with `coverage: incomplete`, missing origins, or explicit host overrides. Repeated incomplete exports can indicate misconfiguration or activity outside the approved host set.

## 6. Residual gaps

- This review verified source, fixtures, automated tests, CLI smoke outputs, byte-equivalent A5e data, and zero-finding local Semgrep/ast-grep rules. It did not execute the unpacked extension in a clean Chromium profile, so A2, A3b, the visible A3c/A3f flows, and M1–M8 remain manual.
- Chrome’s exact permission UI, enterprise logging, and extension-storage paths vary by browser build, operating system, and policy. Defender queries must be adapted to available telemetry.
- The scanners used two focused offline rules and are not a substitute for a broader organization-approved static-analysis policy.
- The generator’s registrable-domain handling is conservative for the synthetic corpus and explicit edge suffixes, not a complete embedded Public Suffix List.
- The review did not assess real client captures, live identity providers, deployment behavior, or production Evilginx compatibility. Those uses are outside this kit’s authorized acceptance scope.
