#!/usr/bin/env python3
"""Executable ACCEPTANCE.md checks; exits nonzero on any failure."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "fixture"


def require(condition: bool, check: str, detail: str) -> None:
    if not condition:
        raise AssertionError(f"{check}: {detail}")
    print(f"PASS {check}: {detail}")


def main() -> int:
    subprocess.run([
        sys.executable, "-m", "after_action.cli", "testdata/fixture_engagement",
        "--output", "reports/fixture",
    ], cwd=ROOT, check=True)
    client = (REPORTS / "client_report.md").read_text(encoding="utf-8")
    html = (REPORTS / "client_report.html").read_text(encoding="utf-8")
    internal = (REPORTS / "internal_learning.md").read_text(encoding="utf-8")
    require(all((REPORTS / name).is_file() for name in ("client_report.md", "client_report.html", "internal_learning.md")), "A1", "fixture builds all reports")
    require("events.jsonl" in internal and "events.csv" in internal, "A2", "JSONL and CSV adapter provenance present")
    timeline_rows = sum(1 for line in client.splitlines() if line.startswith("| 20") and "exact normalized asset" in line)
    require(timeline_rows >= 5, "A3", f"correlated timeline has {timeline_rows} links")
    require(all(section in client for section in ("## Executive Summary", "## Correlated Timeline", "## Detection Recommendations")), "A4", "client sections present")
    require("## Successes" in internal and "## Failures" in internal, "A5", "internal learning sections present")
    planted = ("PLANTED_SECRET_CLIENT_CANARY", "lab-fixture-key-92831", "analyst@example.test", "fixture.header.signature")
    require(not any(value in client or value in html for value in planted), "A6", "planted secrets absent from both client exports")
    require("NOT CLIENT-SAFE" in internal and "does not pass through client redaction" in internal, "A7", "internal/client detail distinction documented")
    opsec = (ROOT / "OPSEC_CARD.md").read_text(encoding="utf-8")
    detection = opsec.split("## 5. Detection Recommendations", 1)[1] if "## 5. Detection Recommendations" in opsec else ""
    require("Detection Recommendations" in opsec and detection.count("\n-") >= 3, "A8", "OPSEC card has at least three detection bullets")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    require("authorized" in readme.casefold() and (ROOT / "ethics" / "AUTHORIZED_USE.md").is_file(), "A9", "authorized-use notice present")
    scanner_files = (ROOT / "scanner-output" / "semgrep.txt", ROOT / "scanner-output" / "ast-grep.txt")
    require(all(path.is_file() and path.stat().st_size > 0 for path in scanner_files), "A10", "scanner outputs archived")
    require(all((os.stat(REPORTS / name).st_mode & 0o777) == 0o600 for name in ("client_report.md", "client_report.html", "internal_learning.md")), "M3", "reports render with restrictive permissions despite fixture warnings")
    print("Manual M1: review client tone. Manual M2: review correlation assumptions and explanations.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, subprocess.CalledProcessError, OSError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
