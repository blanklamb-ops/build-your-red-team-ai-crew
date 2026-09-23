# OPSEC Card — gophish-ics

**Tool:** gophish-ics  
**Version:** 1.0 (research build)  
**Reviewed:** 2026-09-15  
**Reviewer:** OPSEC Reviewer (Pipeline Stage 5)

---

## Summary

`gophish-ics` generates RFC 5545-compliant iCalendar invite files (`.ics`) for use in authorized phishing campaigns. The tool operates as a **sidecar utility** (not a GoPhish fork) that produces calendar invites from campaign JSON data and tracks simulated RSVP responses (accept/decline/tentative) in a local SQLite database.

**Primary use case:** Social engineering engagements where calendar invites appear more trustworthy than traditional phishing emails, bypassing user skepticism of "click this link" messages by instead requesting meeting attendance.

**Safety posture:** ICS generation is disabled by default (`ics_enabled: false` in config). All test fixtures use RFC-reserved domains. Domain allowlist prevents accidental targeting of real addresses. Database files created with restrictive permissions.

---

## Operator Risks

### 1. Configuration Mismanagement

**Risk:** Operator commits config file with `ics_enabled: true` or includes real campaign data in testdata/ directory.

**Burn scenario:** Repository pushed to public/shared Git hosting with live engagement configuration or victim identities exposed.

**Mitigation:**
- Automated test fails CI if config has `ics_enabled: true`
- `.gitignore` excludes `telemetry.db` and `output/*.ics`
- SAFETY_CHECKLIST.md includes pre-commit hook example

### 2. Organizer Identity Attribution

**Risk:** ICS ORGANIZER field leaks operator's real email address or infrastructure domain.

**Burn scenario:** Victim forwards calendar invite to IT security team. ORGANIZER field shows `redteam-operator@realtoolcompany.com` instead of spoofed internal address. Attribution reveals engagement infrastructure.

**Mitigation:**
- Use throwaway email addresses aligned with pretext
- Review generated `.ics` file before deployment
- Test invite appearance in target calendar client before sending to victims

### 3. Timezone Fingerprinting

**Risk:** ICS timestamps may leak operator's timezone or create inconsistencies with spoofed organizer's expected location.

**Burn scenario:** Email headers show UTC+8 send time, but ICS shows America/New_York event creation. Victim notices discrepancy, reports to security team.

**Mitigation:**
- Tool uses explicit UTC timestamps by default
- Review `DTSTART`/`DTEND` fields for timezone alignment with pretext
- Consider target organization's typical meeting scheduling patterns (e.g., US East Coast company rarely schedules 2am meetings local time)

### 4. Telemetry Database Compromise

**Risk:** `telemetry.db` file contains victim email addresses and response patterns. If operator's workstation is compromised or database accidentally shared, victim identities leak.

**Burn scenario:** Operator's laptop stolen during engagement. Unencrypted database file contains 500 real victim email addresses with RSVP timestamps.

**Mitigation:**
- Store `telemetry.db` on encrypted volume
- Use `--db-path` flag to isolate databases per client engagement
- Archive engagement databases to secure storage immediately after engagement
- Delete local copies after secure archival

### 5. Unsafe Domain Testing

**Risk:** Using `--force` flag to bypass domain allowlist during testing accidentally targets real corporate email addresses.

**Burn scenario:** Operator tests campaign with `--force` flag, accidentally loads production campaign file instead of test fixture. ICS generated with 1000 real victim addresses. If deployed, engagement becomes unauthorized.

**Mitigation:**
- Never use `--force` flag outside authorized engagement execution
- Separate directories for test fixtures vs. live campaign data
- Peer review before using `--force` flag
- Use `--demo` flag for all testing (adds visible demo notice)

---

## Artifacts Left Behind

### On Operator System

1. **Telemetry database (`telemetry.db`)**
   - Location: Working directory (default) or `--db-path` target
   - Content: Recipient email addresses, campaign IDs, RSVP statuses, timestamps
   - Persistence: Permanent until manually deleted
   - Risk: PII leakage if system compromised

2. **Generated ICS files (`output/*.ics`)**
   - Location: `output/` directory
   - Content: Full calendar invite with organizer identity, attendee list, event details
   - Persistence: Permanent until manually deleted
   - Risk: Campaign attribution if files recovered

3. **Build artifacts (`bin/*`)**
   - Location: `bin/` directory
   - Content: Compiled Go binaries (generate, simulate-rsvp, report)
   - Persistence: Until cleaned
   - Risk: Low (binaries contain no sensitive data, but indicate tool usage)

4. **Log files (if any)**
   - Location: Not created by default, but operators may redirect stdout/stderr
   - Risk: May contain campaign data or victim identities if logging enabled

### On Victim System

5. **Calendar event entry**
   - Location: Victim's calendar application database (Outlook PST/OST, Google Calendar, Apple Calendar)
   - Content: Meeting invite with ORGANIZER, ATTENDEE, DTSTART/DTEND, DESCRIPTION
   - Persistence: Until victim deletes event (may persist after campaign if not cleaned up)
   - Forensic value: HIGH — shows spoofed organizer identity, tracking URLs (if embedded), event metadata

6. **Email with ICS attachment (if sent via GoPhish)**
   - Location: Victim's mailbox, mail server logs, mail gateway archives
   - Content: Original phishing email with `.ics` attachment
   - Persistence: Months to years (retention policies vary)
   - Forensic value: VERY HIGH — full email headers, SMTP relay path, attachment

7. **Calendar RSVP response (if victim responds)**
   - Location: Mail server logs (victim → organizer)
   - Content: iCal METHOD:REPLY with PARTSTAT change (ACCEPTED/DECLINED/TENTATIVE)
   - Persistence: Mail server retention period
   - Forensic value: HIGH — confirms victim interaction, response timestamp

### Network/Infrastructure

8. **Mail gateway logs**
   - Location: Inbound/outbound mail filters, DLP systems
   - Content: MIME multipart/alternative with text/calendar part, ICS attachment metadata
   - Detection: Unusual sender domain, single-attendee meetings, suspicious ORGANIZER
   - Persistence: 30-90 days typical

9. **Calendar gateway logs (Exchange, O365)**
   - Location: Exchange transport logs, O365 audit logs
   - Content: Calendar item creation events, RSVP processing
   - Detection: Bulk calendar invites from unusual sender, pattern of declines
   - Persistence: 90+ days typical

---

## Safer Operating Guidance

### Pre-Engagement

1. **Infrastructure preparation**
   - Use dedicated phishing domain with proper SPF/DKIM/DMARC records
   - Organizer email address should align with engagement pretext (e.g., `hr-admin@targetcorp.com` spoofed, or controlled domain `hr-events@similar-domain.com`)
   - Test ICS file in target organization's calendar client (if possible via test account)

2. **Configuration hardening**
   - Keep `config/config.yaml` at `ics_enabled: false` until engagement execution
   - Use `--enable-ics` flag for testing, only edit config file for live campaigns
   - Review `config/config.yaml` before every execution (check domain allowlist matches engagement scope)

3. **Fixture validation**
   - All test campaign JSON files use `example.com` or `test.invalid` addresses
   - Real campaign files stored separately from repository (e.g., encrypted volume)
   - No real victim data in version control

### During Engagement

4. **Generation workflow**
   - Generate ICS in isolated directory (`mkdir -p /secure/engagement-ABC/ics`)
   - Use `--db-path /secure/engagement-ABC/telemetry.db` to isolate database
   - Review generated `.ics` in text editor before deployment:
     - ORGANIZER identity matches pretext
     - DTSTART/DTEND timezone aligns with pretext
     - DESCRIPTION does NOT contain `[DEMO ONLY]` notice
     - ATTENDEE list matches authorized scope

5. **Deployment sequencing**
   - Test ICS with single internal recipient first (your own calendar)
   - Verify invite appearance, RSVP buttons work
   - Gradual rollout (small batch first, monitor for alerts)
   - Document send timestamps for correlation with RSVP telemetry

6. **RSVP monitoring**
   - If using real RSVP tracking (requires webhook receiver, out of scope for lab tool):
     - Secure webhook endpoint with authentication
     - Rate-limit to prevent DoS
     - Log all RSVP events for engagement reporting
   - For lab tool: Simulate expected RSVP distribution to test reporting

### Post-Engagement

7. **Evidence handling**
   - Copy `telemetry.db` to secure client deliverable archive
   - Delete local database: `shred -u telemetry.db` (or equivalent secure delete)
   - Delete generated ICS files: `shred -u output/*.ics`
   - Clear shell history if campaign data appeared in CLI arguments

8. **Cleanup verification**
   - `git status` shows no `telemetry.db` or `.ics` files staged
   - `config/config.yaml` reset to `ics_enabled: false`
   - No real campaign data in `testdata/` directory
   - Scanner outputs refreshed (no engagement-specific findings)

9. **Client deliverable**
   - Provide RSVP report (aggregated counts only, not raw database)
   - Document ORGANIZER identities used (for client's future detection logic)
   - Include OPSEC card (this document) with engagement report

---

## Detection Recommendations

**Target audience:** Blue teams, SOC analysts, mail/calendar gateway administrators

### 1. Mail Gateway — Unusual ICS Characteristics

**Detection logic:**
```
Monitor inbound emails with MIME type "text/calendar" or ICS attachments:
- Single attendee in ATTENDEE field (unusual for legitimate corporate meetings)
- ORGANIZER domain does NOT match sender envelope domain
- METHOD:REQUEST from external sender to internal recipient (no prior relationship)
- Calendar events with very short notice (<2 hours from send to DTSTART)
- DESCRIPTION or LOCATION fields contain tracking URLs (http:// links)
```

**Example query (Splunk/ELK for mail gateway logs):**
```
sourcetype=mail_gateway mime_type="text/calendar" 
| where organizer_domain != sender_domain
| where attendee_count == 1
| stats count by sender_domain, organizer_email
```

**Alert threshold:** 5+ calendar invites from same external domain in 1 hour

### 2. Calendar Gateway — Bulk Calendar Event Creation

**Detection logic:**
```
Monitor calendar item creation events (Exchange transport logs, O365 audit):
- Same ORGANIZER creates 50+ calendar items in <1 hour
- ORGANIZER domain is external, newly registered (<90 days), or low reputation
- Events clustered around same DTSTART time with identical SUMMARY
```

**Example O365 audit query:**
```
Operation:MailItemsAccessed OR Operation:Create
| where ItemClass == "IPM.Appointment"
| summarize count() by Organizer, bin(Timestamp, 1h)
| where count_ > 50
```

**Alert threshold:** 50+ events from single organizer in 1 hour

### 3. User Behavior — Unusual RSVP Patterns

**Detection logic:**
```
Monitor calendar RSVP responses (METHOD:REPLY in mail logs):
- High decline rate (>30%) for single organizer's events
- No historical calendar interaction between organizer and attendees
- RSVP responses immediately after event creation (users suspicious, declining quickly)
```

**Example detection:**
```
sourcetype=exchange_transport 
| where ical_method="REPLY" AND partstat="DECLINED"
| stats count by organizer_email
| where count > 20
```

**Alert threshold:** 20+ declines for same organizer in 24 hours (indicates recipients are suspicious)

### 4. Endpoint — ICS File Downloaded or Opened

**Detection logic:**
```
Monitor endpoint file activity (EDR/Sysmon):
- .ics files written to disk by mail client (Outlook, Thunderbird)
- .ics files opened by calendar application
- Correlation: ICS file download followed by browser navigation (if tracking URL clicked)
```

**Example Sysmon query:**
```
EventID=11 (FileCreate) TargetFilename="*.ics" 
| join ProcessGuid 
  [search EventID=3 (NetworkConnect) DestinationHostname!="*.trustedcorp.com"]
```

**Alert threshold:** ICS file download from external sender + network connection to unexpected domain within 5 minutes

### 5. DNS/Web Proxy — Tracking URL Clicks from Calendar Invites

**Detection logic:**
```
Monitor web proxy/DNS logs for tracking domains embedded in ICS DESCRIPTION:
- URL domains with high entropy (e.g., tracking-1a2b3c4d.phish-domain.com)
- URL paths include recipient identifiers (e.g., /rsvp?id=victim@targetcorp.com)
- Correlation: User opened calendar event, then HTTP request to tracking domain
```

**Example proxy log query:**
```
sourcetype=proxy 
| where url_category="Uncategorized" OR url_category="Newly Registered"
| where url contains "calendar" OR url contains "rsvp" OR url contains "meeting"
| stats count by src_user, dest_domain
```

**Alert threshold:** 10+ users accessing same newly registered domain from calendar-related URLs

### 6. Threat Intelligence — Phishing Domain Correlation

**Detection logic:**
```
Cross-reference ORGANIZER domains with threat intelligence feeds:
- Domain registered recently (<30 days)
- Typosquatting similarities to legitimate corporate domain
- WHOIS privacy protection enabled
- No MX records or SPF configured (send-only domain)
```

**Example TI check:**
```
FOR domain IN organizer_domains:
  IF domain_age < 30 days AND whois_privacy == True:
    ALERT "Suspicious calendar organizer domain"
```

### 7. User Reports — Help Desk Tickets

**Detection logic:**
```
Monitor help desk ticketing systems for keywords:
- "Unexpected meeting invite"
- "Calendar invite from unknown sender"
- "Meeting I didn't schedule"
- Spike in calendar-related tickets (>10/day baseline → >50/day)
```

**Process:** Triage reported calendar invites, extract ORGANIZER domains, block via mail gateway policy.

---

## Residual Gaps

### 1. Real RSVP Tracking Not Implemented

**Gap:** Lab demo uses simulated RSVP fixture data. Real calendar client responses (METHOD:REPLY parsing) require webhook receiver and mail gateway integration, which are out of scope.

**Impact:** Operators cannot measure actual victim engagement (accept/decline rates) without manual mail inspection or additional tooling.

**Recommendation:** For production engagements, implement webhook receiver per `docs/architecture.md` or manually parse RSVP emails.

### 2. GoPhish Integration Not Automated

**Gap:** No GoPhish API client for automated campaign export or ICS attachment upload.

**Impact:** Operator must manually export campaign JSON and attach ICS files to GoPhish templates (multi-step workflow, higher chance of error).

**Recommendation:** Future enhancement: GoPhish API wrapper to automate ICS attachment injection.

### 3. Calendar Client Compatibility Not Exhaustively Tested

**Gap:** ICS generation uses RFC 5545-compliant library, but edge cases (Outlook 2010 vs. 2019, Google Calendar vs. Apple Calendar) may render differently.

**Impact:** Calendar invites may display incorrectly in some clients (e.g., timezone shifts, missing RSVP buttons, ORGANIZER display issues).

**Recommendation:** Operators should test generated ICS in target organization's calendar client before deploying to full recipient list. Create test account in target domain if possible.

### 4. No Built-In Obfuscation or Evasion

**Gap:** Tool generates standards-compliant ICS. No evasion techniques for mail gateway detection (e.g., MIME boundary randomization, header fuzzing).

**Impact:** ICS files may be flagged by advanced mail security gateways that profile calendar invite patterns.

**Recommendation:** This is intentional — the tool focuses on core functionality. Evasion techniques are engagement-specific and should be layered via mail infrastructure (SPF/DKIM alignment, domain reputation warming) rather than ICS manipulation.

### 5. Database Encryption Not Enforced

**Gap:** SQLite `telemetry.db` created with `0600` permissions, but file is not encrypted at rest.

**Impact:** If operator's workstation disk is not encrypted, database contents (victim emails, RSVP data) are readable by forensic tools.

**Recommendation:** Operators must ensure full-disk encryption on systems running this tool. Future enhancement: SQLite encryption extension (SQLCipher) or encrypted volume requirement check.

### 6. No Audit Logging of Tool Usage

**Gap:** Tool does not log who executed ICS generation, when, or for which campaign.

**Impact:** If multiple operators share infrastructure, cannot attribute tool usage to individual operator (complicates incident response if misuse occurs).

**Recommendation:** Operators should implement external audit logging (e.g., redirect CLI output to timestamped log files, centralized syslog).

---

## Review Completeness

**Implementation quality:**  
✅ All PROMPT requirements implemented  
✅ Safety defaults enforced (config + automated tests)  
✅ No placeholder stubs (ICS generation, telemetry, reporting all functional)

**Acceptance criteria:**  
✅ A1-A7, A9-A10 satisfied  
✅ A8 (this OPSEC card) now complete with ≥3 detection recommendations (7 provided)

**Security posture:**  
✅ Lab-safe defaults prevent accidental deployment  
⚠️ Operator discipline required for authorized engagements (cannot automate all safety)

**Detection visibility:**  
✅ Detection Recommendations target defender use cases (mail gateway, calendar logs, user behavior, threat intel)  
✅ Artifacts documented for blue team incident response  

---

**Reviewer verdict:** Tool is suitable for authorized research and red team engagements with proper operational controls. Operators must follow SAFETY_CHECKLIST.md pre-flight procedures and secure evidence handling protocols.
