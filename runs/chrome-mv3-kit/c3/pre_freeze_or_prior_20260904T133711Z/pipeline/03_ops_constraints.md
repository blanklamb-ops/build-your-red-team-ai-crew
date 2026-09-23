# Operational Constraints — Chrome MV3 Lab Documentation Kit

## Runtime environment

- Supported operator environment is a desktop Chrome/Chromium profile capable of loading an unpacked MV3 extension, plus Node.js 18+ for offline generators/tests. No administrator/root privilege is required.
- Runtime network activity is limited to browser traffic the operator intentionally visits. The extension and CLIs must not transmit telemetry, update data, fetch resources, or call external services.
- Dependency installation is a preparation step; all ordinary capture, export, validation, snapshot, and generator use must work offline afterward.
- The browser permission prompt is a security boundary. Only operator-entered HTTP(S) origins are requested, despite broad optional patterns being declared in the manifest.
- Files are local evidence. Output directories are operator-controlled; tools fail rather than inventing a destination or overwriting an input.

## Secrets and evidence handling

- Never commit or persist request/response bodies, header values, cookie values, credentials, bearer material, live JWTs, access/refresh tokens, client secrets, or private keys.
- Recorder events use an allowlisted schema. Header processing retains only selected header **names** and parses only Set-Cookie names before `=`; raw headers must not enter state, logs, errors, downloads, fixtures, or test snapshots.
- Fixtures use `example.com`, `.test`, and canonical synthetic identifiers only. A canonical session UUID and ISO timestamps are bookkeeping, not secrets. Cookie names are identifiers even when they contain `token`, `auth`, `jwt`, or `secret`.
- Generator secret scanning applies independently to only value-bearing/free-text fields capable of carrying credential material. A safe hostname elsewhere never suppresses a finding. Reject suspicious material with a field path and no echoed secret.
- Static HTML can itself be sensitive. Sanitize active content and warn operators to store exports with engagement evidence controls and delete them according to their authorization/data-retention plan.

## Operator workflow

1. Confirm written authorization, enumerate every expected HTTP(S) origin, and use a dedicated lab browser profile.
2. Install dependencies/build once, load `extension/` unpacked, enter bare origins, and select **Grant lab host access** from the popup.
3. Complete the browser permission prompt, reload the extension, verify every requested origin is shown as granted with none missing, then select Start.
4. Browse only the authorized synthetic/lab flow. Stop recording, inspect event-source/origin counts and coverage, and treat any missing origin or fallback-only session as incomplete.
5. Export local JSON/Markdown. Run generators and validator against reviewed local input. Never treat the scaffold or traffic skeleton as production-ready.
6. For the manual acceptance smoke, require two origins, five events, and at least one `webRequest` event; record the human result separately.

## Safety defaults

- Recording defaults OFF and cannot start unless the full requested origin set is currently granted. Empty requested sets are an error.
- Requested origins are explicit, visible, canonicalized, deduplicated, and persistent. Invalid scheme, userinfo, query/fragment, or non-root path is rejected before permission APIs are called.
- Capture is metadata-only and all persistence is local. Unexpected input properties are dropped by recorder normalization and forbidden by output schemas.
- `lab_unsafe_modules=false`. Both training modules are separately labeled and remain unavailable unless the global gate and the individual selection are true. They demonstrate awareness only and do not imitate credential prompts or invoke a real file chooser.
- Telemetry/analytics hosts are excluded by a documented default hostname list; operator inclusion requires an explicit CLI option. Scaffold capture/rewrite fields always contain `{{PLACEHOLDER}}` values and validation rejects live patterns.
- No generator has a live/dry-run distinction because all outputs are inert local files. Existing output paths require explicit `--force` before replacement.

## Degradation modes

- Offline operation continues normally. Missing dependencies produce a clear setup error, never an alternate hand-written parser.
- Missing/denied host access blocks Start. Partial grants enumerate missing patterns. An origin discovered through navigation without permission is recorded as a gap and forces `coverage: incomplete`.
- `webRequest` failure degrades to main-frame navigation evidence, but fallback-only diagnostics are visibly incomplete. Deduplication enriches matching events rather than deleting method/status.
- Worker termination loses no committed state; every handler reloads and writes storage-backed state. Storage failure stops the mutation and surfaces an error rather than reporting success.
- Missing diagnostics in imported sessions are derived from events. Partial diagnostics are merged conservatively. Missing structural events/hosts cause generation to fail clearly.
- Malformed YAML, schema mismatch, unknown properties, unsafe values, and non-placeholder fields fail nonzero. No permissive fallback validator is allowed.
- If Semgrep or ast-grep is absent, archive a truthful “not available” report and status; do not install or replace it. Acceptance then exposes the environmental gap.

## Detection-relevant artifacts for OPSEC review

The reviewer must document the unpacked extension ID/profile traces, optional-origin permission grants, `chrome.storage.local` recorder state, browser download history, exported JSON/Markdown/YAML/HTML/profile files, Node/npm command history, local dependency tree, scanner reports, and file timestamps. Defender recommendations should cover monitoring extension installations/permission changes, browser network and download telemetry, file-content signatures for scaffold placeholders/coverage metadata, and cleanup/retention verification.

## Non-negotiable plan deltas for the Architect

- **WP1:** Set `additionalProperties: false` where appropriate; specify only recorder-emitted fields in the fixture; make schemas and safe config committed inputs.
- **WP2:** Serialize storage mutations to avoid callback races; derive origin from URL; never persist raw API callback objects; persist diagnostics and timestamps after every state change.
- **WP3:** Make full-set permission status and missing origins visible before Start; never auto-request permission outside the explicit Grant gesture; include clear incomplete-coverage messaging.
- **WP3:** Snapshot sanitation must remove scripts, event-handler attributes, active embeds, and forms; reports identify removals. Training gates are pure, testable production logic.
- **WP4:** Refuse input/output path collision and existing-output overwrite without `--force`; use parsed-field secret errors without reproducing the value; default to inert local output.
- **WP4:** Preserve placeholders through YAML serialization and enforce them in the JSON Schema; never emit JS or response rewrite recipes.
- **WP5:** Tests must inspect persisted state after constructing a fresh worker/controller instance, not the original object. Subprocess tests capture stderr safely.
- **WP6:** Document evidence sensitivity and manual-vs-automated boundaries. Scanner runs occur only after source generation and archive exact tool availability/version/exit status.
- **WP7:** Acceptance script must not claim manual A2/A3b results. OPSEC files must be byte-identical and contain at least three concrete defender-oriented Detection Recommendations.
