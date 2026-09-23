 # Chrome-MV3-Kit Build Plan

## Repository Layout

```
/chrome-mv3-kit
  /src
    /background.js
    /content.js
    /options.js
    /popup.js
    /manifest.json
  /tests
    /automated
    /manual
  /docs
  /output
```

## Work Packages

1. **WP1: Set up Chrome Extension environment**
   - Configure `manifest.json`
   - Implement background script for data capture

2. **WP2: Implement data capture module**
   - Use `webRequest` API to capture authentication HTTP flows
   - Handle multi-origin navigations and requests (ASSUMPTION: Ignore cross-origin requests)

3. **WP3: Implement phishlet generation module**
   - Generate an Evilginx 2.3.0-format phishlet `.yaml`
   - Minimize operator hand-editing of required fields

4. **WP4: Implement static HTML snapshot module**
   - Save static HTML snapshots of lab pages for offline review
   - Use `downloads` API to download and save snapshots

5. **WP5: Implement HTTP traffic pattern module**
   - Export a commented HTTP traffic-pattern skeleton derived from observed URL patterns

6. **WP6: Implement optional host permissions module**
   - Determine which origins require optional host permissions (ASSUMPTION: Prompt operator for input)
   - Handle cases where the operator does not grant the required optional host permissions (ASSUMPTION: Disable relevant functionality)

7. **WP7: Implement service worker handling module**
   - Handle cases where the service worker is suspended or restarted (ASSUMPTION: Restore data capture upon service worker restart)

8. **WP8: Implement non-HTTP(S) URL handling module**
   - Handle non-HTTP(S) URLs that are observed during data capture (ASSUMPTION: Ignore non-HTTP(S) URLs)

9. **WP9: Implement test plan and acceptance criteria**
   - Write automated tests for data capture, phishlet generation, and static HTML snapshot modules
   - Write manual tests for HTTP traffic pattern module and optional host permissions module

## Interface Contracts

- `background.js`: Exposes functions for data capture, phishlet generation, and static HTML snapshot modules
- `content.js`: Injects into lab pages to capture data
- `options.js`: Allows operator to configure optional host permissions
- `popup.js`: Displays tool usage and outputs to operator

## Requirement Trace Matrix

| PROMPT Requirement ID | Work Package |
|----------------------|--------------|
| PROMPT-1              | WP1, WP2, WP3, WP4, WP5, WP6, WP7, WP8, WP9 |
| PROMPT-2              | WP6, WP9 (manual testing) |
| PROMPT-3              | WP7, WP9 (manual testing) |
| PROMPT-4              | WP8, WP9 (manual testing) |
| PROMPT-5              | WP6, WP9 (manual testing) |

## Test Plan

- Automated tests: Data capture, phishlet generation, and static HTML snapshot modules
- Manual tests: HTTP traffic pattern module, optional host permissions module

## Out of Scope

- Support for browsers other than Chrome
- Support for Manifest V2 extensions
- Support for non-English languages
- Support for non-Windows operating systems
- Support for non-HTTP protocols (e.g. FTP, SFTP)
- Support for non-text data (e.g. images, videos)
- Support for real-time data capture and analysis
- Support for cloud-based data storage and synchronization
- Support for multi-user environments
- Support for advanced threat detection and mitigation
- Support for compliance with specific regulatory frameworks (e.g. GDPR, HIPAA)
- Support for integration with third-party tools and services (e.g. Splunk, ELK stack)