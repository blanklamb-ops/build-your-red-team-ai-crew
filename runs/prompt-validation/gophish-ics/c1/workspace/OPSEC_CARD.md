# OPSEC Card — `gophish-ics`

## 1. Summary

GoPhish-ICS enables calendar invite (ICS/iCal) phishing campaigns with RSVP telemetry tracking. This sidecar tool generates RFC 5545-compliant calendar invites that can be delivered via mail or other channels, then tracks recipient responses (accept/decline/tentative) for campaign assessment.

Calendar-based phishing exploits user trust in meeting invitations and calendar integrations, often bypassing traditional email security filters that focus on URLs and attachments.

## 2. Operator Risks

- **Accidental Disclosure**: Generated ICS files may be accidentally sent to unauthorized recipients if targeting data is misconfigured
- **Attribution**: Organizer email addresses and UID patterns in ICS files can fingerprint campaigns and link them to operators
- **Telemetry Exposure**: RSVP webhook server IP/domain may be discovered and attributed to testing team
- **Config Leakage**: Leaving `ics_enabled: true` in production config or version control exposes active testing
- **Log Residue**: RSVP logs contain recipient PII and response timing which must be sanitized post-engagement

## 3. Artifacts Left Behind

### Mail Gateway Logs
- ICS attachments or embedded content in email logs
- SMTP headers with sender/organizer addresses
- Message-ID and References headers linking campaign emails

### Calendar System Logs
- Calendar event creation timestamps
- RSVP response actions with client fingerprints
- Webhook callback URLs to RSVP server
- UID values in calendar database entries

### Client Device Artifacts
- `.ics` files in download folders or mail client caches
- Calendar entries in local/cloud calendar stores
- RSVP network requests in browser/app logs
- Cached event descriptions containing phishing indicators

### Server-Side Artifacts
- `telemetry.db` SQLite database with full recipient PII
- ICS generator logs showing campaign preparation
- RSVP webhook server access logs
- Generated `.ics` files if not cleaned up post-campaign

## 4. Safer Operating Guidance

### Before Campaign
1. Verify authorization scope and approved target list
2. Use dedicated organizer addresses that don't reveal operator identity
3. Set unique-per-campaign UIDs that don't expose patterns
4. Review ICS content for accidental PII or sensitive details
5. Keep `ics_enabled: false` in checked-in configs; enable only during active testing

### During Campaign
6. Monitor RSVP webhook for unexpected traffic (attribution attempts)
7. Rate-limit RSVP endpoints to avoid DoS on telemetry DB
8. Use authenticated webhook endpoints in production testing
9. Log access from RSVP server with geolocation to detect anomalies

### After Campaign
10. Purge `telemetry.db` or anonymize recipient data
11. Delete generated `.ics` files from operator systems
12. Scrub RSVP server logs of recipient PII
13. Reset `ics_enabled: false` in all configs
14. Archive sanitized metrics (counts only, no PII)

## 5. Detection Recommendations

### For Mail/Calendar Gateway Defenders

- **Monitor ICS Attachment Patterns**: Flag emails with `.ics` attachments from external or untrusted senders, especially when combined with urgency language ("emergency meeting", "urgent security update")

- **Inspect Calendar Event Metadata**: Analyze organizer addresses in calendar invites for spoofing patterns (e.g., look-alike domains, free email providers masquerading as corporate accounts). Check UID fields for anomalous patterns (non-standard domains, sequential numbering indicating bulk generation).

- **Track RSVP Callback Domains**: Calendar invites may include webhook URLs for RSVP tracking. Monitor outbound connections from calendar servers to unknown or recently-registered domains. Correlate multiple users connecting to the same RSVP endpoint as indicator of campaign-scale phishing.

- **Detect Time Manipulation**: Phishing campaigns often use near-term event times to create urgency. Flag calendar invites created <24 hours before event start time, especially when sent to large recipient groups.

- **Content Analysis**: Apply phishing heuristics to event descriptions and location fields - these are often overlooked in calendar security but can contain credential-harvesting links or social engineering content. Look for URL shorteners, suspicious domains, or embedded tracking pixels.

- **Cross-Reference Email Security**: Correlate calendar invite senders with email reputation feeds, DMARC/SPF/DKIM failures, and known phishing infrastructure. Calendar gateways should enforce the same sender validation as email gateways.

- **RSVP Response Rate Anomalies**: Unusual RSVP patterns (e.g., zero responses, or abnormally high accept rates for external senders) may indicate awareness of testing or sophisticated filtering by recipients.

### For Incident Response Teams

- **Calendar Forensics**: Collect `.ics` files from affected users' download folders and mail clients. Extract UIDs, organizer addresses, and RSVP callback URLs for campaign attribution.

- **RSVP Traffic Analysis**: Review firewall/proxy logs for connections to RSVP webhook domains. These requests reveal campaign infrastructure and may contain timing data correlating user actions.

- **Client-Side Indicators**: Check calendar applications for suspicious event entries. Users may not recognize phishing calendar invites as threats and may leave them in their calendars post-click.

## 6. Residual Gaps

- **Calendar-Specific Evasion**: This implementation does not explore advanced evasion techniques such as timezone manipulation to hide events, VTIMEZONE confusion, or malformed ICS fields that exploit parser vulnerabilities
  
- **Multi-Stage Campaigns**: RSVP "accept" actions could trigger second-stage payloads (e.g., credential harvesting landing pages), but this implementation only tracks responses, not downstream exploitation

- **Mobile Calendar Integration**: Mobile devices often auto-add calendar invites from email; detection recommendations focus on gateway-level controls and may not address mobile-specific risks

- **Encrypted Calendar Systems**: End-to-end encrypted calendar platforms (e.g., ProtonCalendar) may prevent gateway inspection of ICS content, limiting detection options to metadata analysis only

- **Cross-Platform Variations**: ICS rendering varies across Outlook, Google Calendar, Apple Calendar, and others; this tool generates standard-compliant ICS but doesn't test platform-specific exploitation vectors
