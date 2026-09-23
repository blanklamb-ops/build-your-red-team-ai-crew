# Operational constraints — chrome-mv3-kit

## Runtime environment assumptions

- Development/test host is a non-privileged Linux/macOS/Windows workstation with current Node.js/npm and Chrome/Chromium capable of MV3. No administrator/root privileges are required.
- Extension runtime must be self-contained and local: no remote scripts, analytics, update fetches, or application network calls. Browser traffic visibility comes only from user-granted optional HTTP(S) host permissions.
- CLI generation and validation must work offline after dependencies are present. Browser loading and manual redirect smoke use an isolated, clean profile and explicitly authorized synthetic/local origins.
- Storage and Downloads APIs may fail because of quota, policy, browser shutdown, or user cancellation. Every such failure must surface visibly; no success toast before the operation completes.
- Static scanner availability is environmental. Use only already-installed `semgrep` and `ast-grep`/`sg`; do not install, upgrade, or substitute scanners.

## Secrets and evidence handling

- Never collect request/response bodies, header values, cookie values, input values, autofill content, rendered credentials, localStorage, sessionStorage, or browser cookies. Persist only the explicit metadata allowlist.
- DOM collection reads form action, field name/type, and trivial submit label. Serialization must construct fresh objects; never spread DOM elements or event objects where a `value` property could leak.
- Session JSON, Markdown, snapshots, generated YAML, and traffic stubs are evidence artifacts. Keep them local, warn that URLs and page HTML may still be sensitive, use timestamped filenames, and require the operator to manage retention and access control.
- Commit only synthetic `.test`, `example.com`, or documentation-range data. Tests must fail if known value-bearing keys or secret-looking free-text values enter a session; URL queries, UUID session IDs, cookie names, timestamps, and paths are explicitly not scanned as secrets.
- Do not write captured content to logs. Console diagnostics may report counts, origins, file names, and errors only.

## Operator workflow

1. Confirm written authorization and enumerate the complete lab origin set before browsing.
2. Load `extension/` unpacked in an isolated Chrome profile; open popup.
3. Choose one-click broad lab access or enter the complete narrower host set; select **Enable lab access**, approve Chrome’s prompt, and reload the extension if needed.
4. Reopen popup and verify requested, granted, and missing lists. **Start** remains blocked unless all requested patterns are granted.
5. Start recording, then browse the authorized multi-origin flow. Stop promptly. Review event/source/origin counts and reject fallback-only, one-event, or permission-gap captures as incomplete.
6. Export JSON and Markdown locally. Generate YAML/traffic documentation with the CLI, validate YAML, inspect host/path/credential choices, complete only operator-owned `sub_filters`/credential search expressions, and test solely in the lab.
7. Snapshot only pages the operator is authorized to retain. Enable either training demo only by deliberately changing `lab_unsafe_modules` and acknowledging its lab-only label.

## Safety defaults

- `recording=false`, empty events, and `lab_unsafe_modules=false` at install. Recording and demo state must never auto-enable after reload/restart.
- Broad origins are declared optional. Permission requests happen only in direct click handlers. The narrow-path input is canonicalized, displayed, and stored before capture.
- Fail closed when any requested origin is missing. An empty requested set also fails unless the operator deliberately uses the one-click broad patterns.
- Coverage defaults to `incomplete` and becomes complete only with at least one request/response observation and no observed/requested permission gaps. A single fallback cannot be upgraded by wording or UI.
- Generator defaults exclude the full documented R4g/telemetry set even when cookies exist. `--include-host` is explicit per hostname; it must not mutate defaults or act as a wildcard.
- Do not invent domains, paths, cookie names, credentials, or observed facts. Empty observed collections serialize as `[]`. Generated YAML always carries the authorized-lab header and an explicit coverage comment.
- Snapshots are static best-effort HTML: strip executable script behavior and do not fetch external resources. Training controls remain separate from ordinary snapshotting.

## Degradation modes

- **Offline:** extension capture, export, generation, validation, and tests continue; external page resources in snapshots remain unresolved and the report says so.
- **Partial host permission:** start fails with exact missing patterns. If redirects reveal an unapproved origin through navigation fallback, export marks coverage incomplete and lists the origin.
- **Header listener unavailable:** navigation fallback records URL/time/origin only. Diagnostics identify fallback source; missing method/status/cookies are never synthesized.
- **Worker suspension/restart:** every operation reloads authoritative storage; queued mutations are serialized. If stored state is malformed, preserve the raw record where possible, stop recording, and return an actionable error rather than reset silently.
- **Content-script inaccessible/no forms:** retain the network/navigation event with `form_fields: []`; credentials remain empty rather than guessed.
- **Download/storage failure:** return an explicit UI error and keep the in-storage session available for retry.
- **No auth-like paths/cookies/forms:** generation may proceed only with structurally sufficient events; arrays remain empty and coverage comments call out the gaps. Missing session/event structure fails nonzero.
- **Scanner absent/fails:** archive command/version/error output and report acceptance A10 as not passed; do not install another scanner.

## Detection-relevant artifacts for Role 5

- Optional host-permission prompts and extension install/reload events.
- `webRequest`/`webNavigation` observation across authentication-like paths.
- `chrome.storage.local` records containing URLs, origin lists, timestamps, source counts, cookie/header names, and form-field names.
- Browser downloads named as session JSON/Markdown/HTML snapshot/report.
- Generated phishlet YAML and traffic-profile stubs on disk; CLI/process/audit history.
- Unpacked-extension developer-mode indicators and service-worker console activity.
- Any explicit activation of training modules, plus overlay/file-picker UI artifacts.

## Non-negotiable plan deltas for the Architect

- **WP1:** Add explicit evidence-handling warnings and config schema/default; copy A5e fixture byte-for-byte and test its digest/equality.
- **WP2:** Make all storage mutations serialized and storage-authoritative; allowlist every persisted event property; initialize coverage incomplete; expose validation errors without clearing evidence.
- **WP3:** Bind permission requests directly to user clicks; show all three origin lists; block empty/partial grants; never log values; strip scripts/event handlers from snapshots; keep demo activation separate and doubly gated by config plus explicit UI action.
- **WP4:** Redact nothing by silently dropping a whole event—reject prohibited value-bearing structures clearly. Preserve source distinctions and derive conservative diagnostics when absent.
- **WP5:** Treat host overrides as exact explicit entries, retain safety/coverage comments, never infer unobserved paths, and produce empty arrays rather than nulls.
- **WP6:** Test storage concurrency/restart, permission failure, fallback-only capture, download failure where mockable, value-key rejection, and unchanged A5e fixture. Imported suites throw/return only.
- **WP7:** Include isolated-profile and retention guidance, manual PASS criteria, incomplete-capture examples, snapshot sensitivity, and exact remaining operator work.
- **WP8:** Record tool versions, commands, exit status, stdout/stderr in scanner artifacts. Do not alter implementation merely to suppress a finding without review.
