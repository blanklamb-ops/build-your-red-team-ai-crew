 # After-Action Collector Operational Constraints

## Runtime Environment

1. The tool should be designed to run on a Unix-based operating system.
2. The tool should not require root privileges.
3. The tool should be able to operate in a network-restricted environment.

## Secrets & Evidence Handling

1. The tool should never commit sensitive information, such as log data, to version control.
2. The tool should have a configuration option for PII/secret redaction rules.
3. The OPSEC Reviewer must document the redaction rules and any assumptions made about the log data.

## Operator Workflow

1. The tool should be invoked with a configuration file specifying the log files, operator decision logs, and output format.
2. The tool should have a dry-run mode for testing the configuration and output format without generating reports.

## Safety Defaults

1. The tool should have an allowlist of supported log formats and operator decision log formats.
2. The tool should require explicit confirmation before generating reports.

## Degradation Modes

1. The tool should be able to operate offline, using cached log data and operator decision logs.
2. The tool should handle partial failure gracefully, logging errors and continuing to generate reports for as much data as possible.

## Plan Deltas

1. The Architect must ensure that the log parsers and operator decision log parsers are designed to handle only the supported log formats.
2. The Architect must ensure that the correlation engine is designed to handle only correlated data.
3. The Architect must ensure that the reporting components are designed to handle only the supported output formats.
4. The Architect must ensure that the redaction utility is designed to handle only the supported redaction rules.
5. The Architect must ensure that the tool is designed to handle only the supported configuration options.
6. The Architect must ensure that the tool is designed to handle only the supported command-line arguments.
7. The Architect must ensure that the tool is designed to handle only the supported environment variables.
8. The Architect must ensure that the tool is designed to handle only the supported exit codes.
9. The Architect must ensure that the tool is designed to log all errors and warnings to a log file.
10. The Architect must ensure that the tool is designed to log all configuration options and command-line arguments to a log file.