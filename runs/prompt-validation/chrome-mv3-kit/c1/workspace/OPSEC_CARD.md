# OPSEC Card — chrome-mv3-kit

**Tool Purpose:** Lab documentation kit for authorized security research. Records browser auth flow metadata and generates Evilginx 2.3.0 phishlets.

**Authorized Use:** Penetration testing engagements, red team exercises, security research, defensive analysis, and education with explicit authorization.

## Detection Recommendations

Defender-oriented mitigations and detection opportunities:

### 1. **Browser Extension Monitoring**

**Risk:** Malicious or unauthorized extensions can intercept authentication flows.

**Mitigations:**
- Deploy enterprise policy to restrict Chrome extensions to approved allowlists (`ExtensionInstallBlocklist`, `ExtensionInstallAllowlist`)
- Monitor for extensions requesting `webRequest` + `webNavigation` permissions on sensitive workstations
- Enable Chrome Enterprise extension telemetry to inventory installed extensions
- Audit extension permissions during security reviews — extensions with broad host access (`http://*/*`, `https://*/*`) pose higher risk
- Flag developer mode and unpacked extensions on non-developer endpoints

**Detection:**
- Chrome stores extension metadata in `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions\` (Windows) or `~/.config/google-chrome/Default/Extensions/` (Linux)
- Look for extension manifests with `webRequest` in `permissions` array and `optional_host_permissions` that include `<all_urls>` or wildcard patterns
- Correlate Chrome process network activity with known-legitimate extension IDs

### 2. **Evilginx Reverse-Proxy Phishing Infrastructure**

**Risk:** Attackers use Evilginx to proxy live IdP flows, capturing session cookies in real-time.

**Mitigations:**
- **Certificate Transparency Monitoring:** Subscribe to CT logs for your domains; alert on unexpected wildcard or subdomain certs (e.g., `login-secure.attacker-domain.com`)
- **User Education:** Train users to verify domain **and** TLD before entering credentials — `login.microsoft.com.attacker.tld` is not `microsoft.com`
- **Phishing-Resistant Authentication:** Deploy FIDO2/WebAuthn MFA bound to origin (credential is domain-scoped; cannot be proxied to different domain)
- **Conditional Access Policies:** Require known/trusted IP ranges, compliant devices, or app-based MFA for sensitive apps
- **DNS Monitoring:** Track newly registered domains with high string similarity to your brands (typosquatting, homograph attacks)

**Detection:**
- Monitor for login attempts from unexpected geographic regions or ASNs (VPS/cloud hosting providers are common Evilginx hosts)
- Alert on certificate issuance for domains that **include** your brand as a substring (e.g., `microsoft-login-verify.com`)
- Inspect referrer headers / landing-page sources — phishing lures often arrive via email campaigns with tracking parameters
- Watch for rapid sequential logins from same user to same app but different source IPs (victim's real IP then attacker replaying session)

### 3. **Session Cookie Theft and Replay**

**Risk:** Even with MFA, session cookies captured during Evilginx proxy are valid until expiry.

**Mitigations:**
- **Short Session Lifetimes:** Reduce cookie TTL for high-value apps (force re-auth)
- **Device Binding:** Bind session tokens to device fingerprint or client certificate (harder to replay cross-device)
- **IP Geofencing:** Invalidate sessions on geographic jump (e.g., US → RU in 5 minutes)
- **User-Agent / TLS Fingerprint Consistency:** Track session to initial UA/JA3; anomaly-score changes mid-session

**Detection:**
- Alert on session token reuse from multiple IPs within short time window
- Monitor for `Set-Cookie` responses followed by immediate access from different IP (attacker replay)
- Track impossible-travel: session token first used from IP A (user) then IP B (attacker) where travel time < 1 hour
- Correlate authentication success with device compliance state — flag sessions from non-compliant devices

### 4. **DNS and Network Indicators**

**Risk:** Phishing domains often have short registration age and low reputation.

**Mitigations:**
- Deploy DNS filtering (block newly registered domains <30 days old, known-bad TLDs like `.tk`, `.ml`)
- Use web proxies with URL reputation feeds (block low-reputation / uncategorized domains)
- HSTS Preloading: Preload your auth domains in browser HSTS lists (prevents SSL strip, enforces HTTPS)

**Detection:**
- WHOIS monitoring for domains registered with your brand keywords
- Passive DNS: correlate login domain FQDNs seen in logs against known-good list; alert on unknown subdomains
- Monitor public phishing feeds (PhishTank, OpenPhish, URLhaus) for your brand

### 5. **Content Analysis and Behavioral Indicators**

**Risk:** Evilginx phishlets may preserve most IdP HTML/JS but inject minor modifications.

**Mitigations:**
- **Subresource Integrity (SRI):** Use SRI tags on critical login-page JS/CSS (detects tampering)
- **CSP Headers:** Lock down Content Security Policy to disallow inline scripts or third-party origins on login pages

**Detection:**
- Monitor for login pages served over HTTP or with invalid/self-signed certs (though Evilginx typically uses valid Let's Encrypt certs)
- Flag login flows with unusual client-side JavaScript errors (phishlet `sub_filters` may break JS if misconfigured)
- Track user reports of "weird login page behavior" or "site looks slightly off"

### 6. **Operational Indicators (Red Team / Engagement Context)**

**Risk:** In authorized testing, stolen credentials may be reused during the engagement.

**Mitigations (Blue Team):**
- Require red teams to use dedicated test accounts (not production user creds)
- Define rules of engagement: credential capture must be reported within X hours, not reused outside engagement scope
- Monitor for logins from red-team-owned infrastructure IPs

**Detection:**
- Correlate authentication sources with known penetration test IP ranges or ASNs
- Require red team to provide test account list and infrastructure inventory before kickoff
- Post-engagement: audit all session tokens issued during test window and force expiry

---

## Summary

**Key Defensive Layers:**
1. **Prevent phishing delivery:** Email filtering, DNS blocking, user training
2. **Detect phishing infrastructure:** CT logs, domain monitoring, IP reputation
3. **Resist credential theft:** FIDO2/WebAuthn, phishing-resistant MFA
4. **Limit session theft impact:** Short token TTL, device binding, impossible-travel detection

**High-Value Detections:**
- Certificate transparency alerts for brand-string domains
- Session token reuse from multiple IPs / geolocations
- Extensions with `webRequest` + broad host access on endpoints
- Newly registered domains with high brand similarity

For security operations teams inheriting this toolkit, **deploy layered defenses** — no single control stops all phishing. Combine prevention, detection, and response.
