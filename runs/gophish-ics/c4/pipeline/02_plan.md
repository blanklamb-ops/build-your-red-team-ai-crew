 # gophish-ics Build Plan

## Repository Layout

```
/gophish-ics
  /src
    /gophish-ics
      main.go
      config.go
      email.go
      ics.go
      telemetry.go
    /gophish-api
      client.go
  /tests
    /unit
    /integration
    /acceptance
  /docs
    README.md
    API.md
```

## Work Packages

1. **WP1: GoPhish API Client**
   - Develop a GoPhish API client to interact with the GoPhish server.
   - Dependencies: None

2. **WP2: Email Content Generation**
   - Implement a template-based approach for generating email content.
   - Dependencies: WP1

3. **WP3: ICS Content Generation**
   - Develop a module to generate ICS content based on the email template.
   - Dependencies: WP2

4. **WP4: Telemetry Collection**
   - Implement a module to collect RSVP/calendar response telemetry.
   - Dependencies: WP3

5. **WP5: Integration**
   - Integrate the modules into the GoPhish workflow.
   - Dependencies: WP1, WP2, WP3, WP4

6. **WP6: Documentation**
   - Write documentation for the tool and its API.
   - Dependencies: WP5

## Interface Contracts

- `gophish-api/client.go`: Functions for interacting with the GoPhish API.
- `email.go`: Functions for generating email content.
- `ics.go`: Functions for generating ICS content.
- `telemetry.go`: Functions for collecting telemetry.

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| R1                   | WP2, WP3, WP5 |
| R2                   | WP3           |
| R3                   | WP1, WP5      |
| R4                   | WP2, WP3, WP5 |
| R5                   | WP2, WP3, WP5 |

## Test Plan

- Unit tests: WP1, WP2, WP3, WP4
- Integration tests: WP5
- Acceptance tests: WP5, WP6

## Out of Scope

- Sending mail to real external victims.
- Bypassing mail security products.
- Unauthorized access to sensitive information or violation of privacy policies.

## Assumptions

- A1: GoPhish uses a template-based approach for generating email content.
- A2: There are no existing open-source projects that can be used as a reference for generating ICS content.
- A3: The best approach for integrating the tool with GoPhish is through an API client.