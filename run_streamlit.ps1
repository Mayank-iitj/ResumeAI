# PowerShell script to run Streamlit app
# Resume Analyzer - Streamlit Launch Script

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "Resume Analyzer - Streamlit Web App" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & ".\venv\Scripts\Activate.ps1"
        Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Virtual environment not found. Run install.ps1 first." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[OK] Virtual environment already activated: $env:VIRTUAL_ENV" -ForegroundColor Green
}

# Check if Streamlit is installed
Write-Host "[INFO] Checking Streamlit installation..." -ForegroundColor Yellow
$streamlit_version = python -c "import streamlit; print(streamlit.__version__)" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Streamlit not found. Installing..." -ForegroundColor Yellow
    pip install streamlit plotly kaleido
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Streamlit installed successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to install Streamlit" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[OK] Streamlit $streamlit_version found" -ForegroundColor Green
}

# Create output directory
if (-not (Test-Path "output")) {
    New-Item -ItemType Directory -Path "output" | Out-Null
    Write-Host "[OK] Created output directory" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "Starting Streamlit App..." -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""
Write-Host "The app will open in your browser at: http://localhost:8501" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run Streamlit
python -m streamlit run app.py
