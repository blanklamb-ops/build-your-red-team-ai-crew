 # gophish-ics Domain Brief

## Operator Goal

The goal of the `gophish-ics` tool is to augment or wrap GoPhish-style phishing campaign workflows. The tool should enable authorized operators to deliver ICS/calendar invite style messages, collect RSVP/calendar response telemetry, and maintain lab safety defaults.

## Constraints

- The tool should be integrated with GoPhish, either through a fork, sidecar, or API client approach.
- The tool should be developed using the same programming language as GoPhish.
- The tool should not send mail to real external victims from this research harness.
- The tool should not bypass mail security products as a stated feature.

## Prior Art

- GoPhish (https://github.com/gophish/gophish): An open-source phishing tool that can be used as a reference for the integration approach.
- ICS (iCalendar) format: The ICS format is widely used for calendar invites. Understanding the format and its limitations is crucial for the tool's development.
- Calendar clients: The tool should be compatible with at least one common calendar client to ensure the ICS content can be opened and interpreted correctly.

## Risks

- **Technical Failure Modes**: Incorrect implementation of the ICS format, compatibility issues with calendar clients, and bugs in the integration approach could lead to the tool failing to generate valid ICS content or collect telemetry.
- **Operational Failure Modes**: Misuse of the tool could lead to unauthorized access to sensitive information or violation of privacy policies.

## Open Questions

- **Q1**: What is the current approach of GoPhish for handling email content? (Assumption: GoPhish uses a template-based approach for generating email content.)
- **Q2**: Are there any existing open-source projects that can be used as a reference for generating ICS content?
- **Q3**: What is the best approach for integrating the tool with GoPhish (fork, sidecar, or API client)?