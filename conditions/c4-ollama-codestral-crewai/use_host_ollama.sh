#!/usr/bin/env bash
# Point this Kali VM at Ollama running on the hypervisor host.
# Usage:
#   source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh 192.168.224.1
#   source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh   # defaults to 192.168.224.1
#
# Must be sourced (not executed) so exports stick in your shell.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: source this script:  source $0 [host-ip]" >&2
  exit 1
fi

HOST_IP="${1:-${OLLAMA_HOST_IP:-192.168.224.1}}"
export OLLAMA_HOST_IP="$HOST_IP"
export OLLAMA_BASE_URL="http://${HOST_IP}:11434"
export OLLAMA_HOST="${HOST_IP}:11434"
export OLLAMA_MODEL="${OLLAMA_MODEL:-codestral}"

# CrewAI writes under $HOME/.local — never leave HOME on the disk_b ollama-home tree.
if [[ "${HOME:-}" == */rootcon-ollama/ollama-home ]] || [[ "${HOME:-}" == */.tools/ollama-home ]]; then
  export HOME="${SUDO_USER:+$(getent passwd "$SUDO_USER" | cut -d: -f6)}"
  export HOME="${HOME:-/home/kali}"
  echo "NOTE: reset HOME=$HOME (was ollama-home; breaks CrewAI storage)"
fi

# Keep CrewAI/Chroma data inside the repo (sandbox-friendly + portable).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$ROOT/.tools/xdg-data}"
mkdir -p "$XDG_DATA_HOME"

echo "OLLAMA_BASE_URL=$OLLAMA_BASE_URL"
echo "OLLAMA_MODEL=$OLLAMA_MODEL"
echo "HOME=$HOME"
echo "XDG_DATA_HOME=$XDG_DATA_HOME"

if curl -sf --max-time 3 "${OLLAMA_BASE_URL}/api/tags" >/dev/null; then
  echo "Host Ollama reachable."
  if command -v ollama >/dev/null 2>&1; then
    ollama list 2>/dev/null || true
  fi
else
  echo "NOT REACHABLE: ${OLLAMA_BASE_URL}" >&2
  echo "On the host: OLLAMA_HOST=0.0.0.0:11434 + firewall TCP 11434" >&2
  echo "Or use SSH tunnel — see HOST_REMOTE.md" >&2
  return 1 2>/dev/null || true
fi
