"""
Metrics Utility
Calculate various metrics for resume analysis
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate metrics for resume analysis"""
    
    @staticmethod
    def calculate_completeness_score(resume_data: Dict) -> float:
        """
        Calculate how complete a resume is (0-100)
        
        Args:
            resume_data: Extracted resume data
            
        Returns:
            Completeness score
        """
        score = 0
        max_score = 100
        
        # Essential sections (60 points)
        if resume_data.get('contact', {}).get('email'):
            score += 10
        if resume_data.get('contact', {}).get('phone'):
            score += 10
        if resume_data.get('skills', {}).get('technical_skills'):
            score += 15
        if resume_data.get('experience'):
            score += 15
        if resume_data.get('education'):
            score += 10
        
        # Optional sections (40 points)
        if resume_data.get('projects'):
            score += 10
        if resume_data.get('certifications'):
            score += 10
        if resume_data.get('contact', {}).get('linkedin'):
            score += 5
        if resume_data.get('contact', {}).get('github'):
            score += 5
        if resume_data.get('contact', {}).get('location'):
            score += 5
        if len(resume_data.get('skills', {}).get('soft_skills', [])) > 0:
            score += 5
        
        return min(max_score, score)
    
    @staticmethod
    def calculate_keyword_density(text: str, keywords: List[str]) -> Dict[str, float]:
        """
        Calculate keyword density for given keywords
        
        Args:
            text: Text to analyze
            keywords: List of keywords
            
        Returns:
            Dictionary mapping keywords to their density
        """
        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words)
        
        if total_words == 0:
            return {kw: 0.0 for kw in keywords}
        
        density = {}
        for keyword in keywords:
            count = text_lower.count(keyword.lower())
            density[keyword] = (count / total_words) * 100
        
        return density
    
    @staticmethod
    def calculate_readability_score(text: str) -> float:
        """
        Calculate text readability score (simplified)
        
        Args:
            text: Text to analyze
            
        Returns:
            Readability score (0-100, higher is more readable)
        """
        sentences = text.split('.')
        words = text.split()
        
        if len(sentences) == 0 or len(words) == 0:
            return 50.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Ideal sentence length is 15-20 words
        if 15 <= avg_sentence_length <= 20:
            return 100.0
        elif 10 <= avg_sentence_length <= 25:
            return 80.0
        elif avg_sentence_length < 10:
            return 70.0  # Too short
        else:
            return max(30.0, 100 - (avg_sentence_length - 20) * 2)  # Too long
    
    @staticmethod
    def calculate_experience_score(experiences: List[Dict]) -> float:
        """
        Calculate experience quality score
        
        Args:
            experiences: List of experience dictionaries
            
        Returns:
            Experience score (0-100)
        """
        if not experiences:
            return 0.0
        
        score = 0
        
        # Total years of experience
        total_years = sum(exp.get('duration_years', 0) for exp in experiences)
        score += min(50, total_years * 10)  # Max 50 points for 5+ years
        
        # Number of positions
        score += min(25, len(experiences) * 8)  # Max 25 points for 3+ positions
        
        # Description quality
        for exp in experiences:
            desc = exp.get('description', '')
            if len(desc) > 100:
                score += 5
            if len(desc) > 200:
                score += 5
        
        score = min(15, score - 50)  # Max 15 points for descriptions
        score += 50  # Add back the base score
        
        return min(100, score)
    
    @staticmethod
    def calculate_skills_diversity_score(skills: Dict) -> float:
        """
        Calculate skills diversity score
        
        Args:
            skills: Skills dictionary
            
        Returns:
            Diversity score (0-100)
        """
        tech_skills = skills.get('technical_skills', [])
        soft_skills = skills.get('soft_skills', [])
        
        total_skills = len(tech_skills) + len(soft_skills)
        
        if total_skills == 0:
            return 0.0
        
        # Score based on total count
        count_score = min(60, total_skills * 3)  # Max 60 for 20+ skills
        
        # Bonus for having both types
        diversity_score = 0
        if len(tech_skills) > 0 and len(soft_skills) > 0:
            diversity_score = 20
        
        # Bonus for many skills
        if total_skills >= 15:
            diversity_score += 20
        
        return min(100, count_score + diversity_score)
