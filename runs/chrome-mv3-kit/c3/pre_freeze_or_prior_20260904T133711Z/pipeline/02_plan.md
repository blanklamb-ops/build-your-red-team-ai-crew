# Build Plan — Chrome MV3 Lab Documentation Kit

## Repository layout

```text
README.md, AUTHORIZED_USE.md, OPSEC_CARD.md, package.json
extension/
  manifest.json, service-worker.js, popup.html, popup.js, popup.css
  lib/origins.js, lib/state.js, lib/diagnostics.js, lib/exports.js
  snapshot.html, snapshot.js
generators/
  cli.js, phishlet.js, validate-phishlet.js, traffic-pattern.js
schemas/
  session.schema.json, phishlet-scaffold.schema.json
config/
  defaults.json
testdata/
  session.json, snapshot-page.html
tests/
  run-tests.js, chrome-mock.js, origins.test.js, lifecycle.test.js
  exports.test.js, phishlet.test.js, validator.test.js, utilities.test.js
pipeline/
  01_domain_brief.md ... 05_opsec_card.md
```

## Work packages

1. **WP1 — Project contracts and schemas.** Define package scripts, safe defaults, exact recorder session schema, strict scaffold schema, and synthetic recorder-exact fixture. No dependency.
2. **WP2 — Shared extension core.** Implement origin canonicalization, complete permission comparison, storage-backed state mutations, event merge/deduplication, diagnostics, JSON/Markdown export. Depends on WP1.
3. **WP3 — MV3 extension/UI.** Add manifest, listeners for request/response/navigation events, popup origin approval/status/start/stop/export controls, downloads, and snapshot page. Depends on WP2.
4. **WP4 — Safe generators.** Normalize recorder snake/camel fields, derive missing origins/diagnostics, filter configurable telemetry hosts, group with PSL semantics, detect credential material only in eligible value fields, emit inert placeholder scaffold, validate YAML+JSON Schema, and generate traffic skeleton. Depends on WP1.
5. **WP5 — Tests and fixtures.** Build a top-level runner whose child suites return/throw. Exercise shared production functions, lifecycle restart, diagnostics, exact fixture/schema, generation E2E, secret regressions, URL-only events, PSL cases, validator mutations, disabled training modules, and traffic output. Depends on WP2–WP4.
6. **WP6 — Operator docs and controlled checks.** Document install/build/load, Grant → Allow → Reload extension → Start → browse, permissions, manual smoke, generator/validator commands, heuristics, limits, snapshot safety, and lab-only use. Run existing Semgrep/ast-grep and archive outputs without changing scanners. Depends on WP5.
7. **WP7 — OPSEC review and acceptance handoff.** Inspect final tree, produce identical OPSEC artifacts with Detection Recommendations, execute the documented test command, and make `ACCEPTANCE.md` directly executable as a repository verification command while retaining manual scoring instructions. Depends on WP6.

## Interface contracts

```text
canonicalizeOrigin(input: string) -> string                // match pattern or throws
comparePermissions(requested: string[], granted: string[]) -> PermissionStatus
loadState(storage) -> Promise<RecorderState>
saveState(storage, state) -> Promise<void>
startSession(chromeApi, requestedOrigins, now?) -> Promise<RecorderState>
recordEvent(chromeApi, rawEvent) -> Promise<RecorderState>
buildDiagnostics(state, grantedOrigins?) -> Diagnostics
exportSession(state) -> SessionExport
renderMarkdown(session) -> string

normalizeSession(input) -> NormalizedSession
assertNoCredentialValues(input) -> void
generatePhishlet(session, options?) -> object
serializePhishlet(scaffold, metadata) -> string
validatePhishletText(yamlText, schema) -> ValidationResult
generateTrafficPattern(session) -> string
sanitizeSnapshot(html, options) -> { html, report }

node generators/cli.js phishlet --input FILE --output FILE [--include-host HOST]
node generators/cli.js traffic --input FILE --output FILE
node generators/validate-phishlet.js FILE
npm test
./ACCEPTANCE.md
```

## Requirement trace matrix

| Requirement | Work package(s) |
|---|---|
| R1 | WP2, WP3, WP6 |
| R2 | WP1, WP2, WP3, WP5 |
| R2a | WP2, WP3, WP5, WP6 |
| R2b | WP2, WP3, WP5 |
| R2c | WP2, WP3, WP5, WP6 |
| R2d | WP1, WP2, WP5 |
| R2e | WP2, WP5 |
| R3 | WP2, WP3, WP5 |
| R4 | WP1, WP4, WP5, WP6 |
| R5 | WP3, WP5, WP6 |
| R6 | WP4, WP5, WP6 |
| R7 | WP4, WP5, WP6 |
| R8 | WP7 |
| R9 | WP6 |
| R10 | WP6 |
| R11 | WP2, WP4, WP5, WP6 |

## Test plan

Automated checks cover A1, A3, A3c–A11 except scanner availability itself; A10 is a post-build command/artifact assertion. Shared production functions are imported for A3e/A3g/A5/A5c/A5d. Validator subprocess tests assert nonzero for malformed YAML, renamed required name, extra property, cookie value, and live regex. E2E invokes the documented phishlet command and validator on the exact recorder fixture. `npm test` is the one complete suite command; only `tests/run-tests.js` sets process status.

Manual checks are A2 and A3b plus fidelity M1–M7. A3b requires a clean authorized two-origin redirect flow with at least five events and a non-fallback request event. The README provides a checklist; automated tests never claim the browser smoke passed.

## Ambiguities and assumptions

- **ASSUMPTION:** “Evilginx 3.x-format” uses the documented 2.3-compatible field vocabulary plus `auto_filter`; the strict local schema is the acceptance authority.
- **ASSUMPTION:** static snapshots are made from operator-supplied saved HTML in the extension page, sanitizing scripts/event handlers; the kit does not broaden permissions to inject content scripts.
- **ASSUMPTION:** `ACCEPTANCE.md` will be a polyglot shell/Markdown executable that runs automated checks and prints the remaining manual checklist.
- **ASSUMPTION:** scanner executables may be unavailable. The controlled step records command, version/absence, output, and exit status; it never installs substitutes.

## Out of scope

Live targeting, secret/body/header-value capture, credential replay, turnkey phishlets, populated capture regexes, response rewrites or injected JavaScript, evasion/bypass guidance, off-host telemetry, active snapshot interaction, and guaranteed IdP/profile compatibility are excluded.
