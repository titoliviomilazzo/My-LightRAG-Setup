# My LightRAG Setup

한국어 내진성능평가 보고서 PDF를 대상으로 LightRAG 기반 질의응답을 수행하는 개인 프로젝트입니다.

## 현재 기준 구성 (2026-02-14)

- Framework: LightRAG `v1.4.9.11`
- Python: `3.11`
- LLM: Groq (`llama-3.1-8b-instant`, OpenAI-compatible API)
- Embedding: OpenAI (`text-embedding-3-small`, `1536` dim)
- Storage:
  - Graph: NetworkX (`graph_chunk_entity_relation.graphml`)
  - Vector: NanoVectorDB
  - KV: JSON

## 실행 환경 경로

- LightRAG 작업 디렉터리: `C:\LightRAG`
- venv: `C:\LightRAG\.venv`
- 설정 파일: `C:\LightRAG\.env`
- 로그 파일: `C:\LightRAG\lightrag.log`
- 스토리지: `C:\LightRAG\rag_storage`

## 서버 실행

```powershell
cd C:\LightRAG
$env:PYTHONIOENCODING = "utf-8"
C:\LightRAG\.venv\Scripts\python.exe -m lightrag.api.lightrag_server
```

- WebUI: `http://127.0.0.1:9700/webui/`
- API Docs: `http://127.0.0.1:9700/docs`

## 최소 필수 .env 항목

```env
HOST=127.0.0.1
PORT=9700

LLM_BINDING=openai
LLM_BINDING_HOST=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.1-8b-instant
LLM_BINDING_API_KEY=...

EMBEDDING_BINDING=openai
EMBEDDING_BINDING_HOST=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
EMBEDDING_BINDING_API_KEY=...

PYTHONIOENCODING=utf-8
SUMMARY_LANGUAGE=Korean
```

## 검증된 상태

- 문서 처리 상태: `processed=1`, `failed=0`
- 그래프 생성: `462 nodes`, `358 edges`
- Retrieval API(`/query`, `/query/data`, `/query/stream`) 응답 확인

## 자주 발생한 이슈

- 포트 충돌: Windows Hyper-V 예약 포트와 충돌 가능 -> `9700` 사용
- 인코딩: 한글 Windows 환경에서 `cp949` 문제 -> `PYTHONIOENCODING=utf-8` 필수
- WebUI Empty/Network Error:
  - 임베딩 실패가 아니라 브라우저 캐시/탭 상태 불일치로 재현 가능
  - 해결: `http://127.0.0.1:9700/webui/`로 재접속 + `Ctrl+F5`

