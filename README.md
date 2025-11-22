# AI Resume Screening & Candidate Fit Prediction System

## Overview
This project provides an end-to-end pipeline to ingest resumes (PDF, DOCX, TXT) and a job description (JD), extract structured features (skills, experience, education, domains), compute semantic similarity using transformer embeddings, produce fit scores, rank candidates, and generate improvement suggestions. A Streamlit web app offers an interactive interface for recruiters and candidates.

## Features (Phase 1 Implemented)
- Multi-file resume upload + JD input (text/file)
- Parsing PDFs / DOCX / TXT into raw text
- Heuristic section splitting (Summary, Experience, Education, Skills, Projects, Certifications)
- spaCy NER for entities (ORG, PERSON, GPE, DATE, etc.)
- Skill extraction via curated keyword list + synonyms + regex
- Sentence-transformer embeddings (all-MiniLM-L6-v2) for semantic similarity
- Scoring engine with configurable weights (skills, experience, education, domain, soft skills)
- Ranking of multiple resumes
- Suggestions module for missing skills, bullet improvements, section recommendations
- Ethical considerations (no use of PII like gender, age; placeholders for anonymization)

## Planned / Placeholder Advanced Features
- Multi-JD comparison per resume
- Resume anonymization pipeline
- Bias/fairness audit hooks
- Model monitoring (score distributions, evaluation metrics)
- Multilingual support (switch to multilingual model)
- Export reports (PDF/CSV)

## Project Structure
```
resume_screening/
  config.py
  parser.py
  nlp_extractor.py
  scoring_engine.py
  suggestions.py
  utils.py
  models/ (cache for downloaded models)
app/
  streamlit_app.py
resumes_samples/
  sample_resume_1.txt
  sample_resume_2.txt
jds_samples/
  sample_jd_data_scientist.txt
requirements.txt
README.md
```

## Configuration
Edit weights, thresholds, synonym maps in `resume_screening/config.py`.

## Running Locally
1. Create virtual environment (recommended):
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```
2. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
3. Launch app:
```bash
streamlit run app/streamlit_app.py
```

## Environment Configuration
Optional environment variables (set in a `.env` file):

```
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SPACY_MODEL=en_core_web_sm
MAX_UPLOAD_MB=2
ENABLE_ANONYMIZATION=true
```

## Deployment (Docker)
Build and run with Docker:
```bash
docker build -t resume-screening .
docker run -p 8501:8501 --env-file .env resume-screening
```
App accessible at: http://localhost:8501

## Production Recommendations
- Use reverse proxy (nginx) for TLS termination.
- Set `MAX_UPLOAD_MB` conservatively (e.g., 2–5 MB).
- Pre-download models in image build stage to avoid cold starts.
- Monitor logs (structured JSON) for error rates and performance.
- Run periodic fairness audits; avoid storing raw PII.

## Usage
1. Upload one JD (paste text or upload file).
2. Upload one or more resumes.
3. Adjust role type and seniority if desired.
4. Click Process to view scores, breakdown charts, missing skills, and suggestions.

## Scoring Logic (Default)
```
Overall = 0.4*Skill + 0.3*Experience + 0.15*Education + 0.1*Domain + 0.05*SoftSkill
```
Each sub-score normalized to 0–100; final overall also 0–100.
Categories:
- 80–100 Strong Fit
- 60–79 Moderate Fit
- < 60 Weak Fit

## Ethical Considerations & Limitations
- Avoid demographic or protected attributes.
- Parsing heuristics may misclassify non-standard resume formats.
- Embedding similarity is approximate; manual review still required.
- Suggestions avoid fabrication—no fake experience or skills.

## Extending
- Add new skill synonyms to `SKILL_SYNONYMS` in config.
- Implement advanced ML pipelines in separate modules (e.g., model selection, fine-tuning).
- Add persistent storage (database) for resumes & results.

## License / Use
Internal / demo use only. Remove or adapt before production deployment.
