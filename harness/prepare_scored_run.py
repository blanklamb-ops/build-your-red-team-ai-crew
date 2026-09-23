#!/usr/bin/env python3
"""Create a fresh, provenance-stamped workspace for one scored run."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ("chrome-mv3-kit", "gophish-ics", "empire-advisor", "after-action")
CONDITIONS = ("c1", "c2", "c3", "c4")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def freeze_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-list", "-n", "1", "freeze-v1.0"], cwd=ROOT, text=True
    ).strip()


def archive_existing(base: Path) -> None:
    names = ("workspace", "pipeline", "scanners", "transcript")
    has_data = any(
        p.is_file() and p.name != ".gitkeep"
        for name in names
        for p in (base / name).rglob("*")
    )
    if not has_data:
        for name in names:
            shutil.rmtree(base / name, ignore_errors=True)
        return

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = base / f"pre_freeze_or_prior_{stamp}"
    archive.mkdir(parents=True)
    for name in names:
        src = base / name
        if src.exists():
            shutil.move(str(src), archive / name)
    for name in ("RUN_LOG.md", "interventions.csv", "acceptance_results.md"):
        src = base / name
        if src.exists():
            shutil.copy2(src, archive / name)
    print(f"archived prior artifacts: {archive.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=TOOLS)
    parser.add_argument("condition", choices=CONDITIONS)
    args = parser.parse_args()

    sha = freeze_sha()
    base = ROOT / "runs" / args.tool / args.condition
    base.mkdir(parents=True, exist_ok=True)
    archive_existing(base)

    for name in ("workspace", "pipeline", "scanners", "transcript"):
        (base / name).mkdir(parents=True, exist_ok=True)
        (base / name / ".gitkeep").touch()

    ws = base / "workspace"
    copies = {
        ROOT / "prompts" / args.tool / "PROMPT.md": ws / "PROMPT.md",
        ROOT / "prompts" / args.tool / "ACCEPTANCE.md": ws / "ACCEPTANCE.md",
        ROOT / "ethics" / "AUTHORIZED_USE.md": ws / "AUTHORIZED_USE.md",
        ROOT / "rubric" / "OPSEC_CARD_TEMPLATE.md": ws / "OPSEC_CARD_TEMPLATE.md",
    }
    for src, dest in copies.items():
        shutil.copy2(src, dest)

    fixtures = ROOT / "prompts" / args.tool / "fixtures"
    if fixtures.is_dir():
        dest = ws / "study-fixtures"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(fixtures, dest)

    if args.condition in {"c2", "c3"}:
        shutil.copytree(ROOT / "agents", ws / "agents")
    if args.condition == "c3":
        shutil.copy2(
            ROOT / "conditions" / "c3-codex-pipeline" / "AGENTS.md",
            ws / "AGENTS.md",
        )

    started = utc_now()
    host = {
        "c1": "Claude Code 2.1.259",
        "c2": "Claude Code 2.1.259",
        "c3": "Codex CLI 0.147.0",
        "c4": "CrewAI 1.15.18 + Ollama on Windows host",
    }[args.condition]
    model = {
        "c1": "claude-sonnet-4-5",
        "c2": "claude-sonnet-4-5",
        "c3": "record from Codex transcript",
        "c4": "ollama/codestral digest 0898a8b286d5...",
    }[args.condition]
    pipeline_mode = "staged-single-session" if args.condition == "c2" else "n/a"
    network = "private-network" if args.condition == "c4" else "n/a"
    (base / "RUN_LOG.md").write_text(
        f"""# RUN_LOG — `{args.tool}` / `{args.condition}`

| Field | Value |
|-------|-------|
| Freeze commit SHA | `{sha}` |
| Operator | automated scored-run harness |
| Host product + version | {host} |
| Model string | {model} |
| C4 Codestral pin (if c4) | `0898a8b286d5…`, Q4_0, 22.2B |
| Scanner versions | Semgrep 1.176.0 · ast-grep 0.45.3 |
| Serena available / used | no / no |
| ACCEPTANCE.md attached to model? | yes |
| Pipeline mode (c2) | {pipeline_mode} |
| Network mode (c4) | {network} |
| time_start_iso | {started} |
| time_first_accept_attempt_iso | |
| time_end_iso | |
| time_minutes | |
| stop_reason | running |
| interventions_count | 0 |
| quality notes (optional) | |

## Preflight checklist

- [x] Fresh workspace
- [x] Correct condition config
- [x] Scanner versions captured
- [x] Frozen prompt copied unchanged

## Postflight checklist

- [ ] transcript archived
- [ ] scanners archived
- [ ] acceptance_results.md filled
- [ ] interventions.csv filled
- [ ] pipeline/ present if c2–c4
""",
        encoding="utf-8",
    )
    (base / "interventions.csv").write_text(
        "timestamp_iso,intervention_number,summary\n", encoding="utf-8"
    )
    (base / "acceptance_results.md").write_text(
        f"# Acceptance results — {args.tool} / {args.condition}\n\n"
        "**Status: PENDING scored run**\n",
        encoding="utf-8",
    )
    print(f"prepared {base.relative_to(ROOT)} at freeze {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
