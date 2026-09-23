 ### FILE: OPSEC_CARD.md

# Empire-Advisor OPSEC Card

## Summary
Empire-Advisor is a tool that intercepts and scores operator commands in a lab Empire-like interface. It suggests documented alternative commands from a local knowledge base and keeps humans in control by never auto-executing alternatives.

## Operator Risks
- **Unintended Command Execution:** The interceptor module may modify commands unintentionally, leading to unintended actions.
- **Reliance on Local Knowledge Base:** The suggestion engine relies on a local knowledge base, which may not be up-to-date or comprehensive.
- **Scoring Engine Misconfiguration:** The scoring engine may misinterpret commands due to incorrect or outdated rules.
- **Insufficient Testing:** The tool may contain undiscovered vulnerabilities or bugs due to insufficient testing.

## Artifacts Left Behind
- **Log Files:** The tool may leave log files containing information about intercepted commands and their scores.
- **Configuration Files:** The tool may leave configuration files containing sensitive information.
- **Temporary Files:** The tool may leave temporary files containing intercepted commands.
- **Network Traffic:** The tool may generate network traffic when communicating with external systems.

## Safer Operating Guidance
- **Secure Configuration Files:** Ensure that configuration files are stored securely and are not accessible to unauthorized users.
- **Regular Updates:** Keep the local knowledge base and scoring engine rules up-to-date.
- **Thorough Testing:** Test the tool thoroughly before using it in a production environment.
- **Monitor Log Files:** Monitor log files for any suspicious activity.

## Detection Recommendations
1. **Monitor for Unusual Command Patterns:** Analyze command patterns for any deviations from the norm.
2. **Monitor for Changes in Command Frequency:** Detect any significant changes in the frequency of commands being executed.
3. **Monitor for Changes in Command Success Rates:** Monitor command success rates for any unusual patterns.
4. **Monitor for Changes in Log File Activity:** Detect any unusual changes in log file activity.
5. **Monitor for Changes in Network Traffic:** Analyze network traffic for any unusual patterns.

## Residual Gaps
- The exact mechanism for offline mode operation is not clear.
- The tool's capabilities and limitations are not clearly documented for operators.
- The tool's safety defaults are not clearly defined.
- The tool's degradation modes are not clearly defined.
- The tool's documentation is not comprehensive.
- The tool's tests are not comprehensive.
- The tool's interface contracts are not documented.
- The tool's requirements trace matrix is not provided.
- The tool's test plan is not provided.
- The tool's assumptions are not documented.
- The tool's out-of-scope items are not documented.
- The tool's runtime environment is not clearly defined.
- The tool's secrets and evidence handling is not clearly defined.
- The tool's operator workflow is not clearly defined.
- The tool's plan deltas are not clearly defined.