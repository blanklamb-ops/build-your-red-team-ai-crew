# Build Notes — Chrome MV3 Lab Documentation Kit

## Implemented

- Manifest V3 extension with only `webRequest`, `webNavigation`, `storage`, and `downloads` API permissions and optional runtime HTTP(S) host scope.
- Popup workflow for canonicalized multi-origin entry, explicit user-gesture grant, requested/granted/missing display, complete-set Start gate, Stop, and JSON/Markdown downloads.
- Metadata-only request/response recording plus main-frame navigation fallback. Events retain source, URL/origin, method/status where available, resource type, selected auth-header names, Set-Cookie names, and timestamp. Same-source duplicate callbacks merge without erasing richer fields.
- Serialized `chrome.storage.local` state controller persisting requested origins, recording state, session ID, timestamps, events, and diagnostics across fresh controller/worker instances.
- Diagnostics by source and origin with session times, permission sets/gaps, and conservative complete/incomplete coverage.
- Exact recorder-format session schema/fixture and strict scaffold schema (`additionalProperties: false`).
- Offline Python generator using Public Suffix List semantics, recorder snake/camel compatibility, URL-derived missing origins, diagnostics derivation, documented host/path heuristics, configurable telemetry exclusion, field-scoped secret detection, and inert credential/sub-filter placeholders.
- Executable real-YAML + Draft 2020-12 JSON Schema validator using PyYAML and `jsonschema`.
- Commented traffic-pattern exporter and sanitized static-snapshot utility with separate two-factor-gated, text-only awareness modules disabled by default.
- One `npm test` parent runner covering five suites. Imported JS/Python suites return or throw; they do not set an exit status.
- Executable `ACCEPTANCE.md`, comprehensive README, safe config, synthetic fixtures, and controlled scanner rules/reports.

## Deviations from the plan

- Generator and validator files use Python rather than the planned Node.js sketches. The environment has PyYAML 6.0.3, jsonschema 4.25.1, and publicsuffix2 available but lacks the proposed npm packages and registry access. This still supplies a real YAML parser, a real JSON Schema implementation, and PSL semantics fully offline. The extension and top-level test runner remain dependency-free JavaScript.
- Scanner artifacts live at `workspace/scanners/` because the writable workspace boundary does not include the sibling `../scanners/` directory; `PROMPT.md` permits a scanners directory at the run root.
- The snapshot utility accepts pasted, previously saved lab HTML rather than adding a content-script permission. This keeps the permission set exactly within R1 while still producing a static snapshot and removal report.

## Verification performed

- `npm test`: five suites passed, covering origin normalization/comparison, missing-permission Start refusal, worker restart restoration, diagnostics/Markdown, training/snapshot gates, session schema, phishlet E2E, PSL cases, snake/camel fields, URL-only events, missing diagnostics, cookies, UUIDs, JWT/long-token safety, traffic output, and validator mutations.
- `node --check` passed for service worker, popup, and snapshot UI; Python compilation passed.
- Documented generation command produced a non-empty two-host scaffold with cookie-name auth tokens and retained placeholders; the documented validator accepted it.
- Semgrep 1.176.0 scanned 15 JavaScript/Python targets with three local rules and reported zero findings. The initial wrapper attempts failed before scanning because its default config/cache locations are read-only; the successful invocation used Semgrep-specific `/tmp` paths, `--no-git-ignore`, and `--disable-version-check`.
- ast-grep 0.45.3 ran the local dynamic-eval rule against extension/tests and reported zero findings.
- Serena was not available in the provided tool set, so it was not used.

## Scanner commands

```sh
SEMGREP_SETTINGS_FILE=/tmp/chrome-mv3-kit-semgrep-settings.yml \
SEMGREP_LOG_FILE=/tmp/chrome-mv3-kit-semgrep.log \
SEMGREP_VERSION_CACHE_PATH=/tmp/chrome-mv3-kit-semgrep-version \
semgrep scan --config scanners/semgrep-rules.yml --metrics off \
  --disable-version-check --no-git-ignore --json-output scanners/semgrep.json \
  extension generators tests

ast-grep scan --rule scanners/ast-grep-rule.yml --json=pretty extension tests
```

## Residual/manual gaps

- A2 and A3b require a human with a clean interactive Chromium profile and an authorized two-origin redirect lab; they are documented but cannot truthfully be marked passed here.
- A3c has automated mock coverage, but its visible popup behavior remains part of the browser smoke.
- No first-full-PASS time is recorded because the required A2/A3b/A3c manual run has not occurred. Automated suites reached full PASS during Role 4.
- The sanitizer is intentionally conservative but not a forensic-grade HTML parser; operators must review static output and handle it as evidence.
