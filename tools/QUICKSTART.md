# 빠른 시작 가이드

OpenAI API quota 문제를 해결하고 로컬에서 LightRAG를 실행하는 가장 빠른 방법입니다.

## 1단계: 외부 도구 설치 (Windows)

### Tesseract OCR (한글 OCR용)
1. 다운로드: https://github.com/UB-Mannheim/tesseract/wiki
2. 설치 시 **Additional language data** 섹션에서 **Korean** 체크
3. 설치 경로를 PATH에 추가 (보통 자동으로 추가됨)

### Poppler (PDF 처리용)
1. 다운로드: https://github.com/oschwartz10612/poppler-windows/releases
2. 최신 릴리스에서 `poppler-xx.xx.x-win64.zip` 다운로드
3. 압축 해제 후 `poppler-xx.xx.x\Library\bin` 폴더를 PATH에 추가

**PATH 추가 방법:**
1. Windows 검색에서 "환경 변수" 검색
2. "시스템 환경 변수 편집" 클릭
3. "환경 변수" 버튼 클릭
4. "시스템 변수" 섹션에서 "Path" 선택 후 "편집"
5. "새로 만들기"를 클릭하고 경로 추가:
   - Tesseract: `C:\Program Files\Tesseract-OCR`
   - Poppler: `C:\poppler-xx.xx.x\Library\bin`

**중요:** PATH 변경 후 PowerShell을 **재시작**해야 합니다.

## 2단계: Python 패키지 설치

PowerShell을 **관리자 권한**으로 실행:

```powershell
cd d:\03.Code\LightRAG
.\tools\setup.ps1
```

## 3단계: 서버 실행

### 터미널 1: 로컬 임베딩 서버

```powershell
cd d:\03.Code\LightRAG
.\tools\run_embedding_server.ps1
```

출력 예시:
```
Loading model: paraphrase-multilingual-mpnet-base-v2...
Model loaded. Embedding dimension: 768
Starting local embedding server on http://127.0.0.1:8001
Press CTRL+C to quit
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### 터미널 2: LightRAG 서버

```powershell
cd d:\03.Code\LightRAG
.\.venv\Scripts\Activate.ps1
lightrag-server
```

출력 예시:
```
INFO:     Uvicorn running on http://0.0.0.0:9621
```

## 4단계: PDF 업로드

### 터미널 3: PDF 처리

```powershell
cd d:\03.Code\LightRAG
.\tools\process_pdf.ps1 "inputs\노원구청_공법제안서(원본)_실리콘점성감쇠장치_20240423.pdf"
```

## 5단계: 웹 UI 접속

브라우저에서 http://localhost:9621/webui 접속

## 문제 해결 체크리스트

### ✓ 임베딩 서버 확인
```powershell
curl http://127.0.0.1:8001
```
예상 출력:
```json
{"status":"ok","model":"paraphrase-multilingual-mpnet-base-v2","dimension":768}
```

### ✓ Tesseract 확인
```powershell
tesseract --version
```

### ✓ Poppler 확인
```powershell
pdfimages -v
```

### ✓ LightRAG 로그 확인
```powershell
Get-Content logs\lightrag.log -Tail 30
```

**에러를 찾으면:**
- `Error code: 429` → 임베딩 서버가 실행 중인지 확인
- `TesseractNotFoundError` → PATH에 Tesseract 추가 후 PowerShell 재시작
- `PDFInfoNotInstalledError` → PATH에 Poppler 추가 후 PowerShell 재시작

## 모든 것이 작동하는지 테스트

```powershell
# 1. 임베딩 서버 테스트
curl http://127.0.0.1:8001

# 2. LightRAG 서버 테스트
curl http://localhost:9621/health

# 3. 샘플 PDF 처리 (이미 있는 파일 사용)
.\tools\process_pdf.ps1 "inputs\노원구청_공법제안서(원본)_실리콘점성감쇠장치_20240423.pdf"

# 4. 로그 확인
Get-Content logs\lightrag.log -Tail 50
```

## 성공 신호

로그에서 다음과 같은 메시지를 찾으면 성공입니다:

```
INFO - Successfully extracted and enqueued file: 노원구청_공법제안서(원본)_실리콘점성감쇠장치_20240423.pdf
INFO - Processing 1 document(s)
INFO - Extracting stage 1/1: 노원구청_공법제안서(원본)_실리콘점성감쇠장치_20240423.pdf
```

**429 에러가 없으면** 로컬 임베딩이 제대로 작동하는 것입니다!

## 다음 단계

- 더 많은 PDF 업로드
- 웹 UI에서 쿼리 테스트
- 그래프 시각화 확인

자세한 내용은 [README.md](README.md)를 참조하세요.
