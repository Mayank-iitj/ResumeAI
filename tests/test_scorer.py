"""
Test Scorer Module
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scorer import ResumeScorer


class TestResumeScorer:
    """Test resume scoring"""
    
    def test_initialization(self):
        """Test scorer initialization"""
        scorer = ResumeScorer(use_embeddings=False)
        assert scorer is not None
    
    def test_scoring(self):
        """Test resume scoring"""
        scorer = ResumeScorer(use_embeddings=False)
        
        resume_data = {
            'skills': {
                'technical_skills': ['python', 'java', 'machine learning'],
                'soft_skills': ['leadership', 'communication'],
                'total_count': 5
            },
            'experience': [
                {
                    'role': 'Software Engineer',
                    'company': 'Tech Corp',
                    'duration_years': 3,
                    'description': 'Developed ML models'
                }
            ],
            'education': [
                {
                    'degree': 'Bachelor of Science',
                    'field': 'Computer Science'
                }
            ],
            'summary': {
                'total_experience_years': 3
            }
        }
        
        jd_text = """
        We are looking for a Software Engineer with 3+ years of experience.
        Required skills: Python, Machine Learning, Java
        """
        
        result = scorer.score_resume(resume_data, jd_text)
        
        assert 'total_score' in result
        assert 'breakdown' in result
        assert 'grade' in result
        assert result['total_score'] >= 0
        assert result['total_score'] <= 100
    
    def test_grade_calculation(self):
        """Test grade calculation"""
        scorer = ResumeScorer(use_embeddings=False)
        
        assert scorer._get_grade(95) == 'A+'
        assert scorer._get_grade(85) == 'A'
        assert scorer._get_grade(75) == 'B'
        assert scorer._get_grade(65) == 'C'
        assert scorer._get_grade(55) == 'D'
        assert scorer._get_grade(45) == 'F'
