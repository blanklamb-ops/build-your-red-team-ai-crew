 ### FILE: OPSEC_CARD.md

```markdown
# OPSEC Card for gophish-ics

## Summary

gophish-ics is a tool that extends GoPhish to support the delivery of ICS/calendar invite-style messages as a campaign content path. It collects RSVP/calendar response telemetry into campaign reporting and maintains clear lab safety defaults.

## Operator Risks

- Unintended exposure of sensitive information: The tool uses SMTP server credentials and an email allowlist, which can be accidentally exposed if not handled securely.
- Misconfiguration: The tool can be misconfigured, leading to unintended behavior or exposure of sensitive information.
- Unauthorized access: If the tool is not properly secured, it can be accessed by unauthorized users.

## Artifacts Left Behind

- Log files: The tool logs its activity, which can contain sensitive information.
- Configuration files: The tool uses a configuration file that contains sensitive information.
- Network traffic: The tool sends and receives ICS messages and RSVP telemetry, which can be intercepted.

## Safer Operating Guidance

- Use environment variables or a secure configuration file to handle sensitive information.
- Follow the principle of least privilege when running the tool.
- Regularly review and update the tool's configuration file.
- Monitor the tool's logs for any suspicious activity.
- Use a secure network connection when sending and receiving ICS messages and RSVP telemetry.

## Detection Recommendations

1. Monitor for unusual activity in the SMTP logs, such as a large number of outgoing ICS messages or RSVP telemetry.
2. Monitor for suspicious ICS messages or RSVP telemetry, such as those with missing or invalid fields.
3. Monitor for changes to the configuration file, such as enabling the ICS feature or modifying the allowlist.
4. Monitor for suspicious activity in the command line logs, such as attempts to invoke the tool with invalid arguments or options.
5. Monitor for changes to the tool's source code, such as those made by unauthorized users.

## Residual Gaps

- The tool's security measures are not exhaustive, and there may be other ways to compromise the tool that were not identified during this review.
- The tool's detection recommendations are not exhaustive, and there may be other ways to detect the tool's activity that were not identified during this review.
```