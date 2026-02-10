# Add Tesseract to System PATH
# Run as Administrator

Write-Host "Adding Tesseract to System PATH..." -ForegroundColor Green

$tesseractPath = "C:\Program Files\Tesseract-OCR"

# Check if Tesseract exists
if (-not (Test-Path "$tesseractPath\tesseract.exe")) {
    Write-Host "ERROR: Tesseract not found at $tesseractPath" -ForegroundColor Red
    exit 1
}

# Get current PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

# Check if already in PATH
if ($currentPath -like "*$tesseractPath*") {
    Write-Host "Tesseract is already in PATH" -ForegroundColor Yellow
    Write-Host "Restart PowerShell and test with: tesseract --version" -ForegroundColor Cyan
    exit 0
}

# Add to PATH
try {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$tesseractPath", "Machine")
    Write-Host "SUCCESS: Tesseract added to PATH" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Close this PowerShell window" -ForegroundColor White
    Write-Host "2. Open new PowerShell window" -ForegroundColor White
    Write-Host "3. Test: tesseract --version" -ForegroundColor White
} catch {
    Write-Host "ERROR: Failed to add to PATH" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
