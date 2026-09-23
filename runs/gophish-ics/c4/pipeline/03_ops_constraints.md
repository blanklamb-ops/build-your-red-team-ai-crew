 # gophish-ics Operational Constraints

## Runtime Environment

1. The tool should run on a Linux-based operating system.
2. The tool should have the necessary privileges to send emails and interact with the GoPhish server.
3. The tool should have outbound network access to the GoPhish server and any external email servers.

## Secrets & Evidence Handling

1. API keys, passwords, and other sensitive information should never be committed to the repository.
2. The tool should use a secure method for storing and accessing secrets.
3. The OPSEC Reviewer must document the tool's secrets handling methods in the security documentation.

## Operator Workflow

1. The tool should be invoked through a command-line interface.
2. The operator should be able to configure the tool using a configuration file.
3. The tool should provide clear and concise output during operation.

## Safety Defaults

1. The tool should have a dry-run mode that allows the operator to test the tool without sending emails or modifying the GoPhish server.
2. The tool should have an allowlist of email addresses that it can send emails to.
3. The tool should require explicit confirmation from the operator before sending emails or modifying the GoPhish server.

## Degradation Modes

1. If the tool loses network connectivity, it should continue to operate in a limited capacity.
2. If the tool encounters an error while sending an email or modifying the GoPhish server, it should log the error and continue to operate.
3. If the tool encounters an error while generating ICS content or collecting telemetry, it should log the error and continue to operate.

## Plan Deltas

1. The Architect must ensure that the GoPhish API client is developed to handle network failures and API errors gracefully.
2. The Architect must ensure that the tool's secrets handling methods are secure and comply with industry standards.
3. The Architect must ensure that the tool's operator workflow is intuitive and easy to use.
4. The Architect must ensure that the tool's safety defaults are implemented and documented.
5. The Architect must ensure that the tool's degradation modes are tested and documented.
6. The Architect must ensure that the tool's documentation includes a section on operational constraints and safety defaults.