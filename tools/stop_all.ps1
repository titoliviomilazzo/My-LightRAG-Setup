# 모든 서버를 중지하는 스크립트

Write-Host "=== Stopping All LightRAG Servers ===" -ForegroundColor Yellow
Write-Host ""

$jobIdsFile = "d:\03.Code\LightRAG\tools\.job_ids.json"

# Job IDs 읽기
if (Test-Path $jobIdsFile) {
    $jobIds = Get-Content $jobIdsFile | ConvertFrom-Json

    Write-Host "Stopping Embedding Server (Job $($jobIds.EmbeddingJobId))..." -ForegroundColor Yellow
    Stop-Job -Id $jobIds.EmbeddingJobId -ErrorAction SilentlyContinue
    Remove-Job -Id $jobIds.EmbeddingJobId -ErrorAction SilentlyContinue

    Write-Host "Stopping LightRAG Server (Job $($jobIds.LightRAGJobId))..." -ForegroundColor Yellow
    Stop-Job -Id $jobIds.LightRAGJobId -ErrorAction SilentlyContinue
    Remove-Job -Id $jobIds.LightRAGJobId -ErrorAction SilentlyContinue

    Remove-Item $jobIdsFile -ErrorAction SilentlyContinue
    Write-Host "All background jobs stopped" -ForegroundColor Green
}

# 포트 기반으로 프로세스 종료
Write-Host ""
Write-Host "Checking for processes on ports 8001 and 9621..." -ForegroundColor Yellow

# 포트 8001 (임베딩 서버)
$embeddingProcess = Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue
if ($embeddingProcess) {
    Write-Host "Killing process on port 8001 (PID: $($embeddingProcess.OwningProcess))" -ForegroundColor Yellow
    Stop-Process -Id $embeddingProcess.OwningProcess -Force -ErrorAction SilentlyContinue
}

# 포트 9621 (LightRAG 서버)
$lightragProcess = Get-NetTCPConnection -LocalPort 9621 -State Listen -ErrorAction SilentlyContinue
if ($lightragProcess) {
    Write-Host "Killing process on port 9621 (PID: $($lightragProcess.OwningProcess))" -ForegroundColor Yellow
    Stop-Process -Id $lightragProcess.OwningProcess -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "=== All Servers Stopped ===" -ForegroundColor Green
