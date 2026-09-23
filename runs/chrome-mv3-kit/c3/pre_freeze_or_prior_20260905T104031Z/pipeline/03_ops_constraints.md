# Operational Constraints — chrome-mv3-kit

## Runtime environment

- Support an unpacked extension in a clean current Chromium/Chrome profile and a local Node.js CLI on Linux/macOS/Windows-compatible JavaScript. Do not require administrator/root privileges.
- The extension and generators make no outbound application/API calls. Browser network observation is limited to operator-approved HTTP(S) origins; generator and validation workflows function offline/air-gapped.
- Treat `chrome.storage.local` as authoritative across MV3 worker suspension. Listener callbacks must tolerate state restoration latency and serialize updates to avoid lost events.
- Do not assume optional host grants survive extension removal. Reload should retain grants/requested origins, but the popup must recompute and display actual permissions before Start.
- Files are local operator-controlled evidence. Downloads must use clear names and must never auto-upload.

## Secrets and evidence handling

- Never collect or persist request/response bodies, header values, cookie values, DOM input values, autofill data, typed credentials, bearer tokens, or passwords.
- Only header names and Set-Cookie cookie names are retained. DOM extraction uses a newly constructed allowlisted object containing URL, resolved form action, field `name`/`type`, and trivially visible submit label; it must never spread/serialize DOM nodes.
- URLs are required evidence but may contain query values. Preserve them capture-faithfully in raw lab exports, label them potentially sensitive, and do not log them to external services. Downstream phishlet generation must reject secret-looking values in free text/query data while not rejecting cookie names or canonical UUID session IDs.
- Commit only synthetic `.test`/`example.com`/reserved-IP fixtures. Never commit real captures, generated evidence from real systems, browser profiles, tokens, or operator identity data. Generated local output should be excluded from version control by default.
- Avoid console logging captured events. Errors should name the failed operation/origin, not dump the entire evidence object.

## Operator workflow

1. Confirm written lab authorization and enumerate the complete expected origin set.
2. Load the unpacked extension in a dedicated clean lab profile.
3. Click **Enable lab access** for the default HTTP(S) grant or enter the complete narrower authorized origin list and request it.
4. Accept Chrome’s grant, reload the extension if needed, and confirm the popup shows requested, granted, and missing sets.
5. Click Start only after all requested origins are granted. The extension must reject Start otherwise.
6. Browse the authorized multi-origin flow, then Stop. Treat a fallback-only or permission-gap session as incomplete and repeat after correcting access.
7. Export JSON and Markdown locally; review diagnostics and redact/manage URL evidence appropriately.
8. Run headless generation/validation on an evidence copy. Complete `credentials.search` and `sub_filters` only through separate operator judgment, then test solely in the lab.

## Safety defaults

- Recording defaults OFF and is explicit per session. Optional training modules default OFF and activate only when configuration is exactly `lab_unsafe_modules: true`.
- Host access is optional/runtime and never silently granted. The broad one-click path remains deliberate; the narrower allowlist is available for least privilege.
- Start performs an exact complete-set permission check. Empty requested sets and any missing requested origin are hard failures.
- New/redirect origins are recorded as diagnostics and marked missing; they are never treated as implicitly authorized or complete coverage.
- Generated output is documentation-only, begins with an authorized-lab warning, and uses placeholders for credential searches and all unevidenced substitutions. No auto-generated live regex, `force_post`, or `js_inject`.
- Auth host inclusion is deny-by-default relative to R4g relevance rules. `--include-host` is explicit and auditable, but must not disable secret checks or schema validation.
- CLI generation fails closed on malformed/structurally incomplete data, unsafe secret-like values, invalid YAML, or schema failure. It never emits partial output as success.
- Snapshot output is static. Training-awareness additions are labeled and remain separated from normal snapshot behavior.

## Degradation modes

- **Offline:** all extension capture, fixture generation, validation, and docs continue; external format documentation is not required at runtime.
- **Missing permission:** Start returns a clear error and remains OFF. Observed navigation to an ungranted origin makes coverage incomplete.
- **webRequest degradation:** `webNavigation` preserves a main-frame fallback record, but diagnostics identify zero request/response callbacks and mark coverage incomplete.
- **Worker suspension/restart:** restore persisted requested origins, status, timestamps, events, and diagnostics before processing messages/events; tests must simulate a fresh worker instance.
- **Duplicate callbacks:** merge by stable request/navigation attributes while preserving method, status, headers, cookie names, source markers, and form fields.
- **No forms/cookies/auth paths:** preserve empty arrays and placeholders; fail only when required capture structure is absent. Never invent missing evidence.
- **Unavailable scanner:** do not install a replacement. Archive a clear availability/error record for that scanner and report A10 honestly.
- **Unavailable browser:** complete automated checks and publish the exact manual checklist; do not mark A2/A3b or visual behavior PASS.

## Detection-relevant artifacts for OPSEC review

- Chrome extension installation/grant prompts, extension ID/profile records, optional host permission state, and `chrome.storage.local` session evidence.
- Browser traffic to the authorized lab origins and repeated authentication/navigation requests during capture.
- Locally downloaded JSON/Markdown/YAML/HTML/profile files, filenames, timestamps, shell history, Node process execution, and scanner logs.
- Static snapshots may retain page text and URLs even though scripts are not active; generated phishlet metadata includes observed hostnames, paths, and cookie names.

## Non-negotiable plan deltas for the Architect

- **WP1:** copy both supplied study files byte-for-byte before deriving tests; add ignore rules for generated outputs/evidence.
- **WP2:** make storage writes serialized and state-first; model source counts, per-origin counts, requested/granted/missing sets, and coverage reason strings explicitly.
- **WP3:** ensure broad Grant is a direct popup click; load shared normalization with a script tag; recompute complete permission state on every popup open and Start; avoid captured-data console logs.
- **WP3:** content script must export/test a pure collector and construct allowlisted records only. Record empty `form_fields` where applicable.
- **WP4:** Markdown and JSON must contain identical diagnostic facts and a prominent incomplete marker/reasons.
- **WP5:** validate before writing success output; apply R4g deny rules before grouping; retain credential POST/form path priority; never relax placeholders through automatic inference.
- **WP6:** normal snapshot mode must not contain dormant-but-triggerable overlay/file-picker behavior; include awareness code only under the exact unsafe flag and label it.
- **WP7:** use temporary directories for generated test outputs; every child suite returns/throws; byte-compare A5e source/destination in the parent-run suite.
- **WP8:** document evidence sensitivity, dedicated-profile use, Grant → Reload → Start → browse, incomplete coverage handling, and manual items not exercised.
- **WP9:** execute only preinstalled scanners after all generated code is stable and preserve raw command/version/exit results.
- **WP10:** OPSEC card must cover the detection artifacts above and give at least three concrete defender recommendations.
