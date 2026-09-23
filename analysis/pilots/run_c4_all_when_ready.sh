#!/usr/bin/env bash
# Poll host Ollama, then run formal C4 for all four tools sequentially.
# Prefer launching via:  bash analysis/pilots/run_c4_detached.sh
# so the job survives Cursor/agent shell teardown.
set -euo pipefail

# Defense in depth if someone launches this with plain `nohup &` from an agent shell.
trap '' HUP
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOST="${OLLAMA_HOST_IP:-192.168.224.1}"
URL="http://${HOST}:11434"
cd "$ROOT"

# If not already session-detached, re-exec under setsid (idempotent).
if [[ "${C4_DETACHED:-}" != "1" ]] && command -v setsid >/dev/null 2>&1; then
  export C4_DETACHED=1
  LOG="$ROOT/analysis/pilots/c4_all_when_ready.log"
  PIDF="$ROOT/analysis/pilots/c4_all_when_ready.pid"
  echo "Re-exec under setsid (detach from parent shell) ..." | tee -a "$LOG"
  setsid -f bash -c "
    echo \$\$ > \"${PIDF}\"
    export C4_DETACHED=1
    export OLLAMA_HOST_IP=\"${HOST}\"
    cd \"${ROOT}\"
    exec bash \"${ROOT}/analysis/pilots/run_c4_all_when_ready.sh\"
  " >>"$LOG" 2>&1
  sleep 0.5
  echo "Detached pid=$(tr -d '[:space:]' <"$PIDF" 2>/dev/null || echo '?') — follow $LOG"
  exit 0
fi

# Record live PID when already detached.
echo $$ > "$ROOT/analysis/pilots/c4_all_when_ready.pid"

echo "Waiting for Ollama at ${URL} ..."
for i in $(seq 1 180); do
  if curl -fsS -m 3 "${URL}/api/tags" >/tmp/ollama_tags.json 2>/dev/null; then
    if python3 -c "import json; m=json.load(open('/tmp/ollama_tags.json')); assert any('codestral' in (x.get('name') or '') for x in m.get('models',[]))" 2>/dev/null; then
      echo "Host Ollama reachable with codestral ($(date -u +%H:%M:%SZ))"
      break
    fi
    echo "Ollama up but codestral missing; pull on host. poll=$i"
  else
    echo "poll $i: not ready ($(date -u +%H:%M:%SZ))"
  fi
  if [ "$i" -eq 180 ]; then
    echo "ERROR: timed out waiting for host Ollama/codestral" >&2
    exit 1
  fi
  sleep 10
done

export HOME="${HOME:-/home/kali}"
# Never leave HOME on an ollama-home tree (breaks CrewAI storage).
if [[ "${HOME}" == */rootcon-ollama/ollama-home ]] || [[ "${HOME}" == */.tools/ollama-home ]]; then
  export HOME=/home/kali
fi
export XDG_DATA_HOME="${XDG_DATA_HOME:-$ROOT/.tools/xdg-data}"
export OLLAMA_BASE_URL="$URL"
export OLLAMA_HOST="${HOST}:11434"
export OLLAMA_MODEL="${OLLAMA_MODEL:-codestral}"
mkdir -p "$XDG_DATA_HOME"

# Optional: C4_TOOLS="empire-advisor after-action" to resume mid-matrix.
# shellcheck disable=SC2206
TOOLS=(${C4_TOOLS:-chrome-mv3-kit gophish-ics empire-advisor after-action})

for tool in "${TOOLS[@]}"; do
  echo "==== C4 $tool ===="
  if [ ! -f "runs/$tool/c4/workspace/PROMPT.md" ]; then
    python3 harness/prepare_scored_run.py "$tool" c4
  fi
  # Keep going after hard_fail so one bad cell does not abort the matrix.
  set +e
  python3 harness/run_scored_condition.py "$tool" c4 --timeout-minutes 240
  rc=$?
  set -e
  echo "==== C4 $tool finished rc=$rc ===="
done

echo "All C4 cells finished ($(date -u +%Y-%m-%dT%H:%M:%SZ))."
