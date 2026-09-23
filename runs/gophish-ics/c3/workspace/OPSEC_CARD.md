# OPSEC Card — gophish-ics

## 1. Summary

gophish-ics is an offline, authorized-research sidecar that generates recipient-specific RFC 5545 calendar invitations from campaign fixtures, validates them, stores normalized RSVP observations in SQLite under stable campaign/recipient IDs, and prints per-campaign counts. Its shipped configuration disables generation, and it contains no mail sender, GoPhish credential handling, external connection, or security-control bypass.

## 2. Operator risks

- Editing or replacing the shipped false configuration with a persistent enabled file weakens the principal safety boundary and can make later invocations generate content unexpectedly.
- Using real attendee addresses, subjects, descriptions, or GoPhish exports leaves sensitive engagement and personal data in JSON, generated .ics files, shell history, backups, and SQLite records.
- Handing an invite to a live mail system can trigger calendar auto-processing, outbound RSVP messages, gateway alerts, recipient notifications, or cross-tenant audit events even if the sidecar itself remains offline.
- Incorrectly mapping email addresses instead of immutable GoPhish result IDs can attribute replies to the wrong person. Replayed or delayed responses remain in the event history even when they are not current.
- Generated invitations contain recognizable PRODID, UID domain, METHOD:REQUEST, and X-GOPHISH-* correlation fields. These are appropriate defender-visible lab markers, not covert identifiers.
- CLI success output exposes the output path, while operating-system process/audit logs may retain command paths, campaign identifiers, and temporary enabled-config locations.

## 3. Artifacts left behind

- **Filesystem:** operator-selected .ics files; campaign and RSVP JSON; temporary ics_enabled: true files; SQLite database plus possible -wal, -shm, or journal sidecars; scanner logs/settings under the chosen temporary directory; shell history and terminal capture.
- **Application/database:** immutable rsvp_events, current rsvp_current rows, stable campaign/recipient IDs, normalized timestamps, and response values. The tool creates no registry keys, service, scheduled task, persistence, or browser storage.
- **Process/host telemetry:** Python execution of gophish_ics.cli, file creates/opens, SQLite access, and acceptance-run temporary directory activity.
- **Network:** none from normal tool operation. If an operator performs the documented external handoff, downstream systems may record GoPhish API/template changes, MIME text/calendar or .ics attachments, SMTP metadata, attachment hashes, calendar ingestion, and iTIP RSVP replies.
- **Mail/calendar systems:** message trace, sender-authentication verdicts, organizer and attendee addresses, UID, METHOD, invite auto-processing decisions, calendar audit records, and outbound accept/decline/tentative replies.

## 4. Safer operating guidance

- Confirm written authorization and test boundaries first. Run unprivileged, offline, and with only synthetic .test fixtures until the approved integration window.
- Keep config/default.yaml unchanged at ics_enabled: false. Create a uniquely named enabled config in an access-controlled temporary case directory, pass it explicitly, and remove it after reconfirming the shipped file hash.
- Preserve the source platform's stable campaign result ID as recipient_id; never substitute email as identity. Validate every invite before any approved handoff.
- Generate only to a new file. Keep invite/database artifacts out of the repository, restrict permissions, hash them when evidence procedures require it, and dispose of them under the engagement retention plan.
- Stage mail/calendar integration in a sink or isolated tenant with external delivery disabled. Confirm gateway auto-processing and automatic RSVP behavior with the client before attachment handoff.
- Treat SQLite errors, missing dependencies, or unavailable gateways as stop conditions. Do not fall back to another delivery route or an untracked telemetry store.

## 5. Detection Recommendations

- **Mail gateway rule:** alert or quarantine inbound messages where MIME type is text/calendar or an attachment ends in .ics and the organizer domain differs from the authenticated sender domain, especially when METHOD:REQUEST and RSVP=TRUE are present. Enrich with SPF, DKIM, DMARC, first-seen sender/domain, attachment hash, and recipient count.
- **Calendar ingestion analytics:** detect invitations from newly observed or external organizers that are auto-added without an established correspondence history. Raise severity for mismatched From, Sender, ORGANIZER, and reply-to identities, or when the UID domain is unrelated to the sender.
- **Known lab-marker query:** during an authorized exercise, search decoded calendar bodies for PRODID:-//Authorized Research//gophish-ics, UID:*@gophish-ics.test, X-GOPHISH-CAMPAIGN-ID, or X-GOPHISH-RECIPIENT-ID. Scope this signature to the agreed exercise window so it remains a deterministic validation signal.
- **RSVP egress correlation:** correlate outbound calendar METHOD:REPLY messages or accept/decline/tentative actions with an inbound invitation seen shortly beforehand. Alert when replies leave the tenant for an untrusted organizer domain or bypass the normal calendar service.
- **Endpoint/file telemetry:** on administration or mail-staging hosts, hunt for Python processes invoking -m gophish_ics.cli, creation of .ics beside temporary enabled.yaml files, and SQLite files containing tables named rsvp_events and rsvp_current. Use this as exercise/investigation context, not a standalone malicious verdict.
- **GoPhish/admin audit:** where GoPhish is authorized, correlate template creation/update events containing text/calendar attachments with campaign launch, recipient result IDs, message trace, and gateway detections. Alert on out-of-window changes or use by an unexpected administrator.
- **Response containment:** preserve the original MIME/calendar body and gateway decision, disable invite auto-processing if risk warrants, search sibling recipients by attachment hash/UID/organizer, and avoid accepting or declining from an analyst mailbox because that can generate external telemetry.

## 6. Residual gaps

- The review did not deliver through SMTP, import the file into a common calendar client, exercise a live GoPhish API, or observe a real calendar gateway; compatibility evidence is the automated narrow-profile RFC 5545 validator and tests.
- RSVP ingestion accepts already normalized operator observations; inbound iTIP/MIME parsing, webhook authenticity, and mail-to-result-ID mapping remain outside this harness and require separate integration review.
- Semgrep used a limited local three-rule safety profile and scanned the six implementation modules; the environment excluded tests under its existing ignore policy. ast-grep covered implementation and tests for three dangerous-call patterns. These are archived checks, not a comprehensive security audit.
- Temporary enabled-config and generated evidence cleanup is documented but not technically enforced after operator handoff. The tool cannot control copies made by mail, calendar, backup, endpoint-monitoring, or case-management systems.
- No required implementation feature was found incomplete, and no blocking safety defect was identified in this review.

