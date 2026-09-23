# OPSEC Card — Chrome MV3 Lab Kit

**Detection Recommendations** (Defender-Oriented)

## Purpose

This document provides detection guidance for security defenders monitoring for unauthorized use of browser-based credential capture techniques in production environments.

## Detection Recommendations

### 1. Browser Extension Monitoring

**Indicator**: Unexpected browser extensions with sensitive permissions

- **Monitor for**: Extensions requesting `webRequest`, `webNavigation`, and broad host permissions (`<all_urls>` or wildcards)
- **Detection method**:
  - Endpoint visibility tools can enumerate installed browser extensions
  - Chrome Enterprise Policy can enforce extension allowlists
  - Query Chrome's `Preferences` and `Secure Preferences` files for extension IDs and permissions
- **Response**: Investigate extensions that have both network-inspection and storage permissions, especially if not from verified corporate catalog

**Example Chrome policy**:
```json
{
  "ExtensionInstallBlocklist": ["*"],
  "ExtensionInstallAllowlist": ["<corporate-extension-id>"]
}
```

### 2. Suspicious Network Patterns

**Indicator**: Parallel authentication flows or credential replay

- **Monitor for**:
  - Multiple authentication sessions from same source IP in rapid succession
  - Session tokens being reused from different user-agents or IP addresses
  - OAuth callback parameters (authorization codes) replayed or accessed from unexpected locations
- **Detection method**:
  - Web application firewall (WAF) rules for replay detection
  - Session binding to TLS fingerprint or client IP
  - Monitoring for `Set-Cookie` headers with `SameSite=None` being accessed cross-origin
- **Response**: Implement token binding, rotate session secrets, and investigate source of duplicated sessions

### 3. Unusual Browser Behavior in Corporate Environment

**Indicator**: Developer/debug flags or automation artifacts

- **Monitor for**:
  - Browser profiles with "Developer mode" enabled on managed endpoints
  - Presence of unpacked extensions in user profiles
  - Chrome debugging ports exposed (`--remote-debugging-port`)
  - User-agents indicating automation frameworks (Puppeteer, Selenium)
- **Detection method**:
  - EDR/endpoint monitoring for Chrome command-line arguments
  - Registry/file monitoring for `extensions/` subdirectories in Chrome user data
  - Network monitoring for Chrome DevTools Protocol traffic (typically port 9222)
- **Response**: Corporate policy enforcement to disable developer mode, EDR alerting on non-standard browser configurations

### 4. Auth Flow Metadata Leakage

**Indicator**: Reconnaissance of authentication endpoints

- **Monitor for**:
  - Scripted or automated traversal of login/OAuth/SAML flows without completion
  - High volume of `OPTIONS` requests to auth endpoints (CORS preflight enumeration)
  - Requests that fetch login pages but never POST credentials (reconnaissance)
  - Unusual `Referer` headers or missing anti-CSRF tokens
- **Detection method**:
  - Rate limiting on authentication endpoints
  - Logging incomplete auth flows (navigation to login without subsequent POST)
  - Honeytokens in hidden form fields to detect automated form scraping
- **Response**: Implement CAPTCHA/risk-based authentication for suspicious patterns, investigate source

### 5. Client-Side Storage Inspection

**Indicator**: Extension accessing sensitive cookies or local storage

- **Monitor for**:
  - Extensions with `storage` permission accessing `localStorage` or `IndexedDB` for authentication domains
  - Cookies marked `HttpOnly` being logged or exfiltrated via extension APIs
  - Extensions calling `chrome.cookies.getAll()` for auth-related domains
- **Detection method**:
  - Browser extension telemetry (if available via enterprise policies)
  - Monitor for Chrome extension sync traffic to non-corporate accounts
  - Code review of approved extensions for cookie/storage access patterns
- **Response**: Enforce `HttpOnly` and `Secure` flags on all auth cookies, use `__Host-` prefix to prevent subdomain access

### 6. Form Field Enumeration

**Indicator**: Automated extraction of form structure without submission

- **Monitor for**:
  - JavaScript that queries `document.querySelectorAll('form')` or `input` elements on login pages
  - Content scripts injected into authentication pages (detectable via CSP violations)
  - Navigation to login pages followed immediately by navigation away (no form submission)
- **Detection method**:
  - Content Security Policy (CSP) with `script-src 'self'` to block injected scripts
  - CSP reporting endpoint to collect violation reports
  - Frontend instrumentation to detect unexpected DOM queries
- **Response**: Harden CSP, investigate CSP violation sources, deploy anti-automation defenses

### 7. Evilginx/Phishing Infrastructure Indicators

**Indicator**: Reverse proxy phishing infrastructure in production

- **Monitor for**:
  - TLS certificates issued for domains similar to corporate login domains (homoglyphs, typos)
  - Certificate Transparency logs showing unexpected SANs for your brand
  - Domains registered with brand keywords + common phishing TLDs (.tk, .ml, .ga)
  - MX/A/AAAA records pointing to hosting providers commonly used for phishing (VPS, bulletproof hosting)
- **Detection method**:
  - Certificate Transparency monitoring services (e.g., Facebook CT Monitor, CertStream)
  - Brand monitoring for domain registrations
  - Threat intelligence feeds for phishing kits mentioning your organization
  - DMARC reports showing unexpected sending domains
- **Response**: Pursue domain takedown, notify users, implement additional auth factors

### 8. OAuth/SAML Redirect Validation

**Indicator**: Open redirect or redirect_uri manipulation

- **Monitor for**:
  - `redirect_uri` parameters pointing to non-allowlisted domains
  - Authorization codes or tokens being sent to unexpected callback URLs
  - Multiple authorization attempts with varying `redirect_uri` values (probing)
- **Detection method**:
  - Strict allowlist validation for OAuth `redirect_uri` (exact match, not prefix)
  - Logging all OAuth authorization grants with full parameter sets
  - Anomaly detection on callback domains (new domains not historically seen)
- **Response**: Reject non-allowlisted redirects, rotate OAuth client secrets, investigate authorization attempts

### 9. Endpoint Indicators

**Indicator**: Research tools or artifacts on managed endpoints

- **Monitor for**:
  - Presence of Evilginx binaries or configuration files
  - Tools like `mitmproxy`, `Burp Suite`, `OWASP ZAP` on non-security team endpoints
  - Lab documentation files with corporate credential field names or auth URL patterns
  - Chrome extension source code with `webRequest`/`webNavigation` listeners in user directories
- **Detection method**:
  - EDR file/process monitoring
  - YARA rules for known phishing kit artifacts
  - Search for `.yaml` files with `auth_tokens`, `sub_filters`, `proxy_hosts` keys
- **Response**: Quarantine endpoint, investigate user activity, audit for data exfiltration

### 10. Network Exfiltration

**Indicator**: Captured session data being exfiltrated

- **Monitor for**:
  - Unusual outbound HTTPS connections from endpoints to personal cloud storage, file-sharing sites, or paste sites
  - Large JSON payloads in HTTP bodies to non-corporate domains
  - DNS queries for exfiltration-related domains (file upload sites, disposable email)
- **Detection method**:
  - DLP/CASB monitoring for sensitive patterns in outbound traffic
  - DNS filtering and logging
  - Egress filtering to block known exfiltration sites
- **Response**: Block exfiltration domain, investigate source endpoint, audit for credential compromise

## Mitigations Summary

- **Extensions**: Allowlist-only extension policy via Chrome Enterprise
- **Cookies**: `HttpOnly`, `Secure`, `SameSite=Strict`, `__Host-` prefix
- **CSP**: Enforce strict Content Security Policy on authentication pages
- **OAuth**: Exact-match `redirect_uri` allowlists, short-lived authorization codes
- **FIDO2/WebAuthn**: Deploy phishing-resistant MFA (hardware tokens)
- **Certificate Transparency**: Monitor for suspicious TLS certificates
- **Endpoint monitoring**: EDR alerting on developer-mode browsers, proxy tools, phishing kit artifacts
- **Network monitoring**: Detect parallel sessions, token replay, exfiltration attempts

## References

- MITRE ATT&CK: T1189 (Drive-by Compromise), T1539 (Steal Web Session Cookie), T1185 (Browser Session Hijacking)
- OWASP: Session Management Cheat Sheet, Authentication Cheat Sheet
- Chrome Enterprise Extension Management: https://support.google.com/chrome/a/answer/9296680

---

**This OPSEC card is for defenders** — use it to harden authentication infrastructure and detect unauthorized credential capture attempts.
