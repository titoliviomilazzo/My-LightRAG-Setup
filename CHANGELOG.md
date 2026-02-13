# Changelog

## 2026-02-12 ~ 2026-02-13: LightRAG 초기 설정 및 트러블슈팅

### 환경 구축
- LightRAG v1.4.9.11 설치 (C:\LightRAG\, Python 3.11 venv)
- GitHub 레포 클론: https://github.com/titoliviomilazzo/My-LightRAG-Setup

### 트러블슈팅 이력

#### 1. 서버 포트 바인딩 실패
- 원인: Windows Hyper-V가 9559-9658 포트 예약
- 해결: PORT=9700으로 변경

#### 2. Unicode 인코딩 에러 (cp949)
- 원인: Windows 한글 환경에서 기본 인코딩 cp949
- 해결: PYTHONIOENCODING=utf-8 환경변수 추가

#### 3. 로컬 Ollama 시도 → 실패/포기
- qwen2.5-coder:14b → 4GB VRAM 초과, 타임아웃
- qwen2.5:7b → 작동하나 청크당 3.8분 (5MB PDF에 3시간), 한중 혼동
- bge-m3 임베딩 → 한글 토큰 "비선형거동"에서 NaN 반환 버그
- 결론: 로컬 LLM/임베딩 모두 폐기

#### 4. 클라우드 API 시도
- Gemini Flash → 429 RESOURCE_EXHAUSTED (무료 할당량 0)
- OpenAI → insufficient_quota (크레딧 없음)
- Groq llama-3.3-70b → 무료 TPM 한도 12,000 초과
- **Groq llama-3.1-8b-instant → 성공** (50/50 청크 추출 완료)

#### 5. Jina 임베딩 URL 버그
- 증상: Jina 요청이 Groq URL로 전송됨 (404 에러)
- 원인: LightRAG config.py의 get_default_host()에 "jina" 항목 없음 → LLM_BINDING_HOST로 폴백
- 해결: .env에 EMBEDDING_BINDING_HOST=https://api.jina.ai/v1/embeddings 명시

#### 6. Groq 일일 토큰 한도 (TPD) 초과
- 증상: Chunk 13/50에서 429 rate_limit_exceeded (500K TPD)
- 해결: Groq Dev Tier 업그레이드 (카드 등록, 사용량 과금)

#### 7. Groq 서버 과부하 (현재 이슈)
- 증상: Chunk 18/50에서 503 over capacity
- 상태: 17/50 청크 캐시됨, 재시도 시 나머지만 처리하면 됨
- 대응: 시간 두고 재업로드 필요

### 현재 상태
- LLM 추출: 17/50 청크 캐시 완료
- 임베딩: Jina URL 수정 완료, 정상 작동 확인
- 전체 파이프라인: 아직 end-to-end 완주 못함 (Groq 503 대기 중)

---

## 2026-02-13 (저녁): OpenAI 임베딩 전환 및 재인덱싱

### 1) 결제/모델 전략 정리
- ChatGPT Pro 구독과 OpenAI API 과금은 별도임을 확인
- 테스트 목적 임베딩은 OpenAI `text-embedding-3-small` 사용으로 결정 (1536 dim)

### 2) .env 구성 변경
- LLM: Groq 유지 (`llama-3.1-8b-instant`)
- Embedding: OpenAI 전환
  - `EMBEDDING_BINDING=openai`
  - `EMBEDDING_BINDING_HOST=https://api.openai.com/v1`
  - `EMBEDDING_MODEL=text-embedding-3-small`
  - `EMBEDDING_DIM=1536`
- API 키는 용도별 분리
  - `LLM_BINDING_API_KEY` (Groq)
  - `EMBEDDING_BINDING_API_KEY` (OpenAI)

### 3) 주요 장애: Embedding dim mismatch
- 에러:
  - `AssertionError: Embedding dim mismatch, expected: 1536, but loaded: 1024`
- 원인:
  - 기존 `rag_storage`가 Jina(1024) 벡터로 생성되어 있었고,
  - OpenAI(1536) 설정과 충돌
- 조치:
  - 기존 저장소 백업 후 신규 저장소로 초기화
  - 백업 디렉터리: `C:\LightRAG\rag_storage_backup_20260213_193830`
  - 신규 디렉터리: `C:\LightRAG\rag_storage`

### 4) 재시작 및 재처리
- 서버 재시작 후 health에서 OpenAI 임베딩 반영 확인
- 문서 재스캔 재개 (`안동중앙고-보고서.pdf`)
- 파이프라인 재실행 상태 확인:
  - `processing=1`, `failed=0`
  - 진행 메시지: `Chunk ... of 50 extracted ...`

### 현재 상태 (업데이트)
- 서버 상태: `healthy`
- 임베딩 바인딩: `openai` (1536 dim)
- 작업 상태: 문서 1건 재인덱싱 진행 중
