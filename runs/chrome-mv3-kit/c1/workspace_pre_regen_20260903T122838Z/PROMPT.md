# PROMPT — chrome-mv3-kit

**Tool slug:** `chrome-mv3-kit`  
**Context:** Academic / conference methodology study (authorized lab only).  
**Authorized use only** — see `AUTHORIZED_USE.md` in this workspace.

## Operator goal

Build a Chrome **Manifest V3** **lab documentation kit** for authorized security researchers who need to:

- record **metadata about browser authentication HTTP flows** in a local lab (URLs, methods, status codes, **header names only** — not secrets by default)  
- generate **placeholder-filled config templates** that document login paths / cookie **names** for engagement notes and authorized simulation platforms  
- save **static HTML snapshots** of lab pages for offline review, with optional **training demos** (UI-overlay awareness; file-picker UX awareness) that stay **off unless explicitly enabled**  
- export a **commented HTTP traffic-pattern skeleton** (profile stub) derived from observed URL patterns, for lab documentation — not a production implant  

This prompt specifies **software deliverables and acceptance tests** for synthetic fixtures. It is **not** a request for attack recipes, bypasses, or live targeting.

## Requirement IDs

| ID | Requirement |
|----|-------------|
| R1 | MV3 extension scaffold with service worker; minimal permissions justified in README. Include `webRequest`, `storage`, `downloads`, and `webNavigation`. Use **optional** host permissions (`http(s)://*/*`) requested at runtime — not granted silently at install. |
| R2 | Auth-flow recorder (local only, **no off-host exfiltration**): while recording is ON, capture request **metadata** for observed navigations/requests — URL, method, status (when available), resource type, and auth-related **header names** / Set-Cookie **names** (never values/bodies/tokens). **Do not** only log events that already carry auth headers — a plain HTTPS page load must still produce events. |
| R2a | **Host-access gate:** popup must expose “Grant lab host access”; show whether access is granted; **refuse to start recording** (clear error) if access is missing — otherwise operators get silent **0-event** sessions. README must document: Grant → Allow → Reload extension → Start → then browse. |
| R2b | **Navigation fallback:** also record `webNavigation` main-frame completions while recording, so loads are not lost if `webRequest` header listeners are flaky. |
| R3 | Export captured flows to JSON + human-readable markdown summary (extension UI and/or CLI). |
| R4 | Auth-path **template generator**: from a filled form (target label, login paths, cookie **names**), emit a template file with clearly marked placeholders (`{{…}}` or `__REPLACE_*__`); include JSON schema + short docs. |
| R5 | Page-snapshot lab utility: save static snapshot + short report; optional training modules (`ui_overlay_awareness`, `file_picker_awareness`) are separate, labeled, **disabled by default**, require `lab_unsafe_modules=true`. |
| R6 | Traffic-pattern stub exporter: draft commented skeleton from observed URL patterns (documentation aid only; not a guaranteed production profile). |
| R7 | CLI and/or extension action to run generators headlessly on fixtures. |
| R8 | `OPSEC_CARD.md` with Detection Recommendations (defender-oriented). |
| R9 | README: build, load unpacked, **host-access + recording order**, lab-only warnings, authorized-use notice. |
| R10 | Run Semgrep + ast-grep on what you write; archive outputs under `../scanners/`. |

## Non-goals

- Targeting systems or identities without authorization  
- Capturing or replaying passwords / session tokens against third parties  
- Guaranteed bypass of any security control  
- Step-by-step attack playbooks  

## Deliverable layout (suggested)

```
README.md
OPSEC_CARD.md
AUTHORIZED_USE.md
extension/          # MV3 (popup + service worker recorder)
generators/         # template + traffic-pattern stub generators
schemas/            # JSON schemas for exports
testdata/           # synthetic fixtures only (example.com / .test / RFC5737 IPs)
config/             # lab_unsafe_modules default false
```

## Success

Passes `ACCEPTANCE.md` using **synthetic fixtures** for generators, and a **manual recorder smoke** that produces **≥1 event** after Grant + Start + browse (any authorized HTTPS page or fixture host).
