# Changelog

## 2026-02-12 ~ 2026-02-13: LightRAG 초기 설정 및 트러블슈팅
### 환경 구축
- LightRAG v1.4.9.11 설치 (`C:\LightRAG\`, Python 3.11 venv)
- GitHub 저장소 클론: https://github.com/titoliviomilazzo/My-LightRAG-Setup

### 트러블슈팅 이력
#### 1) 서버 포트 바인딩 실패
- 원인: Windows Hyper-V 예약 포트와 충돌
- 조치: 서비스 포트를 `9700`으로 변경

#### 2) Windows 콘솔 인코딩(cp949) 문제
- 원인: 기본 인코딩이 cp949로 동작하며 UTF-8 출력이 깨짐
- 조치: `PYTHONIOENCODING=utf-8` 설정 추가

#### 3) 로컬 Ollama 기반 추론 시도 및 중단
- `qwen2.5-coder:14b`: 4GB VRAM 한계로 실패
- `qwen2.5:7b`: 동작 가능하나 처리 속도 과도하게 느림
- `bge-m3`: 일부 한글 토큰에서 임베딩 품질/안정성 이슈 확인
- 결론: 로컬 LLM/임베딩 경로 중단

#### 4) 클라우드 API 경로 전환
- Gemini Flash: `429 RESOURCE_EXHAUSTED`
- OpenAI LLM 경로: `insufficient_quota`
- Groq `llama-3.3-70b`: 무료 TPM 한도 초과
- Groq `llama-3.1-8b-instant`: 인덱싱 파이프라인 정상 동작 확인

#### 5) Jina 임베딩 URL 라우팅 버그
- 증상: 임베딩 호출이 Groq URL로 전달되어 `404`
- 원인: 기본 host 폴백 경로가 LLM host를 참조
- 조치: `.env`에 `EMBEDDING_BINDING_HOST=https://api.jina.ai/v1/embeddings` 명시

#### 6) Groq TPD 한도 초과
- 증상: 인덱싱 중 `429 rate_limit_exceeded`
- 조치: Dev Tier 업그레이드 후 재시도

#### 7) Groq 서버 과부하(간헐)
- 증상: 인덱싱 중 `503 over capacity`
- 상태: 캐시 기반 재시작 가능, 완주 시점 지연

### 당시 상태
- LLM 추출 캐시 누적 진행
- 임베딩 URL 문제 수정 완료
- Groq 서버 상태에 따라 end-to-end 완주가 지연됨

---

## 2026-02-13 (저녁): OpenAI 임베딩 전환 및 재인덱싱
### 설정 변경
- LLM은 Groq 유지 (`llama-3.1-8b-instant`)
- 임베딩을 OpenAI로 전환 (`text-embedding-3-small`, 1536 dim)
- API 키 분리 구성
  - `LLM_BINDING_API_KEY` (Groq)
  - `EMBEDDING_BINDING_API_KEY` (OpenAI)

### 핵심 이슈: Embedding 차원 불일치
- 에러: `Embedding dim mismatch, expected: 1536, but loaded: 1024`
- 원인: 기존 `rag_storage`가 Jina(1024) 기준으로 생성됨
- 조치: 기존 저장소 백업 후 신규 저장소 재생성
  - 백업: `C:\LightRAG\rag_storage_backup_20260213_193830`
  - 신규: `C:\LightRAG\rag_storage`

### 검증
- 서버 재시작 후 `/health` 정상
- 문서 재인덱싱 파이프라인 정상 진행 확인

---

## 2026-02-14: 인덱싱 완료 검증 및 WebUI 이슈 분석
### 백엔드 검증
- `/query`, `/query/data`, `/query/stream` 응답 정상
- 문서 상태: `processed=1`, `failed=0`
- 그래프 상태: `462 nodes`, `358 edges`
- 벡터 차원: `1536` 확인

### WebUI 증상 및 원인
- 증상: Knowledge Graph 탭 `Empty`, Retrieval 탭 네트워크 오류 표시
- 로그: `GET /graph -> 404`, `GET /graphs`(label 없음) -> `422`
- 결론: 임베딩/인덱싱 실패가 아니라 WebUI 캐시/상태 불일치 이슈

### 조치
- `http://127.0.0.1:9700/webui/`로 접속 고정
- 강력 새로고침(`Ctrl+F5`) 또는 시크릿 창 사용
- 서버 프로세스 단일 유지

---

## 2026-02-14 ~ 2026-02-15: 품질 검증 프레임 정리
### 품질 검증표 추가
- 파일: `LightRAG 품질 검증표 (10문항).md`
- 목적: 운영 전 답변 품질 정량 평가 템플릿 확보
- 구성: 10문항, 10점 만점 스코어링, 합격 기준, 총계 집계 항목

### 문서화 상태
- 운영/트러블슈팅/검증 문서 세트 구성 완료
- 설치 -> 운영 -> 품질 검증 흐름 문서화 완료

---

## 2026-02-15: 최신 상태 (LightRAG)
- 스택: Groq LLM + OpenAI Embedding(1536) 조합 유지
- 서버/파이프라인: 헬스체크 및 인덱싱 결과 검증 완료 기록 유지
- 그래프/벡터: 생성 및 차원 일치 확인 완료
- 잔여 작업: 품질 검증표 10문항을 실제 질의 결과로 채점해 베이스라인 확정
