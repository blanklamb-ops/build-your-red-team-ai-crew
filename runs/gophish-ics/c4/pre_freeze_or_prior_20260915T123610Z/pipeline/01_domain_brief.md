 # gophish-ics Domain Brief

## Operator Goal Restatement

The goal is to enhance or extend the functionality of GoPhish, a popular open-source phishing tool, to support the delivery of ICS/calendar invite-style messages as a campaign content path. This enhancement should also collect RSVP/calendar response telemetry into campaign reporting and maintain clear lab safety defaults.

## Constraints

- The platform is assumed to be the same as GoPhish, which is written in Go.
- The language is Go.
- APIs used in GoPhish may be leveraged, but unknowns should be marked as assumptions.
- The tool should support offline/air-gap needs, but this is not explicitly stated.

## Prior Art

- GoPhish: An existing open-source project that the tool will be built upon. (URL: https://github.com/gophish/gophish)
- ICS (Internet Calendaring and Scheduling) format: A standard method for exchanging calendar information. It is used for sharing and exchanging events on the internet. (No specific URL provided)

## Risks

- **Technical Failure Modes**: Incorrect implementation of ICS format or handling of RSVP telemetry could lead to data loss or misinterpretation.
- **Operational Failure Modes**: Misuse of the tool could lead to unauthorized access or data breaches. Lack of proper documentation could also cause confusion or errors in usage.

## Open Questions

- The exact approach for integration (fork vs sidecar vs API client) is not clear.
- The specific requirements for the ICS content generator and RSVP/telemetry path are not fully defined.
- The exact method for generating synthetic data fixtures for local lab demo is not specified.
- The specific requirements for the OPSEC_CARD.md and Detection Recommendations are not fully detailed.