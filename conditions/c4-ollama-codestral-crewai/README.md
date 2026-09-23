# C4 — CrewAI + locally hosted Ollama Codestral

## Intent

Same five roles as C2/C3 on a weaker local model to answer RQ3.

## Model lock

See `MODEL_PIN.md`. Runtime: **Ollama**. Model: **Codestral**.

## Setup

**Preferred on this lab:** run Ollama + Codestral on the **hypervisor host**. C4 is **air-gapped local inference** (no cloud LLM). The Kali guest is ~15 GiB RAM and OOM-kills Codestral, so the model lives on Windows and the VM reaches it over private VMnet. Full steps: [`HOST_REMOTE.md`](HOST_REMOTE.md) / [`HOST_WINDOWS.md`](HOST_WINDOWS.md).

1. Host: install Ollama, `ollama pull codestral`, listen with `OLLAMA_HOST=0.0.0.0:11434`, open firewall TCP 11434 to the VM net.
2. Kali: point at the host (VMnet8 is often `192.168.224.1` for this guest):
   ```bash
   source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh 192.168.224.1
   ```
3. Create Python venv; `pip install -r requirements.txt`.
4. Copy `prompts/{tool}/PROMPT.md` and `ACCEPTANCE.md` into the run workspace. If `prompts/{tool}/fixtures/` exists, copy it to `workspace/study-fixtures/` (`prepare_scored_run.py` does this).
5. After the host has pulled Codestral, C4 inference stays on-lab (Windows Ollama ← Kali over VMnet). Note that topology in RUN_LOG.
6. Enable Semgrep/ast-grep/Serena the same way as other conditions **if** CrewAI can call them; otherwise run scanners as mandatory post-steps and say so in RUN_LOG (document as platform gap, do not skip).

Local-in-VM Ollama is optional and not recommended for Codestral-22B here. See `MODEL_PIN.md`.

## Run

```bash
cd "/home/kali/Desktop/research/rootcon 20"
source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh 192.168.224.1
source conditions/c4-ollama-codestral-crewai/.venv/bin/activate
export OLLAMA_MODEL=codestral
python conditions/c4-ollama-codestral-crewai/run_pipeline.py \
  --tool after-action \
  --workspace runs/after-action/c4/workspace
```

Tool Architect and OPSEC Reviewer receive `FileWriterTool` / read tools scoped to the workspace so source files land on disk (not only markdown notes).


## Kickoff

`run_pipeline.py` loads personas from `agents/` and enforces artifact gates between Crew agents.

## Success artifacts

Same as other conditions under `runs/{tool}/c4/`.
