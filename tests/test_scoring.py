from resume_screening.scoring_engine import skill_score, aggregate_scores


def test_skill_scoring_and_aggregation():
    resume_skills = ["python", "docker", "ml"]
    required = ["python", "machine learning"]
    optional = ["docker"]
    skill_part = skill_score(resume_skills, required, optional)
    parts = {"skill": skill_part, "experience": {"score":0}, "education": {"score":0}, "domain": {"score":0}, "soft": {"score":0}}
    agg = aggregate_scores(parts)
    assert skill_part["score"] >= 0
    assert "overall" in agg and agg["overall"] >= 0
