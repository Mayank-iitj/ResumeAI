# Resume Analyzer CLI - Installation and Setup Script
# For Windows PowerShell

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Resume Analyzer CLI - Installation Script" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Python is installed" -ForegroundColor Green
Write-Host ""

# Create virtual environment
Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists. Skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}
Write-Host ""

# Activate virtual environment
Write-Host "[3/6] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "[4/6] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✓ Pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "[5/6] Installing dependencies (this may take several minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Download NLTK data
Write-Host "[6/6] Downloading NLTK data..." -ForegroundColor Yellow
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"
Write-Host "✓ NLTK data downloaded" -ForegroundColor Green
Write-Host ""

# Download spaCy model
Write-Host "[6/6] Downloading spaCy model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm
Write-Host "✓ spaCy model downloaded" -ForegroundColor Green
Write-Host ""

Write-Host "=" * 80 -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the installation:" -ForegroundColor White
Write-Host "   python analyzer.py --resume data\sample_resumes\sample_resume_ml.txt --jd data\sample_jds\ml_engineer_jd.txt --output output\" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run tests:" -ForegroundColor White
Write-Host "   pytest tests\ -v" -ForegroundColor Gray
Write-Host ""
Write-Host "3. See QUICKSTART.md for more examples" -ForegroundColor White
Write-Host ""
