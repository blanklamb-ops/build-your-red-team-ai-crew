# OPSEC Card — after-action

## 1. Summary

after-action is an offline closeout collector for authorized security engagements. It reads fixed local JSONL/CSV evidence and operator decisions, correlates records by exact normalized asset and an inclusive time window, and writes a redacted client Markdown/HTML draft plus a more detailed internal learning report. It does not collect live telemetry, contact remote services, or grade operator skill. Client redaction is a risk-reduction control; human review remains mandatory.

## 2. Operator risks

- The internal report deliberately retains rationales, outcomes, raw summaries/details, TTP references, asset names, and values that client redaction may remove. Sending it instead of the client report is a direct disclosure.
- Regex rules can miss unknown secret/PII formats, encoded values, unusual identifiers, screenshots, or sensitive correlations. A report labeled “redacted” can still expose client or operator information.
- A misaddressed email, public/shared-drive link, broad collaboration permission, unmanaged local copy, backup, printout, or chat upload turns report handling into an OPSEC failure even when generation worked correctly.
- Incorrect clock assumptions, stale asset names, shared hostnames, or an overly broad window can create misleading associations. A client may treat correlation as causation unless an operator validates each row.
- Input evidence, console history, the internal report, scanner logs, and backups can reveal engagement timing, tooling, assets, operator decisions, or detection coverage.
- Reusing an output directory replaces named reports atomically. Although partial writes are avoided, an operator can still overwrite an earlier report version without external version/retention controls.

## 3. Artifacts left behind

- **Input/evidence:** the operator-supplied engagement.json, events.jsonl, events.csv, and decisions.csv; filesystem access/audit records may show they were read.
- **Reports:** client_report.md, client_report.html, and internal_learning.md in the selected directory. POSIX mode is set to 0600, and same-directory dot-prefixed temporary files exist briefly during atomic writes; abnormal process termination may leave one.
- **Console/process:** shell history, process-execution telemetry for the Python module, sanitized stderr warnings containing filenames/row numbers, and a stdout count summary.
- **Scanner/build:** scanner-output logs, Semgrep settings/log files, Python bytecode caches, test/build process telemetry, and generated fixture reports.
- **Network/registry/browser/mail:** the tool creates no intentional network connections, registry entries, browser state, or mail. Any upload, email, sync-client activity, or remote scanner traffic is external to the collector and must be governed separately.

## 4. Safer operating guidance

1. Work only inside the documented authorization and keep original evidence in the engagement's controlled evidence store. Use a dedicated local staging directory on an encrypted, access-controlled system.
2. Review the engagement metadata, UTC assumptions, exact asset keys, correlation window, and engagement-specific redaction rules before rendering. Do not broaden the window simply to increase match count.
3. Choose a dedicated output directory outside the evidence input. Preserve restrictive permissions; do not rely on 0600 when copying to filesystems or collaboration platforms that use different ACLs.
4. Inspect sanitized warnings, all signed deltas, unlinked counts, and asset identity. Treat each link as an association requiring validation.
5. Search both client files for engagement-specific secrets, PII, internal terminology, and identifiers. Have a second authorized reviewer approve the draft. Never deliver internal_learning.md.
6. Transfer only the reviewed client artifact through an approved encrypted channel with verified recipients and expiration/access controls. Record delivery and remove staging copies according to the retention plan.
7. Run scanners only as the controlled post-run step. Read the archive status: NOT_AVAILABLE or a nonzero/no-match result is not equivalent to a clean comprehensive scan.

## 5. Detection Recommendations

- Monitor endpoint process telemetry for the after_action CLI and correlate it with reads of JSONL/CSV engagement evidence followed by creation or replacement of client_report.md, client_report.html, or internal_learning.md. Validate that execution occurs only on approved assessment workstations and within closeout windows.
- Alert when files named internal_learning.md or matching the marker “INTERNAL SENSITIVE — NOT CLIENT-SAFE” are accessed by users outside the authorized engagement group, copied into sync folders, attached to mail/chat, uploaded through browsers, or written to removable media.
- Apply DLP/secret scanning to client-report transfers for private-key markers, bearer-token shapes, credential key/value forms, email addresses, and engagement-specific canaries. Quarantine or require review on a match; also flag missing expected redaction markers when a known synthetic validation canary is used.
- Audit ACL/share-link changes and external downloads for report directories. Alert on public/anonymous links, organization-wide grants, bulk downloads, unusual geographies/devices, or access after the engagement retention deadline.
- Detect transient dot-prefixed report files and rapid atomic rename/replacement in report directories. A leftover dot-prefixed report file after process exit should trigger review for an interrupted write and possible unreviewed content.
- Track checksum, author, review approval, destination, and transfer time for the delivered client artifact. Alert if the transferred checksum differs from the approved copy or if an internal and client report are sent in the same transaction.
- Monitor deletion/retention workflows for inputs, reports, scanner logs, backups, and collaboration copies. Flag evidence or internal reports persisting beyond the approved schedule.

## 6. Residual gaps

- The review used synthetic fixtures only; it did not validate every client log dialect, filesystem/ACL implementation, collaboration service, DLP product, or real-world timezone/asset-inventory condition.
- Redaction coverage is regex-based and cannot guarantee removal of all PII, secrets, encoded data, or context-sensitive identifiers.
- Semgrep ran two local rules over seven Python targets with zero findings. ast-grep ran one dynamic-eval pattern and returned its no-match exit status. These narrow scans do not establish general security.
- Report confidentiality at rest, key management, recipient verification, delivery tooling, backups, and retention enforcement remain operator/environment responsibilities.
- Exact asset correlation intentionally does not resolve aliases; false negatives and human validation remain possible.
