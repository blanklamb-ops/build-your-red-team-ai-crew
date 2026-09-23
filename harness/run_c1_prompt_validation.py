#!/usr/bin/env python3
"""Generate one tool with the C1 method in a separate prompt-validation track."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from run_scored_condition import C1_PROMPT, iso, now

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ("chrome-mv3-kit", "gophish-ics", "empire-advisor", "after-action")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(tool: str) -> Path:
    base = ROOT / "runs" / "prompt-validation" / tool / "c1"
    if base.exists() and any(base.iterdir()):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive = base.parent / "archive" / stamp
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(base), str(archive))
        print(f"archived previous validation run: {archive.relative_to(ROOT)}")

    workspace = base / "workspace"
    transcript = base / "transcript"
    scanners = base / "scanners"
    for path in (workspace, transcript, scanners):
        path.mkdir(parents=True, exist_ok=True)

    copies = {
        ROOT / "prompts" / tool / "PROMPT.md": workspace / "PROMPT.md",
        ROOT / "prompts" / tool / "ACCEPTANCE.md": workspace / "ACCEPTANCE.md",
        ROOT / "ethics" / "AUTHORIZED_USE.md": workspace / "AUTHORIZED_USE.md",
        ROOT / "rubric" / "OPSEC_CARD_TEMPLATE.md": workspace
        / "OPSEC_CARD_TEMPLATE.md",
    }
    for source, destination in copies.items():
        shutil.copy2(source, destination)

    fixtures = ROOT / "prompts" / tool / "fixtures"
    if fixtures.is_dir():
        dest = workspace / "study-fixtures"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(fixtures, dest)

    metadata = {
        "purpose": "C1 prompt validation; not a formal matrix cell",
        "tool": tool,
        "condition": "c1",
        "method": "single comprehensive prompt; no agent personas",
        "model": "claude-sonnet-4-5",
        "prompt_sha256": sha256(workspace / "PROMPT.md"),
        "acceptance_sha256": sha256(workspace / "ACCEPTANCE.md"),
        "repository_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "prepared_at": iso(now()),
    }
    (base / "validation-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=TOOLS)
    parser.add_argument("--timeout-minutes", type=int, default=180)
    args = parser.parse_args()

    base = prepare(args.tool)
    workspace = base / "workspace"
    command = [
        "claude",
        "--dangerously-skip-permissions",
        "--model",
        "claude-sonnet-4-5",
        "--output-format",
        "stream-json",
        "--verbose",
        "-p",
        C1_PROMPT,
    ]
    started = now()
    print(f"starting C1 prompt validation for {args.tool}: {iso(started)}", flush=True)
    with (base / "transcript" / "raw.jsonl").open(
        "w", encoding="utf-8"
    ) as stdout, (base / "transcript" / "stderr.txt").open(
        "w", encoding="utf-8"
    ) as stderr:
        try:
            process = subprocess.run(
                command,
                cwd=workspace,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                text=True,
                timeout=args.timeout_minutes * 60,
            )
            returncode = process.returncode
            stop_reason = "generated" if returncode == 0 else "hard_fail"
        except subprocess.TimeoutExpired:
            returncode = 124
            stop_reason = "timeout"

    ended = now()
    run_metadata = {
        "start": iso(started),
        "end": iso(ended),
        "minutes": round((ended - started).total_seconds() / 60, 2),
        "returncode": returncode,
        "generation_stop_reason": stop_reason,
    }
    (base / "transcript" / "run-metadata.json").write_text(
        json.dumps(run_metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(run_metadata, indent=2))
    return returncode


if __name__ == "__main__":
    sys.exit(main())
