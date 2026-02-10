Param(
    [string]$RemoteUrl = "https://github.com/titoliviomilazzo/My-LightRAG-Setup.git",
    [string]$CommitMessage = "Sync local LightRAG changes"
)

Set-StrictMode -Version Latest
Push-Location $PSScriptRoot
try {
    if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
        Write-Host "No git repository found — initializing a new repo." -ForegroundColor Yellow
        git init
    }

    $originUrl = git remote get-url origin 2>$null
    if ($LASTEXITCODE -eq 0 -and $originUrl) {
        git remote set-url origin $RemoteUrl
        Write-Host "Updated origin to $RemoteUrl"
    } else {
        git remote add origin $RemoteUrl
        Write-Host "Added origin $RemoteUrl"
    }

    git add -A
    # commit if there's anything staged
    git diff --cached --quiet
    if ($LASTEXITCODE -ne 0) {
        git commit -m $CommitMessage
    } else {
        Write-Host "No staged changes to commit." -ForegroundColor Green
    }

    Write-Host "Pushing to origin (you may be prompted for credentials)..." -ForegroundColor Cyan
    git push -u origin HEAD
} finally {
    Pop-Location
}
