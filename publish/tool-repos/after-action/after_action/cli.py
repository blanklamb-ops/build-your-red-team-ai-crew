"""Command-line orchestration for after-action reports."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .adapters import MAX_INPUT_BYTES, load_csv_events, load_decisions, load_jsonl_events
from .correlate import correlate
from .redact import load_rules
from .render import render_client_html, render_client_markdown, render_internal_markdown

DEFAULT_RULES = Path(__file__).resolve().parent.parent / "config" / "redaction_rules.json"


@dataclass(frozen=True)
class RunSummary:
    events: int
    decisions: int
    links: int
    warnings: int
    output_dir: Path


def _load_metadata(path: Path) -> dict:
    if not path.is_file():
        raise ValueError("required input file is missing: engagement.json")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("engagement.json exceeds the input size limit")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("engagement.json is malformed") from exc
    if not isinstance(value, dict):
        raise ValueError("engagement.json must contain a JSON object")
    return value


def _atomic_write(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
        os.chmod(path, 0o600)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def run(input_dir: Path, output_dir: Path, rules_path: Path, window_minutes: float) -> RunSummary:
    if not math.isfinite(window_minutes) or window_minutes <= 0:
        raise ValueError("window minutes must be a positive finite number")
    source = input_dir.expanduser().resolve()
    destination = output_dir.expanduser().resolve()
    if not source.is_dir():
        raise ValueError("input directory does not exist")
    if source == destination:
        raise ValueError("input and output directories must be different")
    if destination.exists() and not destination.is_dir():
        raise ValueError("output path exists and is not a directory")
    destination.mkdir(parents=True, mode=0o700, exist_ok=True)

    warnings: list[str] = []
    metadata = _load_metadata(source / "engagement.json")
    events = load_jsonl_events(source / "events.jsonl", warnings)
    events.extend(load_csv_events(source / "events.csv", warnings))
    decisions = load_decisions(source / "decisions.csv", warnings)
    if not events:
        raise ValueError("no valid events remain after ingestion")
    if not decisions:
        raise ValueError("no valid decisions remain after ingestion")
    result = correlate(events, decisions, round(window_minutes * 60))
    rules = load_rules(rules_path.expanduser().resolve())
    client_markdown = render_client_markdown(metadata, result, rules)
    client_html = render_client_html(client_markdown)
    internal_markdown = render_internal_markdown(metadata, result, warnings)
    _atomic_write(destination / "client_report.md", client_markdown)
    _atomic_write(destination / "client_report.html", client_html)
    _atomic_write(destination / "internal_learning.md", internal_markdown)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return RunSummary(len(events), len(decisions), len(result.links), len(warnings), destination)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Correlate authorized engagement evidence into after-action reports.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="dedicated report output directory")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES, help="redaction rule JSON")
    parser.add_argument("--window-minutes", type=float, default=10.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        summary = run(args.input_dir, args.output, args.rules, args.window_minutes)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception:
        print("error: unexpected report generation failure", file=sys.stderr)
        return 1
    print(f"rendered 3 reports: {summary.events} events, {summary.decisions} decisions, "
          f"{summary.links} links, {summary.warnings} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
