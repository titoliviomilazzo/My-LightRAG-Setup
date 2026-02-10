# LightRAG Local Tools

로컬 환경에서 LightRAG를 실행하기 위한 도구 모음입니다.

## 구성 요소

1. **로컬 임베딩 서버** (`embedding_server.py`)
   - OpenAI API 대신 로컬 sentence-transformers 모델 사용
   - 한글 지원 멀티링구얼 모델: `paraphrase-multilingual-mpnet-base-v2` (768차원)
   - OpenAI 호환 API 엔드포인트 제공

2. **PDF OCR 및 업로드 도구** (`pdf_ocr_and_submit.py`)
   - PDF에서 텍스트, 표, 이미지 추출
   - 한글/영어 OCR 지원 (Tesseract)
   - LightRAG 서버로 자동 업로드

## 사전 요구사항 (Windows)

### 1. Tesseract OCR 설치
- 다운로드: https://github.com/UB-Mannheim/tesseract/wiki
- 설치 후 PATH에 추가
- 한글 데이터 파일(`kor.traineddata`)이 포함되어 있는지 확인

### 2. Poppler 설치
- 다운로드: https://github.com/oschwartz10612/poppler-windows/releases
- 압축 해제 후 `bin` 폴더를 PATH에 추가

### 3. Python 3.10+
- 이미 설치되어 있어야 함

## 설치 및 실행

### 1. 초기 설정

PowerShell에서 실행:

```powershell
cd d:\03.Code\LightRAG
.\tools\setup.ps1
```

이 스크립트는 다음을 수행합니다:
- Python 가상환경 생성 (`.venv-tools`)
- 필요한 Python 패키지 설치
- Tesseract 및 Poppler 설치 여부 확인

### 2. 로컬 임베딩 서버 실행

새 PowerShell 터미널에서:

```powershell
cd d:\03.Code\LightRAG
.\tools\run_embedding_server.ps1
```

서버가 `http://127.0.0.1:8001`에서 실행됩니다.

**테스트:**
```powershell
curl http://127.0.0.1:8001
```

### 3. LightRAG 서버 시작

다른 PowerShell 터미널에서:

```powershell
cd d:\03.Code\LightRAG
.\.venv\Scripts\Activate.ps1
lightrag-server
```

서버가 `http://0.0.0.0:9621`에서 실행됩니다.

### 4. PDF 처리 및 업로드

새로운 PowerShell 터미널에서:

```powershell
cd d:\03.Code\LightRAG
.\tools\process_pdf.ps1 "경로\파일.pdf"
```

또는 Python 직접 실행:

```powershell
.\.venv-tools\Scripts\Activate.ps1
python tools\pdf_ocr_and_submit.py "경로\파일.pdf"
```

## 설정 파일

### .env 설정 확인

로컬 임베딩 서버를 사용하도록 `.env` 파일이 업데이트되어 있습니다:

```bash
# 로컬 임베딩 설정
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2
EMBEDDING_DIM=768
EMBEDDING_BINDING_HOST=http://127.0.0.1:8001/v1
EMBEDDING_BINDING_API_KEY=local-embedding

# 동시성 제어 (로컬 환경용 낮은 값)
MAX_ASYNC=2
MAX_PARALLEL_INSERT=1
EMBEDDING_FUNC_MAX_ASYNC=1
EMBEDDING_BATCH_NUM=1
```

## 문제 해결

### 1. OpenAI API Quota 초과 에러
```
openai.RateLimitError: Error code: 429 - insufficient_quota
```

**해결책:**
- 로컬 임베딩 서버가 실행 중인지 확인
- `.env`에서 `EMBEDDING_BINDING_HOST=http://127.0.0.1:8001/v1`로 설정되어 있는지 확인

### 2. Tesseract 에러
```
pytesseract.pytesseract.TesseractNotFoundError
```

**해결책:**
- Tesseract가 설치되어 있고 PATH에 추가되어 있는지 확인
- PowerShell을 재시작하여 PATH 변경사항 적용

### 3. Poppler 에러
```
PDFInfoNotInstalledError: Unable to get page count
```

**해결책:**
- Poppler가 설치되어 있고 `bin` 폴더가 PATH에 추가되어 있는지 확인
- PowerShell을 재시작하여 PATH 변경사항 적용

### 4. 한글 OCR 안됨

**해결책:**
- Tesseract 설치 시 언어 데이터 파일 중 Korean(`kor.traineddata`)이 포함되어 있는지 확인
- 경로: `C:\Program Files\Tesseract-OCR\tessdata\kor.traineddata`

## 고급 기능

### 더 나은 표 추출 (선택사항)

Camelot 또는 Tabula를 사용하여 더 정확한 표 추출이 가능합니다:

```powershell
# Java 설치 필요
pip install camelot-py[cv]
# 또는
pip install tabula-py
```

### 더 큰 임베딩 모델 사용

`embedding_server.py`에서 모델 변경:

```python
# 더 큰 모델 (1024차원)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# 한글 특화 모델
MODEL_NAME = "jhgan/ko-sroberta-multitask"
```

`.env`에서 차원 수도 함께 업데이트:

```bash
EMBEDDING_DIM=1024  # 또는 모델에 맞는 차원
```

## 로그 확인

### LightRAG 서버 로그
```powershell
Get-Content d:\03.Code\LightRAG\logs\lightrag.log -Tail 50 -Wait
```

### 임베딩 서버 로그
임베딩 서버를 실행한 터미널에서 직접 확인

## 다음 단계

1. 웹 UI 접속: http://localhost:9621/webui
2. API 문서: http://localhost:9621/docs
3. 문서 업로드 후 쿼리 테스트

## 참고 자료

- LightRAG 문서: [README.md](../README.md)
- Sentence Transformers: https://www.sbert.net/
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- pdfplumber: https://github.com/jsvine/pdfplumber
