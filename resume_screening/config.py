from typing import Dict, List

WEIGHTS = {
    "skill": 0.4,
    "experience": 0.3,
    "education": 0.15,
    "domain": 0.1,
    "soft": 0.05,
}

SKILL_KEYWORDS = [
    # Technical
    "python", "sql", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "spark", "airflow", "docker", "kubernetes", "aws", "azure", "gcp", "java", "c++", "ml", "machine learning", "deep learning", "nlp", "transformers", "data analysis", "tableau", "power bi", "git", "rest", "api", "microservices", "hadoop", "linux", "excel", "statistics", "probability", "matplotlib", "seaborn",
    # Soft
    "communication", "leadership", "teamwork", "collaboration", "problem solving", "critical thinking", "mentoring", "stakeholder management"
]

SKILL_SYNONYMS: Dict[str, List[str]] = {
    "pytorch": ["torch"],
    "tensorflow": ["tf"],
    "scikit-learn": ["sklearn"],
    "nlp": ["natural language processing"],
    "ml": ["machine learning"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud"],
    "airflow": ["apache airflow"],
    "docker": ["container"],
}

SOFT_SKILL_KEYWORDS = [
    "communication", "leadership", "team", "collaboration", "mentoring", "stakeholder", "presentation", "problem", "critical"
]

EDU_KEYWORDS = ["bachelor", "master", "phd", "b.sc", "m.sc", "msc", "bs", "ms", "computer science", "data science", "statistics", "engineering"]

DOMAIN_KEYWORDS = ["finance", "healthcare", "retail", "e-commerce", "manufacturing", "biotech", "education", "energy"]

SENIORITY_MAP = {"junior": 2, "mid": 5, "senior": 8}

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SPACY_MODEL = "en_core_web_sm"

MUST_HAVE_SKILLS = ["python", "sql", "machine learning"]  # Example defaults; can be overridden per JD.

EXPERIENCE_YEARS_REQUIRED_DEFAULT = 3

# Thresholds
SIMILARITY_SECTION_THRESHOLD = 0.55
SKILL_MATCH_THRESHOLD = 0.6
