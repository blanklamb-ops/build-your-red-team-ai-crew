 ### FILE: OPSEC_CARD.md

   # OPSEC Card for After-Action Collector

   ## Summary
   The After-Action Collector is a tool designed to ingest log data from JSON and CSV files, correlate events with decisions made during engagements, and generate client and internal reports. The tool is not fully implemented, and it currently operates in offline mode, ingesting logs from the local file system.

   ## Operator Risks
   - **Mishandling of client reports:** Reveals sensitive information about the engagement, such as the operator's thought process and strategy.
   - **Mishandling of internal reports:** Reveals tool gaps and reusable TTPs, potentially compromising future engagements.
   - **Mishandling of operator decision logs:** Reveals the operator's thought process and strategy, which could be used by defenders to improve their defenses.
   - **Mishandling of PII/secret redaction rules:** Exposure of sensitive information in the reports.
   - **Mishandling of log data:** Unintended exposure of log data, which could contain sensitive information about the engagement.

   ## Artifacts Left Behind
   - **Files:** The tool creates no new files on the operator's system. However, it reads from and potentially modifies log files and configuration files.
   - **Registry:** Not applicable.
   - **Network:** The tool does not transmit data over the network.
   - **Browser:** Not applicable.
   - **Mail:** Not applicable.
   - **Logs:** The tool does not log errors and warnings to a secure log file.

   ## Safer Operating Guidance
   - **Defaults:** Ensure that the tool is configured to use secure defaults, such as encrypted communication channels and secure log files.
   - **Sequencing:** Operate the tool in a secure environment, such as an air-gapped system, to minimize the risk of data exfiltration.
   - **Evidence handling:** Handle log data with care to minimize the risk of data loss or corruption.

   ## Detection Recommendations
   - **Monitor file access:** Monitor access to log files and configuration files to detect unauthorized access or modification.
   - **Monitor network traffic:** Monitor network traffic to detect unauthorized data transmission.
   - **Monitor log files:** Monitor log files for errors and warnings that could indicate misuse of the tool.
   - **Monitor system resources:** Monitor system resources to detect resource exhaustion or other signs of misuse.

   ## Residual Gaps
   - The tool does not log errors and warnings to a secure log file, which makes it difficult to detect misuse.
   - The tool does not prompt the operator to confirm that they want to proceed with the operation, which could lead to unintended data modification.
   - The tool does not handle the expected format of the operator decision log and PII/secret redaction rules, which could lead to data corruption or loss.
   - The tool does not handle large volumes of log data by processing the data in chunks, which could lead to resource exhaustion.
   - The tool does not support rendering the client report in PDF or HTML, which could limit its usability.
   - The tool does not include a fixture engagement pack under `testdata/`, which could make it difficult to test the tool's functionality.