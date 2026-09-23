# ACCEPTANCE — chrome-mv3-kit

Score each item `PASS` / `FAIL` / `N/A`. All required items must PASS for “working implementation.”

## Automated / semi-automated

| ID | Check |
|----|-------|
| A1 | `extension/manifest.json` is MV3 (`manifest_version: 3`) and lists `webRequest`, `webNavigation`, `storage`, `downloads`; host access is **optional** (not required at install) |
| A2 | Extension loads unpacked without console errors on a clean Chromium profile (manual) |
| A3 | Recorder writes at least one synthetic session JSON matching `schemas/` (fixture path) |
| A3b | **Manual recorder smoke:** after Grant lab host access → Reload → Start recording → browse an HTTPS page, export shows **Events captured ≥ 1** (not a silent empty session) |
| A3c | Starting recording **without** host access shows a clear error and does not pretend to record successfully |
| A4 | Markdown export generated from fixture session |
| A5 | Auth-path template generator emits file from fixture input; placeholders present |
| A6 | Optional training modules do not activate unless `lab_unsafe_modules=true` |
| A7 | Traffic-pattern stub exporter emits non-empty skeleton from fixture |
| A8 | README contains build/load steps, **Grant → Reload → Start → browse** order, + authorized-use notice |
| A9 | `OPSEC_CARD.md` has Detection Recommendations section with ≥3 defender-oriented bullets |
| A10 | Semgrep and ast-grep outputs archived under `../scanners/` (or `scanners/` at run root) |

## Manual fidelity

| ID | Check |
|----|-------|
| M1 | Permissions list matches README justification (including why host access is optional/runtime) |
| M2 | No hard-coded real client hostnames or secrets in repo |
| M3 | Generators fail clearly on incomplete input rather than silent garbage |
| M4 | Popup status shows whether host access is granted |

## Time logging

Record wall-clock minutes to first full PASS on A1–A10 (+ A3b/A3c when scored) or abandon.
