from typing import Dict, List

def generate_suggestions(skill_part: Dict, experience_part: Dict, education_part: Dict, jd_text: str) -> Dict[str, List[str]]:
    suggestions = []
    missing = skill_part.get("must_missing", [])
    opt_missing = skill_part.get("opt_missing", [])
    if missing:
        suggestions.append(f"Consider highlighting or gaining these core skills: {', '.join(missing)}")
    if opt_missing:
        suggestions.append(f"Optional skills that could strengthen fit: {', '.join(opt_missing[:10])}")
    yrs_diff = experience_part.get("years_required", 0) - experience_part.get("years_extracted", 0)
    if yrs_diff > 0.5:
        suggestions.append("Emphasize any relevant internships, freelance, or project work to bridge experience gap.")
    edu_present = education_part.get("present", [])
    if not edu_present:
        suggestions.append("Add an Education section with degree and institution.")
    # bullet improvement example
    suggestions.append("Use quantified impact: e.g., 'Improved model accuracy from 82% to 91%'.")
    suggestions.append("Add a Projects section highlighting hands-on work relevant to the JD (e.g., NLP transformer project).")

    return {"suggestions": suggestions}

# Placeholder for advanced LLM rewriting (kept ethical):
# def rewrite_bullet_llm(original: str, jd_text: str) -> str:
#     return original  # integrate with an LLM ensuring no fabrication.
