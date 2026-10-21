# AI Fashion Fabric Analyst - Windows launcher
$ErrorActionPreference = "Stop"

$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Error "Missing project virtual environment. Run .\scripts\ensure_venv.ps1 first."
    exit 1
}

if (-not (Test-Path "app_new.py")) {
    Write-Error "app_new.py not found. Run the launcher from the repository root."
    exit 1
}

& $venvPython -c "import streamlit, dashscope, PIL, streamlit_cropper"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Some dependencies are missing. Run .\scripts\ensure_venv.ps1 first."
    exit 1
}

if (-not (Test-Path ".streamlit\secrets.toml") -and -not $env:DASHSCOPE_API_KEY) {
    Write-Host "No local DashScope key found. You can enter it in the application sidebar." -ForegroundColor Yellow
}

Write-Host "Starting Streamlit on http://localhost:9000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray

# Start only this app. Do not terminate other Streamlit sessions.
& $venvPython -m streamlit run app_new.py --server.port=9000
exit $LASTEXITCODE
