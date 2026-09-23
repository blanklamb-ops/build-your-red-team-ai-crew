# Build Plan — chrome-mv3-kit

## Repository layout

```text
README.md, AUTHORIZED_USE.md, OPSEC_CARD.md, package.json
extension/
  manifest.json, service-worker.js, recorder-core.js, shared.js
  content-script.js, popup.html, popup.js, popup.css
  snapshot.js
generators/
  phishlet.js, traffic-profile.js, exports.js, validate.js, cli.js
schemas/
  capture-session.schema.json, phishlet-schema-2.3.0.json
config/default.json
testdata/
  session.json, no-cookie-session.json, regression-mixed-capture.json
tests/
  run-tests.js, helpers.js, origin.test.js, lifecycle.test.js
  content-script.test.js, exports.test.js, phishlet.test.js
  validator.test.js, regression.test.js, training.test.js
pipeline/01_domain_brief.md … 05_opsec_card.md
```

## Work packages

1. **WP1 — Frozen inputs and package scaffold.** Copy both study fixtures byte-for-byte; create Node package, schemas, safe config, authorized-use notice. Dependency: Role 3 constraints.
2. **WP2 — Shared normalization and state core.** Implement idempotent HTTP(S) origin canonicalization, complete-set permission comparison, initial state, serialized storage mutation, diagnostics, event merge/deduplication, and capture export model. Dependency: WP1.
3. **WP3 — MV3 extension.** Create manifest, popup Grant/Reload/Start workflow, worker listeners (`onBeforeSendHeaders`, `onCompleted` with response/extra headers, navigation fallback), content-script form metadata, downloads, static snapshots, and gated training notices. Dependencies: WP2.
4. **WP4 — Human/JSON exports.** Validate capture structure, compute source/origin counts and gaps, mark incomplete coverage, and render JSON/Markdown. Dependency: WP2.
5. **WP5 — Phishlet generator and validator.** Implement secret-value rejection, URL-origin derivation, registrable-domain grouping, R4g deny/allow policy, login-path ranking, cookie-name aggregation, password-form credential selection, safe object stubs, YAML serialization/parser, and JSON-Schema validation. Dependencies: WP1, WP4.
6. **WP6 — Traffic skeleton CLI.** Emit a commented, non-production pattern profile from observed URL paths; expose headless generator/validator/export commands. Dependency: WP4.
7. **WP7 — Automated tests.** Mock Chrome storage/permissions and DOM; test restart persistence, normalization, capture diagnostics, form privacy, exports, training gates, secret policy, schema mutations, fixtures, and every A5e assertion via production functions. Single top-level runner owns exit status. Dependencies: WP2–WP6.
8. **WP8 — Documentation and manual checklist.** Explain installation, permission justification, Grant → Reload → Start → browse, multi-origin/manual smoke, privacy, limitations, operator completion, and all commands. Dependencies: WP3–WP7.
9. **WP9 — Verification and static-analysis archive.** Run the unified tests; run existing Semgrep and ast-grep without installation; archive stdout/stderr/status under `../scanners/`; record build notes. Dependencies: WP7–WP8.
10. **WP10 — OPSEC review.** Inspect final tree, duplicate the review artifact to `OPSEC_CARD.md`, and include at least three defender Detection Recommendations. Dependency: WP9.

## Interface contracts

- `normalizeOrigin(input: string): string` — canonical `scheme://host[:port]/*`; throws for credentials/non-HTTP(S).
- `comparePermissions(requested: string[], granted: string[]): {requested, granted, missing}` — normalized, deterministic sets.
- `createInitialState(): RecorderState`; `loadState(storage): Promise<RecorderState>`; `mutateState(storage, fn): Promise<RecorderState>`.
- `recordRequest(details)`, `recordResponse(details)`, `recordNavigation(details)`, `recordForms(message)` — sanitize then persist metadata; never accept values/bodies.
- `collectFormMetadata(document, pageUrl): FormRecord[]` — `{url, form_action, fields:[{name,type}], submit_label?}` only.
- Worker messages: `GET_STATUS`, `SET_ORIGINS`, `START`, `STOP`, `FORM_METADATA`, `EXPORT_JSON`, `EXPORT_MARKDOWN`, `SNAPSHOT` → `{ok, ...}` or `{ok:false,error}`.
- `buildDiagnostics(session, granted): Diagnostics` — source/origin counts, permission sets/gaps, timestamps, coverage.
- `generatePhishlet(session, options): object`; options include `author`, explicit credential searches, and `includeHosts`.
- `dumpYaml(value): string`; `parseYaml(text): object`; `validatePhishlet(value, {placeholdersRequired}): string[]` — parser plus shipped-schema errors.
- `generateTrafficProfile(session): string`; `renderMarkdown(session): string`.
- CLI: `node generators/cli.js <phishlet|validate|markdown|traffic> <input> [output] [--author X] [--include-host H]`.

## Requirement trace matrix

| Requirement | Work package(s) |
|---|---|
| R1 | WP3, WP8 |
| R2 | WP2, WP3, WP7 |
| R2a | WP2, WP3, WP7, WP8 |
| R2b | WP3, WP7 |
| R2c | WP2, WP3, WP4, WP7 |
| R2d | WP2, WP4, WP7 |
| R2e | WP2, WP3, WP7 |
| R2f | WP3, WP5, WP7 |
| R3 | WP4, WP7 |
| R4 | WP1, WP5, WP7 |
| R4g | WP5, WP7 |
| R5 | WP3, WP7, WP8 |
| R6 | WP6, WP7, WP8 |
| R7 | WP5, WP6, WP8 |
| R8 | WP10 |
| R9 | WP8 |
| R10 | WP9 |
| R11 | WP7, WP8 |
| R12 | WP1, WP7 |

## Test plan

Automated by `npm test`: A1 manifest inspection; A3 fixture schema; A3c start gate; A3d diagnostics; A3e persistence/restart; A3f complete permission set; A3g shared normalizer; A3h mocked DOM plus generator; A4 exports; A5/A5b/A5c generation shape, host policy, secrets, and fixtures; A5d parser/schema mutation rejection; A5e unchanged regression; A6 config gate; A7 traffic output; A8 README content; A9 OPSEC structure after Role 5; A11 runner coverage. A10 is semi-automated by a script that records each installed scanner’s result or absence without installing it.

Manual: A2 clean-profile load; A3b authorized two-origin redirect capture; popup/console portions of A3c; M1–M8 inspection/fidelity. The README supplies a score sheet and exact smoke procedure. Automated tests cannot claim a manual browser PASS.

## Ambiguities and defaults

- **ASSUMPTION:** no external npm install/network is available. Implement the required YAML subset parser/serializer and JSON-Schema evaluator locally, with mutation tests proving structural—not substring—validation. If system YAML tooling exists it is not required.
- **ASSUMPTION:** `test` and common two-label synthetic domains are registrable; known multi-label public suffixes needed by tests are handled by a compact offline rule set. Hosts beneath denied edge suffixes are removed before grouping.
- **ASSUMPTION:** declarative content script runs on granted HTTP(S) pages and self-gates on persisted recording state/auth relevance. This satisfies declared-content-script acceptance without adding `scripting` permission.
- **ASSUMPTION:** snapshots save the current DOM serialization plus a local report; scripts are removed and no subresources are fetched for offline capture.

## Out of scope

Live targeting, credential/token values, request/response bodies, session replay, security-control bypass, production implants, automated Evilginx deployment, guaranteed IdP compatibility, invented regex/rewrite/`force_post`/`js_inject` recipes, external telemetry, scanner installation, and activating training modules without the explicit unsafe flag.
