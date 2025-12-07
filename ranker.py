"""
Ranker Module
Multi-resume ranking with ensemble scoring
"""
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ResumeRanker:
    """
    Rank multiple resumes based on composite scoring
    Weighting: Skills 40%, Experience 30%, Education 20%, Projects 10%
    """
    
    def __init__(self):
        self.weights = {
            'skills': 0.40,
            'experience': 0.30,
            'education': 0.20,
            'projects': 0.10
        }
    
    def rank_resumes(self, resumes_data: List[Dict], jd_text: str = None) -> List[Dict]:
        """
        Rank multiple resumes
        
        Args:
            resumes_data: List of dictionaries containing resume data and scores
            jd_text: Optional job description for enhanced ranking
            
        Returns:
            Sorted list of resumes with rankings
        """
        logger.info(f"Ranking {len(resumes_data)} resumes...")
        
        # Calculate composite scores
        for i, resume in enumerate(resumes_data):
            resume['composite_score'] = self._calculate_composite_score(resume)
            resume['original_index'] = i
        
        # Sort by composite score
        ranked = sorted(resumes_data, key=lambda x: x['composite_score'], reverse=True)
        
        # Add rank numbers
        for rank, resume in enumerate(ranked, 1):
            resume['rank'] = rank
        
        logger.info(f"Ranking completed. Top score: {ranked[0]['composite_score']:.2f}")
        return ranked
    
    def _calculate_composite_score(self, resume_data: Dict) -> float:
        """
        Calculate composite score based on multiple factors
        
        Args:
            resume_data: Resume data dictionary
            
        Returns:
            Composite score (0-100)
        """
        scores = {
            'skills': 0,
            'experience': 0,
            'education': 0,
            'projects': 0
        }
        
        # If ATS score is available, use it
        if 'ats_score' in resume_data and 'breakdown' in resume_data['ats_score']:
            breakdown = resume_data['ats_score']['breakdown']
            scores['skills'] = breakdown.get('skills_match', 0)
            scores['experience'] = breakdown.get('experience_relevance', 0)
            # Use total score components
            if 'total_score' in resume_data['ats_score']:
                return resume_data['ats_score']['total_score']
        
        # Otherwise, calculate from extracted data
        extracted = resume_data.get('extracted_data', resume_data)
        
        # Skills score
        skills_data = extracted.get('skills', {})
        total_skills = skills_data.get('total_count', 0)
        scores['skills'] = min(100, total_skills * 5)  # 20+ skills = 100
        
        # Experience score
        experience_data = extracted.get('experience', [])
        total_years = sum(exp.get('duration_years', 0) for exp in experience_data)
        scores['experience'] = min(100, total_years * 20)  # 5+ years = 100
        
        # Education score
        education_level = extracted.get('summary', {}).get('education_level', 'Not specified')
        edu_scores = {
            'Phd': 100, 'Doctorate': 100,
            'Master': 85, 'Mba': 85,
            'Bachelor': 70,
            'Associate': 50,
            'Diploma': 40
        }
        scores['education'] = edu_scores.get(education_level, 30)
        
        # Projects score
        projects = extracted.get('projects', [])
        scores['projects'] = min(100, len(projects) * 25)  # 4+ projects = 100
        
        # Calculate weighted composite
        composite = sum(scores[key] * self.weights[key] for key in scores)
        
        return round(composite, 2)
    
    def get_top_candidates(self, ranked_resumes: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Get top K candidates
        
        Args:
            ranked_resumes: List of ranked resumes
            top_k: Number of top candidates to return
            
        Returns:
            List of top K candidates
        """
        return ranked_resumes[:top_k]
    
    def compare_resumes(self, resume1: Dict, resume2: Dict) -> Dict:
        """
        Compare two resumes side by side
        
        Args:
            resume1: First resume data
            resume2: Second resume data
            
        Returns:
            Comparison results
        """
        comparison = {
            'resume1': {
                'name': resume1.get('extracted_data', {}).get('contact', {}).get('name', 'Candidate 1'),
                'score': resume1.get('composite_score', 0),
                'rank': resume1.get('rank', 0)
            },
            'resume2': {
                'name': resume2.get('extracted_data', {}).get('contact', {}).get('name', 'Candidate 2'),
                'score': resume2.get('composite_score', 0),
                'rank': resume2.get('rank', 0)
            },
            'winner': None,
            'differences': {}
        }
        
        # Determine winner
        if comparison['resume1']['score'] > comparison['resume2']['score']:
            comparison['winner'] = 'resume1'
        elif comparison['resume2']['score'] > comparison['resume1']['score']:
            comparison['winner'] = 'resume2'
        else:
            comparison['winner'] = 'tie'
        
        # Compare specific aspects
        r1_data = resume1.get('extracted_data', {})
        r2_data = resume2.get('extracted_data', {})
        
        comparison['differences']['skills'] = {
            'resume1': r1_data.get('skills', {}).get('total_count', 0),
            'resume2': r2_data.get('skills', {}).get('total_count', 0)
        }
        
        comparison['differences']['experience_years'] = {
            'resume1': r1_data.get('summary', {}).get('total_experience_years', 0),
            'resume2': r2_data.get('summary', {}).get('total_experience_years', 0)
        }
        
        comparison['differences']['education'] = {
            'resume1': r1_data.get('summary', {}).get('education_level', 'Not specified'),
            'resume2': r2_data.get('summary', {}).get('education_level', 'Not specified')
        }
        
        return comparison
