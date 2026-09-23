 # Chrome-MV3-Kit Domain Brief

## Operator Goal

The operator's goal is to build a Chrome Manifest V3 lab documentation kit that records metadata about browser authentication HTTP flows in a local lab and generates an operator-ready Evilginx 2.3.0-format phishlet `.yaml` that minimizes operator hand-editing of required fields. The kit should also save static HTML snapshots of lab pages for offline review and export a commented HTTP traffic-pattern skeleton derived from observed URL patterns for lab documentation.

## Constraints

- Platform: Chrome Manifest V3 extension
- Language: JavaScript
- APIs: Chrome Extension APIs (webRequest, storage, downloads, webNavigation)
- Offline/Air-gap needs: The tool should be able to operate locally without exfiltrating data off-host.

## Prior Art

- Existing open projects: None specified in the prompt.
- Formats: Evilginx 2.3.0 Phishlet File Format ([link](https://github.com/kgretzky/evilginx2/wiki/Phishlet-File-Format-(2.3.0)))
- Interfaces: Chrome Extension Development ([link](https://developer.chrome.com/docs/extensions/mv3/))

## Risks

- Technical failure modes: Inaccurate or incomplete data capture, failure to generate a valid phishlet, or inability to save static HTML snapshots.
- Operational failure modes: Misuse of the tool for unauthorized activities, failure to comply with authorized use policies, or inability to properly document the tool's usage and outputs.

## Open Questions

- How should the tool handle multi-origin navigations and requests?
- How should the tool determine which origins require optional host permissions?
- How should the tool handle cases where the service worker is suspended or restarted?
- How should the tool handle non-HTTP(S) URLs that are observed during data capture?
- How should the tool handle cases where the operator does not grant the required optional host permissions?
- Assumption: The tool will use the Chrome Extension APIs to implement the required functionality.