# Reference: LightRAG Installation & Configuration (Ollama)

This document serves as a persistent record of the LightRAG setup performed on this system.

## System Paths

- **Installation Directory**: `C:\LightRAG`
- **Virtual Environment**: `C:\LightRAG\.venv`
- **Configuration File**: `C:\LightRAG\.env`
- **Log File**: `C:\LightRAG\lightrag.log`
- **Data Storage**: `C:\LightRAG\rag_storage` (JSON/NetworkX/NanoVectorDB)

## Technology Stack

- **Framework**: LightRAG v1.4.9.11 (HKUDS/LightRAG)
- **Environment**: Python 3.x (Installed via `pip install lightrag-hku[api]` in `.venv`)
- **LLM Engine**: Ollama
- **Models**:
  - **LLM**: `qwen2.5:7b` (general-purpose, good Korean support)
  - **Embedding**: `bge-m3:latest` (Dim: 1024)
- **Hardware**: RTX 3050 Laptop GPU (4GB VRAM)

## Commands and Access

- **Startup Command**:

  ```powershell
  cd C:\LightRAG
  .venv\Scripts\activate
  $env:PYTHONIOENCODING="utf-8"
  lightrag-server
  ```

- **Web UI**: [http://localhost:9700](http://localhost:9700)
- **API Docs**: [http://localhost:9700/docs](http://localhost:9700/docs)

## Key Configuration (.env)

| Setting | Value | Notes |
|---|---|---|
| `HOST` | `localhost` | `0.0.0.0` causes `[Errno 13]` on Windows |
| `PORT` | `9700` | Ports 9559-9658 reserved by Hyper-V |
| `LLM_BINDING` | `ollama` | |
| `LLM_MODEL` | `qwen2.5:7b` | 4.7GB, fits partially in 4GB VRAM |
| `EMBEDDING_BINDING` | `ollama` | |
| `EMBEDDING_MODEL` | `bge-m3:latest` | 1024-dim embedding |
| `SUMMARY_LANGUAGE` | `Korean` | For Korean document processing |
| `CHUNK_SIZE` | `800` | Reduced from default 1200 to prevent LLM timeout |
| `CHUNK_OVERLAP_SIZE` | `100` | |

## Troubleshooting Notes

### Port Binding Error (`[Errno 13]`)
Windows Hyper-V reserves dynamic port ranges (e.g., 9559-9658). Check reserved ranges:
```powershell
netsh interface ipv4 show excludedportrange protocol=tcp
```
Solution: Use a port outside all reserved ranges (e.g., 9700).

### UnicodeEncodeError (cp949)
Korean Windows uses cp949 encoding which cannot render Unicode box-drawing characters in the LightRAG splash screen.
Solution: Set `PYTHONIOENCODING=utf-8` before launching the server.

### LLM Timeout on PDF Processing
With limited VRAM (4GB), large models like `qwen2.5-coder:14b` (9GB) run on CPU only, causing `httpx.ReadTimeout` during entity extraction.
Solution: Use a smaller model (`qwen2.5:7b`, 4.7GB) and reduce `CHUNK_SIZE` to 800.

---
*Note: This summary is designed to be distilled into a Knowledge Item (KI) for context persistence.*
