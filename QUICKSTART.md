# Quick Start Guide - Resume Analyzer CLI

## Installation

```powershell
# Navigate to project directory
cd D:\resume-analyzer-cli

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Quick Test

```powershell
# Test with sample data
python analyzer.py --resume data\sample_resumes\sample_resume_ml.txt --jd data\sample_jds\ml_engineer_jd.txt --output output\
```

## Example Commands

### Single Resume Analysis
```powershell
python analyzer.py --resume path\to\resume.pdf --jd path\to\job_desc.txt --output results\
```

### Batch Processing
```powershell
python analyzer.py --resumes data\sample_resumes\ --jd data\sample_jds\ml_engineer_jd.txt --output results\ --topk 5
```

### Generate PDF Report
```powershell
python analyzer.py --resume resume.pdf --jd job_desc.txt --report pdf
```

## Running Tests

```powershell
# Run all tests
pytest tests\ -v

# Run with coverage
pytest tests\ --cov=. --cov-report=html
```

## Project Structure
```
resume-analyzer-cli/
├── analyzer.py          # Main CLI
├── parsers/             # PDF/DOCX/TXT parsing
├── extractors/          # Data extraction
├── scorer.py            # ATS scoring
├── ranker.py            # Candidate ranking
├── optimizer.py         # Feedback generation
├── utils/               # Utilities
├── reports/             # Report generators
├── tests/               # Test suite
└── data/                # Sample data
```

## Output

Results are saved in the output directory:
- `resume_analysis.json` - Detailed JSON report
- `candidate_rankings.csv` - CSV ranking table
- `report.pdf` - PDF report (if requested)

## Troubleshooting

If you encounter import errors, ensure:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. You're running from the project root directory

## Next Steps

1. Add your own resumes to `data/sample_resumes/`
2. Add job descriptions to `data/sample_jds/`
3. Run batch analysis to rank candidates
4. Customize scoring weights in `scorer.py`
5. Extend skill database in `extractors/skills_extractor.py`
