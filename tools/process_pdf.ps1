# Process PDF with OCR and submit to LightRAG (Windows PowerShell)
# Usage: .\tools\process_pdf.ps1 <path_to_pdf_file>

param(
    [Parameter(Mandatory=$true)]
    [string]$PdfFile
)

Write-Host "=== PDF Processing Tool ===" -ForegroundColor Green
Write-Host ""

if (-not (Test-Path $PdfFile)) {
    Write-Host "[ERROR] File not found: $PdfFile" -ForegroundColor Red
    exit 1
}

$venvPath = "d:\03.Code\LightRAG\.venv-tools"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "[ERROR] Virtual environment not found. Please run setup.ps1 first" -ForegroundColor Red
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& $activateScript

Write-Host "Processing PDF: $PdfFile" -ForegroundColor Yellow
Write-Host ""

Set-Location "d:\03.Code\LightRAG"
python tools\pdf_ocr_and_submit.py $PdfFile
