# Build Plan — chrome-mv3-kit

## Repository layout

```text
README.md, AUTHORIZED_USE.md, OPSEC_CARD.md, package.json
extension/
  manifest.json, service-worker.js, popup.html, popup.js, popup.css
  shared.js, form-metadata.js
generators/
  capture.js, phishlet.js, traffic-profile.js, snapshot.js, yaml.js
  cli.js, validate-phishlet.js
schemas/
  capture-session.schema.json, phishlet-schema-2.3.0.json
config/default.json
testdata/
  session.json, no-cookie-session.json, secret-session.json
  regression-mixed-capture.json
tests/
  run-tests.js, helpers.js, origin.test.js, persistence.test.js
  form-metadata.test.js, generators.test.js, validation.test.js
  regression.test.js, training.test.js
pipeline/01_domain_brief.md … 05_opsec_card.md
```

`outputs/` is created by explicit CLI examples/tests and ignored if transient. The two harness study fixtures are copied byte-for-byte to their required destinations.

## Work packages

1. **WP1 — Fixture/schema foundation.** Copy study fixtures unchanged; inspect their structures; add a strict capture-session schema and package/test runner. Dependencies: none.
2. **WP2 — Shared origin and state core.** Implement idempotent HTTP(S) match-pattern normalization, rejection of userinfo/non-HTTP schemes, grant comparison, initial session shape, event merge/deduplication, diagnostics, and storage adapter. Dependencies: WP1.
3. **WP3 — MV3 extension.** Add manifest, persistent service-worker listeners, response `extraHeaders`, navigation fallback, form-metadata injection/result handling, popup one-click broad grant plus narrow host entry, Start guard, state display, and JSON/Markdown downloads. Dependencies: WP2.
4. **WP4 — Capture exports.** Normalize input, validate structural completeness, derive diagnostics/coverage, and render JSON/Markdown summaries. Dependencies: WP1–WP3.
5. **WP5 — Phishlet derivation/validation.** Implement secret-value screening; auth host deny/allow logic; registrable-domain grouping; representative host, cookie-name, auth URL, login path, and password-form credential selection; conservative object stub; YAML serialization; parser plus JSON-Schema validation. Dependencies: WP1, WP4.
6. **WP6 — Ancillary lab generators.** Emit commented traffic-pattern documentation skeleton and static HTML snapshot/report. Gate separately labeled awareness modules on `lab_unsafe_modules === true`, default false. Dependencies: WP4.
7. **WP7 — CLI and automated suite.** Provide headless subcommands and one parent runner covering production functions for origin normalization, permissions, lifecycle restart, DOM metadata, exports, generators, secret screening, schema mutations, ancillary modules, and unchanged A5e regression. Imported suites throw/return; only the parent sets exit status. Dependencies: WP1–WP6.
8. **WP8 — Documentation and verification.** Write build/load/use sequence, permission rationale, limitations, operator completion, manual smoke procedure, authorized-use notice, and acceptance scorecard; run single test command. Dependencies: WP3–WP7.
9. **WP9 — Controlled scanners.** After generation, run existing Semgrep and ast-grep only; archive their raw outputs under `../scanners/`; do not install or replace scanners. Dependencies: WP8.
10. **WP10 — OPSEC review.** Review final tree and write duplicate pipeline/root OPSEC cards with detection recommendations. Dependencies: WP9.

## Interface contracts

```js
normalizeOrigin(input: string): string                 // canonical scheme://host[:port]/* or throw
normalizeOrigins(inputs: string[]): string[]
comparePermissions(requested: string[], granted: string[]): {requested, granted, missing}
createSession(now?: string): CaptureSession
mergeEvent(session: CaptureSession, event: CaptureEvent): CaptureSession
deriveDiagnostics(session: CaptureSession): Diagnostics
restoreState(storage): Promise<CaptureSession>
persistState(storage, session: CaptureSession): Promise<void>

collectFormMetadata(document, pageUrl: string): FormMetadata[]
isAuthRelevantUrl(url: string): boolean

normalizeCapture(raw: object): CaptureSession
renderMarkdown(session: CaptureSession): string
generatePhishlet(session, options?: {author?: string, includeHosts?: string[]}): object
serializeYaml(value: object, header?: string): string
parseYaml(text: string): object
validatePhishletObject(value: object, options?: {placeholdersRequired?: boolean}): void
validatePhishletYaml(text: string, options?): object
generateTrafficProfile(session: CaptureSession): string
snapshotHtml(html: string, options): {html: string, report: string}
```

CLI contract:

```text
node generators/cli.js summarize INPUT --json OUT --markdown OUT
node generators/cli.js phishlet INPUT --out OUT [--author TEXT] [--include-host HOST]
node generators/cli.js validate YAML [--placeholders-required]
node generators/cli.js traffic INPUT --out OUT
node generators/cli.js snapshot INPUT_HTML --out OUT --report OUT [--config CONFIG]
npm test
```

Service-worker messages: `GET_STATE`, `SET_REQUESTED_ORIGINS`, `START_RECORDING`, `STOP_RECORDING`, `FORM_METADATA`, and `EXPORT_SESSION`; each returns `{ok, ...}` or `{ok:false,error}`.

## Requirement trace matrix

| Requirement | Work package(s) |
|---|---|
| R1 | WP2, WP3, WP8 |
| R2 | WP2, WP3, WP4 |
| R2a | WP2, WP3, WP7, WP8 |
| R2b | WP3, WP7 |
| R2c | WP2, WP3, WP4, WP7 |
| R2d | WP2, WP4, WP7 |
| R2e | WP2, WP3, WP7 |
| R2f | WP3, WP5, WP7 |
| R3 | WP3, WP4, WP7 |
| R4 | WP1, WP5, WP7 |
| R4g | WP5, WP7 |
| R5 | WP6, WP7, WP8 |
| R6 | WP6, WP7 |
| R7 | WP7 |
| R8 | WP10 |
| R9 | WP8 |
| R10 | WP9 |
| R11 | WP7, WP8 |
| R12 | WP1, WP7 |

## Test plan

Automated by `npm test`: A1, A3, A3d–A3h, A4, A5–A5e, A6, A7, A8 content checks, A9 content checks, and A11. Tests import shared/production functions. A5d mutations are parsed and schema-validated; malformed YAML and each forbidden shape/key/version fail. A5e first proves fixture byte equality, invokes the production generator, validates YAML, then asserts every listed host/domain/path/credential/filter rule.

Semi-automated: A10 records scanner availability, commands, exit codes, and outputs after code generation. Missing preinstalled scanners are reported rather than installed.

Manual: A2, A3b, A3c UI behavior, A3f reload visibility, and M1–M8. README supplies a two-origin `.test` lab smoke procedure and an evidence checklist. **ASSUMPTION:** manual browser execution may be unavailable in the build environment; it cannot be marked PASS without observation.

## Ambiguities/defaults

- **ASSUMPTION:** content-script declaration uses broad HTTP(S) matches but cannot execute without optional host grant; it performs an auth-URL/form relevance check and returns names/types only.
- **ASSUMPTION:** fixture-focused registrable-domain logic handles `.test`, common two-label domains, and explicit edge suffixes deterministically, without claiming a complete embedded PSL.
- **ASSUMPTION:** URLs remain capture-faithful as required, while generator secret screening rejects recognized secret-like query/free-text values.
- **ASSUMPTION:** the supplied study schema is copied unchanged and used as the base; an additional validator layer enforces placeholder-only research policy if the schema omits it.

## Out of scope

Live IdP targeting; credential/token values; password replay; off-host telemetry; phishing deployment; bypass/evasion guidance; production-ready implant/profile; automated `force_post`, `js_inject`, body rules, or JavaScript/rewrite recipes; guaranteed Evilginx compatibility beyond the specified 2.3.0 structure; installing new static-analysis tools; and claiming unexecuted manual checks as passing.
