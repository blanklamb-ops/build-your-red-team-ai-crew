 ## OPSEC Card

   ### 1. Summary

   The `gophish-ics` tool is a Go-based application that augments GoPhish-style phishing campaigns by enabling operators to send ICS/calendar invite style messages, collect RSVP/calendar response telemetry, and maintain lab safety defaults.

   ### 2. Operator Risks

   - **Unauthorized Use:** The tool is intended for authorized use only. Unauthorized use could lead to violation of privacy, data breaches, and legal consequences.
   - **Misconfiguration:** Improper configuration could lead to sending emails to unintended recipients, modifying the GoPhish server incorrectly, or exposing sensitive information.
   - **Network Failures:** The tool does not handle network failures and API errors gracefully, which could lead to data loss or inconsistency.

   ### 3. Artifacts Left Behind

   - **Files:** `config.json`, `email.go`, `ics.go`, `telemetry.go`, `client.go`, `README.md`, `API.md`
   - **Registry:** Depends on the GoPhish API and the operating system
   - **Network:** Outgoing API calls to the GoPhish server, outgoing emails
   - **Browser:** None
   - **Mail:** Outgoing emails with ICS attachments
   - **Logs:** Depends on the GoPhish server and the operating system

   ### 4. Safer Operating Guidance

   - **Configuration:** Ensure that the `config.json` file is properly configured and secure.
   - **Confirmation:** Require explicit confirmation from the operator before sending emails or modifying the GoPhish server.
   - **Error Handling:** Implement graceful handling for network failures and API errors.
   - **Allowlist:** Implement an allowlist of email addresses that the tool can send emails to.
   - **Dry-Run Mode:** Implement a dry-run mode to test the tool's functionality without sending actual emails or modifying the GoPhish server.

   ### 5. Detection Recommendations

   - **Unusual API Calls:** Monitor for unusual API calls to the GoPhish server, especially those that modify the email queue or the server configuration.
   - **ICS Attachments:** Monitor for emails with ICS attachments, especially those that contain suspicious content.
   - **Telemetry Collection:** Monitor for changes in the telemetry store, especially those that occur at unusual times or frequencies.
   - **Configuration Changes:** Monitor for changes to the `config.json` file, especially those that occur outside of normal operating hours or that contain suspicious content.

   ### 6. Residual Gaps

   - **ICS Content Generation:** The extraction of event details from email content and the creation of iCalendar objects are not fully implemented, which could lead to undetected errors or vulnerabilities.
   - **Telemetry Collection:** The opening of the telemetry store, the collection of telemetry data, and the writing of telemetry data to the store are not fully implemented, which could lead to data loss or inconsistency.
   - **GoPhish API Client:** The creation of email objects and the sending of emails using the GoPhish API are not fully implemented, which could lead to undetected errors or vulnerabilities.
   - **Documentation:** The documentation is not fully implemented, which could lead to misunderstandings or misuse of the tool.
   - **Command-Line Interface:** The tool does not have a command-line interface, which could make it difficult to use or automate.
   - **Secrets Handling:** The tool does not have a section on secrets handling methods in the documentation, which could lead to unintentional exposure of sensitive information.
   - **Operator Workflow:** The tool does not have a section on operator workflow in the documentation, which could lead to misunderstandings or errors.