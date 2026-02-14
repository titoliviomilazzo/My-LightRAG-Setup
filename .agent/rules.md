# LightRAG 운영 규칙 메모

## 프로젝트 목적

한국어 구조공학/내진성능평가 PDF를 LightRAG에 적재하고, 보고서 기반 질의응답 및 그래프 탐색을 안정적으로 수행한다.

## 현재 표준 구성

- LightRAG: `v1.4.9.11`
- Python: `3.11`
- LLM:
  - Binding: `openai` (Groq 호환)
  - Host: `https://api.groq.com/openai/v1`
  - Model: `llama-3.1-8b-instant`
- Embedding:
  - Binding: `openai`
  - Host: `https://api.openai.com/v1`
  - Model: `text-embedding-3-small`
  - Dim: `1536`

## 필수 운영 규칙

1. 서버는 단일 프로세스만 유지한다.
2. 실행은 venv Python으로 고정한다.
3. `PYTHONIOENCODING=utf-8`을 항상 설정한다.
4. WebUI 접속은 `http://127.0.0.1:9700/webui/`를 사용한다.
5. UI 이상 시 먼저 백엔드 상태를 API로 확인한다.

## 서버 실행 명령

```powershell
cd C:\LightRAG
$env:PYTHONIOENCODING = "utf-8"
C:\LightRAG\.venv\Scripts\python.exe -m lightrag.api.lightrag_server
```

## 상태 확인 명령

```powershell
Invoke-RestMethod http://127.0.0.1:9700/health
Invoke-RestMethod http://127.0.0.1:9700/documents/status_counts
Invoke-RestMethod http://127.0.0.1:9700/graph/label/list
```

## 자주 발생한 이슈와 원인

1. `Embedding dim mismatch (1536 vs 1024)`
- 기존 Jina(1024) 저장소와 OpenAI(1536) 설정 충돌
- 해결: `rag_storage` 백업 후 재생성

2. Knowledge Graph가 Empty로 보임
- 백엔드 장애가 아니라 UI 상태/캐시 문제일 수 있음
- 로그에서 `/graph` 404, `/graphs` 422(label 누락) 패턴 확인 가능

3. Retrieval에서 Network connection error
- 실제 네트워크 문제가 아니라 브라우저 탭 캐시 불일치로 재현 가능
- 해결: 새 탭 + `Ctrl+F5` 또는 시크릿 창

## 현재 검증 결과 (2026-02-14)

- 문서 상태: `processed=1`, `failed=0`
- 그래프: `462 nodes`, `358 edges`
- Retrieval API 정상 작동 확인

