# Domain Brief — gophish-ics

**Pipeline step:** 1/5  
**Role:** Domain Researcher

## Goal restatement

Enable authorized phishing operators to send calendar invite (ICS) payloads through GoPhish campaigns and track victim responses (accept/decline/tentative) as campaign telemetry. Success means operators can add calendar-based social engineering to their engagement toolkit while maintaining lab safety defaults that prevent accidental live deployment.

## Constraints

**Platform:**
- GoPhish is Go-based, open-source phishing framework (https://github.com/gophish/gophish)
- Core architecture: HTTP API, SQLite/MySQL storage, template-driven email campaigns
- Options: fork GoPhish (full control, maintenance burden) OR sidecar integration (lower coupling, limited hooks into reporting UI)

**Technical:**
- Must generate RFC 5545-compliant iCalendar format (`.ics` files)
- ICS must work with common calendar clients (Outlook, Google Calendar, Apple Calendar)
- RSVP telemetry requires webhook/callback mechanism (iCal supports PARTSTAT changes, but actual response tracking depends on mail/calendar gateway implementation)
- GoPhish already tracks email opens and link clicks — RSVP telemetry should align with existing event schema

**Safety:**
- Configuration must default to ICS generation DISABLED
- Test data must use RFC 5737/2606 reserved addresses (example.com, test.invalid)
- No live SMTP sending from test harness

## Prior art

**iCalendar format:**
- RFC 5545 (Internet Calendaring and Scheduling Core Object Specification): https://datatracker.ietf.org/doc/html/rfc5545
- RFC 6047 (iTIP - iCalendar Transport-Independent Interoperability Protocol): https://datatracker.ietf.org/doc/html/rfc6047
- Key properties: VEVENT, DTSTART/DTEND, ORGANIZER, ATTENDEE, METHOD (REQUEST for invites)

**Go ICS libraries:**
- `github.com/arran4/golang-ical` — popular library with 200+ stars, actively maintained
- `github.com/emersion/go-ical` — RFC-compliant parser/generator from ProtonMail ecosystem

**GoPhish integration points:**
- Template system already supports custom MIME parts and attachments
- Campaign results stored in `events` and `results` tables
- Webhook support exists for notification callbacks
- `/api/campaigns/{id}/results` returns recipient-level tracking

**RSVP tracking challenges:**
- True RSVP responses require mail server cooperation (PARTSTAT in iCal replies)
- Alternatives: (1) embed tracking URLs in ICS DESCRIPTION field, (2) webhook receiver for calendar gateway callbacks, (3) mailbox monitoring (complex, out of scope)
- **ASSUMPTION:** For lab demo, simulate RSVP responses via API or fixture data rather than relying on real calendar client behavior

## Risks

**Technical:**
- ICS timezone handling is notoriously error-prone (VTIMEZONE blocks vs TZID references)
- Calendar client compatibility varies — Outlook interprets some fields differently than RFC-compliant clients
- GoPhish template rendering may escape/corrupt ICS MIME boundaries if not carefully handled
- RSVP webhook endpoint becomes new attack surface if not secured

**Operational:**
- Misconfigured "disabled" flag could deploy ICS payloads to real targets
- Calendar invites may bypass some email security filters that catch traditional phishing
- Operators unfamiliar with calendar artifacts may leave forensic traces (meeting organizer identity, timezone leakage)

**Detection:**
- Unusual ICS characteristics (single attendee, suspicious ORGANIZER domain, tracking URLs in DESCRIPTION)
- Mail gateway logs showing MIME multipart/alternative with text/calendar
- Calendar accept/decline replies to non-existent organizer addresses

## Open questions

**Q1:** Does GoPhish's template system support multipart/alternative MIME construction with text/calendar part?  
**ASSUMPTION:** Yes, via custom HTML templates or attachment mechanism. If not, sidecar approach sends ICS as attachment fallback.

**Q2:** What storage schema for RSVP events — extend existing GoPhish `events` table or separate tracking DB?  
**ASSUMPTION:** Add `event_details` JSONB column to existing events table with `{rsvp_status: "accepted|declined|tentative"}` to minimize schema changes.

**Q3:** Lab demo without live calendar clients — use test harness or manual ICS file inspection?  
**ASSUMPTION:** Provide (1) automated ICS validation via library parser, (2) instructions to import `.ics` into local calendar app for manual verification, (3) fixture data for RSVP simulation.

## Sources

- RFC 5545: https://datatracker.ietf.org/doc/html/rfc5545
- GoPhish documentation: https://docs.getgophish.com/
- golang-ical library: https://github.com/arran4/golang-ical
- GoPhish webhook API: https://github.com/gophish/gophish/wiki/Webhooks

---

**Word count:** ~620  
**Next step:** Planner converts this into executable work packages.
