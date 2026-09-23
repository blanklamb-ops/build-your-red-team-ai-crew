# Role 2 — Build Plan

## Repository layout

```text
README.md, AUTHORIZED_USE.md, OPSEC_CARD.md, ACCEPTANCE.md
package.json, package-lock.json
extension/
  manifest.json, shared.js, service-worker.js, content-script.js
  popup.html, popup.js, popup.css
generators/
  session-utils.js, export-session.js, phishlet-generator.js
  validate-phishlet.js, traffic-pattern-generator.js, snapshot.js
schemas/session-schema.json, schemas/phishlet-schema.json
config/lab_config.json
testdata/session-fixture.json, testdata/snapshot-page.html
tests/run-all-tests.js, tests/test-*.js
pipeline/01_domain_brief.md … pipeline/05_opsec_card.md
../scanners/{semgrep,ast-grep}.{stdout,stderr,json}.txt (as available)
```

## Work packages

1. **WP1 — Project contract and schemas.** Create package scripts/dependencies, config with `lab_unsafe_modules=false`, strict session/phishlet schemas, synthetic fixture, and documentation skeleton. Depends on Role 3 constraints.
2. **WP2 — Shared capture primitives.** Implement idempotent origin normalization/comparison, allowlisted header/cookie-name parsing, default session state, diagnostics/coverage derivation, and serialized `chrome.storage.local` persistence. Depends on WP1.
3. **WP3 — MV3 recorder and popup.** Build the manifest, runtime host grant UI (one-click all HTTP(S), plus optional origin set), start refusal on any missing permission, request/response/redirect/navigation capture, event merge, state restoration, exports/downloads, and explicit status/coverage. Depends on WP2.
4. **WP4 — Form metadata and snapshots.** Build content-script allowlist extraction and main-frame messaging; snapshot utility writes static HTML plus report. Optional overlay/file-picker training metadata is produced only when the unsafe flag is explicitly true. Depends on WP2–WP3.
5. **WP5 — Session reports and traffic skeleton.** Normalize snake/camel-case inputs, generate JSON/Markdown diagnostics and non-empty commented URL-pattern documentation stub. Depends on WP1–WP2.
6. **WP6 — Capture-complete phishlet pipeline.** Apply secret-value rejection, default host/path exclusions, `--include-host`, PSL domain grouping, cookie-name aliases, auth-path filtering, primary/form-action login selection, exact priority username selection, credentials generation, YAML serialization, coverage comments, and real YAML+schema validation. Depends on WP1, WP5.
7. **WP7 — Automated verification.** One top-level test runner invokes suites that return/throw: normalization/permissions, lifecycle restart, DOM extraction/no values, exports, generator edge cases, secret rejection, validator mutations, snapshot gating, and fixture E2E. Depends on WP2–WP6.
8. **WP8 — Documentation/manual checks.** Finish README permission rationale, Grant → Reload → Start → browse workflow, manual multi-origin smoke, generator/validator/snapshot commands, limitations, excluded hosts, operator completion, and authorized-use warning. Make ACCEPTANCE.md executable by adding a concrete checker/script and command without removing the registered checklist. Depends on WP1–WP7.
9. **WP9 — Controlled static analysis and handoff.** Run only preinstalled Semgrep and ast-grep, archive stdout/stderr/machine output outside the workspace under the run’s scanner directory, record tool absence honestly, fix in-scope findings, and write Role 4 notes. Depends on WP7–WP8.

## Interface contracts

- `normalizeOrigin(input: string): string`; `normalizeOrigins(text|string[]): string[]`; reject userinfo/non-HTTP(S), preserve canonical `scheme://host[:port]/*` idempotently.
- `comparePermissions(requested: string[], granted: string[]): {requested, granted, missing}`.
- `defaultState(): SessionState`; `loadState(storage): Promise<SessionState>`; `updateState(storage, mutator): Promise<SessionState>`.
- `recordRequest(details)`, `recordResponse(details)`, `recordNavigation(details)`, `recordForms(message)` persist allowlisted events; no event body/value input is stored.
- Popup messages: `GET_STATE`, `SET_REQUESTED_ORIGINS`, `START_RECORDING`, `STOP_RECORDING`, `CLEAR_SESSION`, `EXPORT_SESSION`; responses are `{ok, state?, error?}`.
- `extractFormMetadata(document, pageUrl): FormMetadata[]` returns `{url, form_action, fields:[{name,type}], submit_label?}`.
- `normalizeSession(input): Session`; `deriveDiagnostics(events, permissions): Diagnostics`; `toMarkdown(session): string`.
- `generatePhishlet(session, {name, includeHosts, usernameSearch?, passwordSearch?}): object`; CLI `node generators/phishlet-generator.js --input FILE --output FILE [--name NAME] [--include-host HOST] [--username-search REGEX] [--password-search REGEX]`.
- `validatePhishlet(path|object, {session?}): ValidationResult`; CLI exits nonzero only at its top level.
- `generateTrafficStub(session): string`; CLI accepts `--input` and `--output`.
- `snapshotHtml({input, output, report, labUnsafeModules, modules}): Result`; training module requests fail unless gate is true.
- `npm test` is the single all-suite command; `node scripts/check-acceptance.js` performs repository/automated acceptance checks and exits nonzero on failures.

## Requirement trace matrix

| Requirement | Work package(s) |
|---|---|
| R1 | WP2, WP3, WP8 |
| R2 | WP2, WP3, WP7 |
| R2a | WP2, WP3, WP7, WP8 |
| R2b | WP3, WP7 |
| R2c | WP2, WP3, WP6, WP7 |
| R2d | WP2, WP3, WP5, WP7 |
| R2e | WP2, WP3, WP7 |
| R2f | WP4, WP6, WP7 |
| R3 | WP3, WP5, WP7 |
| R4 | WP1, WP5, WP6, WP7, WP8 |
| R5 | WP4, WP7, WP8 |
| R6 | WP5, WP7 |
| R7 | WP5, WP6, WP7 |
| R8 | Role 5 after WP9 |
| R9 | WP8 |
| R10 | WP9 |
| R11 | WP7, WP8 |

## Test plan

Automated: A1, A3, A3d–A3h, A4–A7, A8–A11 (except scanner availability itself), M2–M3, M6 and structural portions of M1/M4/M5/M7. Tests import production normalization, persistence, DOM extraction, generator, and validator functions. Validator mutation subprocesses assert nonzero at CLI boundaries. The E2E test reads the shipped fixture itself and asserts recorder spellings.

Manual: A2 (clean Chromium load), A3b (two-origin/user-gesture redirect smoke), A3c’s visual behavior, A3f’s reload display, and final visual fidelity portions of M1/M4/M5/M7. `scripts/check-acceptance.js` prints these as explicit `MANUAL` rather than claiming PASS. A10 passes only when archived outputs demonstrate both installed scanners ran; missing tools are a reported failure/limitation, never silently substituted.

## Ambiguities and defaults

- **ASSUMPTION:** Because PROMPT requires top-level keys exactly while upstream historically derives a name from filename, the kit follows PROMPT’s exact schema and labels it “Evilginx 3.x-compatible kit contract”; validation does not add upstream fields.
- **ASSUMPTION:** A declared content script can run on optionally granted hosts using `matches: ["http://*/*", "https://*/*"]`; it returns empty metadata on non-auth-relevant/no-form pages, while the worker associates results only during recording.
- **ASSUMPTION:** “Static HTML snapshot” is an offline CLI copy/sanitized metadata report, not a browser-perfect recursive mirror. Training demos are inert annotations in the saved snapshot.
- **ASSUMPTION:** “Make ACCEPTANCE.md executable” means retain the checklist and add an executable repository checker plus an invocation in the document; Markdown itself is not a program.

## Out of scope

Live targeting, credential/cookie values, body capture, replay, exfiltration, production proxy deployment, IdP-specific recipes, bypass guidance, invented regexes/rewrite rules, `force_post`, `js_inject`, recursive site mirroring, scanner installation/replacement, and claims that a manual browser workflow ran when it did not.
