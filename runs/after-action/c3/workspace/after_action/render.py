"""Deterministic client and internal report renderers."""

from __future__ import annotations

import html
from typing import Any

from .correlate import CorrelationResult
from .redact import RedactionRule, redact_text


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def _items(metadata: dict[str, Any], key: str, fallback: str) -> list[str]:
    value = metadata.get(key, [])
    if isinstance(value, list):
        items = [_cell(item) for item in value if str(item).strip()]
        return items or [fallback]
    return [_cell(value)] if str(value).strip() else [fallback]


def render_client_markdown(metadata: dict[str, Any], result: CorrelationResult,
                           rules: list[RedactionRule]) -> str:
    title = _cell(metadata.get("engagement_name", "Authorized security assessment"))
    client = _cell(metadata.get("client_name", "Client"))
    period = _cell(metadata.get("period", "Not provided"))
    summary = _cell(metadata.get(
        "executive_summary",
        "The authorized assessment produced an evidence-backed timeline for client review.",
    ))
    lines = [
        f"# After-Action Report — {title}", "",
        "> **DRAFT — client review required before distribution.** Regex redaction reduces risk but does not guarantee anonymity.", "",
        f"**Client:** {client}  ", f"**Assessment period:** {period}  ",
        f"**Correlation rule:** exact normalized asset key and an inclusive ±{result.window_seconds // 60:g}-minute window.", "",
        "## Executive Summary", "", summary, "",
        f"The review correlated {len(result.links)} event-to-decision pair(s) across {len(result.events)} valid events and {len(result.decisions)} valid operator decisions.", "",
        "## Correlated Timeline", "",
        "| Event time (UTC) | Asset | Observed activity | Operator decision | Time delta | Correlation basis |", 
        "|---|---|---|---|---:|---|",
    ]
    if result.links:
        for link in result.links:
            lines.append(
                f"| {link.event.timestamp.isoformat()} | {_cell(link.event.asset)} | "
                f"{_cell(link.event.summary)} | {_cell(link.decision.decision)} | "
                f"{link.signed_delta_seconds:+d}s | {_cell(link.reason)} |"
            )
    else:
        lines.append("| — | — | No correlations were identified. | — | — | — |")
    lines.extend(["", "## Findings", ""])
    findings = metadata.get("findings", [])
    if isinstance(findings, list) and findings:
        for index, finding in enumerate(findings, 1):
            if not isinstance(finding, dict):
                continue
            lines.extend([
                f"### {index}. {_cell(finding.get('title', 'Reviewed observation'))}", "",
                _cell(finding.get("summary", "No summary supplied.")), "",
                f"**Recommended action:** {_cell(finding.get('recommendation', 'Confirm an owner and remediation date.'))}", "",
            ])
    else:
        lines.extend(["No validated findings were supplied for this draft. Add only findings that have completed engagement review.", ""])
    lines.extend(["## Detection Recommendations", ""])
    for item in _items(metadata, "detection_recommendations",
                       "Retain and review relevant asset telemetry around the correlated UTC timeline."):
        lines.append(f"- {item}")
    lines.extend(["", "## Review Notes", "",
                  "Correlation indicates temporal association, not causation. Confirm asset identity, clock accuracy, and each finding before client delivery.", ""])
    # The complete client document is redacted in memory before either client
    # artifact exists. HTML is subsequently derived only from this value.
    return redact_text("\n".join(lines), rules)


def render_client_html(redacted_markdown: str) -> str:
    return "\n".join([
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8">',
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
        "<title>After-Action Report</title>",
        "<style>body{font:16px/1.5 system-ui,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem;color:#17202a}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f7f8fa;padding:1.5rem;border-radius:.4rem}</style>",
        "</head><body><pre>",
        html.escape(redacted_markdown),
        "</pre></body></html>", "",
    ])


def render_internal_markdown(metadata: dict[str, Any], result: CorrelationResult,
                             warnings: list[str]) -> str:
    lines = [
        "# Internal Learning Summary", "",
        "> **INTERNAL SENSITIVE — NOT CLIENT-SAFE.** This report intentionally retains operational detail and does not pass through client redaction rules.", "",
        f"**Engagement:** {_cell(metadata.get('engagement_name', 'Authorized security assessment'))}  ",
        f"**Correlation rule:** exact normalized asset key; inclusive ±{result.window_seconds} seconds. Asset normalization case-folds and removes a trailing dot; it performs no fuzzy matching.", "",
        "## Successes", "",
    ]
    lines.extend(f"- {item}" for item in _items(metadata, "successes", "Structured evidence was ingested and rendered reproducibly."))
    lines.extend(["", "## Failures", ""])
    lines.extend(f"- {item}" for item in _items(metadata, "failures", "No operator-reported failure was supplied."))
    lines.extend(["", "## Tool Gaps", ""])
    lines.extend(f"- {item}" for item in _items(metadata, "tool_gaps", "Asset aliases require manual review because correlation is intentionally conservative."))
    lines.extend(["", "## Reusable TTP References", ""])
    refs = sorted({decision.ttp_ref for decision in result.decisions if decision.ttp_ref != "Not provided"})
    lines.extend(f"- `{_cell(ref)}`" for ref in (refs or ["No reference supplied"]))
    lines.extend(["", "## Detailed Correlation Evidence", "",
                  "| Event source | Decision source | Asset | Event summary and details | Rationale | Outcome | Signed delta | Absolute delta |",
                  "|---|---|---|---|---|---|---:|---:|"])
    for link in result.links:
        lines.append(
            f"| {_cell(link.event.source)} | {_cell(link.decision.source)} | {_cell(link.event.asset)} | "
            f"{_cell(link.event.summary)} — {_cell(link.event.details)} | {_cell(link.decision.rationale)} | {_cell(link.decision.outcome)} | "
            f"{link.signed_delta_seconds:+d}s | {link.absolute_delta_seconds}s |"
        )
    if not result.links:
        lines.append("| — | — | — | No correlation | — | — | — | — |")
    lines.extend(["", "## Unlinked Records", "",
                  f"- Events: {len(result.unlinked_events)}", f"- Decisions: {len(result.unlinked_decisions)}", "",
                  "## Ingestion Warnings", ""])
    lines.extend(f"- {_cell(warning)}" for warning in (warnings or ["None"] ))
    lines.append("")
    return "\n".join(lines)
