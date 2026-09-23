# Build Plan — chrome-mv3-kit

## Repository layout

```text
README.md, AUTHORIZED_USE.md, OPSEC_CARD.md
package.json
extension/
  manifest.json, background.js, popup.{html,css,js}, shared.js
  form_capture.js, snapshot.js
generators/
  capture.js, phishlet.js, traffic_stub.js, yaml.js, validate.js, cli.js
schemas/
  capture-session.schema.json, phishlet-schema-2.3.0.json
config/default.json
testdata/
  README.md, regression-mixed-capture.json, session-fixture.json
tests/
  run.js, helpers.js, origins.test.js, lifecycle.test.js
  forms.test.js, exports.test.js, generator.test.js
  validation.test.js, regression.test.js, safety.test.js
pipeline/01_domain_brief.md … 05_opsec_card.md
../scanners/semgrep.txt, ../scanners/ast-grep.txt
```

## Work packages

1. **WP1 — Fixture/schema baseline** (no dependencies): copy study fixtures byte-for-byte; copy the supplied 2.3.0 phishlet schema; define a capture-session schema and a representative synthetic session.
2. **WP2 — Shared capture model and origin permissions** (WP1): implement idempotent HTTP(S) match-pattern normalization, wildcard-aware permission comparison, event sanitation/deduplication, diagnostics, JSON/Markdown serialization, and storage-backed session state.
3. **WP3 — MV3 extension** (WP2): add the required/optional permissions, service-worker listeners, response `extraHeaders`, navigation fallback, form metadata injection/collection, popup grant/status/start/stop/export UI, data-URL downloads, and reload-safe state display.
4. **WP4 — Offline generators and validator** (WP1, WP2): implement conservative auth-host classification, registrable-domain grouping, credential/login ranking, phishlet object/YAML generation, YAML parsing plus JSON-Schema validation, and traffic-pattern skeleton export.
5. **WP5 — Snapshot/training safeguards** (WP3): save sanitized static HTML plus report; provide clearly separated awareness demos gated by `lab_unsafe_modules`, default false.
6. **WP6 — Automated test harness** (WP2–WP5): use production exports and mocked Chrome/DOM APIs to cover normalization, complete-set permissions, lifecycle restart, forms/no-values, exports, secrets, generator/schema mutations, all fixtures, and every A5e assertion. Only `tests/run.js` controls process exit.
7. **WP7 — Operator documentation** (WP3–WP6): document build/load, Grant → Reload → Start → browse, scope, permissions, incomplete coverage, CLI, output limitations, snapshot risks, and manual smoke procedure.
8. **WP8 — Verification/static analysis** (WP6, WP7): run the single test command, compare copied fixture hashes, perform syntax/manifest checks, run available preinstalled Semgrep and ast-grep without installing/replacing scanners, archive outputs, and record unavailable tools explicitly.
9. **WP9 — OPSEC review** (WP8): inspect the complete tree, produce identical pipeline/final OPSEC cards, and include at least three defender detection recommendations.

## Interface contracts

```text
normalizeOrigin(input: string) -> string | throws
comparePermissions(requested: string[], granted: string[]) -> {granted, missing}
createSession(requestedOrigins: string[], now?: string) -> Session
sanitizeEvent(raw: object) -> CaptureEvent | null
mergeEvent(session: Session, event: CaptureEvent) -> Session
buildDiagnostics(session: Session, grantedOrigins: string[]) -> Diagnostics
sessionToMarkdown(session: Session) -> string

captureFormMetadata(document, pageUrl: string) -> FormMetadata[]

generatePhishlet(session: Session, options?: {author, includeHosts}) -> object | throws
serializeYaml(value: object, headerComments?: string[]) -> string
parseYaml(text: string) -> object | throws
validatePhishlet(value: object, schema: object) -> {valid, errors}
generateTrafficStub(session: Session) -> string

CLI:
node generators/cli.js phishlet <capture.json> <output.yaml> [--author X] [--include-host H]
node generators/cli.js markdown <capture.json> <output.md>
node generators/cli.js traffic <capture.json> <output.txt>
node generators/cli.js validate <phishlet.yaml>
```

Extension messages use `{type, payload}`. Required types: `STATE_GET`, `ORIGINS_SET`, `START`, `STOP`, `FORM_METADATA`, `EXPORT_JSON`, `EXPORT_MARKDOWN`, `SNAPSHOT`. Responses use `{ok, data?, error?}`. Persistent storage uses one versioned `captureState` object containing requested origins, recording flag, events, start/stop timestamps, and diagnostics.

## Requirement trace matrix

| Requirement | Work package(s) |
|---|---|
| R1 | WP2, WP3, WP7 |
| R2 | WP2, WP3, WP6 |
| R2a | WP2, WP3, WP6, WP7 |
| R2b | WP3, WP6 |
| R2c | WP2, WP3, WP6 |
| R2d | WP2, WP3, WP6 |
| R2e | WP2, WP3, WP6 |
| R2f | WP3, WP4, WP6 |
| R3 | WP2, WP3, WP6 |
| R4 | WP1, WP4, WP6 |
| R4g | WP4, WP6 |
| R5 | WP5, WP6, WP7 |
| R6 | WP4, WP6 |
| R7 | WP4, WP7 |
| R8 | WP9 |
| R9 | WP7 |
| R10 | WP8 |
| R11 | WP6, WP7 |
| R12 | WP1, WP6, WP8 |

## Test plan

Automated: A1 structural manifest assertions; A3 fixture/schema; A3d–A3h diagnostics, lifecycle, normalization, forms; A4 exports; A5–A5e generation, safety, parsing/schema mutations, mixed regression; A6 config gate; A7 traffic stub; A8/A9 documentation structure; A11 runner coverage. Semi-automated: A10 invokes available scanners and checks archived outputs. Manual: A2 unpacked load; A3b two-origin redirect smoke; A3c popup user gesture/error behavior; M1–M8 operator inspection. Tests must verify the exact R2 listener spec and that non-HTTP(S) noise is omitted without exceptions.

## Assumptions and out of scope

**ASSUMPTION:** Use dependency-free CommonJS/UMD JavaScript and a small purpose-built YAML subset parser/serializer plus JSON-Schema validator sufficient for the shipped 2.3.0 schema; tests prove structural—not substring-only—validation. **ASSUMPTION:** `.test` registrable-domain handling is deterministic and conservative; no network PSL lookup is needed.

Out of scope: live IdP compatibility, domain/lure provisioning, credential/token values or replay, request bodies, evasion or anti-bot bypasses, production traffic implants, unauthorized targets, automatic form submission, and capture-evidence-free `force_post` or `js_inject` rules.
