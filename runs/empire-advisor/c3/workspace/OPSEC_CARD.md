# OPSEC Card — empire-advisor

Review date: 2026-09-04

## Summary

empire-advisor is an offline, operator-side pre-submit advisor for authorized Empire-like lab workflows. It reads command text, applies 15 transparent deterministic heuristics, and returns an allow, warn, or deny advisory with matched rationales and cited local alternatives. It does not connect to Empire, enforce a decision, retrieve citations, or execute either the submitted command or any suggestion; execution_performed is always false.

## Operator risks

- Supplying a real command on the shell command line can expose targets, usernames, paths, and intent in shell history, process-command-line telemetry, terminal scrollback, CI logs, screen recordings, or redirected output.
- Treating a low score or allow state as “safe” or “undetected” can create false confidence. Allow means only that no shipped regex matched; the rules are neither an EDR model nor a guarantee of authorization.
- The offline shim is an explicit wrapper, not a universal Empire pre-task hook. An operator can bypass it, and a deny result cannot prevent separate task submission.
- Copying a KB template without replacing and reviewing its placeholders can cause an out-of-scope query. Even read-only alternatives can create process, PowerShell, directory-service, file-access, and endpoint telemetry.
- Editing rules, thresholds, or KB entries without peer review changes the policy and can invalidate score comparisons. The output does not embed policy hashes.
- Saving advisory JSON alongside engagement data may retain the complete analyzed command beyond the intended evidence-retention window.

## Artifacts left behind

- **Repository:** the package, plugin.yaml, rules.yaml, kb.yaml, synthetic fixtures, tests, scanner configurations/results, and pipeline documents remain wherever the repository is copied.
- **Local host:** Python may create empire_advisor/__pycache__ and tests/__pycache__ unless bytecode writing is disabled. Import/file-access telemetry can show reads of rules.yaml and kb.yaml.
- **Process and shell:** process accounting can record python3, -m empire_advisor.cli, --command/--fixture, and path arguments. Interactive invocation may be retained by shell history.
- **Output and logs:** stdout/stderr repeats analyzed commands. Redirection, terminal capture, notebooks, CI, EDR, or session recording can persist it. The application itself creates no runtime log.
- **Empire:** the shim creates no Empire record. If an operator later submits a command separately, normal Empire user, plugin/API, agent-task, and result records remain independently observable.
- **Endpoint and network:** the advisor makes no registry changes, browser/mail actions, sockets, DNS, or HTTP requests. Citation URLs are inert metadata. Any later suggested command can still create normal endpoint and directory telemetry.
- **Build-only:** the recorded Semgrep run used /tmp/empire-advisor-semgrep-settings.yml and /tmp/empire-advisor-semgrep.log. Their lifecycle depends on the build host; they contain scanner settings/logging rather than engagement fixtures.

## Safer operating guidance

- Run only with written authorization, on an engagement-controlled operator workstation, as an unprivileged user. Review scope before placing any real command in a fixture or argument.
- Prefer synthetic fixtures for testing. For engagement use, avoid --command when shell history or process capture is not approved; use the organization’s approved secure input/evidence workflow and account for the CLI’s unavoidable echoed output.
- Set PYTHONDONTWRITEBYTECODE=1 where cache artifacts are undesirable, and remove generated caches and temporary operator output before packaging.
- Review and version-control rules.yaml and kb.yaml. Record their SHA-256 hashes with private engagement evidence when reproducibility matters, and require peer review for policy changes.
- Invoke the advisor before the separate Empire submission step. Treat warn/deny as prompts for human authorization and technical review; do not interpret allow as approval.
- Replace KB placeholders only with already-approved values. Reassess every alternative for host role, collection scope, logging impact, and client rules of engagement.
- Keep advisory output under the engagement retention policy. Do not commit tokens, staging keys, agent IDs, customer identifiers, internal addresses, or raw C2 transcripts.

## Detection Recommendations

- On managed operator, jump, and CI hosts, alert or inventory process creation where python or python3 command lines contain empire_advisor.cli, empire_advisor.empire_plugin, --fixture, or --command. Protect captured command lines as potentially sensitive assessment evidence.
- Monitor file-open telemetry and integrity changes for plugin.yaml, rules.yaml, and kb.yaml. Unexpected threshold/rule edits should trigger review because they can suppress or alter advisory outcomes.
- Treat network activity from a process identified as empire-advisor as anomalous. The delivered runtime has no network path; investigate DNS, HTTP, socket creation, or child-process activity attributed to it or its Python parent.
- Retain and correlate Empire authentication, /api/v2/plugins activity, operator identity, agent tasking, and task-result records. A local advisor result is not evidence that a task was blocked, and later Empire tasking must be detected on its own merits.
- On Windows test endpoints, correlate process creation (Security 4688 or Sysmon Event ID 1 where deployed), PowerShell Script Block Logging (4104 where enabled), and relevant Defender/EDR telemetry for the actual submitted command. Do not reduce monitoring because the advisor labeled a command allow.
- Build high-confidence alerts for the dangerous behaviors represented by deny fixtures: event-log clearing (Security 1102 and System 104), endpoint-protection/firewall configuration changes, shadow-copy deletion, and sensitive registry-hive export. Correlate with actor, parent process, host role, and approved test window.
- Hunt for broad discovery bursts—full token, process, filesystem, network-interface, domain-user, privileged-group, or domain-controller enumeration—especially when several occur from one user/agent in a short interval. Baseline administrative tooling and apply engagement allowlists in the SIEM, not by disabling source telemetry.
- Scan CI and evidence repositories for accidental advisory output containing real commands, internal hostnames/addresses, or credentials. Apply access control and retention to findings rather than copying sensitive text into tickets.

## Residual gaps

- No live Empire 5.x or 6.x server/Starkiller instance was supplied, so registration, UI rendering, authentication/audit behavior, and API drift were not exercised. Only the documented execute(command, **kwargs) shape and offline adapter were verified.
- No Windows endpoint or client EDR/SIEM was available. Event identifiers and query ideas require validation against the client’s audit policy, product schemas, data quality, and retention.
- Regex heuristics can miss aliases, unusual quoting, other languages, or novel commands and can false-positive on text. The 15-rule policy is illustrative and transparent, not comprehensive.
- Public citation pages may move, and their content was not fetched during offline execution. Citation reachability and template suitability require periodic human review.
- Static analysis used three local Semgrep rules and one local ast-grep rule. Both reported zero findings, but this limited controlled scan is not a comprehensive security audit.
- The output does not sign or hash its loaded policy. Reproducibility across evidence sets requires the operator to record file hashes externally.

