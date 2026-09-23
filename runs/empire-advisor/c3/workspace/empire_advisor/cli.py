"""Offline command-line interface for the advisory engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from .engine import Advisor, ROOT
from .models import Advisory, AdvisorError, InputError


def load_fixture(path: Path) -> list[dict[str, str]]:
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read fixture {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid fixture JSON in {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != "1.0":
        raise InputError("fixture must be an object with schema_version '1.0'")
    rows = data.get("commands")
    if not isinstance(rows, list) or not rows:
        raise InputError("fixture commands must be a non-empty array")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise InputError(f"fixture commands[{index}] must be an object")
        fixture_id, command = row.get("id"), row.get("command")
        source = row.get("source", "fixture")
        if not isinstance(fixture_id, str) or not fixture_id.strip():
            raise InputError(f"fixture commands[{index}].id must be a non-empty string")
        if fixture_id in seen:
            raise InputError(f"duplicate fixture id: {fixture_id}")
        if not isinstance(command, str) or not command.strip():
            raise InputError(f"fixture commands[{index}].command must be a non-empty string")
        if not isinstance(source, str) or not source.strip():
            raise InputError(f"fixture commands[{index}].source must be a non-empty string")
        seen.add(fixture_id)
        result.append({"id": fixture_id, "command": command, "source": source})
    return result


def analyze_fixture(path: Path, advisor: Advisor) -> list[tuple[str, Advisory]]:
    return [
        (row["id"], advisor.analyze(row["command"], source=row["source"]))
        for row in load_fixture(path)
    ]


def render_text(advisory: Advisory, *, fixture_id: str | None = None) -> str:
    lines = []
    if fixture_id is not None:
        lines.append(f"Fixture: {fixture_id}")
    lines.extend(
        [
            f"State: {advisory.state.upper()} (advisory only)",
            f"Score: {advisory.score}/100",
            f"Command: {advisory.command}",
            f"Summary: {advisory.summary}",
            "Matched rules:",
        ]
    )
    if advisory.matched_rules:
        for hit in advisory.matched_rules:
            lines.append(
                f"  - {hit.id} [{hit.severity}, +{hit.weight}]: {hit.rationale} Evidence: {hit.evidence!r}"
            )
    else:
        lines.append("  - none")
    lines.append("Suggestions (never auto-executed):")
    if advisory.suggestions:
        for suggestion in advisory.suggestions:
            lines.extend(
                [
                    f"  - {suggestion.id}: {suggestion.title}",
                    f"    Template: {suggestion.template}",
                    f"    Why: {suggestion.rationale}",
                    f"    Citation: {suggestion.citation.title} — {suggestion.citation.url}",
                ]
            )
    else:
        lines.append("  - none")
    lines.append("Execution performed: false")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="empire-advisor",
        description="Analyze command text offline; never submits or executes commands.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--command", help="command text to analyze (quote carefully)")
    source.add_argument("--fixture", type=Path, help="JSON fixture transcript to analyze")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--rules", type=Path, default=ROOT / "rules.yaml")
    parser.add_argument("--kb", type=Path, default=ROOT / "kb.yaml")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        advisor = Advisor.from_paths(args.rules, args.kb)
        if args.command is not None:
            advisory = advisor.analyze(args.command)
            output: Any = advisory.to_dict()
            rendered = json.dumps(output, indent=2, ensure_ascii=False) if args.format == "json" else render_text(advisory)
        else:
            results = analyze_fixture(args.fixture, advisor)
            if args.format == "json":
                rendered = json.dumps(
                    [{"fixture_id": fixture_id, **advisory.to_dict()} for fixture_id, advisory in results],
                    indent=2,
                    ensure_ascii=False,
                )
            else:
                rendered = "\n\n".join(
                    render_text(advisory, fixture_id=fixture_id) for fixture_id, advisory in results
                )
        print(rendered)
        return 0
    except AdvisorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
