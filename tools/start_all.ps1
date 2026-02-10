# 모든 서버를 한번에 시작하는 스크립트
# 주의: 이 스크립트는 백그라운드로 서버를 실행합니다
# 종료하려면 stop_all.ps1을 실행하세요

Write-Host "=== LightRAG All Servers Starter ===" -ForegroundColor Green
Write-Host ""

$lightragRoot = "d:\03.Code\LightRAG"

# 1. 임베딩 서버 시작 (백그라운드)
Write-Host "[1/2] Starting Embedding Server..." -ForegroundColor Yellow
$embeddingJob = Start-Job -ScriptBlock {
    Set-Location "d:\03.Code\LightRAG"
    & ".\.venv-tools\Scripts\python.exe" "tools\embedding_server.py"
}
Write-Host "      Embedding Server Job ID: $($embeddingJob.Id)" -ForegroundColor Green

Start-Sleep -Seconds 5

# 2. LightRAG 서버 시작 (백그라운드)
Write-Host "[2/2] Starting LightRAG Server..." -ForegroundColor Yellow
$lightragJob = Start-Job -ScriptBlock {
    Set-Location "d:\03.Code\LightRAG"
    & ".\.venv\Scripts\Activate.ps1"
    & "lightrag-server"
}
Write-Host "      LightRAG Server Job ID: $($lightragJob.Id)" -ForegroundColor Green

Write-Host ""
Write-Host "=== All Servers Started ===" -ForegroundColor Green
Write-Host ""
Write-Host "Embedding Server: http://127.0.0.1:8001" -ForegroundColor Cyan
Write-Host "LightRAG Server:  http://localhost:9621" -ForegroundColor Cyan
Write-Host "WebUI:            http://localhost:9621/webui" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check logs:" -ForegroundColor Yellow
Write-Host "  Receive-Job -Id $($embeddingJob.Id) -Keep" -ForegroundColor White
Write-Host "  Receive-Job -Id $($lightragJob.Id) -Keep" -ForegroundColor White
Write-Host ""
Write-Host "Stop servers:" -ForegroundColor Yellow
Write-Host "  .\tools\stop_all.ps1" -ForegroundColor White
Write-Host ""

# Job IDs 저장
@{
    EmbeddingJobId = $embeddingJob.Id
    LightRAGJobId = $lightragJob.Id
} | ConvertTo-Json | Out-File "$lightragRoot\tools\.job_ids.json"

Write-Host "Servers are running in background. Close this window anytime." -ForegroundColor Green
