#!/usr/bin/env python3
"""C4 CrewAI pipeline skeleton — Codestral via Ollama.

Enforces the five frozen roles and artifact gates. Does not embed tool
prompts; load them from the workspace. Operator completes MCP/scanner
parity outside or via wrappers as documented in README.md.

CrewAI >=1.x expects crewai.LLM (or a model string), not LangChain ChatOllama.

Codestral on Ollama does **not** support tool calling. Tool Architect emits
`### FILE: path` fenced blocks; we materialize them to disk after kickoff.
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

from crewai import Agent, Crew, LLM, Process, Task

from materialize_files import materialize
from stub_scan import scan as stub_scan


ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "agents"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_llm() -> LLM:
    model = os.environ.get("OLLAMA_MODEL", "codestral")
    # CrewAI native provider form: ollama/<tag>
    if "/" not in model:
        model = f"ollama/{model}"
    base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    # Ensure scheme; OLLAMA_HOST alone is often host:port without http://
    if not base.startswith(("http://", "https://")):
        base = f"http://{base}"
    # CrewAI uses the OpenAI-compatible client against Ollama's /v1. Long
    # Architect/OPSEC prompts on Codestral can exceed the default request
    # timeout; the SDK then logs "Failed to connect to OpenAI API" even though
    # the target is local Ollama — raise timeout + retries for host Codestral.
    timeout = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "600"))
    retries = int(os.environ.get("OLLAMA_MAX_RETRIES", "3"))
    return LLM(
        model=model,
        base_url=base,
        api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
        temperature=0.2,
        timeout=timeout,
        max_retries=retries,
    )


def warmup_llm(llm: LLM) -> None:
    """Force-load Codestral before the crew so the first real task is not cold."""
    try:
        llm.call("Reply with exactly: OK")
        print("OLLAMA_WARMUP_OK", flush=True)
    except Exception as exc:  # noqa: BLE001 — preflight only
        raise SystemExit(
            f"OLLAMA_WARMUP_FAIL base={os.environ.get('OLLAMA_BASE_URL')}: {exc}"
        ) from exc


def persona_agent(llm: LLM, role_file: str, role_name: str) -> Agent:
    backstory = read(AGENTS_DIR / role_file)
    return Agent(
        role=role_name,
        goal=f"Complete the mission in {role_file} exactly.",
        backstory=backstory,
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


FILE_FORMAT = """
When creating source files, emit each file exactly in this format (no tools):

### FILE: relative/path/from/workspace

```python
# FULL working source — every function body implemented
```

Hard rules (violation = failed task):
- NEVER write `pass` as a function/test body (including "Implement … here" + `pass`).
- NEVER write "omitted for brevity", "implementation details omitted", or TODO stubs.
- Every function/method must contain real working logic or a real assertion.
- Match PROMPT.md / ACCEPTANCE.md paths exactly (chrome-mv3-kit: `extension/manifest.json`
  for Chromium Load unpacked — do **not** put the MV3 root under `src/` only).
- Include real `testdata/fixture_engagement/` fixtures (events.jsonl, events.csv,
  decisions.csv) with a planted fake secret for redaction tests.
- Include a runnable CLI entrypoint and at least one real unit test that asserts.
- Prefer stdlib when possible. Paths are relative to the workspace root.
- Include README.md, requirements.txt, package modules, tests, and testdata.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="C4 five-agent pipeline")
    parser.add_argument("--tool", required=True, help="Tool slug under prompts/")
    parser.add_argument("--workspace", required=True, type=Path)
    args = parser.parse_args()

    workspace: Path = args.workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "pipeline").mkdir(exist_ok=True)

    prompt_path = ROOT / "prompts" / args.tool / "PROMPT.md"
    accept_path = ROOT / "prompts" / args.tool / "ACCEPTANCE.md"
    if not prompt_path.exists():
        raise SystemExit(f"missing {prompt_path}")

    prompt = read(prompt_path)
    acceptance = read(accept_path) if accept_path.exists() else ""

    # Pin OpenAI-compatible env so no CrewAI/httpx path can hit api.openai.com.
    base = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    if not base.startswith(("http://", "https://")):
        base = f"http://{base}"
    os.environ["OLLAMA_BASE_URL"] = base
    os.environ.setdefault("OPENAI_API_KEY", "ollama")
    os.environ["OPENAI_BASE_URL"] = f"{base.rstrip('/')}/v1"
    os.environ["OPENAI_API_BASE"] = os.environ["OPENAI_BASE_URL"]

    llm = build_llm()
    warmup_llm(llm)

    # CrewAI treats output_file as cwd-relative and mishandles absolute paths
    # that contain spaces (writes under ./home/.../rootcon 20/...). Always
    # chdir into the workspace and use short relative output paths.
    os.chdir(workspace)

    researcher = persona_agent(llm, "01_domain_researcher.md", "Domain Researcher")
    planner = persona_agent(llm, "02_planner.md", "Planner")
    ops = persona_agent(llm, "03_ops_advisor.md", "Ops Advisor")
    architect = persona_agent(llm, "04_tool_architect.md", "Tool Architect")
    opsec = persona_agent(llm, "05_opsec_reviewer.md", "OPSEC Reviewer")

    t1 = Task(
        description=(
            f"Workspace: {workspace}\n\nPROMPT:\n{prompt}\n\n"
            "Produce the full contents of pipeline/01_domain_brief.md "
            "(markdown only for this stage)."
        ),
        expected_output="pipeline/01_domain_brief.md contents",
        agent=researcher,
        output_file="pipeline/01_domain_brief.md",
    )
    t2 = Task(
        description="Using the domain brief and PROMPT, write pipeline/02_plan.md.",
        expected_output="pipeline/02_plan.md contents",
        agent=planner,
        context=[t1],
        output_file="pipeline/02_plan.md",
    )
    t3 = Task(
        description="Write pipeline/03_ops_constraints.md from plan + PROMPT.",
        expected_output="pipeline/03_ops_constraints.md contents",
        agent=ops,
        context=[t1, t2],
        output_file="pipeline/03_ops_constraints.md",
    )
    t4 = Task(
        description=(
            f"Implement the tool under workspace {workspace} per plan and ops "
            f"constraints.\nACCEPTANCE:\n{acceptance}\n\n"
            f"{FILE_FORMAT}\n"
            "Your output must include every implementation file as ### FILE: "
            "blocks, then a short build-notes summary. Do not invent tool calls. "
            "Do not omit implementations — full source only. Every acceptance "
            "check must be achievable from the files you emit, including A5e "
            "when study-fixtures/ is present (copy those files into testdata/ "
            "unchanged)."
        ),
        expected_output=(
            "### FILE blocks for COMPLETE implementation + build notes markdown"
        ),
        agent=architect,
        context=[t1, t2, t3],
        output_file="pipeline/04_build_notes.md",
    )
    t5 = Task(
        description=(
            "Review the planned implementation and write OPSEC_CARD.md content "
            "with Detection Recommendations (≥3 bullets). Also emit:\n"
            "### FILE: OPSEC_CARD.md\n"
            "with the full card body in a markdown fence."
        ),
        expected_output="OPSEC_CARD.md as ### FILE block plus narrative",
        agent=opsec,
        context=[t4],
        output_file="pipeline/05_opsec_card.md",
    )

    crew = Crew(
        agents=[researcher, planner, ops, architect, opsec],
        tasks=[t1, t2, t3, t4, t5],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff()
    print(result)

    # Materialize ### FILE blocks from Architect/OPSEC outputs into workspace.
    written = materialize(
        workspace,
        [
            workspace / "pipeline" / "04_build_notes.md",
            workspace / "pipeline" / "05_opsec_card.md",
        ],
    )
    print(f"MATERIALIZED {len(written)} files")
    for w in written:
        print(f"  {w.relative_to(workspace)}")

    stubs = stub_scan(workspace)
    if stubs:
        print(f"STUB_SCAN_FAIL {len(stubs)} file(s)")
        for path, pat in stubs:
            print(f"  {path.relative_to(workspace)} :: {pat}")
    else:
        print("STUB_SCAN_OK")

    # Mirror pipeline artifacts into runs/.../pipeline for archive layout
    archive_pipeline = workspace.parent / "pipeline"
    archive_pipeline.mkdir(parents=True, exist_ok=True)
    for name in (
        "01_domain_brief.md",
        "02_plan.md",
        "03_ops_constraints.md",
        "04_build_notes.md",
        "05_opsec_card.md",
    ):
        src = workspace / "pipeline" / name
        if src.exists():
            shutil.copy2(src, archive_pipeline / name)

    print("CREW_DONE")
    if stubs:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
