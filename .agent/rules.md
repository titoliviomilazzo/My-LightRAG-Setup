# LightRAG 내진성능평가 보고서 RAG 시스템

# 이 프로젝트는 뭔가
한국 구조공학 문서 기반 RAG 시스템이다.
내진성능평가 보고서, 점성댐퍼를 이용한 내진보강 보고서, MIDAS Gen 해석결과, Perform-3D 결과를 파싱해서 질의응답하는 시스템.


## 기술 스택
- Python 3.11
- LightRAG v1.4.9.11 (HKUDS/LightRAG) - Graph-based RAG 프레임워크
- Groq Cloud API (OpenAI-compatible) - LLM 추론
- Jina AI API - 임베딩
- Ollama - 로컬 LLM/임베딩 (대안, 현재 미사용)
- Windows 11 / RTX 3050 Laptop (4GB VRAM)

## LLM 설정
- 바인딩: openai (Groq 호환)
- 모델: llama-3.1-8b-instant (Groq Dev Tier)
- 호스트: https://api.groq.com/openai/v1
- 타임아웃: 120초
- MAX_ASYNC: 1 (동시 LLM 호출 1개로 제한, rate limit 방지)

## 임베딩 설정
- 바인딩: jina
- 모델: jina-embeddings-v3
- 차원: 1024
- 호스트: https://api.jina.ai/v1/embeddings
- 주의: EMBEDDING_BINDING_HOST를 명시적으로 설정해야 함 (미설정 시 LLM_BINDING_HOST로 폴백되는 버그)

## RAG 설정
- CHUNK_SIZE: 500
- CHUNK_OVERLAP_SIZE: 50
- SUMMARY_LANGUAGE: Korean
- MAX_PARALLEL_INSERT: 2
- 서버 포트: 9700 (기본 9621은 Hyper-V 포트 예약과 충돌)

## 스토리지
- KV: JsonKVStorage
- Vector: NanoVectorDBStorage
- Graph: NetworkXStorage
- RAG 디렉토리: rag_storage

## 경로
- LightRAG 서버: C:\LightRAG\
- 가상환경: C:\LightRAG\.venv\
- 설정파일: C:\LightRAG\.env
- 로그: C:\LightRAG\lightrag.log
- GitHub 레포: J:\내 드라이브\Code\My-LightRAG-Setup\

## 지금까지 결정된 것들
- 서버 포트 9700 사용 (Windows Hyper-V가 9559-9658 포트 예약하므로)
- PYTHONIOENCODING=utf-8 필수 (Windows cp949 인코딩 문제 해결)
- 로컬 Ollama qwen2.5:7b → 너무 느림 (청크당 3.8분, 5MB PDF에 3시간) → 폐기
- 로컬 Ollama bge-m3 임베딩 → 한글 토큰에서 NaN 반환 버그 → 폐기
- Groq llama-3.3-70b-versatile → 무료 티어 TPM 한도(12,000) 너무 낮음 → 폐기
- Groq llama-3.1-8b-instant 선택 (속도 빠르고 TPM 한도 높음)
- Jina embeddings-v3 선택 (한글 품질 우수, bge-m3 NaN 버그 회피)
- Groq Dev Tier 업그레이드 완료 (일일 50만 토큰 한도 해제)
- LLM 캐시 활성화 (ENABLE_LLM_CACHE_FOR_EXTRACT=True) → 실패 후 재시도 시 이전 청크 스킵 가능

## 알려진 이슈
- Groq 503 (서버 과부하): llama-3.1-8b-instant가 일시적으로 과부하 상태일 때 발생. 시간 두고 재시도 필요
- Jina 429 (동시접속 제한 2/2): 초기 임베딩 단계에서 발생하나 tenacity 재시도로 자동 해결됨
- LLM 출력 포맷 에러 (WARNING): Entity/Relation 필드 수 불일치. 무시해도 처리는 계속됨
- PDF 처리 실패 시 rag_storage 삭제 후 재시도 권장

## 서버 실행 명령
cd C:\LightRAG
PYTHONIOENCODING=utf-8 .venv\Scripts\python.exe -m lightrag.api.lightrag_server



## 비용 추산 (Groq Dev Tier + Jina)
- LLM: ~$0.03-0.05/PDF (5MB 기준)
- Embedding: ~$0.016/PDF
- 10개 PDF: ~$0.50 이하
- 100개 PDF (각 10MB): ~$5-8