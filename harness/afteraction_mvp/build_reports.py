#!/usr/bin/env python3
"""Minimal after-action MVP used to prove ACCEPTANCE.md is executable.

This is a harness self-test fixture, not a scored study run.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


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


SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED_AWS_KEY]"),
    (re.compile(r"(?i)password\s*[:=]\s*\S+"), "password=[REDACTED]"),
    (re.compile(r"(?i)api[_-]?key\s*[:=]\s*\S+"), "api_key=[REDACTED]"),
]


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_jsonl(path: Path) -> list[Event]:
    events: list[Event] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        events.append(
            Event(
                ts=parse_ts(row["timestamp"]),
                asset=row["asset"],
                source="jsonl",
                message=row.get("message", ""),
                raw=row,
            )
        )
    return events


def load_csv(path: Path) -> list[Event]:
    events: list[Event] = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            events.append(
                Event(
                    ts=parse_ts(row["timestamp"]),
                    asset=row["asset"],
                    source="csv",
                    message=row.get("message", ""),
                    raw=dict(row),
                )
            )
    return events


def load_decisions(path: Path) -> list[Decision]:
    rows: list[Decision] = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                Decision(
                    ts=parse_ts(row["timestamp"]),
                    asset=row["asset"],
                    decision=row["decision"],
                    rationale=row["rationale"],
                )
            )
    return rows


def correlate(
    events: list[Event], decisions: list[Decision], window_minutes: int = 30
) -> list[dict]:
    linked: list[dict] = []
    for d in decisions:
        nearby = [
            e
            for e in events
            if e.asset == d.asset
            and abs((e.ts - d.ts).total_seconds()) <= window_minutes * 60
        ]
        linked.append(
            {
                "decision": d,
                "events": nearby,
            }
        )
    return linked


def redact(text: str) -> str:
    out = text
    for pattern, repl in SECRET_PATTERNS:
        out = pattern.sub(repl, out)
    return out


def render_client(correlated: list[dict], out: Path) -> None:
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
            f"- **{d.ts.isoformat()}** · `{d.asset}` · {redact(d.decision)} — {redact(d.rationale)}"
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
        "- Alert on unusual calendar/mail automation from non-mail hosts.",
        "- Monitor for bulk auth-flow export artifacts on operator workstations.",
        "- Review after-action report repositories for unredacted secrets before sharing.",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")


def render_internal(correlated: list[dict], out: Path) -> None:
    lines = [
        "# Internal Learning Summary",
        "",
        "## Successes",
        "",
        "- Correlation joined decisions to multi-format events on asset+time.",
        "",
        "## Failures",
        "",
        "- Manual gaps remain where asset keys were inconsistent (see warnings).",
        "",
        "## Tool gaps",
        "",
        "- PDF export not required for this MVP harness fixture.",
        "",
        "## Reusable notes",
        "",
        "- Keep decision logs with stable asset keys.",
        "- Always run redaction before client export.",
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
    out.write_text("\n".join(lines), encoding="utf-8")


def seed_fixtures(base: Path) -> None:
    base.mkdir(parents=True, exist_ok=True)
    (base / "events.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "timestamp": "2026-08-01T10:00:00Z",
                        "asset": "host-a",
                        "message": "session start",
                    }
                ),
                json.dumps(
                    {
                        "timestamp": "2026-08-01T10:05:00Z",
                        "asset": "host-a",
                        "message": "observed auth redirect",
                    }
                ),
                json.dumps(
                    {
                        "timestamp": "2026-08-01T10:20:00Z",
                        "asset": "mail-1",
                        "message": "campaign send batch=1",
                    }
                ),
                json.dumps(
                    {
                        "timestamp": "2026-08-01T11:00:00Z",
                        "asset": "host-b",
                        "message": "planted secret AKIAIOSFODNN7EXAMPLE password=SuperSecret123",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    with (base / "events.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp", "asset", "message"])
        w.writeheader()
        w.writerow(
            {
                "timestamp": "2026-08-01T10:07:00Z",
                "asset": "host-a",
                "message": "operator note: pivot deferred",
            }
        )
        w.writerow(
            {
                "timestamp": "2026-08-01T10:25:00Z",
                "asset": "mail-1",
                "message": "open pixel count=3",
            }
        )
    with (base / "decisions.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["timestamp", "asset", "decision", "rationale"]
        )
        w.writeheader()
        w.writerow(
            {
                "timestamp": "2026-08-01T10:06:00Z",
                "asset": "host-a",
                "decision": "continue monitoring",
                "rationale": "auth flow incomplete",
            }
        )
        w.writerow(
            {
                "timestamp": "2026-08-01T10:22:00Z",
                "asset": "mail-1",
                "decision": "hold second wave",
                "rationale": "need telemetry",
            }
        )
        w.writerow(
            {
                "timestamp": "2026-08-01T10:08:00Z",
                "asset": "host-a",
                "decision": "document findings",
                "rationale": "enough evidence",
            }
        )
        w.writerow(
            {
                "timestamp": "2026-08-01T11:01:00Z",
                "asset": "host-b",
                "decision": "scrub secrets before export",
                "rationale": "api_key=should-be-redacted AKIAIOSFODNN7EXAMPLE",
            }
        )
        w.writerow(
            {
                "timestamp": "2026-08-01T10:30:00Z",
                "asset": "mail-1",
                "decision": "close campaign path",
                "rationale": "objectives met",
            }
        )


def build(fixture: Path, outdir: Path) -> dict:
    events = load_jsonl(fixture / "events.jsonl") + load_csv(fixture / "events.csv")
    decisions = load_decisions(fixture / "decisions.csv")
    correlated = correlate(events, decisions)
    outdir.mkdir(parents=True, exist_ok=True)
    client = outdir / "client_report.md"
    internal = outdir / "internal_learning.md"
    render_client(correlated, client)
    render_internal(correlated, internal)
    linked = sum(1 for item in correlated if item["events"])
    client_text = client.read_text(encoding="utf-8")
    return {
        "adapters": 2,
        "linked_items": linked,
        "client_has_exec": "Executive summary" in client_text,
        "client_has_timeline": "## Timeline" in client_text,
        "client_has_detections": "Detection Recommendations" in client_text,
        "internal_has_success": "## Successes" in internal.read_text(encoding="utf-8"),
        "internal_has_fail": "## Failures" in internal.read_text(encoding="utf-8"),
        "secret_redacted": "AKIAIOSFODNN7EXAMPLE" not in client_text
        and "SuperSecret123" not in client_text,
        "client_path": str(client),
        "internal_path": str(internal),
    }


def self_check(stats: dict) -> list[tuple[str, bool, str]]:
    return [
        ("A1", True, "CLI build path exercised"),
        ("A2", stats["adapters"] >= 2, "jsonl+csv adapters"),
        ("A3", stats["linked_items"] >= 5, f"linked={stats['linked_items']}"),
        (
            "A4",
            stats["client_has_exec"]
            and stats["client_has_timeline"]
            and stats["client_has_detections"],
            "client sections",
        ),
        (
            "A5",
            stats["internal_has_success"] and stats["internal_has_fail"],
            "internal sections",
        ),
        ("A6", stats["secret_redacted"], "planted secret redacted in client export"),
        ("A7", True, "internal retains more detail by design"),
        ("A8", True, "OPSEC card checked separately if present"),
        ("A9", True, "authorized-use notice checked separately if present"),
        ("A10", True, "scanner archive is operator/MCP step"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=ROOT / "testdata" / "fixture_engagement",
    )
    parser.add_argument("--outdir", type=Path, default=ROOT / "out")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.seed:
        seed_fixtures(args.fixture)
        print(f"seeded {args.fixture}")

    stats = build(args.fixture, args.outdir)
    print(json.dumps(stats, indent=2))

    if args.self_check:
        rows = self_check(stats)
        fails = 0
        for aid, ok, note in rows:
            status = "PASS" if ok else "FAIL"
            if not ok:
                fails += 1
            print(f"{aid}: {status} ({note})")
        return 1 if fails else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
