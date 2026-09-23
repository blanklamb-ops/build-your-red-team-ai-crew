#!/usr/bin/env bash
# Detached formal C4 matrix launcher.
# Survives Cursor/agent shell teardown (uses setsid — NOT plain nohup &).
#
# Usage (from a real terminal, or Cursor with full/"all" permissions so the
# sandbox proxy cannot 403 host Ollama):
#   bash analysis/pilots/run_c4_detached.sh
#   bash analysis/pilots/run_c4_detached.sh 192.168.224.1
#
# Status:
#   tail -f analysis/pilots/c4_all_when_ready.log
#   kill "$(cat analysis/pilots/c4_all_when_ready.pid)"   # stop matrix

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOST_IP="${1:-${OLLAMA_HOST_IP:-192.168.224.1}}"
LOG="$ROOT/analysis/pilots/c4_all_when_ready.log"
PIDF="$ROOT/analysis/pilots/c4_all_when_ready.pid"
RUNNER="$ROOT/analysis/pilots/run_c4_all_when_ready.sh"

cd "$ROOT"
chmod +x "$RUNNER"

if [[ -f "$PIDF" ]]; then
  old="$(tr -d '[:space:]' <"$PIDF" || true)"
  if [[ -n "$old" ]] && kill -0 "$old" 2>/dev/null; then
    echo "C4 matrix already running pid=$old"
    echo "log: $LOG"
    exit 0
  fi
fi

# Probe without sandbox proxy if possible.
if ! curl -fsS -m 5 "http://${HOST_IP}:11434/api/tags" >/tmp/ollama_tags_c4.json 2>/dev/null; then
  echo "ERROR: host Ollama not reachable at http://${HOST_IP}:11434" >&2
  echo "  On Windows: see conditions/c4-ollama-codestral-crewai/HOST_WINDOWS.md" >&2
  echo "  On Kali:    source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh ${HOST_IP}" >&2
  echo "  If started from Cursor agent: re-run with unrestricted network (no sandbox proxy)." >&2
  exit 1
fi
if ! python3 -c "import json; m=json.load(open('/tmp/ollama_tags_c4.json')); assert any('codestral' in (x.get('name') or '') for x in m.get('models',[]))"; then
  echo "ERROR: Ollama is up but codestral is missing — run: ollama pull codestral" >&2
  exit 1
fi

{
  echo "==== DETACH $(date -u +%Y-%m-%dT%H:%M:%SZ) host=${HOST_IP} ===="
} >>"$LOG"

# New session + process group, reparented to init. Cursor shell exit cannot SIGHUP this.
# The inner shell writes its own PID (post-setsid) then execs the runner.
setsid -f bash -c "
  echo \$\$ > \"${PIDF}\"
  export OLLAMA_HOST_IP=\"${HOST_IP}\"
  export HOME=\"${HOME:-/home/kali}\"
  export XDG_DATA_HOME=\"${XDG_DATA_HOME:-$ROOT/.tools/xdg-data}\"
  export OLLAMA_BASE_URL=\"http://${HOST_IP}:11434\"
  export OLLAMA_HOST=\"${HOST_IP}:11434\"
  export OLLAMA_MODEL=\"\${OLLAMA_MODEL:-codestral}\"
  export C4_DETACHED=1
  export C4_TOOLS=\"\${C4_TOOLS:-}\"
  mkdir -p \"\$XDG_DATA_HOME\"
  cd \"${ROOT}\"
  exec bash \"${RUNNER}\"
" >>"$LOG" 2>&1

# Wait briefly for PID file.
for _ in 1 2 3 4 5 6 7 8 9 10; do
  if [[ -s "$PIDF" ]] && kill -0 "$(tr -d '[:space:]' <"$PIDF")" 2>/dev/null; then
    break
  fi
  sleep 0.2
done

pid="$(tr -d '[:space:]' <"$PIDF" 2>/dev/null || true)"
if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
  echo "ERROR: detached C4 failed to start — see $LOG" >&2
  exit 1
fi

echo "C4 matrix detached pid=$pid"
echo "log: $LOG"
echo "tail -f \"$LOG\""
