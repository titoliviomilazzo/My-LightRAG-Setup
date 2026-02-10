Param(
    [Parameter(Mandatory=$true)][string]$KeyName,
    [Parameter(Mandatory=$true)][string]$Value
)

# Safe .env updater
$repoRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
Set-Location (Join-Path $repoRoot "..")

$envPath = Join-Path (Get-Location) ".env"
if (-Not (Test-Path $envPath)) {
    Write-Error ".env not found in repository root"
    exit 1
}

# Backup
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$backup = "$envPath.bak.$timestamp"
Copy-Item -Path $envPath -Destination $backup -Force
Write-Host "Backed up .env -> $backup"

# Read lines and replace or append
$lines = Get-Content $envPath
$found = $false
$newLines = @()
foreach ($line in $lines) {
    if ($line.Trim().StartsWith('#') -or $line.Trim() -eq '') {
        $newLines += $line
        continue
    }
    $idx = $line.IndexOf('=')
    if ($idx -lt 0) { $newLines += $line; continue }
    $k = $line.Substring(0,$idx).Trim()
    if ($k -ieq $KeyName) {
        $newLines += "${KeyName}=${Value}"
        $found = $true
    } else {
        $newLines += $line
    }
}
if (-not $found) { $newLines += "${KeyName}=${Value}" }

# Write back
Set-Content -Path $envPath -Value $newLines -Encoding UTF8
Write-Host ".env updated: $KeyName set. Restart the server to apply changes."
