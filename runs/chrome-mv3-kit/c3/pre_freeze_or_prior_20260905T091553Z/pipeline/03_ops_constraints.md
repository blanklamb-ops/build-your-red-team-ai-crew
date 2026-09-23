# Operational Constraints — chrome-mv3-kit

## Runtime environment

- Supported operator environment is a local Linux/macOS/Windows workstation with a current Chromium-family browser in Developer mode and Node.js 18+ for offline CLI/tests. Loading the extension requires no administrator/root privileges.
- The recorder runs only in an explicitly authorized browser profile. Treat the profile as study evidence; do not mix routine browsing into a recording session.
- Runtime network access is only the operator's authorized lab browsing. The extension and CLI must make no outbound requests of their own, load no remote scripts/assets, and include no analytics/update channel outside Chrome's normal unpacked-extension behavior.
- All CLI generation and validation must work offline. No package installation is part of normal build/test. Scanner availability is environmental and checked only after generation.
- Storage quota is finite. A bounded event count and a visible error on storage failure are required; never silently discard and report complete coverage.

## Secrets and evidence handling

- Never collect, log, persist, export, snapshot-report, or test with credential values, autofill values, authorization values, cookie values, request/response bodies, tokens, or live personal identifiers. Header names and cookie names are metadata and are allowed.
- Content-script messages use a strict allowlist: page URL, absolute form action, field `name`, normalized field `type`, and trivial submit label. No generic DOM object serialization and no `.value` access.
- URL query strings can contain secrets. The capture requirement calls for URLs, so retain them in the raw local session but label exports sensitive; secret-value screening must reject generator input containing token-like free-text/query values. Markdown/traffic summaries should reduce URLs to origin/path patterns.
- Static HTML snapshots inherently may contain entered or server-rendered data. Before saving, clone and clear form-control values, remove scripts, event-handler attributes, and sensitive meta content where practical. The UI must warn that page text may still be sensitive and that the snapshot remains local.
- Only synthetic fixtures belong in version control. Generated real-lab sessions, snapshots, Markdown, YAML, and profiles are engagement evidence and must be stored outside the repository, access-controlled, retained per the study plan, and deleted through the operator's evidence process.
- Errors must identify the field/path that failed without echoing its value. Test logs must not dump rejected secret-looking content.

## Operator workflow

1. Confirm written authorization and enumerate every expected HTTP(S) origin for the lab flow.
2. Load `extension/` unpacked in a dedicated browser profile. Open the popup and review the lab-only notice.
3. Use **Enable lab access** for the one-click HTTP(S) default or enter the complete narrower origin set. Review requested/granted/missing sets and approve Chrome's prompt.
4. **Reload the extension if needed**, reopen the popup, confirm the requested origins persisted and no origin is missing, then press **Start**. Start must fail closed on any missing requested permission.
5. Browse only the authorized multi-origin flow. Stop recording promptly. Review event source/origin counts and the coverage marker; fallback-only, one-event, storage-error, or permission-gap sessions are incomplete.
6. Export local JSON/Markdown. Run the CLI on a copy. Inspect selected hosts, login path, cookie names, and form keys. Complete `credentials.*.search` and `sub_filters` manually only within the authorized lab; validate and lab-test. Generated output is not a live-deployment guarantee.
7. Optionally save a sanitized snapshot. Training demonstrations require editing explicit config to `lab_unsafe_modules=true` and an additional labeled action; they never follow from starting capture.

## Safety defaults

- Recording defaults OFF; events received while off are ignored. Requested origins and state persist, but reload must not implicitly begin a new recording if state integrity cannot be verified.
- Broad host access remains optional and user-granted. Narrow origin mode canonicalizes and displays the exact complete set. Non-HTTP(S), userinfo-bearing, malformed, or empty entries fail with actionable errors.
- Capture and generators are local-only and non-mutating with respect to target sites. Generators write documentation artifacts; no deployment/invocation of Evilginx is provided.
- Default host selection applies the R4g deny rules. `--include-host` is an explicit, visible operator override and must not bypass secret checks or schema validation.
- Unknown credential searches and every sub-filter body rule remain `{{PLACEHOLDER}}`; absence of password-form evidence leaves both credential keys as placeholders.
- Unsafe training modules default false in committed config and require both the configuration gate and explicit UI action. They must be visually labeled training-only.
- Output files should not overwrite existing paths without a clear error. Stdout is acceptable when no output path is supplied.

## Degradation modes

- **No/partial permission:** refuse Start for the requested set; if a newly observed navigation origin lacks access, retain the fallback event and export `coverage: incomplete` with the missing origin.
- **Header listener limitation:** navigation fallback records the main-frame completion, but cannot imply request/response completeness. Zero webRequest events forces incomplete coverage.
- **Worker restart:** reload all authoritative state from `chrome.storage.local`; serialize writes. Corrupt/missing state resets safely to recording OFF and reports a diagnostic rather than guessing.
- **Storage/download failure:** leave the prior stored state intact where possible, mark a storage/export error, and prompt the operator to stop/retry. Do not claim a successful export.
- **No forms/dynamic forms:** emit empty form metadata and placeholder credentials. Never infer password keys from OTP or username-only forms.
- **No cookies/auth URLs:** emit typed empty lists, not alternative shapes. If structural evidence is insufficient for a required host/login, fail clearly rather than emit garbage.
- **Offline:** recorder and all generators continue normally. Source links in docs are informational only.
- **Scanner absent:** do not install or substitute one. Archive a deterministic `NOT_INSTALLED` record and the version/check command; the human acceptance scorer decides A10.

## Detection-relevant artifacts for Role 5

The extension creates optional-host permission prompts, `chrome.storage.local` keys, download events, local JSON/Markdown/YAML/profile files, and sanitized `.html` snapshots. Browser extension installation, service-worker registrations, `webRequest`/`webNavigation` listener activity, repeated lab authentication requests, and filesystem creation are defender-visible. Generated phishlet vocabulary and placeholder strings are high-signal on disk. Role 5 must cover these artifacts, retention/cleanup, permission revocation, and at least three defensive detections.

## Non-negotiable plan deltas

- **WP2:** bound stored events; persist an explicit error list/state version; serialize state mutations; redact error messages; summarize query-free paths outside raw JSON.
- **WP3:** content script must never read `.value`; sanitize snapshot clones; show lab warning and exact permission sets; fail Start on any gap; no remote resources; no implicit restart after corrupt state.
- **WP4:** raw JSON must be sensitivity-labeled; Markdown is path-only; incomplete reasons include fallback-only, permission gap, too few events, and persistence/storage error.
- **WP5:** fail before writing on secrets/structural errors; never echo rejected values; no overwrite by default; explicit include-host override remains auditable in coverage metadata.
- **WP6:** banner every traffic output as a documentation skeleton, not production/deployment material.
- **WP7:** assert content code has no value access, unsafe defaults remain false, errors do not leak fixtures, bounded storage behavior, and output no-overwrite behavior.
- **WP8:** add dedicated-profile/evidence handling, snapshot sensitivity, permission revocation, incomplete-coverage interpretation, and manual-test non-claims.
- **WP9:** use installed scanners only and archive version, command, stdout, stderr, and exit status; never modify findings to obtain PASS.
- **WP10:** document all detection-relevant artifacts above plus cleanup that does not promise secure deletion.
