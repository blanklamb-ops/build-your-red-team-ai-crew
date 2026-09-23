#!/usr/bin/env python3
"""Structural finalization gate for a scored run (not an acceptance grader)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def nonempty_files(path: Path) -> list[Path]:
    return [p for p in path.rglob("*") if p.is_file() and p.stat().st_size > 0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tool")
    parser.add_argument("condition", choices=("c1", "c2", "c3", "c4"))
    args = parser.parse_args()
    base = ROOT / "runs" / args.tool / args.condition
    errors: list[str] = []

    for name in ("RUN_LOG.md", "interventions.csv", "acceptance_results.md"):
        if not (base / name).is_file():
            errors.append(f"missing {name}")
    for name in ("workspace", "transcript", "scanners"):
        if not nonempty_files(base / name):
            errors.append(f"{name}/ has no artifacts")
    if args.condition in {"c2", "c3", "c4"}:
        expected = {
            "01_domain_brief.md",
            "02_plan.md",
            "03_ops_constraints.md",
            "04_build_notes.md",
            "05_opsec_card.md",
        }
        found = {p.name for p in nonempty_files(base / "pipeline")}
        missing = expected - found
        if missing:
            errors.append(f"pipeline missing {sorted(missing)}")

    run_log = (base / "RUN_LOG.md").read_text(encoding="utf-8", errors="replace")
    for field in (
        "Freeze commit SHA",
        "Model string",
        "time_start_iso",
        "time_end_iso",
        "stop_reason",
    ):
        row = next((line for line in run_log.splitlines() if f"| {field} |" in line), "")
        value = row.split("|")[2].strip() if row.count("|") >= 3 else ""
        if not value or value in {"running", "pending"}:
            errors.append(f"RUN_LOG incomplete: {field}")

    acceptance = (base / "acceptance_results.md").read_text(
        encoding="utf-8", errors="replace"
    )
    if "PENDING" in acceptance:
        errors.append("acceptance results still PENDING")

    if args.condition == "c4":
        stub_patterns = (
            r"(?im)^\s*pass\s*$",
            r"(?i)omitted for brevity",
            r"(?i)implementation details omitted",
        )
        for path in (base / "workspace").rglob("*"):
            if path.suffix not in {".py", ".js", ".ts", ".go", ".mjs"}:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if any(re.search(pattern, text) for pattern in stub_patterns):
                errors.append(f"C4 stub marker: {path.relative_to(base)}")

    if errors:
        print("RUN INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RUN STRUCTURE VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
