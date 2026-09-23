#!/usr/bin/env python3
"""Detect stub / placeholder implementations after C4 materialize."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

STUB_PATTERNS = [
    re.compile(r"(?i)omitted for brevity"),
    re.compile(r"(?i)implementation details omitted"),
    re.compile(r"(?i)test cases omitted"),
    re.compile(r"(?i)\bTODO\b.*\bimplement\b"),
    re.compile(r"(?m)^\s*pass\s*$"),
]


def scan(workspace: Path) -> list[tuple[Path, str]]:
    hits: list[tuple[Path, str]] = []
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".js", ".ts", ".mjs", ".go"}:
            continue
        if "pipeline" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pat in STUB_PATTERNS:
            if pat.search(text):
                hits.append((path, pat.pattern))
                break
    return hits


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", type=Path, required=True)
    args = p.parse_args()
    hits = scan(args.workspace.resolve())
    if not hits:
        print("stub_scan: clean")
        return 0
    print(f"stub_scan: {len(hits)} suspicious file(s)")
    for path, pat in hits:
        print(f"  {path}: /{pat}/")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
