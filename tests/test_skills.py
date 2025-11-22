from resume_screening.nlp_extractor import extract_skills


def test_basic_skill_extraction():
    text = "Experienced in Python, machine learning and docker orchestration."
    skills = extract_skills(text)
    assert "python" in skills
    assert "machine learning" in skills or "ml" in skills
