Param(
    [string]$Python = "python",
    [string]$Mirror = ""
)

$ErrorActionPreference = "Stop"

Write-Host "Preparing project virtual environment..." -ForegroundColor Cyan

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Could not create .venv. Install Python and try again."
        exit 1
    }
}

$venvPython = ".\.venv\Scripts\python.exe"

if (-not (Test-Path "requirements.txt")) {
    Write-Error "requirements.txt not found. Run this script from the repository root."
    exit 1
}

$pipArgs = @("-m", "pip", "install", "-r", "requirements.txt")
if ($Mirror) {
    # Only apply the mirror to this command; never modify global pip configuration.
    $pipArgs += @("--index-url", $Mirror)
}

Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
& $venvPython @pipArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "Dependency installation failed."
    exit 1
}

Write-Host "Environment ready. Start the app with .\run.ps1" -ForegroundColor Green
