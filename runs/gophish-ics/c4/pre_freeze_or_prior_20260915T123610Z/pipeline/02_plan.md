 # gophish-ics Build Plan

## Repository Layout

```
/gophish-ics
  /src
    /gophish-ics
      main.go
      /ics
        ics_generator.go
        rsvp_handler.go
      /reporting
        telemetry_processor.go
        report_generator.go
      /utils
        synthetic_data_generator.go
  /docs
    OPSEC_CARD.md
    DETECTION_RECOMMENDATIONS.md
  /tests
    /unit
    /integration
    /acceptance
  README.md
```

## Work Packages

1. **WP1: ICS Content Generator**
   - Tasks: Implement ICS message generator, RSVP handler
   - Dependencies: None
2. **WP2: Telemetry Processing**
   - Tasks: Implement RSVP telemetry processor, report generator
   - Dependencies: WP1
3. **WP3: Utilities**
   - Tasks: Implement synthetic data generator
   - Dependencies: None
4. **WP4: Documentation**
   - Tasks: Write OPSEC_CARD.md, DETECTION_RECOMMENDATIONS.md
   - Dependencies: WP1, WP2, WP3

## Interface Contracts

- `ics_generator.go`:
  - `GenerateICS(event) string`: Generates an ICS message from an event object
  - `HandleRSVP(rsvp)`: Handles an RSVP message
- `rsvp_handler.go`:
  - `ProcessRSVP(rsvp)`: Processes an RSVP message
- `telemetry_processor.go`:
  - `AddTelemetry(telemetry)`: Adds telemetry data to the processor
  - `GenerateReport() string`: Generates a report from the telemetry data
- `report_generator.go`:
  - `GenerateReport(data) string`: Generates a report from data
- `synthetic_data_generator.go`:
  - `GenerateData(size) []data`: Generates synthetic data of a given size

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PROMPT-1              | WP1           |
| PROMPT-2              | WP2           |
| PROMPT-3              | WP3           |
| PROMPT-4              | WP4           |

## Test Plan

- Unit tests for all functions in `/src`
- Integration tests for the ICS message generation and RSVP handling
- Acceptance tests for the full functionality of the tool, including offline/air-gap support and lab safety defaults

## Out of Scope

- Detailed design and implementation of the GoPhish UI/UX
- Extensive testing beyond the scope of the acceptance tests
- Any features not explicitly mentioned in the PROMPT

## Assumptions

- The ICS format will be implemented using the iCalendar RFC (https://tools.ietf.org/html/rfc5545)
- The RSVP telemetry will be handled using the iTIP RFC (https://tools.ietf.org/html/rfc5323)
- The tool will be integrated as a sidecar application to GoPhish
- The synthetic data generator will generate random data for testing purposes
- The OPSEC_CARD.md and DETECTION_RECOMMENDATIONS.md will be written based on best practices and industry standards