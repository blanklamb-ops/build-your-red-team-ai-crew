#!/usr/bin/env python3
"""Executable acceptance checklist for empire-advisor."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from empire_advisor.cli import analyze_fixture, main as cli_main  # noqa: E402
from empire_advisor.engine import Advisor  # noqa: E402
from empire_advisor.empire_plugin import Plugin  # noqa: E402


def check(condition: bool, check_id: str, description: str, failures: list[str]) -> None:
    label = "PASS" if condition else "FAIL"
    print(f"{label} {check_id}: {description}")
    if not condition:
        failures.append(check_id)


def run() -> int:
    failures: list[str] = []
    os.chdir(ROOT)

    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    stream = io.StringIO()
    unit_result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    check(unit_result.wasSuccessful(), "TESTS", "unit and integration suite", failures)
    if not unit_result.wasSuccessful():
        print(stream.getvalue())

    try:
        manifest = json.loads((ROOT / "plugin.yaml").read_text(encoding="utf-8"))
        plugin_result = json.loads(Plugin().execute({"Command": "whoami.exe /all"}))
        a1 = manifest["entrypoint"] == "empire_advisor.empire_plugin:Plugin" and plugin_result["state"] == "warn"
    except Exception:
        a1 = False
    check(a1, "A1", "plugin-shaped adapter and manifest load", failures)

    advisor = Advisor.default()
    fixture_results = dict(analyze_fixture(ROOT / "fixtures/commands.json", advisor))
    check(
        all(not result.execution_performed for result in fixture_results.values()),
        "A2",
        "fixture submissions return advice without execution",
        failures,
    )
    check(
        len(advisor.rules) >= 10 and all(rule.id and rule.rationale for rule in advisor.rules),
        "A3",
        "at least ten rules have ids and rationales",
        failures,
    )
    check(
        advisor.analyze("whoami /all").to_dict() == advisor.analyze("whoami /all").to_dict(),
        "A4",
        "same input produces identical advisory",
        failures,
    )
    suggestions = [item for result in fixture_results.values() for item in result.suggestions]
    check(
        any(item.template and item.citation.url.startswith(("http://", "https://")) for item in suggestions),
        "A5",
        "fixture produces a concrete suggestion with citation",
        failures,
    )
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        cli_status = cli_main(["--fixture", str(ROOT / "fixtures/commands.json"), "--format", "json"])
    check(cli_status == 0 and isinstance(json.loads(output.getvalue()), list), "A6", "offline fixture CLI works", failures)

    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    check(
        "Empire 5" in readme and "Empire 6" in readme and "shim" in readme.lower(),
        "A7",
        "README documents Empire compatibility and shim limits",
        failures,
    )
    opsec = (ROOT / "OPSEC_CARD.md").read_text(encoding="utf-8") if (ROOT / "OPSEC_CARD.md").exists() else ""
    detection_section = opsec.split("## Detection Recommendations", 1)
    detection_bullets = detection_section[1].count("\n- ") if len(detection_section) == 2 else 0
    check(detection_bullets >= 3, "A8", "OPSEC card has at least three detection recommendations", failures)
    check(
        "authorized security testing" in readme.lower()
        and (ROOT / "ethics/AUTHORIZED_USE.md").exists(),
        "A9",
        "authorized-use notice is present",
        failures,
    )
    archives = [ROOT / "scanner-output/semgrep.txt", ROOT / "scanner-output/ast-grep.txt"]
    valid_status = ("status: pass", "status: findings", "status: error", "status: not-installed")
    check(
        all(path.exists() and any(item in path.read_text(encoding="utf-8").lower() for item in valid_status) for path in archives),
        "A10",
        "Semgrep and ast-grep run records are archived",
        failures,
    )
    check(
        all(result.summary and all(hit.rationale for hit in result.matched_rules) for result in fixture_results.values()),
        "M1",
        "rendered data carries understandable scoring rationale (manual wording review still required)",
        failures,
    )
    check(
        bool(suggestions) and all(item.template and item.citation.title for item in suggestions),
        "M2",
        "suggestions are concrete KB templates with citations (manual suitability review still required)",
        failures,
    )
    check(
        fixture_results["destructive-log-clear"].state == "deny"
        and fixture_results["security-control-change"].state == "deny",
        "M3",
        "dangerous fixture rules produce deny advisories",
        failures,
    )

    if failures:
        print(f"\nAcceptance failed: {', '.join(failures)}")
        return 1
    print("\nAll automated acceptance checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
