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


## Quality Recovery Workflow

Use these scripts before re-indexing and re-scoring:

```powershell
# 1) Normalize extracted corpus text (in-place write)
python scripts/normalize_corpus.py --input-dir C:\LightRAG\inputs --write --report-file normalization_report.json

# 2) Validate corpus quality (non-zero exit when issues remain)
python scripts/validate_corpus.py --input-dir C:\LightRAG\inputs --report-file validation_report.json

# 3) Re-evaluate 10 questions against running LightRAG API
python scripts/re_evaluate_quality.py --quality-md "LightRAG 품질 검증표 (10문항).md" --base-url http://127.0.0.1:9700 --mode hybrid
```

Replacement map file:
- `config/pua_replacements.json`

## Strict Project-Aware Query Run

```powershell
python scripts/run_strict_project_queries.py --quality-md "LightRAG 품질 검증표 (10문항).md" --output-md "LightRAG 프로젝트별 엄격 질의 결과.md" --base-url http://127.0.0.1:9700 --mode local --min-target-hits 1
```

- Output: `LightRAG 프로젝트별 엄격 질의 결과.md`
- This report always shows target project, dominant referenced project, and pass/fail per row.

## Isolated Index Evaluation (Option 1)

```powershell
python scripts/run_isolated_project_evaluation.py --quality-md "LightRAG 품질 검증표 (10문항).md" --output-md "LightRAG 프로젝트별 분리인덱스 엄격 결과.md" --base-url http://127.0.0.1:9700 --restore-full-index
```

- This runs project-by-project with isolated index (single PDF loaded each run).
- It is slow on large PDFs and can take hours.
- During the run, LightRAG pipeline stays busy.

## Retrieval Presets (Recommended)

### 1) 운영 기본 (출처 명확 + 혼합 최소화)
- Additional Output Prompt:
  - `답변 각 항목 끝에 [프로젝트명 | 파일명]을 붙이고, 근거 없는 내용은 "근거없음"으로 표시.`
- Query Mode: `local` (일반 질의는 `hybrid`)
- KG Top K: `16`
- Chunk Top K: `10`
- Max Entity Tokens: `3000`
- Max Relation Tokens: `3000`
- Max Total Tokens: `12000`
- Enable Rerank: `ON`
- Only Need Context: `OFF` (검증 시 `ON`)
- Only Need Prompt: `OFF`
- Stream Response: `ON`

### 2) 표/수치 추출 모드
- 목적: 표의 수치/조건 정확 추출
- Additional Output Prompt:
  - `수치는 원문 단위 그대로 쓰고, 항목별로 [프로젝트명 | 파일명 | 표/본문] 근거를 붙여라.`
- Query Mode: `local`
- KG Top K: `12`
- Chunk Top K: `10`
- Max Entity Tokens: `2500`
- Max Relation Tokens: `2500`
- Max Total Tokens: `10000`
- Enable Rerank: `ON`
- Only Need Context: `OFF` (값 검증할 때 `ON`)

### 3) 그래프/관계 해석 모드
- 목적: 부재-관계, 보강 전후 관계 설명
- Additional Output Prompt:
  - `관계 해석은 항목별로 근거를 제시하고, 프로젝트가 다르면 절대 합치지 말라.`
- Query Mode: `hybrid`
- KG Top K: `20`
- Chunk Top K: `10`
- Max Entity Tokens: `3000`
- Max Relation Tokens: `3500`
- Max Total Tokens: `14000`
- Enable Rerank: `ON`
- Only Need Context: `OFF`

### Quick Rules
- 프로젝트가 특정된 질문이면 `local` + 낮은 `Chunk Top K` 사용
- 프로젝트가 섞이는 답이 나오면 `KG Top K`, `Chunk Top K`, `Max Total Tokens`를 먼저 낮춤
- 최종 보고 전에는 `Only Need Context=ON`으로 근거 청크를 한 번 확인
