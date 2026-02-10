# Windows PATH 설정 가이드

## Poppler 설치 및 PATH 추가

### 1단계: Poppler 다운로드
1. 브라우저에서 https://github.com/oschwartz10612/poppler-windows/releases 접속
2. 최신 릴리스의 **Assets** 섹션에서 `poppler-xx.xx.x_x64.7z` 다운로드
   - 예: `poppler-24.08.0_x64.7z`

### 2단계: 압축 해제
1. 다운로드한 `.7z` 파일을 **C 드라이브 루트**에 압축 해제
   - 7-Zip이 없으면 https://www.7-zip.org/ 에서 설치
2. 압축 해제 후 폴더 구조 확인:
   ```
   C:\poppler-24.08.0\
   ├── Library\
   │   └── bin\          ← 이 폴더를 PATH에 추가
   │       ├── pdfimages.exe
   │       ├── pdfinfo.exe
   │       └── ... (기타 실행 파일들)
   └── ... (기타 폴더들)
   ```

### 3단계: PATH에 추가 (방법 1 - GUI)

#### 3-1. 시스템 속성 열기
- **Windows 11/10:**
  1. 키보드에서 `Windows 키` 누름
  2. "환경 변수"라고 입력
  3. **"시스템 환경 변수 편집"** 클릭 (제어판 항목)

- **또는 직접 실행:**
  1. `Windows 키 + R` 눌러서 실행 창 열기
  2. `sysdm.cpl` 입력 후 Enter
  3. **"고급"** 탭 클릭
  4. **"환경 변수"** 버튼 클릭

#### 3-2. Path 변수 편집
1. **"시스템 변수"** 섹션(아래쪽)에서 **"Path"** 찾기
   - 주의: "사용자 변수"(위쪽)가 아닌 "시스템 변수"(아래쪽)
2. **"Path"** 선택 후 **"편집"** 버튼 클릭

#### 3-3. 새 경로 추가
1. **"새로 만들기"** 버튼 클릭
2. 다음 경로 입력:
   ```
   C:\poppler-24.08.0\Library\bin
   ```
   - **중요:** 본인이 압축 해제한 실제 경로로 변경
   - 예: `C:\poppler-24.08.0\Library\bin`
   - 또는: `C:\Program Files\poppler\Library\bin`

3. **"확인"** 버튼 3번 클릭하여 모든 창 닫기
   - 환경 변수 편집 창 → 확인
   - 환경 변수 창 → 확인
   - 시스템 속성 창 → 확인

### 3단계: PATH에 추가 (방법 2 - PowerShell)

**관리자 권한 PowerShell**에서 실행:

```powershell
# 현재 PATH 확인
[Environment]::GetEnvironmentVariable("Path", "Machine")

# Poppler bin 경로 추가
$oldPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$newPath = "C:\poppler-24.08.0\Library\bin"
[Environment]::SetEnvironmentVariable("Path", "$oldPath;$newPath", "Machine")

# 추가 확인
[Environment]::GetEnvironmentVariable("Path", "Machine") -split ";"
```

### 4단계: 변경사항 적용

**중요: PATH 변경 후 반드시 PowerShell/터미널을 재시작해야 합니다!**

1. 열려있는 모든 PowerShell 창 닫기
2. 새 PowerShell 창 열기
3. 테스트 명령 실행:
   ```powershell
   pdfimages -v
   ```

**성공 시 출력 예:**
```
pdfimages version 24.08.0
Copyright 2005-2024 The Poppler Developers - http://poppler.freedesktop.org
...
```

**실패 시 출력:**
```
pdfimages : 용어 'pdfimages'이(가) cmdlet, 함수, 스크립트 파일 또는 실행할 수 있는 프로그램 이름으로 인식되지 않습니다.
```
→ PATH 설정을 다시 확인하거나 PowerShell 재시작

---

## Tesseract OCR PATH 추가

### 1단계: Tesseract 설치
1. https://github.com/UB-Mannheim/tesseract/wiki 접속
2. **Windows Installer** 다운로드
   - 예: `tesseract-ocr-w64-setup-5.5.0.20241111.exe`
3. 설치 실행

### 2단계: 설치 옵션
설치 중 다음 옵션 선택:
- ✅ **Additional language data** 섹션에서:
  - ✅ **Korean** (kor) - 체크 필수!
  - ✅ English (eng) - 기본 선택됨
- ✅ **Add Tesseract to PATH** - 체크 (자동으로 PATH 추가됨)

기본 설치 경로: `C:\Program Files\Tesseract-OCR`

### 3단계: PATH 확인
대부분 자동으로 추가되지만, 안 될 경우 수동 추가:

**경로:** `C:\Program Files\Tesseract-OCR`

위의 **"Poppler PATH 추가"** 방법과 동일하게 추가

### 4단계: 테스트
```powershell
tesseract --version
```

**성공 시 출력 예:**
```
tesseract 5.5.0
 leptonica-1.84.1
  libjpeg 8d (libjpeg-turbo 3.0.1) : libpng 1.6.43 : libtiff 4.6.0 : zlib 1.3.1
```

---

## 전체 확인 스크립트

모든 설정이 완료되었는지 한번에 확인:

```powershell
Write-Host "=== PATH 설정 확인 ===" -ForegroundColor Green
Write-Host ""

# Python 확인
Write-Host "[1] Python:" -ForegroundColor Yellow
try {
    python --version
    Write-Host "    ✓ OK" -ForegroundColor Green
} catch {
    Write-Host "    ✗ NOT FOUND" -ForegroundColor Red
}

# Tesseract 확인
Write-Host "[2] Tesseract OCR:" -ForegroundColor Yellow
try {
    tesseract --version 2>&1 | Select-Object -First 1
    Write-Host "    ✓ OK" -ForegroundColor Green
} catch {
    Write-Host "    ✗ NOT FOUND" -ForegroundColor Red
}

# Poppler 확인
Write-Host "[3] Poppler:" -ForegroundColor Yellow
try {
    pdfimages -v 2>&1 | Select-Object -First 1
    Write-Host "    ✓ OK" -ForegroundColor Green
} catch {
    Write-Host "    ✗ NOT FOUND" -ForegroundColor Red
}

Write-Host ""
Write-Host "모든 항목이 OK이면 설치 완료!" -ForegroundColor Green
```

---

## 문제 해결

### PATH가 너무 길다는 에러
- Windows 10 이전 버전에서는 PATH 길이 제한(2048자)이 있음
- 해결: 짧은 경로 사용 (`C:\poppler\Library\bin` 등)

### 설정했는데도 명령이 안 먹힘
1. PowerShell/CMD를 **완전히 재시작** (중요!)
2. 혹은 PC 재부팅
3. PATH에 정확한 `bin` 폴더 경로가 들어갔는지 확인
   ```powershell
   $env:Path -split ";"
   ```

### "권한이 없습니다" 에러
- PowerShell을 **관리자 권한**으로 실행
  1. 시작 메뉴에서 "PowerShell" 검색
  2. 우클릭 → **"관리자 권한으로 실행"**

### Tesseract에서 한글이 안됨
```powershell
# 한글 데이터 파일 확인
ls "C:\Program Files\Tesseract-OCR\tessdata\kor.traineddata"
```
파일이 없으면:
1. Tesseract 재설치
2. 설치 중 **Korean** 언어 데이터 체크 확인
