#!/usr/bin/env python3
"""Assemble C1/C2 kickoff messages and verify prompt files are readable."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = "after-action"


def main() -> int:
    prompt = (ROOT / "prompts" / TOOL / "PROMPT.md").read_text(encoding="utf-8")
    accept = (ROOT / "prompts" / TOOL / "ACCEPTANCE.md").read_text(encoding="utf-8")
    c1 = (ROOT / "conditions/c1-claude-single/README.md").read_text(encoding="utf-8")
    c2 = (ROOT / "conditions/c2-claude-pipeline/README.md").read_text(encoding="utf-8")

    assert "You are implementing the tool described in PROMPT.md" in c1
    assert "five-stage pipeline" in c2.lower() or "five-stage" in c2.lower() or "Five-agent" in c2 or "five roles" in c2.lower() or "five-stage pipeline" in c2
    # C2 uses "five-stage" in kickoff
    assert "agents/01_domain_researcher.md" in c2
    assert "R1" in prompt and "R10" in prompt
    assert "A1" in accept and "A10" in accept

    out = ROOT / "analysis" / "pilots" / "kickoff_smoke.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"# Kickoff smoke — {TOOL}\n\n"
        f"## PROMPT bytes\n{len(prompt)}\n\n"
        f"## ACCEPTANCE bytes\n{len(accept)}\n\n"
        f"## C1 kickoff present\nyes\n\n"
        f"## C2 persona refs present\nyes\n",
        encoding="utf-8",
    )
    print(f"PASS: kickoff assembly for {TOOL} ({len(prompt)} + {len(accept)} bytes)")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"FAIL: {e}")
        raise SystemExit(1)
