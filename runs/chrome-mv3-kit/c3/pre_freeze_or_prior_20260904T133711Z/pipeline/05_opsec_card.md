+# OPSEC Card — chrome-mv3-kit

## Summary

chrome-mv3-kit is an authorized-lab, offline-first documentation utility comprising a Chrome Manifest V3 extension and local generators. The extension records URL/method/status/resource/source metadata, selected authentication-related header names, and Set-Cookie names for explicitly approved origins; it stores no bodies or credential values. Local exports drive a human-readable summary, a sanitized static snapshot/report, an inert schema-validated Evilginx-compatible scaffold with enforced placeholders, and a commented traffic-pattern skeleton. It provides no targeting, delivery, credential replay, response-rewrite recipe, or off-host telemetry capability.

## Operator risks

- Optional host access is broad in the manifest even though grants are origin-specific at runtime. Approving an out-of-scope origin, using a personal profile, or failing to remove the extension can expose unnecessary browsing metadata to local extension storage.
- A missed origin or flaky `webRequest` listener creates partial evidence. Treating a fallback-only or permission-gap export as complete can produce incorrect engagement conclusions.
- URLs, cookie names, page text, and filenames can still contain client identifiers or sensitive evidence even without values/bodies. Static snapshots are particularly likely to retain visible confidential content.
- Generated YAML structurally resembles a phishlet. Removing safety placeholders or moving it into an operational tool without review changes its risk and exceeds this kit's intended use.
- Developer-mode extension use, permission prompts, downloads, local CLI runs, dependency caches, and scanner reports leave durable artifacts that can identify the research activity.
- Editing `training-config.js` to enable awareness demonstrations creates a custom build that must be separately reviewed; both module-level flags and the global gate are required.

## Artifacts left behind

- **Browser:** unpacked-extension registration and ID, Developer-mode indicators, optional-origin grants, extension service-worker logs, `chrome.storage.local` key `recorder_state_v1`, profile history/cache for visited lab URLs, and download history.
- **Filesystem:** source tree; npm/Python cache metadata; JSON and Markdown sessions; YAML scaffolds; commented traffic skeletons; sanitized HTML and JSON reports; `scanners/semgrep.json` and `scanners/ast-grep.json`; shell history; editor/terminal history; timestamps and temporary outputs.
- **Network/security telemetry:** ordinary traffic to the operator-visited authorized origins, including redirects and browser subresources. The extension itself has no fetch, beacon, WebSocket, or external telemetry path.
- **Host logs:** Chrome/Chromium process and extension activity, endpoint file-creation events, Python/Node process execution, and any EDR command-line/process ancestry records.
- **Registry/keychain/mail:** no intentional registry, credential-store, or email artifacts. Platform/browser management systems may still log extension policy and permission state.

## Safer operating guidance

- Use a dedicated disposable lab browser profile on an evidence-controlled workstation. Confirm written scope and enumerate the full origin set before granting anything.
- Follow **Grant → Allow → Reload extension → Start → then browse**. Before Start, require Requested and Granted to match exactly and Missing to show none. Stop promptly after the scoped flow.
- Reject a smoke result unless it contains at least five events across two origins and a non-fallback `webRequest` event. Any fallback-only session or missing observed origin is incomplete regardless of operator expectation.
- Review JSON before generation. Keep source and outputs in an engagement evidence directory with least-privilege access, encryption where required, a retention deadline, and a documented deletion process.
- Keep `lab_unsafe_modules=false` unless a separately reviewed awareness exercise requires a module. Never add real credential prompts, automatic file pickers, active overlays, capture regexes, or response rewrites.
- Validate every scaffold with `python3 generators/validate-phishlet.py FILE`. Preserve the authorized-use header, coverage comments, and `{{PLACEHOLDER}}` fields until an explicitly authorized, separately governed lab workflow takes ownership.
- Remove the unpacked extension and its dedicated profile after the engagement; verify storage, permission grants, downloads, temporary output, and shell history are handled according to the evidence plan.

## Detection Recommendations

- Inventory Chrome/Chromium extension installations and alert on unmanaged unpacked MV3 extensions, Developer-mode additions, or extensions combining `webRequest`, `webNavigation`, `storage`, `downloads`, and optional broad HTTP(S) host declarations. Correlate the extension ID with approved research change records before escalation.
- Monitor browser preference/extension state for new runtime host grants and changes spanning multiple authentication-related origins. Correlate permission changes with extension reloads, service-worker startup, and visits to login/OAuth/SAML paths.
- Hunt endpoint file telemetry for clusters containing `schema_version`, `event_counts_by_source`, `webNavigation.fallback`, `permission_gaps`, or the literal `{{USERNAME_CAPTURE_REGEX}}` / `{{RESPONSE_SEARCH_PATTERN}}`. Validate context: these signatures identify this documentation kit or derived artifacts, not malicious intent by themselves.
- Correlate `chrome`/Chromium activity with child or nearby `python3 generators/cli.py phishlet`, `validate-phishlet.py`, Node test-runner, Semgrep, or ast-grep executions and subsequent creation of JSON, Markdown, YAML, HTML, or traffic-pattern files.
- In proxy/DNS telemetry, identify a dedicated research workstation visiting a burst of two or more identity-flow origins around OAuth/SAML redirects while an unmanaged extension permission change occurs. Baseline approved lab destinations and avoid treating legitimate identity traffic alone as an indicator.
- Review browser download records and DLP/file scans for scaffold header text (`AUTHORIZED LAB USE ONLY — inert scaffold`) plus `proxy_hosts`, `auth_tokens`, and placeholder-only `credentials` / `sub_filters`. Escalate artifacts where placeholders have been replaced, secrets appear, or client retention rules are violated.
- Verify post-engagement cleanup by checking that the extension registration, optional grants, `recorder_state_v1`, dedicated profile, downloads, and generated artifacts were removed or retained under the approved evidence schedule. Preserve relevant telemetry before cleanup if an investigation or audit hold applies.

## Residual gaps

- This review did not load the extension in a clean interactive Chromium profile, execute the authorized two-origin redirect smoke, or inspect browser console output; A2/A3b and visual A3c/M4–M6 remain manual.
- Browser/EDR artifact locations and managed-extension audit fields vary by operating system and enterprise policy; defenders must map the listed concepts to their own telemetry schema.
- Static HTML sanitization is conservative string-based processing rather than a forensic-grade parser. Operators must inspect outputs and should render them only in an isolated offline context.
- Scanner coverage used three narrow local Semgrep rules and one ast-grep rule and reported no matches; it is not a comprehensive security audit.
- Generator compatibility is enforced against the shipped schema and documented Evilginx-compatible vocabulary, not a live Evilginx deployment. No production deployment was attempted or is endorsed.

