# Build Notes — chrome-mv3-kit

## Implemented

- Manifest V3 extension with runtime-only optional HTTP(S) host access, broad one-click and narrow multi-origin grants, exact Start gate, visible permission sets, persistent `chrome.storage.local` session state, serialized writes, request/response metadata, required `onCompleted` response `extraHeaders`, main-frame navigation fallback, and local JSON/Markdown downloads.
- Allowlisted content-script form inspection records only resolved actions, control names/types, and trivial submit labels. It runs while recording on auth-relevant URLs or pages containing a password form and never reads/stores field values.
- Shared production origin normalization, permission comparison, event merge/deduplication, diagnostics, storage, capture normalization, Markdown, phishlet, YAML, validation, traffic-pattern, and static-snapshot functions.
- Conservative Evilginx 2.3.0-format generator with R4g host filtering/grouping, one optional auth asset domain, Set-Cookie-name grouping, auth URL selection, password-form/login-path priority, map-shaped credentials, and object-shaped placeholder `sub_filters`. No live rewrite, `force_post`, or `js_inject` logic is produced.
- Real PyYAML parsing plus Draft 7 `jsonschema` validation against the byte-copied study schema before CLI phishlet output is accepted.
- Static snapshot/report and exactly gated, separately labeled awareness modules; all unsafe-module defaults are false.
- One `npm test` command runs eight JS suites and the Python schema/parser suite. A5e byte-compares and exercises the unchanged supplied regression fixture through production generation and validation.

## Verification performed

`npm test` passes:

```text
PASS MV3 manifest and recorder wiring
PASS origin normalization and permissions
PASS MV3 lifecycle persistence
PASS form metadata allowlist
PASS capture and generator behavior
PASS YAML and JSON Schema mutations
PASS A5e regression mixed capture
PASS snapshot and training gates
PASS 8 JavaScript suites
PASS capture fixture schema and real YAML parser availability
```

CLI smoke generated JSON, Markdown, schema-valid phishlet YAML, traffic skeleton, snapshot HTML, and snapshot report in a temporary directory. Both study files compare byte-equal with their shipped destinations.

Controlled post-generation scans used preinstalled Semgrep 1.176.0 and ast-grep 0.45.3 with local offline `eval`/unexpected-`fetch` rules. Both returned zero findings. Raw outputs and reproducible commands are in `scanners/`. This workspace-local location is the acceptance-permitted run-root alternative because the managed filesystem does not authorize writes to `../scanners/`.

## Deviations from plan

- Scanner artifacts are under `scanners/`, not `../scanners/`, due the managed writable-root boundary; `ACCEPTANCE.md` explicitly permits the run-root scanner location.
- YAML parsing/schema validation uses already-installed Python packages instead of npm dependencies, keeping the project install-free and offline.
- `OPSEC_CARD.md` is intentionally not written in Role 4; sequential Role 5 owns both required identical OPSEC artifacts.

## Residual gaps

- **Manual only / not yet executed:** A2 unpacked clean-profile console check, A3b two-origin browser smoke, A3c visible revoked-permission Start behavior, A3f reload observation, and M1–M8. README contains the exact procedure and evidence threshold. Automated mocks cover the underlying Start comparison, persistence, source/origin diagnostics, fallback incompleteness, and normalization logic, but do not substitute for browser observation.
- Registrable-domain logic is deliberately conservative for the synthetic study corpus and explicit edge suffixes; it is not advertised as a complete embedded Public Suffix List. Unknown/non-registrable hosts fail or are dropped rather than producing junk.
- URLs are retained because the required evidence model calls for them. README warns they may contain sensitive query data; downstream generator screening ignores URL/query values as directed by R4 while rejecting secret-looking free-text fields.

## Scanner rerun

Use the two commands recorded in `scanners/README.md` after any source change, then rerun `npm test`.
