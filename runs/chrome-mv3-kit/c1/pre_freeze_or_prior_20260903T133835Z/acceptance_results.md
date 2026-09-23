# Acceptance results — chrome-mv3-kit / c1 (regen)

Independent verification 2026-09-03 after fresh Claude C1 regen from updated PROMPT (R2a/R2b). Prior hand-patched build remains under `workspace_pre_regen_*` (not scored).

| ID | Result | Notes |
|----|--------|-------|
| A1 | **PASS** | MV3; `webRequest`, `webNavigation`, `storage`, `downloads`; `optional_host_permissions` only |
| A2 | **PASS** | Loaded unpacked; live session `80c90c2f-…` on Chromium |
| A3 | **PASS** | Fixture `testdata/sample_session.json` → report with 4 events |
| A3b | **PASS** | Live export: **22 events**; host access yes; request + navigation rows |
| A3c | **PASS** | `startRecording()` returns clear error if `hasHostAccess()` false; popup shows banner |
| A4 | **PASS** | `node generators/cli.mjs report --input testdata/sample_session.json` |
| A5 | **PASS** | template emits `__REPLACE_*__` / `{{…}}` placeholders |
| A6 | **PASS** | `lab_unsafe_modules: false` in config + extension/config |
| A7 | **PASS** | traffic stub non-empty (~2KB) from `sample_urls.json` |
| A8 | **PASS** | README has load unpacked + Grant → Reload → Start → browse + AUTHORIZED_USE |
| A9 | **PASS** | Detection Recommendations ≥5 defender bullets |
| A10 | **PASS** | Semgrep + ast-grep under `../scanners/` |

## Manual fidelity

| ID | Result | Notes |
|----|--------|-------|
| M1 | **PASS** | README justifies each permission incl. optional host access |
| M2 | **PASS** | Fixtures use `example.com`; no real client hostnames in code |
| M3 | **PASS** | Incomplete template input → exit 1 + schema errors |
| M4 | **PASS** | Popup `host-access-status`: granted / not granted |

**Working implementation?** yes (model-generated regen; R2a/R2b not hand-patched)

**Automated checks run:** generators CLI on fixtures; incomplete-input fail; config gate; OPSEC/README spot-checks; live Chromium smoke (22 events).
