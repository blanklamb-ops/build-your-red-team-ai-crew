# Domain Brief — gophish-ics

## Goal restatement

Deliver a local, authorized-research sidecar that turns synthetic campaign and recipient fields into standards-conformant iCalendar invitations, refuses to generate them under the shipped disabled configuration, records RSVP states against stable campaign-recipient identifiers, and reports per-campaign counts. Success is an offline demo and executable acceptance workflow; transmitting mail or changing GoPhish itself is unnecessary.

## Constraints and assumptions

- Scope is a lab harness: no external delivery, real mailboxes, credential capture, or security-product bypass. Checked-in fixtures must use reserved/synthetic domains.
- Prefer a sidecar and CLI over a GoPhish fork: it minimizes coupling and still permits attachment creation and result correlation. GoPhish templates support attachments, while its documented campaign API exposes results/timeline and stable result identifiers ([template API](https://github.com/gophish/python-api-documentation/blob/master/templates.md), [campaign API](https://docs.getgophish.com/api-documentation/campaigns)).
- Assume Python 3 and its standard library are present. Avoid network-dependent runtime packages so generation, validation tests, telemetry, reporting, and demo work air-gapped.
- Treat fixture timestamps as RFC 3339/ISO 8601 values with explicit `Z` or numeric offsets; reject naive local timestamps. Normalize emitted event times to UTC.
- The shipped YAML configuration is simple enough for a narrowly validated loader without adding a YAML dependency. Tests must load that exact file and preserve it byte-for-byte.
- RSVP ingestion is a controlled CLI/API-like sidecar boundary, not direct inbound-email parsing. It accepts only `accept`, `decline`, `tentative`, or `none` and keys records by campaign ID plus recipient ID.
- Serena is unavailable in the provided toolset, so it is not used.

## Prior art and interfaces

- **iCalendar (RFC 5545):** the transport-independent calendar representation, including `VCALENDAR`, `VEVENT`, content-line folding/escaping, `UID`, `DTSTAMP`, `DTSTART`, `DTEND`, `ORGANIZER`, and `ATTENDEE`. RFC 5545 explicitly supports exchange over SMTP, HTTP, or files ([RFC 5545](https://datatracker.ietf.org/doc/html/rfc5545)). Emit CRLF line endings, UTF-8, and folded content lines.
- **iTIP (RFC 5546):** defines scheduling semantics such as organizer `METHOD:REQUEST`, attendee `METHOD:REPLY`, and participation states ([RFC 5546](https://datatracker.ietf.org/doc/html/rfc5546)). The sidecar generates requests and models reply state without pretending to be a full calendar transport agent.
- **GoPhish:** campaigns have recipient results and a timeline; results can be fetched from `/api/campaigns/:id/results`. Optional signed webhooks push campaign events, providing future integration points without inventing a new GoPhish endpoint ([campaign API](https://docs.getgophish.com/api-documentation/campaigns), [webhooks](https://docs.getgophish.com/user-guide/documentation/webhooks)).
- **SQLite:** Python's standard-library driver provides a local transactional telemetry store and deterministic aggregate queries. The schema should enforce allowed RSVP values and a unique campaign/recipient key.

## Risks and mitigations

- **Calendar incompatibility:** malformed escaping, folding, MIME expectations, or ambiguous dates may make clients ignore an invite. Use strict serialization, UTC times, CRLF, deterministic automated parsing/validation tests, and document that client-specific MIME delivery is outside this harness.
- **Identity drift:** using email as the key breaks when addresses change and can misattribute events. Require stable recipient IDs and preserve an event history while maintaining latest state.
- **Duplicate/out-of-order replies:** retries or delayed replies can distort counts. Store immutable events with timestamps and use the most recently recorded state as the recipient's current state; define deterministic tie ordering.
- **Unsafe enablement:** a demo could silently leave generation enabled. Keep `config/default.yaml` false, require an explicit temporary override, and have tests hash/read the shipped file before and after demo execution.
- **Injection/data leakage:** unescaped newlines could inject iCalendar properties, and fixtures/logs could expose personal data. Escape all text/parameter values, reject control characters in identifiers/addresses, use synthetic fixtures, and avoid logging invite bodies by default.
- **Unavailable dependencies:** GoPhish, SMTP, calendar clients, or scanners may be absent. Core demo remains offline; document sidecar handoff/failure modes. Static scanner artifacts are archived controlled inputs/results, not replaced or installed during generation.

## Planning blockers

None. Assumptions above select a standard-library Python CLI sidecar, SQLite telemetry, fixture-driven tests, and archived scanner outputs. A real GoPhish deployment may later map its result ID directly to `recipient_id` and attach generated bytes through the documented template attachment interface, but that live adapter is not required for the local acceptance scope.
