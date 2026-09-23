# OPSEC Card — `gophish-ics`

## 1. Summary

GoPhish ICS Integration adds calendar invite functionality to phishing campaigns. Operators generate RFC 5545-compliant `.ics` files that can be attached to campaign emails, and track recipient RSVP responses (accept/decline/tentative) as telemetry.

**Operator use case:** Increase engagement rates by delivering phishing content as calendar invites, which may bypass certain email filters and leverage calendar client trust relationships.

## 2. Operator risks

- **Calendar client fingerprinting:** Generated ICS files contain identifiable `PRODID` and formatting patterns that may be detectable
- **Telemetry infrastructure exposure:** RSVP tracking requires webhook endpoints or manual recording that can reveal campaign infrastructure
- **Email gateway inspection:** ICS attachments may be parsed by email security gateways for malicious content
- **Metadata leakage:** Organizer addresses, server URLs in ICS files can reveal campaign origin
- **Time zone correlation:** Event times may correlate with operator location if not using explicit UTC

## 3. Artifacts left behind

- **Calendar events:** Recipients who accept invites will have persistent calendar entries until manually deleted
- **Email with ICS attachment:** Email and attachment persist in mailbox, logs, and backups
- **Calendar client logs:** ICS processing logged by Outlook, Google Calendar, etc.
- **RSVP responses:** Email or HTTP responses from recipients to organizer/tracking endpoints
- **Database records:** SQLite telemetry database (`telemetry.db`) on operator infrastructure
- **Email gateway logs:** Security products log ICS attachment metadata and content inspection results

## 4. Safer operating guidance

### Pre-engagement
- Verify written authorization for calendar invite delivery
- Use dedicated infrastructure with no attribution to operator organization
- Configure throw-away organizer addresses
- Test ICS generation against target email/calendar stack in lab first

### During engagement
- Use explicit UTC timestamps (avoid time zone leakage)
- Randomize or minimize `PRODID` and other ICS metadata
- Host tracking webhooks on segregated infrastructure
- Monitor for defensive responses (SOC tickets, incident response)

### Post-engagement
- Collect and delete calendar events from willing participants
- Destroy telemetry database securely
- Remove RSVP tracking infrastructure
- Include ICS artifacts in engagement report for client defensive review

## 5. Detection Recommendations

**Defender guidance for security operations and calendar/mail gateway teams:**

- **Email gateway inspection:** Parse `.ics` attachments and inspect `ORGANIZER`, `ATTENDEE`, `UID`, and `PRODID` fields for anomalies or known-bad indicators. Flag invites with suspicious organizer domains, external attendee lists, or generic product identifiers.

- **Calendar gateway monitoring:** Monitor for bulk calendar invite acceptance/creation events from external senders. High volumes of invites with identical `UID` patterns or organizer addresses may indicate campaign activity. Alert on invites with tracking URLs in `DESCRIPTION` or `LOCATION` fields.

- **RSVP telemetry correlation:** Track outbound RSVP responses (email replies or HTTP callbacks) to unknown or suspicious endpoints. Correlate with email attachment patterns — legitimate calendar systems have established infrastructure, while phishing campaigns often use new or ephemeral domains.

- **Anomalous calendar behavior:** Alert on user accounts that suddenly accept large numbers of external invites, especially if from previously unseen domains. Monitor for invites with exfiltration vectors (links to credential harvest pages) in event descriptions.

- **ICS structure validation:** Enforce RFC 5545 compliance strictly and flag deviations. Reject or quarantine invites with missing required fields, malformed timestamps, or suspicious embedded content (e.g., JavaScript in HTML-formatted descriptions).

- **User training:** Educate users that calendar invites from unknown senders can be phishing vectors. Encourage verification of organizer identity before accepting, especially for urgent or unusual meeting requests.

- **Endpoint detection:** Monitor calendar client logs (Outlook, Thunderbird, Google Calendar sync) for automated processing of ICS from untrusted sources. Detect bulk import or processing of invites from anomalous origins.

## 6. Residual gaps

- **Mobile calendar clients:** Detection coverage may be limited on mobile devices where calendar apps auto-process ICS without centralized visibility
- **Encrypted email:** ICS attachments in encrypted emails bypass gateway inspection until endpoint delivery
- **BYOD environments:** Personal devices may sync external calendar invites to corporate calendars without IT visibility
- **Multi-tenant calendar systems:** Cloud calendar services (Google Workspace, M365) may not expose sufficient telemetry to tenant admins for RSVP correlation
- **Legacy calendar systems:** Older Exchange or Lotus Notes deployments may lack modern inspection capabilities for ICS content
