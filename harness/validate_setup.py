#!/usr/bin/env python3
"""Structural validation for the methodology harness (pre-run gate)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ["chrome-mv3-kit", "gophish-ics", "empire-advisor", "after-action"]
CONDS = ["c1", "c2", "c3", "c4"]
AGENTS = [
    "01_domain_researcher.md",
    "02_planner.md",
    "03_ops_advisor.md",
    "04_tool_architect.md",
    "05_opsec_reviewer.md",
]


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def req_ids(text: str) -> set[str]:
    return set(re.findall(r"\bR\d+\b", text))


def accept_ids(text: str) -> set[str]:
    return set(re.findall(r"\bA\d+\b", text))


def main() -> int:
    errors: list[str] = []
    checks = 0

    # Core files
    for rel in [
        "protocol.md",
        "README.md",
        "OPERATOR_NEXT.md",
        "mcp/SHARED_MCP.md",
        "ethics/AUTHORIZED_USE.md",
        "analysis/comparison.csv",
        "conditions/c1-claude-single/README.md",
        "conditions/c2-claude-pipeline/README.md",
        "conditions/c3-codex-pipeline/README.md",
        "conditions/c3-codex-pipeline/AGENTS.md",
        "conditions/c4-ollama-codestral-crewai/README.md",
        "conditions/c4-ollama-codestral-crewai/MODEL_PIN.md",
        "conditions/c4-ollama-codestral-crewai/run_pipeline.py",
        "rubric/dimensions.md",
        "rubric/SCORING_PROCEDURE.md",
    ]:
        checks += 1
        if not (ROOT / rel).is_file():
            fail(f"missing {rel}", errors)

    for name in AGENTS:
        checks += 1
        if not (ROOT / "agents" / name).is_file():
            fail(f"missing agents/{name}", errors)

    # Prompts + acceptance
    for tool in TOOLS:
        prompt = ROOT / "prompts" / tool / "PROMPT.md"
        accept = ROOT / "prompts" / tool / "ACCEPTANCE.md"
        checks += 2
        if not prompt.is_file():
            fail(f"missing {prompt.relative_to(ROOT)}", errors)
            continue
        if not accept.is_file():
            fail(f"missing {accept.relative_to(ROOT)}", errors)
            continue
        ptext = prompt.read_text(encoding="utf-8")
        atext = accept.read_text(encoding="utf-8")
        checks += 3
        if "Authorized use" not in ptext and "authorized use" not in ptext.lower():
            fail(f"{tool}: PROMPT missing authorized-use language", errors)
        rids = req_ids(ptext)
        if not {"R1", "R10"}.issubset(rids):
            fail(f"{tool}: PROMPT missing R1/R10 (found {sorted(rids)})", errors)
        aids = accept_ids(atext)
        if not {"A1", "A10"}.issubset(aids):
            fail(f"{tool}: ACCEPTANCE missing A1/A10 (found {sorted(aids)})", errors)
        if tool == "chrome-mv3-kit":
            checks += 3
            fixture = ROOT / "prompts" / tool / "fixtures" / "regression-mixed-capture.json"
            if not fixture.is_file():
                fail("chrome-mv3-kit: missing prompts/.../fixtures/regression-mixed-capture.json", errors)
            else:
                ftext = fixture.read_text(encoding="utf-8")
                if "set_cookie_names" not in ftext or "form_fields" not in ftext:
                    fail("chrome-mv3-kit: regression fixture missing recorder fields", errors)
                if "uhf-exp-fd-gbcrdgggfbggh0g3" not in ftext:
                    fail("chrome-mv3-kit: regression fixture missing PSL junk-host trap", errors)
            if "A5e" not in atext or "R4g" not in ptext or "R12" not in ptext:
                fail("chrome-mv3-kit: PROMPT/ACCEPTANCE missing R4g/R12/A5e", errors)
            if "2.3.0" not in ptext or "2.3.0" not in atext:
                fail("chrome-mv3-kit: PROMPT/ACCEPTANCE must target Evilginx 2.3.0", errors)
            schema_ref = ROOT / "prompts" / tool / "fixtures" / "phishlet-schema-2.3.0.json"
            if not schema_ref.is_file():
                fail("chrome-mv3-kit: missing fixtures/phishlet-schema-2.3.0.json", errors)

    # Run matrix folders
    for tool in TOOLS:
        for c in CONDS:
            base = ROOT / "runs" / tool / c
            for name in ["RUN_LOG.md", "interventions.csv", "acceptance_results.md"]:
                checks += 1
                if not (base / name).is_file():
                    fail(f"missing runs/{tool}/{c}/{name}", errors)
            for d in ["transcript", "workspace", "scanners", "pipeline"]:
                checks += 1
                if not (base / d).is_dir():
                    fail(f"missing runs/{tool}/{c}/{d}/", errors)

    # comparison.csv has 16 data rows
    csv_path = ROOT / "analysis" / "comparison.csv"
    if csv_path.is_file():
        lines = [ln for ln in csv_path.read_text().splitlines() if ln.strip()]
        checks += 1
        if len(lines) != 17:  # header + 16
            fail(f"comparison.csv expected 17 lines, got {len(lines)}", errors)

    # C4 must mention Codestral + Ollama
    c4 = (ROOT / "conditions/c4-ollama-codestral-crewai/README.md").read_text(encoding="utf-8")
    checks += 2
    if "Codestral" not in c4 and "codestral" not in c4:
        fail("C4 README missing Codestral", errors)
    if "Ollama" not in c4 and "ollama" not in c4:
        fail("C4 README missing Ollama", errors)

    # Protocol RQs
    proto = (ROOT / "protocol.md").read_text(encoding="utf-8")
    checks += 1
    if not all(x in proto for x in ["RQ1", "RQ2", "RQ3"]):
        fail("protocol.md missing RQ1–RQ3", errors)

    print(f"checks_run={checks}")
    if errors:
        print(f"FAIL ({len(errors)} errors)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: harness structure, prompts, run matrix, and C4 Codestral lock look consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
