#!/usr/bin/env bash
# Start workspace-local Ollama with models on /mnt/disk_b (sdb1).
#
# IMPORTANT: run this in a normal terminal (outside the Cursor agent).
# Cursor sandbox cannot write under /mnt/disk_b, and a full Codestral
# generate from the agent can hang the chat for minutes while the model loads.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DISK_B_ROOT="${OLLAMA_DISK_B:-/mnt/disk_b/rootcon-ollama}"
BINDIR="$DISK_B_ROOT/ollama"
# Prefer disk_b binary; fall back to workspace symlink/copy
if [ ! -x "$BINDIR/bin/ollama" ] && [ -x "$ROOT/.tools/ollama/bin/ollama" ]; then
  BINDIR="$ROOT/.tools/ollama"
fi

# Logs stay in the workspace so Cursor sandbox can read them; models stay on disk_b.
LOG_DIR="${OLLAMA_LOG_DIR:-$ROOT/.tools/ollama-logs}"
mkdir -p "$LOG_DIR"

export HOME="$DISK_B_ROOT/ollama-home"
export OLLAMA_MODELS="$DISK_B_ROOT/ollama/models"
export LD_LIBRARY_PATH="$BINDIR/lib/ollama${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="$BINDIR/bin:$PATH"
export OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"

mkdir -p "$HOME" "$OLLAMA_MODELS"

if [ ! -x "$BINDIR/bin/ollama" ]; then
  echo "ERROR: ollama binary not found at $BINDIR/bin/ollama" >&2
  echo "Run: bash conditions/c4-ollama-codestral-crewai/migrate_to_disk_b.sh" >&2
  exit 1
fi

if curl -sf --max-time 2 "http://${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
  echo "ollama already up at $OLLAMA_HOST"
else
  # Also mirror pid/log under disk_b when writable (normal terminal).
  if mkdir -p "$DISK_B_ROOT/logs" 2>/dev/null && touch "$DISK_B_ROOT/logs/.w" 2>/dev/null; then
    rm -f "$DISK_B_ROOT/logs/.w"
    SERVE_LOG="$DISK_B_ROOT/logs/ollama-serve.log"
    SERVE_PID="$DISK_B_ROOT/logs/ollama-serve.pid"
  else
    SERVE_LOG="$LOG_DIR/ollama-serve.log"
    SERVE_PID="$LOG_DIR/ollama-serve.pid"
  fi
  # Keep a workspace copy for the agent to read either way.
  ln -sfn "$SERVE_LOG" "$LOG_DIR/ollama-serve.log" 2>/dev/null || true
  ln -sfn "$SERVE_PID" "$LOG_DIR/ollama-serve.pid" 2>/dev/null || true

  nohup env HOME="$HOME" OLLAMA_MODELS="$OLLAMA_MODELS" LD_LIBRARY_PATH="$LD_LIBRARY_PATH" \
    OLLAMA_HOST="$OLLAMA_HOST" \
    http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= \
    "$BINDIR/bin/ollama" serve >"$SERVE_LOG" 2>&1 &
  echo $! >"$SERVE_PID"
  # Also write pid into workspace always (agent-readable).
  cp "$SERVE_PID" "$LOG_DIR/ollama-serve.pid" 2>/dev/null || true

  up=0
  for _ in $(seq 1 30); do
    if curl -sf --max-time 2 "http://${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
      echo "ollama started (pid $(cat "$SERVE_PID"))"
      up=1
      break
    fi
    sleep 0.5
  done
  if [ "$up" -ne 1 ]; then
    echo "ERROR: ollama did not become ready at $OLLAMA_HOST" >&2
    echo "Log: $SERVE_LOG" >&2
    exit 1
  fi
fi

echo "OLLAMA_MODELS=$OLLAMA_MODELS"
"$BINDIR/bin/ollama" --version
"$BINDIR/bin/ollama" list
echo
echo "Health OK. Do NOT run 'ollama run codestral' from the Cursor agent —"
echo "first load can take several minutes and will stall the chat."
echo "Smoke in this terminal instead:"
echo "  ollama show codestral"
echo "  ollama run codestral 'Reply with exactly: OK'"
