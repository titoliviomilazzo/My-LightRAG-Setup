# Start Local Embedding Server (Windows PowerShell)
# This server provides OpenAI-compatible embedding API at http://127.0.0.1:8001

Write-Host "=== Starting Local Embedding Server ===" -ForegroundColor Green
Write-Host ""

$venvPath = "d:\03.Code\LightRAG\.venv-tools"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "[ERROR] Virtual environment not found. Please run setup.ps1 first" -ForegroundColor Red
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& $activateScript

Write-Host "Starting embedding server on http://127.0.0.1:8001" -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location "d:\03.Code\LightRAG"
python tools\embedding_server.py
