# OPSEC Card — `chrome-mv3-kit`

## 1. Summary

`chrome-mv3-kit` is a Chrome MV3 extension + Node CLI for **authorized lab
documentation**: recording auth-flow HTTP metadata, generating
placeholder-filled template files, saving static page snapshots, and
drafting a commented traffic-pattern skeleton. It is not a working
credential harvester, phishing proxy, or C2 implant. This card is intended
for inclusion in client/engagement reports alongside `AUTHORIZED_USE.md`.

## 2. Operator risks

- **Browser extension installation is visible.** An unpacked/dev-mode
  extension shows up in `chrome://extensions`, in enterprise extension
  inventory tools (e.g. Chrome Browser Cloud Management), and in
  `chrome://version` → profile data. Treat it as an artifact requiring the
  same handling as any other engagement tooling.
- **Runtime host-permission grants are logged.** The `optional_host_permissions`
  request (`http(s)://*/*`) triggers a Chrome permission prompt; some
  enterprise policies audit or block runtime permission grants.
- **Exported files land on local disk via `chrome.downloads`.** JSON/Markdown
  session exports and CLI-generated templates are ordinary files subject to
  EDR file-write and DLP inspection like any other artifact.
- **Gated modules still leave artifacts if misconfigured.** The
  `lab_unsafe_modules` review artifacts (`framing_review.html`,
  `file_prompt_review.html`, `decoy_placeholder.txt`) are inert, but their
  presence in an output directory should still be treated as sensitive
  engagement material and cleaned up post-report.
- **Templates are not attack-ready but shouldn't be mistaken for such.**
  `phishlet_template.yaml` / profile-stub output contain obvious
  `__REPLACE_*__` placeholders; do not hand these directly to downstream
  tooling without operator review, and never point them at anything outside
  signed authorization scope.

## 3. Artifacts left behind

- Extension install record in the browser profile (`chrome://extensions`,
  `Preferences`/`Secure Preferences` extension state).
- `chrome.storage.local` entries: current/last `AuthFlowSession` object.
- Downloaded exports: `chrome-mv3-kit-session-<id>.{json,md}`.
- CLI output directory (default `out/`): `session_export.json`,
  `session_summary.md`, `phishlet_template.yaml`, `profile_stub.txt`,
  `clone/snapshot.html`, `clone/clone_report.json`, and — only when both
  gates are enabled — `framing_review.html`, `file_prompt_review.html`,
  `decoy_placeholder.txt`.
- Standard Node/npm process execution and file-write activity from running
  `generators/cli.js`.

## 4. Safer operating guidance

- Keep `config/lab.config.json` `lab_unsafe_modules: false` except for the
  specific, time-boxed review that needs the gated modules; revert
  afterward.
- Scope `optional_host_permissions` down to the actual lab/target hosts in
  `manifest.json` rather than granting `http(s)://*/*` when the target set
  is known ahead of time.
- Store session exports and generated templates in the engagement's
  evidence-handling location, not general-purpose cloud storage; strip
  before any public repo archive per `AUTHORIZED_USE.md`.
- Uninstall the extension and clear `chrome.storage.local` at the end of
  the lab session (`Clear session` button, then remove the extension from
  `chrome://extensions`).
- Review every `__REPLACE_*__` / `{{PLACEHOLDER}}` field before any
  generated template is used downstream; do not automate placeholder
  substitution against production hostnames.

## 5. Detection Recommendations

Write from the operator's perspective as defender-side guidance suitable for a client report.

- **Extension inventory monitoring:** alert on unpacked/developer-mode
  extension installs and on extensions requesting broad host permissions
  (`<all_urls>` or runtime-granted `http(s)://*/*`) via Chrome Browser
  Cloud Management, `ExtensionInstallBlocklist`/`ExtensionInstallAllowlist`
  policy, or EDR browser-extension telemetry.
- **webRequest-capable extension activity:** flag extensions holding the
  `webRequest` permission alongside `downloads`, especially when paired
  with recently-granted optional host permissions — this combination
  (observe traffic, then export to disk) is a reasonable detection
  heuristic even though this kit only records header *names*.
  Note that `manifest.json`'s baseline `permissions` (`storage`,
  `webRequest`, `downloads`) contain no host access by themselves; the
  detectable signal is the *separate*, user-approved
  `optional_host_permissions` grant, not the base install.
- **Local file exports:** DLP/EDR file-creation rules for
  `chrome-mv3-kit-session-*.{json,md}` naming patterns, or more generally
  for browser-downloads-initiated JSON/Markdown files immediately following
  a new extension install, can catch this class of tooling regardless of
  branding.
- **Outbound network baseline:** because this kit performs no off-host
  exfiltration by design, any outbound traffic *from the extension's
  service worker* (as opposed to normal page/browsing traffic) is anomalous
  for this tool specifically and worth alerting on if observed — it would
  indicate a modified/malicious fork rather than expected behavior.
- **CLI/process telemetry:** `node generators/cli.js …` process creation
  with arguments referencing `phishlet:generate`, `profile:generate`, or
  `clone:run --lab-unsafe` is a useful EDR command-line detection rule for
  environments that want to flag this tool class even when run outside the
  browser.
- **File-system artifacts:** the presence of `framing_review.html`,
  `file_prompt_review.html`, or `decoy_placeholder.txt` in a directory is a
  reliable indicator that the gated "unsafe" lab modules ran; these
  filenames make good YARA/file-monitoring signatures for engagement
  cleanup verification.

## 6. Residual gaps

- No automated cleanup/uninstall script is provided; artifact removal
  (Section 4) is manual.
- Cookie-name and auth-header-name detection in `extension/lib/auth_header_patterns.js`
  is a static allow-list; it will miss custom/nonstandard auth header names
  used by a given target, which is a coverage gap for the recorder, not a
  safety gap.
- The traffic-pattern stub (`profile_stub.js`) and phishlet template
  (`phishlet_template.js`) are intentionally incomplete; this card does not
  cover risks introduced by whatever an operator fills those placeholders
  in with downstream, which falls outside this tool's scope.
- This kit has not been tested against enterprise Chrome policies that
  block unpacked extensions or optional host-permission prompts outright;
  behavior in such environments is undefined.
