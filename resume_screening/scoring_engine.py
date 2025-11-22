from typing import Dict, List
from .config import WEIGHTS, MUST_HAVE_SKILLS, EDU_KEYWORDS, DOMAIN_KEYWORDS, SENIORITY_MAP
from .utils import extract_years_of_experience

import numpy as np

def skill_score(extracted_skills: List[str], jd_required: List[str], jd_optional: List[str]) -> Dict[str, float]:
    extracted_set = set(extracted_skills)
    must_have = set(jd_required) if jd_required else set(MUST_HAVE_SKILLS)
    optional = set(jd_optional)

    must_match = must_have & extracted_set
    must_missing = must_have - extracted_set
    opt_match = optional & extracted_set
    opt_missing = optional - extracted_set

    must_ratio = len(must_match) / max(len(must_have), 1)
    opt_ratio = len(opt_match) / max(len(optional), 1) if optional else 0

    score = 100 * (0.8 * must_ratio + 0.2 * opt_ratio)
    return {
        "score": score,
        "must_match": list(must_match),
        "must_missing": list(must_missing),
        "opt_match": list(opt_match),
        "opt_missing": list(opt_missing),
    }

def experience_score(resume_text: str, jd_years_required: int, seniority: str) -> Dict[str, float]:
    yrs = extract_years_of_experience(resume_text)
    required = jd_years_required or SENIORITY_MAP.get(seniority.lower(), 3)
    ratio = min(yrs / required, 1.2)  # allow slight bonus
    score = 100 * (ratio / 1.2)  # normalize
    return {"score": score, "years_extracted": yrs, "years_required": required}

def education_score(resume_text: str, min_required: str) -> Dict[str, float]:
    lower = resume_text.lower()
    tokens = lower.split()
    present = [kw for kw in EDU_KEYWORDS if kw in lower]
    base = 0
    if min_required and min_required.lower() in lower:
        base = 60
    if any(d for d in present if d.startswith("phd") or d == "phd"):
        base = max(base, 90)
    elif any(d for d in present if d.startswith("master") or d.startswith("m.sc") or d == "ms"):
        base = max(base, 75)
    elif any(d for d in present if d.startswith("bachelor") or d.startswith("b.sc") or d == "bs"):
        base = max(base, 65)
    richness = min(len(present) / 10, 1)
    score = min(base + 35 * richness, 100)
    return {"score": score, "present": present}

def domain_score(resume_text: str, jd_text: str) -> Dict[str, float]:
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    jd_domains = [d for d in DOMAIN_KEYWORDS if d in jd_lower]
    resume_domains = [d for d in DOMAIN_KEYWORDS if d in resume_lower]
    overlap = set(jd_domains) & set(resume_domains)
    if jd_domains:
        ratio = len(overlap) / len(set(jd_domains))
    else:
        ratio = 0.3 if resume_domains else 0  # small baseline when JD not explicit
    score = 100 * ratio
    return {"score": score, "jd_domains": jd_domains, "resume_domains": resume_domains, "overlap": list(overlap)}

def soft_skill_score(extracted_skills: List[str], resume_text: str) -> Dict[str, float]:
    soft = [s for s in extracted_skills if s in ["communication", "leadership", "teamwork", "collaboration", "problem solving", "critical thinking", "mentoring"]]
    # rough heuristic based on count
    count = len(set(soft))
    score = min(count / 7, 1) * 100
    return {"score": score, "soft_skills": list(set(soft))}

def aggregate_scores(parts: Dict[str, Dict]) -> Dict[str, float]:
    overall = 0.0
    for key in ["skill", "experience", "education", "domain", "soft"]:
        w = WEIGHTS[key]
        overall += w * parts[key]["score"]
    # Normalize weights sum (should be 1.0) but safeguard
    weight_sum = sum(WEIGHTS.values())
    overall = overall / weight_sum
    return {"overall": overall}

def categorize(overall: float) -> str:
    if overall >= 80:
        return "Strong Fit"
    if overall >= 60:
        return "Moderate Fit"
    return "Weak Fit"
