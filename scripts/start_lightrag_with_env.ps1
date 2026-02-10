Param()
# Start script for LightRAG (PowerShell)
# - loads variables from .env (root)
# - creates logs/ if missing and writes stdout+stderr to logs/lightrag.log

$repoRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
Set-Location (Join-Path $repoRoot "..")

$envfile = ".env"
$logdir = ".\logs"
if (-Not (Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
$logfile = Join-Path $logdir "lightrag.log"

Write-Host "Loading environment from $envfile"
if (Test-Path $envfile) {
    Get-Content $envfile | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $idx = $line.IndexOf("=")
        if ($idx -lt 0) { return }
        $k = $line.Substring(0,$idx).Trim()
        $v = $line.Substring($idx+1).Trim()
        if ($v.StartsWith('"') -and $v.EndsWith('"')) { $v = $v.Substring(1,$v.Length-2) }
        [System.Environment]::SetEnvironmentVariable($k, $v)
    }
} else {
    Write-Warning ".env not found in repository root"
}

Write-Host "Writing logs to $logfile"
# Ensure UTF-8 output to avoid console encoding errors on Windows (cp949)
# Prefer PowerShell Core; for Windows PowerShell we'll try to set UTF8 code page.
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {
    Write-Warning "Could not set [Console]::OutputEncoding: $_"
}

# Set Python IO encoding environment so Python prints UTF-8
[System.Environment]::SetEnvironmentVariable('PYTHONIOENCODING','utf-8')

# Try switching console code page to UTF-8 (may require administrator in old powershell)
try {
    chcp 65001 > $null 2>&1
} catch {
    Write-Warning "Failed to change code page to UTF-8: $_"
}

# Run server and pipe all output to logfile while showing it in console
try {
    & python -u -m lightrag.api.lightrag_server *>&1 | Tee-Object -FilePath $logfile
} catch {
    Write-Error "Failed to start server: $_"
}
