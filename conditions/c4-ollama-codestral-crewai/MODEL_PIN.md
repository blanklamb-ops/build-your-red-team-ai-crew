# C4 model pin

| Field | Value |
|-------|-------|
| **Runtime location** | **Windows host** (not Kali VM) — see [`HOST_WINDOWS.md`](HOST_WINDOWS.md) |
| Runtime | Ollama (Windows) |
| Model | `codestral:latest` |
| Model ID | `0898a8b286d5` |
| Digest | `0898a8b286d56d8105587049fec69634fce83c957230fc13f0acfe03b7b11909` |
| Parameter size | **22.2B** |
| Quantization | **Q4_0** |
| On-disk size | ~12 GB (`12569170438` bytes) |
| Host bind | `0.0.0.0:11434` |
| Host VMnet8 IP | **`192.168.224.1`** |
| Kali API | `OLLAMA_BASE_URL=http://192.168.224.1:11434` |
| Verified | 2026-09-03 — `use_host_ollama.sh` → Host Ollama reachable |

## Kali client (each C4 shell)

```bash
cd "/home/kali/Desktop/research/rootcon 20"
source conditions/c4-ollama-codestral-crewai/use_host_ollama.sh 192.168.224.1
```

## Optional local VM install

Kept under `/mnt/disk_b/rootcon-ollama/` for smaller models only — Codestral OOM-kills on this ~15 GiB Kali VM. Do not use for scored C4 runs.
