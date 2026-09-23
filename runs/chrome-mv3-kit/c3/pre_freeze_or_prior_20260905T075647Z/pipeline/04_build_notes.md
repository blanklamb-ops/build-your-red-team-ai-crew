# Role 4 — Build Notes

## Delivered

- Chrome MV3 extension with optional runtime HTTP(S) host access, one-click broad grant and complete narrow-origin workflow, full-set Start gate, persistent storage-backed state, request/response/navigation capture, redirect gap tracking, local JSON/Markdown downloads, and allowlisted DOM form metadata.
- Production shared helpers for idempotent normalization, permission comparison, safe event projection, diagnostics, coverage, and serialized persistence.
- Strict session and phishlet JSON Schemas; recorder-native synthetic multi-origin fixture and checked-in generated outputs.
- Capture-complete Python generator with Set-Cookie spelling aliases, Public Suffix List grouping, exact username priority (including hidden names), form-action login preference, telemetry/static exclusions, explicit include-host override, empty-array fidelity, secret-value rejection, coverage comments, and atomic output replacement.
- PyYAML + jsonschema validator with semantic checks and nonzero CLI failures; normalized JSON/Markdown exporter, documentation-only traffic skeleton, and static snapshot/report utility with fail-closed training gate.
- One test command covering imported production browser helpers and Python generator/validator utilities. `ACCEPTANCE.md` is an executable shell/Markdown polyglot that runs the preflight.
- README build/load/use/safety/permission/limitations documentation and safe default config.

## Verification performed

`./scripts/run-tests.sh` passes three imported JavaScript suites plus eight Python test cases, an actual generator CLI invocation, and standalone validator CLI invocation. Tests cover normalization, whole-set permissions, cookie-name projection without values, diagnostics, lifecycle restart/storage failure, mocked DOM extraction without `.value`, native/camel/legacy cookie aliases, empty arrays, missing diagnostics, hidden username priority, PSL `co.uk` grouping, telemetry/Copilot filtering and override, JWT/long-value rejection, UUID/cookie-name allowance, malformed YAML, all required schema mutations, reports, traffic output, snapshot gating, and E2E assertions.

JavaScript syntax and Python AST parsing passed. Generated fixture YAML validates and has two proxy hosts, non-empty cookie tokens/auth URLs, capture-derived `login` and credentials, and only the mandated `sub_filters`/credential-search placeholders.

## Scanner execution

Preinstalled tools only; nothing was installed or replaced:

```sh
SEMGREP_SETTINGS_FILE=/tmp/chrome-mv3-semgrep-settings.yml SEMGREP_LOG_FILE=/tmp/chrome-mv3-semgrep.log XDG_CACHE_HOME=/tmp/chrome-mv3-xdg-cache XDG_CONFIG_HOME=/tmp/chrome-mv3-xdg-config semgrep scan --disable-version-check --no-git-ignore --config scanner-rules/semgrep.yml --json --output scanners/semgrep.json extension generators tests scripts
ast-grep scan --rule scanner-rules/ast-grep-js.yml --json=pretty extension tests
ast-grep scan --rule scanner-rules/ast-grep-python.yml --json=pretty generators tests scripts
```

Semgrep scanned 11 applicable JavaScript/Python targets with six local rules and found zero issues; both ast-grep rules returned zero issues. Status, versions, JSON, stdout, and stderr are under `scanners/`.

## Deviations from plan

- Headless tooling uses Python with installed PyYAML 6.0.3, jsonschema 4.25.1, and publicsuffix2 instead of planned npm packages. The sandbox was offline and blocked nested Node subprocesses; direct Python provides the same real parser/schema/PSL contracts and makes the tool dependency-light. `requirements.txt` pins the environment.
- Scanner output could not be written to required sibling `../scanners/`: the research sandbox exposes that directory read-only. Complete evidence is archived at `workspace/scanners/`. This is the only R10 path deviation; commands and successful statuses are preserved for the harness/operator to copy to the run-level scanner directory.
- Serena was not available in this session, so navigation/editing used `rg`, shell reads, and `apply_patch`; no Serena usage is claimed.

## Residual/manual gaps

- Clean Chromium unpacked loading (A2) and the user-gesture two-origin redirect smoke (A3b/A3c, plus visual M1/M4/M5/M7 checks) require an interactive browser and authorized lab origins. They are documented precisely and are not falsely marked automated PASS.
- Scanner coverage is purpose-built for the safety contract rather than a remote managed ruleset; restricted network access prevented remote rule retrieval, consistent with the no-install/no-replacement constraint.
- The mandated `sub_filters` value and credential `search` values remain `{{PLACEHOLDER}}` exactly where PROMPT.md says metadata cannot evidence them. Captured credential keys and `login` references are fully populated.
