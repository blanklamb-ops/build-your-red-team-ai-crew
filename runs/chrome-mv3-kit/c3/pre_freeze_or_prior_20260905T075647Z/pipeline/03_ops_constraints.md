# Role 3 — Operational Constraints

## Runtime environment

- Supported operator environment: a current Chromium/Chrome build with Manifest V3, loaded unpacked by an interactive non-root lab user; Node.js 18+ and npm for local generators/tests. No elevated OS privileges are required.
- The extension may observe only explicitly authorized HTTP(S) lab origins. It makes no network requests of its own and has no remote backend. Generator, validator, snapshot, and test execution must remain offline after dependencies are present.
- Optional host permission prompts require a real user gesture. Browser reload and redirect smoke checks are manual. Headless tests mock Chrome APIs and must never claim the manual checks passed.
- Preinstalled Semgrep and ast-grep are controlled post-run tools. Do not install, upgrade, alias, or replace either scanner. Archive exact execution status and stderr as evidence.

## Secrets and evidence handling

- Never persist or commit request/response bodies, input `value` properties, Cookie/Set-Cookie values, Authorization values, tokens, passwords, autofill text, local browser profiles, HAR files, or live customer hostnames.
- The recorder’s positive data allowlist is URL, origin, method, status, resource type, timestamp, event source, request ID, auth-related header **names**, Set-Cookie **names**, redirect origin, and form action/control name/type/trivial submit label. Header parsers may inspect a Set-Cookie string transiently only to retain the name before the first `=`; no raw header object enters storage.
- Static snapshots are evidence and may contain page-rendered data even when scripts are removed. Operators must use synthetic/sanitized pages, store output in the engagement evidence boundary, review before sharing, and delete per engagement retention policy.
- Generated reports/YAML can reveal lab topology and cookie/form names. Treat them as engagement evidence. Fixture data is limited to reserved/synthetic domains.
- Secret scanning targets values in unexpected/free-text input only. Cookie names, field names, canonical UUID `session_id`, timestamps, hosts, and paths are bookkeeping and must not trigger rejection.

## Operator workflow

1. Confirm written authorization and enumerate every expected origin, including redirects.
2. Load `extension/` unpacked; open popup. Choose one-click **Enable lab access** for declared HTTP(S) patterns or enter the complete narrower set. Review requested/granted/missing lists and approve Chrome’s prompt.
3. Reload the extension if required. Reopen popup and confirm the requested set persisted and every requested origin is granted.
4. Click Start. Start must fail closed if any requested permission is missing. Browse the authorized redirect flow. Do not enter real secrets; use synthetic accounts/data.
5. Stop, inspect event/source/origin counts and coverage. A fallback-only, one-event, or permission-gap session is incomplete and must be recaptured, not relabeled.
6. Export JSON/Markdown locally; run the documented generator/validator and traffic/snapshot commands. Review capture-derived YAML and manually complete only the `sub_filters` rewrite recipe in a controlled lab. Validate and lab-test; do not treat output as live-deployment-ready.
7. Run the single test command and acceptance checker. Execute/document the manual smoke separately, then retain or dispose of artifacts under engagement policy.

## Safety defaults

- Recording defaults OFF, with empty events and no host access at install. Origin grants and Start are separate explicit actions. Clear/reset is explicit and local.
- Broad `http://*/*` and `https://*/*` access is offered because R2a requires a one-click default, but UI and README must label its breadth and offer narrower canonical origins. Access alone never starts capture.
- Capture is passive metadata observation: no request modification, blocking, replay, proxying, exfiltration, body access, or credential-value access.
- Coverage is pessimistic: any permission gap or zero non-fallback webRequest events yields `incomplete`; no diagnostics block is reconstructed from events, never assumed complete.
- Host selection is deny-by-default for known telemetry/analytics/CDN categories. Explicit `--include-host` is scoped to named hosts and recorded in comments; it does not disable other filters globally.
- Unknown auth paths are never invented. Arrays remain explicit `[]`. Credential regex search stays a placeholder unless supplied deliberately on the CLI. `sub_filters` always contains the required placeholder and no generated recipe.
- Training modules are inert unless both named and `lab_unsafe_modules=true`; default config is false. The snapshot utility must reject a requested training module when the gate is false.

## Degradation modes

- **Offline:** extension capture/export and installed Node dependencies continue locally. No remote enrichment or silent download is attempted. Missing dependencies produce a clear nonzero CLI error.
- **Partial permissions/redirects:** Start refuses known missing requested origins; newly observed navigation origins are retained as gaps and force incomplete coverage.
- **webRequest blind spot/cache/API flakiness:** main-frame `webNavigation` provides a labeled fallback, never a substitute claim. Fallback-only sessions remain incomplete.
- **Worker suspension/write collision:** every mutation reloads and atomically writes stored state through a serialized queue; restart tests prove restoration. If storage fails, return an error and do not claim recording/export success.
- **No forms/cookies/auth paths:** generate valid empty arrays; login uses the best non-static observed auth URL. If no structurally valid host/login candidate exists, fail clearly.
- **Malformed/unsafe input:** parse/schema/secret failures exit nonzero and do not write a final output. Write to a temporary sibling and rename only after successful generation/validation where practical.
- **Scanner unavailable:** archive command-not-found/status evidence and report A10 not met. Do not install replacements.

## Detection-relevant artifacts for Role 5

Document Chrome extension installation/permission prompts, extension storage and downloads, repeated auth navigation generated by manual lab exercise, local JSON/Markdown/YAML/snapshot/profile files, Node process/CLI history, npm dependency tree, and scanner logs. Defender recommendations must cover extension inventory/host grants, unusual access to authentication URLs, artifact discovery/DLP, and confirmation that no off-host network destinations exist.

## Plan deltas the Architect must respect

- **WP1:** Schemas use `additionalProperties: false` where required; fixture includes recorder-native `set_cookie_names`, hidden `login` plus password form fields, auth paths, telemetry, two origins, and no secret values.
- **WP2:** Use positive field projection before persistence; serialize all storage mutations; derive diagnostics deterministically from stored events.
- **WP3:** Persist the requested set before/with grants, compare the entire set at Start, and expose exact requested/granted/missing lists. Add redirect capture and origin-gap recording. Never send network requests.
- **WP4:** DOM extraction must never access/serialize `.value`; snapshot reporting must warn about rendered sensitive content and training gating.
- **WP5:** Both JSON and Markdown carry the same diagnostics and prominent coverage label.
- **WP6:** Fail before final output on secret/structure/schema errors; exact username-name priority and form-action preference are mandatory. Include-host is explicit per host. Comments disclose incomplete coverage and operator-supplied regexes.
- **WP7:** Assert prohibited fields are absent recursively; simulate storage failure and worker restart; child suites return/throw only.
- **WP8:** Document evidence handling, broad-vs-narrow grants, truthful manual status, and operator completion limits.
- **WP9:** Record exact scanner versions/commands/status; never mutate scanner installation.
