# C4 — run Ollama on the host, call it from the Kali VM

The Kali VM has ~15 GiB RAM; Codestral-22B needs ~12 GiB of model weights in memory and was OOM-killed here. Run Ollama + Codestral on the **host**, and point CrewAI on the VM at the host API.

## Architecture

```
[Host]  ollama serve 0.0.0.0:11434  +  codestral
   ↑
   |  TCP 11434  (VMware NAT / bridged / SSH tunnel)
   |
[Kali VM]  CrewAI  OLLAMA_BASE_URL=http://<host-ip>:11434
```

`run_pipeline.py` already reads `OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`).

---

## 1) Host: install, pull, listen on all interfaces

**Windows PowerShell host:** follow [`HOST_WINDOWS.md`](HOST_WINDOWS.md) (copy-paste commands).

Linux/macOS host:

```bash
ollama --version
ollama pull codestral

# CRITICAL: default bind is 127.0.0.1 only — VM cannot reach that
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

Confirm on the host: `curl http://127.0.0.1:11434/api/tags` and `ollama show codestral`.

### Firewall (host)

Allow inbound **TCP 11434** from the VM network only (not the whole internet).

- **Windows:** see `HOST_WINDOWS.md` (`New-NetFirewallRule` … `-RemoteAddress 192.168.224.0/24`).
- **Linux:** `ufw allow from 192.168.224.0/24 to any port 11434 proto tcp`

---

## 2) Find the host IP from this Kali VM

This guest is on VMware-style NAT:

| Role | Address |
|------|---------|
| Kali (guest) | `192.168.224.133/24` (`eth0`) |
| NAT gateway / DNS | `192.168.224.2` |
| Host on VMnet8 (typical) | `192.168.224.1` |

On the **host**, confirm the adapter IP:

- Windows: `ipconfig` → **VMware Network Adapter VMnet8** (or Fusion/Workstation equivalent)
- Linux host: `ip -br a` on `vmnet8`

From Kali, test (replace with the real host IP):

```bash
HOST_IP=192.168.224.1   # or whatever VMnet8 shows on the host
curl -sf --max-time 3 "http://${HOST_IP}:11434/api/tags" && echo OK
```

If `.1` does not work, try the host’s LAN/Wi‑Fi IP (bridged) or use the SSH tunnel below.

**Note:** OpenVPN (`tun1`) full-tunnels most internet traffic on this VM, but `192.168.224.0/24` stays on `eth0`, so host↔guest LAN should still work.

---

## 3) Kali VM: point C4 at the host

```bash
cd "/home/kali/Desktop/research/rootcon 20"

# one-shot for this shell
export OLLAMA_HOST_IP=192.168.224.1          # <-- your host VMnet8 IP
export OLLAMA_BASE_URL="http://${OLLAMA_HOST_IP}:11434"
export OLLAMA_MODEL=codestral
export OLLAMA_HOST="${OLLAMA_HOST_IP}:11434" # for `ollama` CLI on the VM

# stop any local VM ollama (saves RAM; optional)
pkill -x ollama 2>/dev/null || true

curl -sf --max-time 3 "${OLLAMA_BASE_URL}/api/tags"
ollama list    # talks to host if OLLAMA_HOST is set

# then CrewAI
python conditions/c4-ollama-codestral-crewai/run_pipeline.py \
  --tool after-action \
  --workspace runs/after-action/c4/workspace
```

Or use the helper:

```bash
source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh 192.168.224.1
```

Pin the remote endpoint in `MODEL_PIN.md` once it works (host IP + `ollama show` digest from the host).

---

## 4) If direct TCP fails: SSH tunnel (most reliable)

On the host, enable SSH (or use any account you can reach). From Kali:

```bash
# forwards VM localhost:11434 → host's local Ollama
ssh -N -L 11434:127.0.0.1:11434 YOU@HOST_LAN_OR_VMNET_IP
```

Leave that running, then on Kali:

```bash
export OLLAMA_BASE_URL=http://127.0.0.1:11434
curl -sf http://127.0.0.1:11434/api/tags
```

Host Ollama can stay on `127.0.0.1` in this mode (no firewall open). Prefer this if corporate Wi‑Fi / host firewall is painful.

---

## 5) Optional: Tailscale (both sides)

Both host and Kali on Tailscale → use the host Tailscale IP (`100.x`) as `OLLAMA_HOST_IP`. Same `OLLAMA_HOST=0.0.0.0:11434` (or Tailscale IP only) on the host. This Kali install is currently logged out of Tailscale.

---

## What not to do

- Do **not** `ollama pull codestral` again inside the VM (disk + RAM).
- Do **not** start host Ollama from the Cursor agent with a Codestral generate — start it on the host terminal.
- Do **not** leave host Ollama on `0.0.0.0` exposed past your lab LAN without a firewall scope.

## Record in RUN_LOG

For each C4 run, note: `OLLAMA_BASE_URL`, host OS/RAM, Codestral digest from host `ollama show`, and whether access was VMnet direct or SSH tunnel (platform confound for RQ3).
