# Safety Checklist — gophish-ics

## Before Running Any Command

Use this checklist before generating ICS files or loading telemetry data to prevent accidental deployment of research artifacts.

---

## Pre-Flight Checks

### 1. Configuration Safety

- [ ] `config/config.yaml` has `ics_enabled: false` (unless explicitly enabling for authorized engagement)
- [ ] If enabling ICS generation, confirm you have **written authorization** for the target engagement
- [ ] Config file is NOT checked into git with `ics_enabled: true`

**Verify:**
```bash
grep "ics_enabled" config/config.yaml
# Should show: ics_enabled: false
```

---

### 2. Test Data Validation

- [ ] All campaign fixtures use RFC-reserved domains only:
  - `example.com`, `example.org`, `example.net`
  - `test.invalid`
  - `*.localdomain`
- [ ] No real target email addresses in `testdata/` directory
- [ ] Campaign IDs are synthetic (e.g., `fixture-campaign-001`, not real client identifiers)
- [ ] Timestamps in fixtures are obviously synthetic (e.g., `2025-01-01T12:00:00Z`)

**Verify:**
```bash
# Check for common real domains (should return no matches)
grep -Ri "gmail\|outlook\|yahoo\|company\.com" testdata/
```

---

### 3. Evidence Isolation

- [ ] Telemetry database (`telemetry.db`) is NOT in git staging area
- [ ] Output directory is empty of prior engagement artifacts
- [ ] If using engagement-specific database, `--db-path` points to separate file outside repo
- [ ] No `.ics` files checked into git

**Verify:**
```bash
git status | grep -E "telemetry.db|\.ics"
# Should return no matches
```

---

### 4. Demo Mode vs. Live Mode

- [ ] For testing: Using `--demo` flag (adds `[DEMO ONLY]` notice to ICS description)
- [ ] For live engagements: Removed `--demo` flag AND have written authorization
- [ ] For testing: Using `--enable-ics` CLI flag (does not modify config file)
- [ ] For live engagements: Consciously edited `config/config.yaml` to enable ICS

---

### 5. Tool Invocation Safety

**For demos/testing:**
- [ ] Using `--enable-ics` flag (not editing config)
- [ ] Using `--demo` flag
- [ ] NOT using `--force` flag (domain safety checks active)

**For authorized engagements:**
- [ ] Edited `config/config.yaml` to `ics_enabled: true` (conscious decision)
- [ ] Reviewed target email domains against allowlist
- [ ] Only using `--force` if targets are outside allowlist AND engagement is authorized
- [ ] Documented why `--force` was necessary

---

## Post-Execution Checks

### After Demo

- [ ] `config/config.yaml` still has `ics_enabled: false` (demo did not modify it)
- [ ] Cleaned up demo artifacts:
  ```bash
  rm -f telemetry.db output/*.ics
  ```
- [ ] No test data left in production directories

### After Live Engagement

- [ ] Copied `telemetry.db` to secure storage (outside repo)
- [ ] Reset `config/config.yaml` to `ics_enabled: false`
- [ ] Removed or redacted campaign data from `testdata/` before committing
- [ ] Generated `.ics` files archived or securely deleted (not in git)

---

## Git Pre-Commit Hook (Optional)

Prevent accidental commits of sensitive data:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for enabled config
if grep -q "ics_enabled: true" config/config.yaml; then
    echo "ERROR: Attempting to commit config with ics_enabled: true"
    echo "Reset to ics_enabled: false before committing"
    exit 1
fi

# Check for database files
if git diff --cached --name-only | grep -q "telemetry.db"; then
    echo "ERROR: Attempting to commit telemetry database"
    exit 1
fi

# Check for ICS files
if git diff --cached --name-only | grep -q "\.ics$"; then
    echo "ERROR: Attempting to commit .ics files"
    exit 1
fi

exit 0
```

**Install:**
```bash
chmod +x .git/hooks/pre-commit
```

---

## Emergency: Accidental Deployment

If you accidentally generated ICS for real targets:

1. **Stop immediately** — do not send the campaign
2. Delete generated `.ics` files
3. Verify no mail was sent via GoPhish (check campaign status)
4. Document the incident per your organization's security procedures
5. If mail was sent, follow engagement de-escalation procedures
6. Reset `config/config.yaml` to `ics_enabled: false`
7. Review this checklist to identify missed steps

---

## Responsible Disclosure

If you discover safety issues with this tool:

1. Do NOT publish details publicly
2. Report to your security team or engagement lead
3. Document the issue and remediation
4. Propose checklist updates to prevent recurrence

---

## Engagement Authorization Template

Before enabling ICS generation for a live engagement, ensure you have documentation similar to:

```
Engagement: [Client Name]
Authorized by: [Client Contact]
Scope: [IP ranges / domains / user populations]
Duration: [Start Date] to [End Date]
Rules of Engagement: [Link to signed SOW/RoE]
Tool usage: Calendar-based phishing simulation
Target domains: [List of authorized domains]
```

Keep this documentation **outside this repository** in secure engagement records.

---

## Training & Onboarding

New operators should:

1. Read `README.md` and `AUTHORIZED_USE.md`
2. Run `scripts/demo.sh` to understand workflow
3. Review this checklist
4. Complete dry-run with synthetic data and mentor oversight
5. Confirm understanding of `--enable-ics` vs. config file editing
6. Practice emergency de-escalation procedures

---

## Audit Trail

Log all ICS generation operations:

```bash
# Example: Log to engagement journal
echo "$(date -Iseconds) - Generated ICS for campaign-001 (authorized engagement ABC)" >> /secure/engagements/journal.log
```

---

**Remember:** Tools are only as safe as their operators. When in doubt, ask for peer review before executing commands.
