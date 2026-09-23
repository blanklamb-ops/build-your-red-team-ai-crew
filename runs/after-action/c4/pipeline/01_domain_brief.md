 # Domain Brief: After-Action Collector

## Operator Goal

The After-Action Collector is designed to create two reports: a client-facing report and an internal learning summary. The tool ingests various log formats and operator decision logs, correlates events with decisions, and generates the required reports.

## Constraints

- The tool should support ingesting at least two log formats (e.g. JSON lines + CSV) via adapters.
- The tool should support offline/air-gap needs as it's a post-engagement tool.
- The tool should be platform-agnostic and written in a language that is widely supported and secure.
- The tool should not require live log shipping from production client networks during the study.

## Prior Art

- There are no known open projects that exactly match the requirements of the After-Action Collector.
- However, there are similar tools available in the market that can be used as references. For example, [Splunk](https://www.splunk.com/) and [LogRhythm](https://logrhythm.com/) have features for log correlation and reporting.

## Risks

- **Technical Failure Modes:** Incorrect implementation of log ingestion, correlation, and reporting mechanisms could lead to inaccurate or misleading results.
- **Operational Failure Modes:** Mishandling of reports could lead to OPSEC failures. This risk can be mitigated by including a PII/secret redaction pass and an OPSEC card in the tool.

## Open Questions

- The specific log formats to be supported are not mentioned. Assuming that the formats are known and documented, we can proceed with the development of the log ingestion adapters.
- The operator decision log format is not specified. Assuming a structured format (e.g. JSON or CSV), we can design the ingestion mechanism.
- The correlation engine's time window and asset key are not defined. Assuming a reasonable time window (e.g. 5 minutes) and a unique asset key, we can implement the correlation engine.
- The specific requirements for the client report renderer and the internal learning renderer are not detailed. Assuming a professional and non-jargony tone for the client report and a structured format for the internal learning summary, we can design the renderers.