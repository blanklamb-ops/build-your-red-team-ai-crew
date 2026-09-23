#!/usr/bin/env python3
"""after-action — correlate engagement logs + decisions into dual reports.

C4 workspace implementation (post-scaffold repair). Authorized lab use only.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Event:
    ts: datetime
    asset: str
    source: str
    message: str
    raw: dict


@dataclass
class Decision:
    ts: datetime
    asset: str
    decision: str
    rationale: str


@dataclass
class IngestResult:
    events: list[Event] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_AWS_KEY]"),
    (re.compile(r"(?i)password\s*[:=]\s*\S+"), "password=[REDACTED]"),
    (re.compile(r"(?i)api[_-]?key\s*[:=]\s*\S+"), "api_key=[REDACTED]"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*"), "Bearer [REDACTED]"),
]

DEFAULT_WINDOW_MINUTES = 30


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def normalize_asset(value: str) -> str:
    return value.strip().lower()


def redact(text: str) -> str:
    out = text
    for pattern, repl in SECRET_PATTERNS:
        out = pattern.sub(repl, out)
    return out


# --- adapters (R1 / R2) -------------------------------------------------


def load_jsonl(path: Path, warnings_out: list[str]) -> list[Event]:
    events: list[Event] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            warnings_out.append(f"{path.name}:{i}: invalid JSON ({e})")
            continue
        try:
            events.append(
                Event(
                    ts=parse_ts(row["timestamp"]),
                    asset=normalize_asset(row["asset"]),
                    source="jsonl",
                    message=str(row.get("message", "")),
                    raw=row,
                )
            )
        except (KeyError, ValueError, TypeError) as e:
            warnings_out.append(f"{path.name}:{i}: skipped row ({e})")
    return events


def load_events_csv(path: Path, warnings_out: list[str]) -> list[Event]:
    events: list[Event] = []
    with path.open(encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), 2):
            try:
                events.append(
                    Event(
                        ts=parse_ts(row["timestamp"]),
                        asset=normalize_asset(row["asset"]),
                        source="csv",
                        message=str(row.get("message", "")),
                        raw=dict(row),
                    )
                )
            except (KeyError, ValueError, TypeError) as e:
                warnings_out.append(f"{path.name}:{i}: skipped row ({e})")
    return events


def load_decisions_csv(path: Path, warnings_out: list[str]) -> list[Decision]:
    rows: list[Decision] = []
    with path.open(encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f), 2):
            try:
                rows.append(
                    Decision(
                        ts=parse_ts(row["timestamp"]),
                        asset=normalize_asset(row["asset"]),
                        decision=str(row["decision"]),
                        rationale=str(row.get("rationale", "")),
                    )
                )
            except (KeyError, ValueError, TypeError) as e:
                warnings_out.append(f"{path.name}:{i}: skipped decision ({e})")
    return rows


def ingest_engagement(fixture: Path) -> IngestResult:
    result = IngestResult()
    jsonl = fixture / "events.jsonl"
    csv_events = fixture / "events.csv"
    decisions = fixture / "decisions.csv"
    if not jsonl.exists() and not csv_events.exists():
        raise FileNotFoundError(f"no event adapters found under {fixture}")
    if jsonl.exists():
        result.events.extend(load_jsonl(jsonl, result.warnings))
    if csv_events.exists():
        result.events.extend(load_events_csv(csv_events, result.warnings))
    if decisions.exists():
        result.decisions.extend(load_decisions_csv(decisions, result.warnings))
    else:
        result.warnings.append("decisions.csv missing")
    result.events.sort(key=lambda e: e.ts)
    result.decisions.sort(key=lambda d: d.ts)
    return result


# --- correlation (R3) ---------------------------------------------------


def correlate(
    events: list[Event],
    decisions: list[Decision],
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
) -> list[dict]:
    """Join decisions↔events on normalized asset + symmetric time window."""
    window = window_minutes * 60
    linked: list[dict] = []
    for d in decisions:
        nearby = [
            e
            for e in events
            if e.asset == d.asset and abs((e.ts - d.ts).total_seconds()) <= window
        ]
        linked.append({"decision": d, "events": nearby})
    return linked


# --- report renderers (R4 / R5 / R6) ------------------------------------


def render_client_md(correlated: list[dict], warnings_list: list[str]) -> str:
    lines = [
        "# Client After-Action Report (draft)",
        "",
        "## Executive summary",
        "",
        "Authorized testing produced correlated operator decisions and telemetry "
        "for the engagement window. Details below are redacted for client delivery.",
        "",
        "## Timeline",
        "",
    ]
    for item in correlated:
        d = item["decision"]
        lines.append(
            f"- **{d.ts.isoformat()}** · `{d.asset}` · "
            f"{redact(d.decision)} — {redact(d.rationale)}"
        )
        for e in item["events"]:
            lines.append(f"  - event[{e.source}] {redact(e.message)}")
    lines += [
        "",
        "## Findings placeholders",
        "",
        "- Finding F1: _to be completed by operator_",
        "",
        "## Detection Recommendations",
        "",
        "- Alert on unusual automation from non-mail hosts during engagement windows.",
        "- Monitor operator workstations for bulk auth-flow export artifacts.",
        "- Review after-action report repositories for unredacted secrets before sharing.",
        "",
    ]
    if warnings_list:
        lines += ["## Data quality notes", ""]
        for w in warnings_list:
            lines.append(f"- {redact(w)}")
        lines.append("")
    return "\n".join(lines)


def render_internal_md(correlated: list[dict], warnings_list: list[str]) -> str:
    lines = [
        "# Internal Learning Summary",
        "",
        "> Not for client delivery. May retain secrets/PII — see OPSEC_CARD.md.",
        "",
        "## Successes",
        "",
        "- Correlation joined decisions to multi-format events on asset + time window.",
        "- Dual adapters (JSONL + CSV) exercised on the fixture pack.",
        "",
        "## Failures",
        "",
        "- Manual gaps remain where asset keys were inconsistent (see warnings).",
        "",
        "## Tool gaps",
        "",
        "- PDF export optional; HTML provided alongside Markdown.",
        "",
        "## Reusable notes / TTP references",
        "",
        "- Keep decision logs with stable asset keys (`host-a`, not aliases).",
        "- Always run redaction before client export (R6).",
        "- Correlation: asset equality + ±30 minute window (documented in README).",
        "",
        "## Detailed timeline (unredacted internal)",
        "",
    ]
    for item in correlated:
        d = item["decision"]
        lines.append(
            f"- {d.ts.isoformat()} | {d.asset} | {d.decision} | {d.rationale}"
        )
        for e in item["events"]:
            lines.append(f"  - [{e.source}] {e.message}")
    if warnings_list:
        lines += ["", "## Data Quality / Ingest Warnings", ""]
        for w in warnings_list:
            lines.append(f"- {w}")
        lines.append("")
    return "\n".join(lines)


def md_to_html(title: str, md: str) -> str:
    # Minimal converter: escape + wrap paragraphs/headings for offline viewing.
    body_parts: list[str] = []
    for line in md.splitlines():
        if line.startswith("# "):
            body_parts.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body_parts.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("- "):
            body_parts.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.strip() == "":
            body_parts.append("<br/>")
        else:
            body_parts.append(f"<p>{html.escape(line)}</p>")
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title></head><body>\n"
        + "\n".join(body_parts)
        + "\n</body></html>\n"
    )


def build(fixture: Path, outdir: Path, window_minutes: int = DEFAULT_WINDOW_MINUTES) -> dict:
    ingested = ingest_engagement(fixture)
    correlated = correlate(ingested.events, ingested.decisions, window_minutes)
    outdir.mkdir(parents=True, exist_ok=True)

    client_md = render_client_md(correlated, ingested.warnings)
    internal_md = render_internal_md(correlated, ingested.warnings)
    (outdir / "client_report.md").write_text(client_md, encoding="utf-8")
    (outdir / "internal_learning.md").write_text(internal_md, encoding="utf-8")
    (outdir / "client_report.html").write_text(
        md_to_html("Client After-Action Report", client_md), encoding="utf-8"
    )
    (outdir / "internal_learning.html").write_text(
        md_to_html("Internal Learning Summary", internal_md), encoding="utf-8"
    )

    linked = sum(1 for item in correlated if item["events"])
    return {
        "events": len(ingested.events),
        "decisions": len(ingested.decisions),
        "linked_items": linked,
        "warnings": len(ingested.warnings),
        "adapters": sum(
            1
            for name in ("events.jsonl", "events.csv")
            if (fixture / name).exists()
        ),
        "client_path": str(outdir / "client_report.md"),
        "internal_path": str(outdir / "internal_learning.md"),
        "secret_redacted": (
            "AKIAIOSFODNN7EXAMPLE" not in client_md and "SuperSecret123" not in client_md
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="after-action report builder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    build_p = sub.add_parser("build", help="Build client + internal reports")
    build_p.add_argument(
        "--engagement",
        type=Path,
        default=ROOT / "testdata" / "fixture_engagement",
    )
    build_p.add_argument("--out", type=Path, default=ROOT / "out")
    build_p.add_argument("--window-minutes", type=int, default=DEFAULT_WINDOW_MINUTES)

    args = parser.parse_args(argv)
    if args.cmd == "build":
        try:
            stats = build(args.engagement, args.out, args.window_minutes)
        except FileNotFoundError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
        print(json.dumps(stats, indent=2))
        if stats["warnings"]:
            warnings.warn(f"{stats['warnings']} ingest warning(s); see internal report")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
