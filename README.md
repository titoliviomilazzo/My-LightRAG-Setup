# Reference: LightRAG Installation & Configuration (Ollama)

This document serves as a persistent record of the LightRAG setup performed on this system.

## 📂 System Paths

- **Installation Directory**: `C:\LightRAG`
- **Virtual Environment**: `C:\LightRAG\.venv`
- **Configuration File**: `C:\LightRAG\.env`
- **Log File**: `C:\LightRAG\lightrag.log`
- **Data Storage**: `C:\LightRAG\rag_storage` (Default JSON/NetworkX/NanoVectorDB)

## 🛠️ Technology Stack

- **Framework**: LightRAG (HKUDS/LightRAG)
- **Environment**: Python 3.x (Installed via `pip` in `.venv`)
- **LLM Engine**: Ollama
- **Models**:
  - **LLM**: `qwen2.5-coder:14b` (Context: 32768)
  - **Embedding**: `bge-m3:latest` (Dim: 1024)

## 🚀 Commands and Access

- **Startup Command**:

  ```powershell
  cd C:\LightRAG
  .venv\Scripts\activate
  lightrag-server
  ```

- **Web UI**: [http://localhost:9621](http://localhost:9621)
- **API Docs**: [http://localhost:9621/docs](http://localhost:9621/docs)

## ⚙️ Key Configuration (.env)

- `LLM_BINDING=ollama`
- `EMBEDDING_BINDING=ollama`
- `LLM_MODEL=qwen2.5-coder:14b`
- `EMBEDDING_MODEL=bge-m3:latest`
- `HOST=0.0.0.0`, `PORT=9621`

---
*Note: This summary is designed to be distilled into a Knowledge Item (KI) for context persistence.*
