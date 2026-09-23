 ### FILE: OPSEC_CARD.md

   # OPSEC Card for After-Action Collector

   ## Summary

   The After-Action Collector is a tool designed to ingest, correlate, and report on engagement logs and operator decisions. It supports the ingestion of JSON and CSV files, and the generation of reports in Markdown and PDF formats.

   ## Operator Risks

   - **Unauthorized Access:** The tool is not designed to handle sensitive data without proper encryption and access controls. Unauthorized access to the tool could result in the exposure of sensitive data.
   - **Modification of Source Code:** Modifying the source code could introduce vulnerabilities or backdoors into the tool.
   - **Data Exfiltration:** The tool does not currently have built-in data redaction or anonymization capabilities. If used with sensitive data, it could potentially be used to exfiltrate that data.

   ## Artifacts Left Behind

   - **Files:** The tool reads and writes files, including JSON and CSV logs, Markdown and PDF reports, and source code files.
   - **Registry:** The tool does not interact with the system registry.
   - **Network:** The tool does not make network connections.
   - **Browser:** The tool does not interact with the browser.
   - **Mail:** The tool does not interact with email.
   - **Logs:** The tool does not currently have a built-in logging mechanism.

   ## Safer Operating Guidance

   - **Data Handling:** Ensure that the tool is used with properly anonymized and redacted data.
   - **Source Code Modification:** Avoid modifying the source code unless absolutely necessary.
   - **Access Controls:** Ensure that the tool is used in a secure environment with appropriate access controls.

   ## Detection Recommendations

   1. **File Access Monitoring:** Monitor for unusual file access patterns, especially in the `src/` and `tests/` directories. This could indicate an attempt to modify the source code or exfiltrate data.
   2. **Source Code Modification:** Monitor for attempts to modify the source code files. This could indicate an attempt to introduce vulnerabilities or backdoors into the tool.
   3. **Data Exfiltration:** Monitor for attempts to exfiltrate data from the tool. This could be done by monitoring for attempts to write large amounts of data to files, or by monitoring for attempts to send data over the network.

   ## Residual Gaps

   - **Incomplete Implementation:** The `src/correlate/correlate.py`, `src/report/markdown_report.py`, `src/report/pdf_report.py`, `src/utils/utils.py`, and `src/decision_log.py` modules are not currently implemented. This could leave the tool vulnerable to certain types of attacks or data leaks.
   - **Lack of Logging:** The tool does not currently have a built-in logging mechanism. This could make it more difficult to detect and respond to security incidents.