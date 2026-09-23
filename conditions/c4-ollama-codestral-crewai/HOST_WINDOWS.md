# Windows host (PowerShell) — Ollama for Kali VM

Run these on the **Windows host** in PowerShell. Kali stays the client.

C4 is **air-gapped local inference**: Codestral never calls a cloud LLM API. Ollama is on Windows only because the Kali VM cannot hold the model; the guest talks to the host over private VMnet (`192.168.224.1`).

## 1) Install + pull Codestral

```powershell
# If not installed: https://ollama.com/download  (restart PowerShell after install)
ollama --version
ollama pull codestral
ollama show codestral
```

## 2) Make Ollama listen on the LAN (not only localhost)

If `netstat` shows only `127.0.0.1:11434`, the VM **cannot** connect. Fix:

```powershell
# 1) Persist for your user (and this session)
[System.Environment]::SetEnvironmentVariable("OLLAMA_HOST", "0.0.0.0:11434", "User")
$env:OLLAMA_HOST = "0.0.0.0:11434"

# 2) Fully kill every Ollama process (tray + server)
Get-Process ollama* -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 3) Confirm port is free
netstat -an | findstr 11434
# (should print nothing)

# 4) Start serve with the new bind (prefer this over the tray for lab use)
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
if (-not (Test-Path $ollama)) { $ollama = "ollama" }  # if on PATH
Start-Process -FilePath $ollama -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep -Seconds 2
netstat -an | findstr 11434
# MUST show:  0.0.0.0:11434  LISTENING
# If you still see only 127.0.0.1 — the env was not applied; redo step 1–4
# in a NEW PowerShell window after setting the User variable.

curl http://127.0.0.1:11434/api/tags
curl http://192.168.224.1:11434/api/tags
```

**Why this happens:** the Windows tray app often starts before `OLLAMA_HOST` is set, and keeps binding localhost until every `ollama` process is killed and restarted.

## 3) Firewall — allow only the VMware NAT net

```powershell
# Run PowerShell as Administrator
New-NetFirewallRule -DisplayName "Ollama from Kali VMnet" `
  -Direction Inbound -Action Allow -Protocol TCP -LocalPort 11434 `
  -RemoteAddress 192.168.224.0/24
```

(Adjust `-RemoteAddress` if your VMnet subnet differs.)

## 4) Find the host IP the VM should use

```powershell
Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.InterfaceAlias -match 'VMware|VMnet8|VirtualBox' } |
  Select-Object InterfaceAlias, IPAddress
```

Typical VMware NAT: **VMnet8** → `192.168.224.1`.

Also note your Wi‑Fi/Ethernet IP if you use bridged networking instead.

Quick self-test from Windows:

```powershell
$vmnet = "192.168.224.1"   # paste IP from above
curl "http://${vmnet}:11434/api/tags"
```

## 5) On Kali (after host is up)

```bash
cd "/home/kali/Desktop/research/rootcon 20"
pkill -x ollama 2>/dev/null || true
source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh 192.168.224.1
# use the IP from step 4 if different
```

### Formal C4 matrix (detached — survives Cursor shell teardown)

Do **not** use plain `nohup … &` from the Cursor agent shell; that process group often dies when the tool session ends. Use `setsid` via:

```bash
cd "/home/kali/Desktop/research/rootcon 20"
source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh 192.168.224.1
bash analysis/pilots/run_c4_detached.sh
# status:
tail -f analysis/pilots/c4_all_when_ready.log
```

If you start C4 from the Cursor agent, the shell must have **unrestricted network** (no sandbox HTTP proxy) — otherwise curls to `192.168.224.1:11434` return **403** and the watcher never starts.

**Note:** CrewAI talks to Ollama through an OpenAI-compatible client (`…:11434/v1`). If a long Codestral call times out, logs may say `Failed to connect to OpenAI API` even though the target is host Ollama — that is a local timeout, not cloud OpenAI. The pipeline sets a 600s request timeout and warmups Codestral before the crew.
## If Kali still cannot connect — SSH tunnel

On Windows, enable OpenSSH Server (Optional Features) or use any SSH you already have. From Kali:

```bash
ssh -N -L 11434:127.0.0.1:11434 YOU@WINDOWS_LAN_OR_VMNET_IP
export OLLAMA_BASE_URL=http://127.0.0.1:11434
curl -sf http://127.0.0.1:11434/api/tags
```

With the tunnel, host Ollama can stay on `127.0.0.1` (skip step 2 bind / firewall).

## Checklist

| Step | OK when |
|------|---------|
| Pull | `ollama show codestral` works on Windows |
| Bind | `netstat` shows `0.0.0.0:11434` |
| Firewall | rule present for TCP 11434 |
| Kali | `use_host_ollama.sh` prints `Host Ollama reachable` |
