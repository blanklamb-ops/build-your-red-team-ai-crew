 # Domain Brief: After-Action Collector

## Operator Goal

The primary goal of the after-action collector is to create two reports: a client-facing report and an internal learning summary. The tool should ingest at least two log formats and operator decision logs, correlate events with decisions, and render the reports in Markdown or HTML format. The client-facing report should include an executive summary, timeline, findings placeholders, and detection recommendations. The internal learning summary should highlight successes, failures, tool gaps, and reusable TTPs.

## Constraints

- The tool should be platform-agnostic.
- The programming language is not specified, but it should be Python-friendly.
- APIs are not specified; any unknowns will be marked as assumptions.
- The tool should support offline use, as it may not have access to live log shipping during the study.

## Prior Art

- Splunk: A popular log analysis tool that can ingest multiple log formats and correlate events.
- ELK Stack (Elasticsearch, Logstash, Kibana): An open-source data platform for real-time log analysis and visualization.
- Loggly: A cloud-based log management solution that can ingest, parse, and analyze logs in real-time.

## Risks

- **Technical Failure Modes**: Incorrect log parsing, correlation engine failures, or rendering errors.
- **Operational Failure Modes**: Mishandling of sensitive information in the reports, leading to OPSEC failures.

## Open Questions

- The specific format of the operator decision log is not mentioned. Assuming a CSV format with timestamp, decision, rationale, and related asset columns.
- The exact method for PII/secret redaction is not specified. A regex/rules configuration option will be assumed.
- The tool's architecture and data flow are not detailed. Assuming a modular design with separate components for log ingestion, correlation, and reporting.