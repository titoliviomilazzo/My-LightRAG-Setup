# 설치 확인 스크립트 - 모든 필수 도구가 설치되었는지 확인
# Usage: .\tools\check_installation.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LightRAG 설치 확인 스크립트" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# 1. Python 확인
Write-Host "[1/3] Python 확인 중..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "    ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Python이 설치되지 않았거나 PATH에 없습니다" -ForegroundColor Red
    Write-Host "      → https://www.python.org/downloads/ 에서 Python 3.10+ 설치" -ForegroundColor Yellow
    $allOk = $false
}

Write-Host ""

# 2. Tesseract OCR 확인
Write-Host "[2/3] Tesseract OCR 확인 중..." -ForegroundColor Yellow
try {
    $tesseractVersion = tesseract --version 2>&1 | Select-Object -First 1
    Write-Host "    ✓ $tesseractVersion" -ForegroundColor Green

    # 한글 데이터 파일 확인
    $tesseractPath = (Get-Command tesseract).Source
    $tesseractDir = Split-Path $tesseractPath
    $korDataPath = Join-Path $tesseractDir "..\tessdata\kor.traineddata"

    if (Test-Path $korDataPath) {
        Write-Host "    ✓ 한글(Korean) 언어 데이터 있음" -ForegroundColor Green
    } else {
        Write-Host "    ⚠ 한글 언어 데이터가 없습니다!" -ForegroundColor Yellow
        Write-Host "      → Tesseract 재설치 시 Korean 언어 선택" -ForegroundColor Yellow
    }
} catch {
    Write-Host "    ✗ Tesseract가 설치되지 않았거나 PATH에 없습니다" -ForegroundColor Red
    Write-Host "      → https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
    Write-Host "      → 설치 시 반드시 'Korean' 언어 데이터 체크" -ForegroundColor Yellow
    Write-Host "      → 설치 후 'Add to PATH' 옵션 체크" -ForegroundColor Yellow
    $allOk = $false
}

Write-Host ""

# 3. Poppler 확인
Write-Host "[3/3] Poppler 확인 중..." -ForegroundColor Yellow
try {
    $popplerVersion = pdfimages -v 2>&1 | Select-Object -First 1
    Write-Host "    ✓ $popplerVersion" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Poppler가 설치되지 않았거나 PATH에 없습니다" -ForegroundColor Red
    Write-Host "      → https://github.com/oschwartz10612/poppler-windows/releases" -ForegroundColor Yellow
    Write-Host "      → poppler-xx.xx.x_x64.7z 다운로드" -ForegroundColor Yellow
    Write-Host "      → C:\에 압축 해제" -ForegroundColor Yellow
    Write-Host "      → C:\poppler-xx.xx.x\Library\bin 폴더를 PATH에 추가" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    자세한 방법: tools\PATH_설정_가이드.md 참조" -ForegroundColor Cyan
    $allOk = $false
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($allOk) {
    Write-Host "✓ 모든 필수 도구가 설치되었습니다!" -ForegroundColor Green
    Write-Host ""
    Write-Host "다음 단계:" -ForegroundColor Cyan
    Write-Host "  1. .\tools\setup.ps1 실행 (Python 패키지 설치)" -ForegroundColor White
    Write-Host "  2. .\tools\run_embedding_server.ps1 실행 (임베딩 서버)" -ForegroundColor White
    Write-Host "  3. LightRAG 서버 실행" -ForegroundColor White
} else {
    Write-Host "✗ 일부 도구가 설치되지 않았습니다" -ForegroundColor Red
    Write-Host ""
    Write-Host "PATH 설정 가이드: tools\PATH_설정_가이드.md" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠ PATH 변경 후에는 PowerShell을 재시작해야 합니다!" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
