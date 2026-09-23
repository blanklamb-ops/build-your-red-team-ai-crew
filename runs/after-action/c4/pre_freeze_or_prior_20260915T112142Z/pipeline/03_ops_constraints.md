 # Operational Constraints for After-Action Collector

## Runtime Environment Assumptions

- The tool will be run on a Linux-based operating system.
- The tool will require sufficient privileges to read and write to the file system and network access to ingest logs.
- The tool will assume a stable network connection during operation.

## Secrets & Evidence Handling

- The tool will not commit any secrets or evidence to the repository.
- The operator decision log and PII/secret redaction rules will be stored securely and not committed to the repository.
- The tool will log all errors and warnings to a secure log file.
- The OPSEC Reviewer must document the secure storage and handling of the operator decision log and PII/secret redaction rules.

## Operator Workflow

- The tool will be invoked by the operator using a command-line interface.
- The operator will provide the paths to the log files, operator decision log, and PII/secret redaction rules as arguments to the tool.
- The tool will output the client report and internal learning summary to the file system.

## Safety Defaults

- The tool will have a dry-run mode that allows the operator to preview the output of the tool without making any changes to the data.
- The tool will have an allowlist of supported log formats that the operator can use to ensure that the tool can handle the log data.
- The tool will prompt the operator to confirm that they want to proceed with the operation before making any changes to the data.

## Degradation Modes

- If the tool is unable to establish a network connection, it will operate in offline mode and ingest logs from the local file system.
- If the tool is unable to correlate events or decisions, it will log the errors and continue processing the data.
- If the tool is unable to render a report, it will log the errors and output the data in a structured format.
- If the tool is unable to redact PII/secrets, it will log the errors and output the report as is.

## Plan Deltas

- The Architect must ensure that the tool can handle the expected format of the operator decision log and PII/secret redaction rules.
- The Architect must ensure that the tool can handle large volumes of log data by processing the data in chunks.
- The Architect must ensure that the tool can operate in offline mode and ingest logs from the local file system.
- The Architect must ensure that the tool can log all errors and warnings to a secure log file.
- The Architect must ensure that the tool can operate in dry-run mode and prompt the operator to confirm that they want to proceed with the operation.
- The Architect must ensure that the tool can output the data in a structured format if it is unable to render a report.
- The Architect must ensure that the tool can log errors if it is unable to redact PII/secrets.