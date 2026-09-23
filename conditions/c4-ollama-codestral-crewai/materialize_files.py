#!/usr/bin/env python3
"""Materialize ### FILE: path blocks from CrewAI markdown into the workspace.

Codestral via Ollama does not support tool calling, so C4 cannot use
FileWriterTool. Architects are instructed to emit:

### FILE: relative/path.py
```python
...
```

This script writes those blocks to disk under --workspace.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

FILE_HDR = re.compile(r"(?m)^\s*### FILE:\s+(\S+)\s*$")
FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)


def extract_files(text: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    matches = list(FILE_HDR.finditer(text))
    for i, m in enumerate(matches):
        rel = m.group(1).lstrip("./")
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        fence = FENCE.search(chunk)
        if fence:
            content = fence.group(1).rstrip() + "\n"
        else:
            # Allow unfenced body (common for OPSEC_CARD.md)
            content = chunk.rstrip() + "\n"
        if content.strip():
            out.append((rel, content))
    return out


def materialize(workspace: Path, sources: list[Path]) -> list[Path]:
    written: list[Path] = []
    for src in sources:
        if not src.exists():
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        for rel, content in extract_files(text):
            dest = (workspace / rel).resolve()
            if not str(dest).startswith(str(workspace.resolve())):
                raise SystemExit(f"refusing path escape: {rel}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            written.append(dest)
    return written


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument(
        "--from",
        dest="sources",
        nargs="+",
        type=Path,
        help="Markdown files containing ### FILE: blocks",
    )
    args = p.parse_args()
    workspace = args.workspace.resolve()
    sources = [Path(s) for s in (args.sources or [])]
    if not sources:
        sources = [
            workspace / "pipeline" / "04_build_notes.md",
            workspace / "pipeline" / "05_opsec_card.md",
        ]
    written = materialize(workspace, sources)
    print(f"materialized {len(written)} files under {workspace}")
    for w in written:
        print(f"  {w.relative_to(workspace)}")


if __name__ == "__main__":
    main()
