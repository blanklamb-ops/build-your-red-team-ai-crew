# Build plan — chrome-mv3-kit

## Repository layout

```text
extension/{manifest.json,service-worker.js,shared.js,content-script.js,popup.html,popup.js,popup.css,snapshot.js}
generators/{session.js,phishlet.js,traffic-profile.js,export-markdown.js,validate-phishlet.js,cli.js}
schemas/{session.schema.json,phishlet.schema.json}
config/default.json
testdata/{session.json,regression-mixed-capture.json}
tests/{run.js,origins.test.js,persistence.test.js,content-script.test.js,generator.test.js,validator.test.js,regression.test.js,extension-static.test.js}
pipeline/{01_domain_brief.md,02_plan.md,03_ops_constraints.md,04_build_notes.md,05_opsec_card.md}
README.md, OPSEC_CARD.md, AUTHORIZED_USE.md, ACCEPTANCE.md, package.json, package-lock.json
```

`ACCEPTANCE.md` remains the human checklist and gains executable permission; `npm test` is the single automated command. Generated test outputs go to a temporary directory, not the source tree.

## Work packages

1. **WP1 — Foundations and fixtures.** Create package metadata/dependencies, schemas, safe default config, authorized-use notice, synthetic recorder-faithful fixture, and byte-for-byte copy of the study regression. Dependencies: none.
2. **WP2 — Shared capture state and origin contract.** Implement UMD-style production helpers usable by popup `<script>` and service worker `importScripts`: idempotent origin normalization, complete permission comparison, default state, diagnostic aggregation, event merge/deduplication, and storage-backed state transitions. Dependencies: WP1.
3. **WP3 — MV3 extension.** Add MV3 manifest, popup one-click broad grant plus optional narrow set, visible requested/granted/missing status, refusal to start without the complete grant, service-worker request/response/navigation listeners, restart-safe storage, form metadata content script, JSON/Markdown export/download, static snapshot action, and gated training demos. Dependencies: WP2.
4. **WP4 — Session/export library.** Normalize snake/camel recorder fields, derive absent origins, validate structure and reject credential-like captured values, derive diagnostics when absent, export readable Markdown, and produce the commented traffic-pattern skeleton. Dependencies: WP1.
5. **WP5 — Capture-complete phishlet generator.** Implement PSL-backed registrable-domain grouping; R4/R4g host exclusions and `--include-host`; auth path selection; cookie-name aggregation; password-form credential/login ranking; exact username-name priority; deterministic YAML with only allowed top-level keys and placeholders; parse/schema validate. Dependencies: WP4.
6. **WP6 — CLI and tests.** Implement generate/validate/markdown/traffic commands and one parent runner. Test shared production functions for origin normalization, permissions, persistence/restart, DOM extraction/no values, exports, secret rejection, schema mutations, fixtures, end-to-end CLI, and every A5e assertion. Dependencies: WP2–WP5.
7. **WP7 — Documentation and manual protocol.** Document build/load, permission rationale, Grant → Reload → Start → browse, two-origin smoke, snapshot sensitivity, incomplete coverage, generator limits/operator completion, and training gate. Dependencies: WP3–WP6.
8. **WP8 — Controlled verification.** Run `npm test`, generation/validation commands, fixture checksum comparison, inspect manifest/tree, make `ACCEPTANCE.md` executable, then run existing Semgrep and ast-grep binaries without installing/replacing tools; archive results under `../scanners/`. Dependencies: WP7.

## Interface contracts

- `normalizeOrigin(input: string): string` → canonical `http(s)://host[:port]/*`; throws on credentials, unsupported schemes, or invalid host.
- `normalizeOrigins(inputs: string[]): string[]` → stable unique canonical patterns.
- `comparePermissions(requested: string[], granted: string[]): {requested, granted, missing, complete}`.
- `getState(storage): Promise<CaptureState>` / `updateState(storage, mutator): Promise<CaptureState>`; state contains requested origins, recording flag, events, timestamps, and diagnostics.
- `recordEvent(rawEvent): Promise<void>` → allowlisted persisted event, merged by request/source identity without losing method/status.
- runtime messages: `GET_STATUS`, `SET_ORIGINS`, `START_RECORDING`, `STOP_RECORDING`, `FORM_METADATA`, `EXPORT_SESSION`, `EXPORT_MARKDOWN`, `SAVE_SNAPSHOT`.
- `extractFormMetadata(document, pageUrl): FormMetadata[]` → actions and `{name,type}` only.
- `normalizeSession(input): Session`; throws for absent/invalid event structure or captured secret-like value fields.
- `deriveDiagnostics(session): Diagnostics` and `sessionToMarkdown(session): string`.
- `generatePhishlet(session, {name?, includeHosts?}): object`; `serializePhishlet(object): string`.
- `validatePhishlet(yamlText, schema): {valid, errors}` using `js-yaml` + Ajv.
- `generateTrafficSkeleton(session): string` → nonempty commented documentation stub.
- CLI: `node generators/cli.js phishlet <session.json> <out.yaml> [--name NAME] [--include-host HOST]`; analogous `markdown`, `traffic`, and `validate` subcommands.

## Requirement trace matrix

| Requirement | Work package(s) |
|---|---|
| R1 | WP2, WP3, WP7 |
| R2 | WP2, WP3, WP6 |
| R2a | WP2, WP3, WP6, WP7 |
| R2b | WP3, WP6 |
| R2c | WP2, WP3, WP6, WP7 |
| R2d | WP2, WP3, WP4, WP6 |
| R2e | WP2, WP3, WP6 |
| R2f | WP3, WP5, WP6 |
| R3 | WP3, WP4, WP6 |
| R4 | WP1, WP4, WP5, WP6, WP7 |
| R4g | WP5, WP6, WP7 |
| R5 | WP1, WP3, WP6, WP7 |
| R6 | WP4, WP6 |
| R7 | WP6 |
| R8 | WP7 and Role 5 review |
| R9 | WP7 |
| R10 | WP8 |
| R11 | WP6, WP8 |
| R12 | WP1, WP6, WP8 |

## Test plan

Automated `npm test`: A1, A3, A3d–A3h, A4, A5/A5b–A5e, A6, A7, structural portions of A8/A9, A11, and M2/M3/M6/M7/M8. It imports production modules, invokes the real CLI, uses mocked Chrome storage/permissions and DOM objects, parses YAML, validates JSON Schema, tests all mandated invalid mutations, and checks byte identity for A5e. WP8 directly verifies A10 and executable mode.

Manual: A2 requires loading the unpacked extension and inspecting its popup/service-worker console. A3b requires a consented two-origin browser redirect exercise. A3c, A3f, M1, M4, and M5 receive automated coverage plus documented manual confirmation. Manual capture fidelity cannot be truthfully claimed from the shell, so the checklist/report must label those pending rather than fabricate a pass.

## Assumptions and ambiguity defaults

- **ASSUMPTION:** A manifest-declared content script with optional-host match patterns satisfies A1; Chrome activates it only after host permission. Service-worker `webNavigation` also requests programmatic execution on relevant completions as a robustness path if needed.
- **ASSUMPTION:** Request and response callbacks remain separately countable by source while sharing a request ID for merge/deduplication; exports retain enough stage data to meet diagnostics.
- **ASSUMPTION:** Static snapshots use the active tab DOM via a content script and download a self-contained best-effort HTML file plus report; no resource fetching or script execution is added.
- **ASSUMPTION:** `credentials.search` placeholders are represented only when a captured username/password credential exists; their `key` is observed, `type` is fixed, and `search` alone is `{{PLACEHOLDER}}`.

## Out of scope

Live targets, password/token values, replay, bypass guidance, IdP-specific invented regexes, JS rewrite recipes, `force_post`, `js_inject`, remote telemetry, a production implant/profile, a guaranteed deployable phishlet, browser automation of the manual smoke, and installing/replacing static scanners.
