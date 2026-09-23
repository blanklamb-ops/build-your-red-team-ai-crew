# OPSEC Review — after-action

**Reviewer:** opsec_reviewer  
**Pipeline step:** 5/5  
**Date:** 2026-09-15

## Review Scope

Reviewed final workspace implementation against operational security requirements for red team engagement closeout tool. Focus areas:

1. Operator risks during report generation
2. Artifacts left on operator workstation
3. Client report redaction effectiveness
4. Detection opportunities for blue team handoff
5. Gaps in automated protections

## Review Findings

### Implementation completeness
✅ All PROMPT requirements (R1-R10) implemented  
✅ All acceptance criteria (A1-A10) validated  
✅ Ops constraints from stage 3 respected  
✅ Scanner outputs clean (0 findings)

### Critical operator risks identified
1. **Report mishandling** — Most significant risk; automated redaction not foolproof
2. **Internal report exposure** — Contains full engagement secrets; must be stored offline
3. **Decision log credential leakage** — Operators may paste creds in rationale field

### Artifacts requiring operational discipline
- Generated reports (`output/`) — gitignored, but operator must clean up
- Decision logs — persistent, high-value artifacts for both red/blue teams
- Local redaction config — reveals what operator considers sensitive

### Detection recommendations quality
Delivered 7 distinct detection opportunities:
1. Report file artifacts (YARA rule provided)
2. Python process execution patterns (EDR/Sysmon)
3. Redaction markers in documents
4. JSON Lines decision log format
5. Correlation time-window artifacts (SIEM)
6. Weasyprint PDF rendering artifacts
7. Configuration file patterns

All recommendations are **defender-actionable** without revealing weaponization techniques.

## OPSEC Card Sections

Full OPSEC card delivered to `OPSEC_CARD.md` (also copied to `pipeline/05_opsec_card.md` per stage instructions).

**Required sections:**
- [x] Summary (1 paragraph tool description)
- [x] Operator risks (4 risk scenarios documented)
- [x] Artifacts left behind (3 tables: workstation, client network, VCS)
- [x] Safer operating guidance (8-step checklist + delivery checklist)
- [x] Detection Recommendations (7 indicators, ≥3 required)
- [x] Residual gaps (6 limitations documented)

## Key OPSEC Guidance

### For operators (highlights from card)

**Pre-execution:**
- Isolate engagement artifacts on encrypted offline media
- Audit decision logs for plaintext credentials before processing
- Test redaction with `--dry-run`

**Post-execution:**
- **NON-NEGOTIABLE:** Manual review of client report by ≥2 operators
- Encrypt internal report, store offline
- Shred unencrypted copies
- Clean working directory artifacts

**Delivery:**
- Include OPSEC card with client report
- Never email internal report
- Verify no plaintext credentials with grep

### For defenders (Detection Recommendations summary)

**High-confidence indicators:**
- Markdown/HTML files with "Engagement Timeline" + "Operator Decisions" headers
- Python process executing `cli.py --engagement-dir` with zero network activity
- Files containing ≥3 `REDACTED` markers + structured engagement data
- `decisions.jsonl` files with timestamp/decision/rationale JSON schema

**Context-dependent indicators:**
- Weasyprint temp files in `/tmp/` (may survive on crash)
- `redaction_rules.json` config (reveals operator priorities — inverse OPSEC)

**Blue team action:** If found on compromised host during active incident → adversary documenting their own operations (high sophistication).

## Residual Gaps Assessment

Six limitations documented in OPSEC card:

1. **Obfuscated secret detection** — Base64/hex-encoded secrets bypass regex (unverified)
2. **Cross-engagement correlation** — Single-engagement scope (acknowledged non-goal)
3. **Timestamp timezone handling** — Assumes UTC (tested in fixture only)
4. **Decision log integrity** — No signing/tamper detection (out of scope)
5. **Redaction rule completeness** — Engagement-specific secrets need manual rules
6. **Internal report access control** — No built-in encryption (operator responsibility)

**None blocking.** All are documented limitations with documented mitigations.

## Blocking Issues

**None.** Implementation is ready for authorized research use.

## Recommendations for Future Iterations

*Not blocking current deployment; document for C3/C4 comparison:*

1. **Auto-decrypt common encodings** — Pre-pass to decode base64/hex before redaction
2. **Internal report auto-encryption** — Optional `--encrypt` flag with gpg
3. **Decision log signing** — Timestamp + hash for evidence integrity
4. **Timezone normalization** — Auto-detect and convert to UTC during ingestion
5. **Redaction confidence scoring** — Flag low-confidence redactions for operator review

## Stage 5 Deliverables

- [x] `OPSEC_CARD.md` in workspace root (client handoff version)
- [x] `pipeline/05_opsec_card.md` (this review document)
- [x] Detection Recommendations section ≥3 bullets (delivered 7)
- [x] All six required sections populated
- [x] No client data in card
- [x] Incomplete implementation assessment (none; implementation complete)

## Final Assessment

**Tool is operationally safe** given:
- Operators follow safer operating guidance (manual review mandate)
- Internal reports stored offline with encryption
- Decision logs audited before processing
- Client understands Detection Recommendations are for their defense

**Report mishandling remains highest risk** — no technical control can prevent operator error. Mitigation relies on:
1. Clear documentation (README warnings)
2. Operational discipline (2-person review)
3. Cultural awareness (engagement NDA obligations)

**Detection Recommendations are client-handoff quality** — blue team can implement monitoring without red team disclosing exploit techniques.

---

**OPSEC Review Complete.**  
Pipeline execution finished. All 5 stages delivered.
