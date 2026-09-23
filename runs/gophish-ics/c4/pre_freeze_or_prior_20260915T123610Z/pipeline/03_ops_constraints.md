 # gophish-ics Operational Constraints

## Runtime Environment

1. The tool is assumed to run on a Linux-based operating system.
2. The tool requires network access to send and receive ICS messages and RSVP telemetry.
3. The tool should be run with the minimum privileges necessary to perform its functions.

## Secrets & Evidence Handling

1. API keys, passwords, and other sensitive information must never be committed to the repository.
2. The tool should support the use of environment variables or a secure configuration file for sensitive information.
3. The OPSEC Reviewer must document the use of any sensitive information in the OPSEC_CARD.md.

## Operator Workflow

1. The tool should be invoked from the command line.
2. The tool should support a help command that displays usage information.
3. The tool should support a configuration file that allows the operator to customize its behavior.

## Safety Defaults

1. The tool should support a dry-run mode that allows the operator to test its functionality without sending any ICS messages or RSVP telemetry.
2. The tool should support an allowlist that specifies which email addresses are allowed to receive ICS messages.
3. The tool should prompt the operator to confirm any destructive actions before performing them.

## Degradation Modes

1. If the tool is unable to connect to the network, it should continue to operate in a limited capacity, allowing the operator to view and modify its configuration.
2. If the tool is unable to send or receive ICS messages or RSVP telemetry, it should log the errors and continue to operate in a limited capacity.

## Plan Deltas

1. The Architect must ensure that the tool is designed to handle offline/air-gap needs by implementing appropriate fallback mechanisms.
2. The Architect must ensure that the tool is designed to handle unauthorized access or data breaches by implementing appropriate security measures.
3. The Architect must ensure that the tool is documented appropriately by including a README.md file that explains how to install, configure, and use the tool.
4. The Architect must ensure that the tool is tested thoroughly by implementing a comprehensive test plan that includes unit tests, integration tests, and acceptance tests.
5. The Architect must ensure that the tool is integrated with GoPhish as a sidecar application, as specified in the build plan.
6. The Architect must ensure that the tool is designed to handle the ICS format and RSVP telemetry as specified in the build plan and the assumptions.
7. The Architect must ensure that the tool is designed to handle the generation of synthetic data for local lab demo as specified in the build plan and the assumptions.
8. The Architect must ensure that the OPSEC_CARD.md and DETECTION_RECOMMENDATIONS.md are written based on best practices and industry standards, as specified in the build plan and the assumptions.