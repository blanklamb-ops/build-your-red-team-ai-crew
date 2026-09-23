# Comparison Test - Internal Learning Summary

**Report Generated:** 2026-09-04 01:13 UTC  
**For:** Red Team / Operator Review

---

## What Worked (Successes)

### validate-credentials on WORKSTATION-7

**Outcome:** Credentials obtained from phishing site, testing against DC

**Supporting Events:** 2 correlated technical events

**Why it worked:** [Manual analysis recommended - check for defensive gaps, misconfigurations, or valid attack path validation]

### pivot-to-domain-controller on DC01

**Outcome:** Valid domain user creds obtained, escalating to DC for credential dump

**Supporting Events:** 2 correlated technical events

**Why it worked:** [Manual analysis recommended - check for defensive gaps, misconfigurations, or valid attack path validation]

### extract-domain-credentials on DC01

**Outcome:** Administrative access achieved on DC01, dumping credential material

**Supporting Events:** 1 correlated technical events

**Why it worked:** [Manual analysis recommended - check for defensive gaps, misconfigurations, or valid attack path validation]

### lateral-movement-to-exchange on EXCHANGE-01

**Outcome:** Domain admin creds obtained, moving to Exchange for email access

**Supporting Events:** 2 correlated technical events

**Why it worked:** [Manual analysis recommended - check for defensive gaps, misconfigurations, or valid attack path validation]

### exfiltrate-data on EXCHANGE-01

**Outcome:** Data staged successfully, exfiltrating to external C2 infrastructure

**Supporting Events:** 2 correlated technical events

**Why it worked:** [Manual analysis recommended - check for defensive gaps, misconfigurations, or valid attack path validation]

---

## What Failed (Failures)

*No clear failures identified in automated analysis. Review timeline manually.*

---

## Tool Gaps

*Document tools or capabilities that would have improved efficiency or success rate:*

- [ ] [Tool category] - [Specific gap identified]
- [ ] [Example: More reliable credential dumping for modern EDR environments]
- [ ] [Example: Better C2 channel for restrictive network egress]

---

## Reusable TTPs

The following tactics, techniques, and procedures showed promise for future engagements:

### validate-credentials

**Context:** Credentials obtained from phishing site, testing against DC

**Technique Reference:** Credential Access

**Reuse Notes:** [Document prerequisites, tool variants, defensive considerations]

### pivot-to-domain-controller

**Context:** Valid domain user creds obtained, escalating to DC for credential dump

**Technique Reference:** Lateral Movement

**Reuse Notes:** [Document prerequisites, tool variants, defensive considerations]

### extract-domain-credentials

**Context:** Administrative access achieved on DC01, dumping credential material

**Technique Reference:** Credential Access

**Reuse Notes:** [Document prerequisites, tool variants, defensive considerations]

### lateral-movement-to-exchange

**Context:** Domain admin creds obtained, moving to Exchange for email access

**Technique Reference:** Lateral Movement

**Reuse Notes:** [Document prerequisites, tool variants, defensive considerations]

### exfiltrate-data

**Context:** Data staged successfully, exfiltrating to external C2 infrastructure

**Technique Reference:** Exfiltration

**Reuse Notes:** [Document prerequisites, tool variants, defensive considerations]

---

## Defensive Observations

### What Defenders Did Well

- [Note effective detections, quick response times, proper segmentation]
- [Example: EDR caught process injection within 30 seconds]

### What Defenders Missed

- [Note blind spots, delayed responses, misconfigured controls]
- [Example: No monitoring on legacy file shares allowed undetected exfiltration]

---

## Recommendations for Future Engagements

1. **Preparation:**
   - [Pre-engagement improvements based on this run]

2. **Execution:**
   - [Tactical adjustments for similar environments]

3. **Tooling:**
   - [Tool updates or additions to capability set]

4. **Documentation:**
   - [Process improvements for logging and decision tracking]

---

*This internal summary is for operator learning only. Do not share with clients. 
For client deliverables, use the client-facing report with appropriate redaction.*
