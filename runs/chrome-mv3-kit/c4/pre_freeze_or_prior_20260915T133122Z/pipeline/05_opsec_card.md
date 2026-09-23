 ## OPSEC Card

### 1. Summary

Chrome-MV3-Kit is a Chrome Manifest V3 extension that records metadata about browser authentication HTTP flows in a local lab and generates an operator-ready Evilginx 2.3.0-format phishlet `.yaml`.

### 2. Operator Risks

- Unintentionally capturing sensitive data during data capture.
- Generating a phishlet without properly configuring it, which may lead to ineffective or malfunctioning phishing campaigns.
- Inadequate handling of optional host permissions may result in the tool not functioning as intended.
- Inadequate handling of non-HTTP(S) URLs may lead to data loss or incorrect analysis.

### 3. Artifacts Left Behind

- Generated phishlets in Evilginx 2.3.0 format.
- Static HTML snapshots of lab pages.
- HTTP traffic patterns derived from observed URL patterns.
- Optional host permissions configured by the operator.
- Data captured during authentication flows.

### 4. Safer Operating Guidance

- Ensure that the tool is used in a controlled and secure lab environment.
- Configure optional host permissions carefully and only grant them to trusted origins.
- Handle non-HTTP(S) URLs with caution and only when necessary.
- Review and validate generated phishlets before using them in a phishing campaign.
- Securely store and handle captured data.

### 5. Detection Recommendations

1. Monitor for unusual network traffic patterns, such as a large number of requests to authentication endpoints.
2. Monitor for the presence of Evilginx 2.3.0-format phishlets in the lab environment.
3. Monitor for the presence of static HTML snapshots of lab pages in the lab environment.
4. Monitor for the presence of optional host permissions configured by the Chrome-MV3-Kit extension.
5. Monitor for the presence of data captured by the Chrome-MV3-Kit extension during authentication flows.

### 6. Residual Gaps

- The tool's ability to handle multi-origin navigations and requests was not explicitly tested.
- The tool's ability to handle service worker suspension or restart was not explicitly tested.
- The tool's ability to handle non-HTTP protocols was not explicitly tested.
- The tool's ability to handle non-text data was not explicitly tested.
- The tool's ability to handle real-time data capture and analysis was not implemented.
- The tool's ability to handle cloud-based data storage and synchronization was not implemented.
- The tool's ability to handle multi-user environments was not tested.
- The tool's ability to comply with specific regulatory frameworks was not explicitly tested.

### FILE: OPSEC_CARD.md

```markdown
# Chrome-MV3-Kit OPSEC Card

## Summary

Chrome-MV3-Kit is a Chrome Manifest V3 extension that records metadata about browser authentication HTTP flows in a local lab and generates an operator-ready Evilginx 2.3.0-format phishlet `.yaml`.

## Operator Risks

- Unintentionally capturing sensitive data during data capture.
- Generating a phishlet without proper configuration.
- Inadequate handling of optional host permissions.
- Inadequate handling of non-HTTP(S) URLs.

## Artifacts Left Behind

- Generated phishlets.
- Static HTML snapshots.
- HTTP traffic patterns.
- Optional host permissions.
- Captured data.

## Safer Operating Guidance

- Use in a controlled lab environment.
- Carefully configure optional host permissions.
- Handle non-HTTP(S) URLs with caution.
- Review and validate generated phishlets.
- Securely store and handle captured data.

## Detection Recommendations

1. Monitor for unusual network traffic patterns.
2. Monitor for the presence of Evilginx 2.3.0-format phishlets.
3. Monitor for the presence of static HTML snapshots.
4. Monitor for the presence of optional host permissions.
5. Monitor for the presence of captured data.

## Residual Gaps

- Multi-origin navigations and requests not tested.
- Service worker suspension or restart not tested.
- Non-HTTP protocols not tested.
- Non-text data not tested.
- Real-time data capture and analysis not implemented.
- Cloud-based data storage and synchronization not implemented.
- Multi-user environments not tested.
- Compliance with specific regulatory frameworks not tested.
```