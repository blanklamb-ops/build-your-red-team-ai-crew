# Build Notes — chrome-mv3-kit

## Implemented

- MV3 extension with runtime-only HTTP(S) host permissions; persistent storage-backed capture state; request, response, and navigation sources; exact response-header `extraHeaders` listener; complete-set permission gate; popup origin/access/coverage status; data-URL exports.
- Idempotent shared origin normalization and wildcard-aware comparison used by both production UI/service-worker paths and tests.
- Form capture of action, field names/types, and trivial submit label without reading values; navigation-time injection plus declared content script.
- JSON/Markdown exports with source/origin counts, timestamps, permission gaps, warnings, safe non-HTTP(S) omission, and incomplete-coverage marking.
- Sanitized static snapshot plus report. Awareness modules are separate and gated by `lab_unsafe_modules=true`; defaults are false.
- Offline generator for a conservative, placeholder-free Evilginx 2.3.0 phishlet with R4g host/path rules, registrable-domain grouping, DOM-evidenced or disclosed heuristic credential keys, hostname rewrite objects, secret rejection, and explicit include-host override.
- Block-style YAML serializer/parser and recursive JSON-Schema validator against the byte-identical study 2.3.0 schema; malformed and structurally mutated YAML fails.
- Commented traffic-pattern documentation skeleton and CLI commands.
- Nine-suite test runner covering structure, normalization, permissions, MV3 restart, forms, exports, generation, schema mutations, A5e, secrets, fixture hashes, and safe config.

## Verification performed

- `npm test`: PASS, all 9 suites.
- `node --check` was run over extension, generator, and test JavaScript.
- Generated and validated `/tmp/chrome-mv3-kit-regression.yaml` from `testdata/regression-mixed-capture.json`.
- Generated Markdown and traffic skeletons from `testdata/session-fixture.json`.
- SHA-256 of source and shipped A5e fixture: `eddf034a05b205d7c2018e088f55a54a520c12c4c02b0463e46f869fe7b2a95f` for both.
- Semgrep: 3 local rules, 13 JavaScript targets, 0 findings. Output: `scanners/semgrep.json`.
- ast-grep: dynamic-eval rule over extension/generators/tests, 0 findings. Output: `scanners/ast-grep.json`.

Scanner commands (preinstalled tools only; no install/replacement):

```sh
XDG_CONFIG_HOME=/tmp/chrome-mv3-kit-semgrep XDG_CACHE_HOME=/tmp/chrome-mv3-kit-semgrep/cache SEMGREP_SEND_METRICS=off semgrep scan --no-git-ignore --config scanners/semgrep-rules.yml --json --output scanners/semgrep.json extension generators tests
ast-grep scan --rule scanners/ast-grep-rules.yml --json=pretty extension generators tests > scanners/ast-grep.json
```

## Plan deviations

- Scanner artifacts are under workspace-local `scanners/` instead of `../scanners/` because the managed filesystem only permits writes inside the workspace. This retains the required artifacts in the final deliverable tree.
- The implementation uses dependency-free JavaScript and a real block-YAML parser plus recursive draft-07 subset validator rather than external YAML/Ajv packages, preserving offline operation. The shipped schema features used by the study are all enforced and mutation-tested.
- The popup snapshot action communicates with the declared snapshot content script; no separate extension page was needed.

## Known/manual gaps

- **NOT AUTOMATED:** A2 unpacked Chromium load and A3b multi-origin redirect smoke require a clean authorized browser profile. README provides the exact procedure and pass threshold.
- Chrome UI permission prompt rendering and download save dialogs are manual fidelity checks.
- Static snapshot sanitation removes active content and form state but cannot decide whether visible page text is engagement-sensitive; operator review remains required.

## Time log

Approximately 14 wall-clock minutes from the first pipeline artifact to the first full automated PASS plus scanner archive. Manual A2/A3b time is not included and remains to be recorded by the lab operator.
