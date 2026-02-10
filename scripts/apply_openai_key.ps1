Param()

# Prompt for OpenAI API key and apply to .env for minimal manual steps.
# Actions:
# 1. Prompt securely for key (masked input)
# 2. Backup .env
# 3. Set OPENAI_API_KEY, LLM_BINDING_API_KEY, EMBEDDING_BINDING_API_KEY
# 4. Stop running lightrag server processes (if found)
# 5. Start server using start_lightrag_with_env.ps1

$repoRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
Set-Location (Join-Path $repoRoot "..")

$envPath = Join-Path (Get-Location) ".env"
if (-Not (Test-Path $envPath)) {
    Write-Error ".env not found in repository root"
    exit 1
}

Write-Host "This script will update .env with your OpenAI API key and restart the server."
$secure = Read-Host -AsSecureString "Paste your OpenAI API key (input hidden)"
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
$key = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)

if (-not $key -or $key.Trim() -eq "") {
    Write-Error "No key provided. Aborting."
    exit 1
}

# Backup .env
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$backup = "$envPath.bak.$timestamp"
Copy-Item -Path $envPath -Destination $backup -Force
Write-Host "Backed up .env -> $backup"

function Set-Or-ReplaceKey([string]$path, [string]$keyName, [string]$value) {
    $lines = Get-Content $path -ErrorAction Stop
    $found = $false
    for ($i = 0; $i -lt $lines.Length; $i++) {
        $line = $lines[$i]
        if ($line.Trim().StartsWith('#') -or $line.Trim() -eq '') { continue }
        $idx = $line.IndexOf('=')
        if ($idx -lt 0) { continue }
        $k = $line.Substring(0,$idx).Trim()
        if ($k -ieq $keyName) {
            $lines[$i] = "$keyName=$value"
            $found = $true
            break
        }
    }
    if (-not $found) { $lines += "$keyName=$value" }
    Set-Content -Path $path -Value $lines -Encoding UTF8
}

Write-Host "Updating keys in .env..."
Set-Or-ReplaceKey -path $envPath -keyName "OPENAI_API_KEY" -value $key
Set-Or-ReplaceKey -path $envPath -keyName "LLM_BINDING_API_KEY" -value $key
Set-Or-ReplaceKey -path $envPath -keyName "EMBEDDING_BINDING_API_KEY" -value $key

Write-Host "Stopping existing LightRAG server processes (if any)..."
try {
    $procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'lightrag.api.lightrag_server' }
    if ($procs) {
        foreach ($p in $procs) {
            Write-Host "Stopping PID $($p.ProcessId) - $($p.CommandLine)"
            Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 1
    } else {
        Write-Host "No running LightRAG server processes found."
    }
} catch {
    Write-Warning "Could not reliably detect/stop existing processes: $_"
}

Write-Host "Starting LightRAG server using scripts/start_lightrag_with_env.ps1"
Start-Process -FilePath powershell -ArgumentList "-NoExit","-ExecutionPolicy","Bypass","-File","$repoRoot\start_lightrag_with_env.ps1"

Write-Host "Done. Server should start in a new PowerShell window. Check logs/log file for status."
