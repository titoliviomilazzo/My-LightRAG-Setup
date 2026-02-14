# LightRAG 내진성능평가 보고서 RAG 시스템

한국 구조공학 문서(내진성능평가/보강 보고서) 기반 LightRAG 운영 메모.

## 기술 스택

- Python 3.11
- LightRAG v1.4.9.11
- LLM: Groq Cloud API (OpenAI-compatible)
- Embedding: OpenAI API
- OS/HW: Windows 11 / RTX 3050 Laptop (4GB VRAM)

## 현재 설정

### LLM
- `LLM_BINDING=openai`
- `LLM_BINDING_HOST=https://api.groq.com/openai/v1`
- `LLM_MODEL=llama-3.1-8b-instant`
- `MAX_ASYNC=1`

### Embedding
- `EMBEDDING_BINDING=openai`
- `EMBEDDING_BINDING_HOST=https://api.openai.com/v1`
- `EMBEDDING_MODEL=text-embedding-3-small`
- `EMBEDDING_DIM=1536`

### RAG 파라미터
- `CHUNK_SIZE=500`
- `CHUNK_OVERLAP_SIZE=50`
- `SUMMARY_LANGUAGE=Korean`
- `MAX_PARALLEL_INSERT=2`
- `PORT=9700`

## 경로

- 서버 루트: `C:\LightRAG`
- venv: `C:\LightRAG\.venv`
- env: `C:\LightRAG\.env`
- 로그: `C:\LightRAG\lightrag.log`
- 저장소: `C:\LightRAG\rag_storage`
- GitHub 작업 디렉터리: `J:\내 드라이브\Code\My-LightRAG-Setup`

## 검증된 상태 (2026-02-14)

- 문서 상태: `processed=1`, `failed=0`
- 그래프: `462 nodes`, `358 edges`
- 벡터 차원: `1536` (`vdb_entities.json` 확인)
- Retrieval API 정상 응답: `/query`, `/query/data`, `/query/stream`

## 주요 이슈 이력

1. 포트 충돌
- 원인: Hyper-V 예약 포트 대역
- 조치: `9700` 고정

2. Windows 인코딩(cp949)
- 원인: 콘솔 기본 인코딩
- 조치: `PYTHONIOENCODING=utf-8`

3. 임베딩 차원 충돌
- 증상: `Embedding dim mismatch, expected: 1536, but loaded: 1024`
- 원인: Jina(1024)로 만든 기존 `rag_storage`와 OpenAI(1536) 설정 충돌
- 조치: `rag_storage` 백업 후 재생성

4. WebUI Empty / Network error
- 증상: KG 탭 Empty, Retrieval 탭 Network connection error
- 분석: 백엔드 정상 + UI 탭 캐시/상태 불일치
- 로그 패턴: `GET /graph` 404, `GET /graphs`(label 없음) 422
- 조치:
  - `http://127.0.0.1:9700/webui/` 재접속
  - `Ctrl+F5` 또는 시크릿 창
  - 서버 프로세스 단일화

## 서버 실행 명령

```powershell
cd C:\LightRAG
$env:PYTHONIOENCODING = "utf-8"
C:\LightRAG\.venv\Scripts\python.exe -m lightrag.api.lightrag_server
```

