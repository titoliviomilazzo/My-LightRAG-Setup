# Setup script for Local Embedding Server & PDF OCR Tools (Windows PowerShell)
# Run this script to install all dependencies

Write-Host "=== LightRAG Local Tools Setup ===" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.10+ and add to PATH" -ForegroundColor Red
    exit 1
}

# Check if Tesseract is installed
Write-Host ""
Write-Host "Checking Tesseract OCR..." -ForegroundColor Yellow
try {
    $tesseractVersion = tesseract --version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Tesseract found: $tesseractVersion" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Tesseract not found in PATH" -ForegroundColor Yellow
    Write-Host "Download from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
    Write-Host "After installation, add to PATH and restart PowerShell" -ForegroundColor Yellow
}

# Check if Poppler is installed
Write-Host ""
Write-Host "Checking Poppler (for pdf2image)..." -ForegroundColor Yellow
try {
    $pdfimagesVersion = pdfimages -v 2>&1 | Select-Object -First 1
    Write-Host "[OK] Poppler found: $pdfimagesVersion" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Poppler not found in PATH" -ForegroundColor Yellow
    Write-Host "Download from: https://github.com/oschwartz10612/poppler-windows/releases" -ForegroundColor Yellow
    Write-Host "Extract and add 'bin' folder to PATH, then restart PowerShell" -ForegroundColor Yellow
}

# Create virtual environment if it doesn't exist
Write-Host ""
Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
$venvPath = "d:\03.Code\LightRAG\.venv-tools"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath" -ForegroundColor Yellow
    python -m venv $venvPath
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual environment already exists" -ForegroundColor Green
}

# Activate venv and install packages
Write-Host ""
Write-Host "Installing Python packages..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

pip install --upgrade pip
pip install -r "d:\03.Code\LightRAG\tools\requirements.txt"

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Make sure Tesseract and Poppler are in your PATH"
Write-Host "2. Run: .\tools\run_embedding_server.ps1"
Write-Host "3. In another terminal, process PDFs with: .\tools\process_pdf.ps1 <file.pdf>"
Write-Host ""
