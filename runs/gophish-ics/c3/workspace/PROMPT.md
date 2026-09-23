# PROMPT — gophish-ics

**Tool slug:** `gophish-ics`  
**Authorized use only** — see `ethics/AUTHORIZED_USE.md`.

## Operator goal

Augment or wrap [GoPhish](https://github.com/gophish/gophish)-style phishing campaign workflows so authorized operators can:

- deliver **ICS/calendar invite** style messages as a campaign content path  
- collect **RSVP / calendar response telemetry** into campaign reporting  
- keep clear lab safety defaults (explicit enable flags, synthetic data fixtures)

Do not assume a fork is mandatory — a sidecar integration is acceptable if documented.

## Requirement IDs

| ID | Requirement |
|----|-------------|
| R1 | Documented integration approach (fork vs sidecar vs API client) with architecture diagram or equivalent |
| R2 | ICS/iCal content generator from campaign fields (organizer, summary, dtstart/dtend, description, attendees placeholders) |
| R3 | Valid `.ics` output that opens in at least one common calendar client **or** passes an ICS linter/tests in CI |
| R4 | RSVP/telemetry path: record responses (accept/decline/tentative/none) keyed to campaign recipient ID |
| R5 | Dashboard or CLI report: per-campaign RSVP counts |
| R6 | Feature flag / config to disable ICS path entirely. The checked-in/shipped configuration must set it to **false**. Automated tests must read the actual shipped config and prove generation is blocked by default; demos may use a temporary override but must not modify or leave the shipped default enabled. |
| R7 | Seed data + instructions for local lab demo without real victim mailboxes |
| R8 | `OPSEC_CARD.md` with Detection Recommendations (mail + calendar gateway angles) |
| R9 | README + authorized-use notice |
| R10 | Scanner outputs archived |

## Non-goals

- Sending mail to real external victims from this research harness  
- Bypassing mail security products as a stated feature  

## Success

Passes `ACCEPTANCE.md` using local/lab fixtures only.
