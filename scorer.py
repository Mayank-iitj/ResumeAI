"""
Scorer Module
ATS scoring and job description matching using TF-IDF, embeddings, and keyword analysis
"""
import re
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class ResumeScorer:
    """
    Score resumes against job descriptions using multiple methods:
    - Keyword matching (80%)
    - Semantic similarity via embeddings (20%)
    """
    
    def __init__(self, use_embeddings=True):
        self.use_embeddings = use_embeddings
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Initialize embedding model if requested
        self.embedding_model = None
        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded embedding model: all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"Could not load embedding model: {e}. Using TF-IDF only.")
                self.use_embeddings = False
    
    def score_resume(self, resume_data: Dict, jd_text: str) -> Dict:
        """
        Comprehensive ATS scoring of resume against job description
        
        Args:
            resume_data: Extracted resume data dictionary
            jd_text: Job description text
            
        Returns:
            Dictionary with scores and detailed breakdown
        """
        logger.info("Starting resume scoring...")
        
        # Prepare resume text
        resume_text = self._prepare_resume_text(resume_data)
        
        # 1. Keyword matching score (80% weight)
        keyword_score = self._calculate_keyword_score(resume_text, jd_text)
        
        # 2. Skills matching score
        skills_score = self._calculate_skills_match(resume_data, jd_text)
        
        # 3. Experience relevance score
        experience_score = self._calculate_experience_score(resume_data, jd_text)
        
        # 4. Semantic similarity score (20% weight)
        semantic_score = 0
        if self.use_embeddings and self.embedding_model:
            semantic_score = self._calculate_semantic_score(resume_text, jd_text)
        else:
            # Fallback to TF-IDF similarity
            semantic_score = self._calculate_tfidf_similarity(resume_text, jd_text)
        
        # 5. Format/ATS compatibility score
        format_score = self._calculate_format_score(resume_data)
        
        # Calculate weighted total score
        total_score = (
            keyword_score * 0.30 +
            skills_score * 0.25 +
            experience_score * 0.20 +
            semantic_score * 0.15 +
            format_score * 0.10
        )
        
        result = {
            'final_score': round(total_score, 2),
            'breakdown': {
                'keyword_score': round(keyword_score, 2),
                'skills_score': round(skills_score, 2),
                'experience_score': round(experience_score, 2),
                'semantic_score': round(semantic_score, 2),
                'format_score': round(format_score, 2)
            },
            'grade': self._get_grade(total_score),
            'status': self._get_match_status(total_score)
        }
        
        logger.info(f"Scoring completed: {result['total_score']}/100 ({result['grade']})")
        return result
    
    def _prepare_resume_text(self, resume_data: Dict) -> str:
        """Combine all resume sections into text"""
        parts = []
        
        # Skills
        if 'skills' in resume_data:
            skills = resume_data['skills']
            all_skills = skills.get('technical_skills', []) + skills.get('soft_skills', [])
            parts.append(' '.join(all_skills))
        
        # Experience
        if 'experience' in resume_data:
            for exp in resume_data['experience']:
                parts.append(exp.get('role', ''))
                parts.append(exp.get('description', ''))
        
        # Education
        if 'education' in resume_data:
            for edu in resume_data['education']:
                parts.append(edu.get('degree', ''))
                parts.append(edu.get('field', '') or '')
        
        # Projects
        if 'projects' in resume_data:
            for proj in resume_data['projects']:
                parts.append(proj.get('description', ''))
        
        return ' '.join(parts)
    
    def _calculate_keyword_score(self, resume_text: str, jd_text: str) -> float:
        """Calculate keyword matching score"""
        # Extract important keywords from JD
        jd_keywords = self._extract_keywords(jd_text)
        resume_lower = resume_text.lower()
        
        if not jd_keywords:
            return 50.0
        
        # Count matches
        matches = sum(1 for keyword in jd_keywords if keyword.lower() in resume_lower)
        score = (matches / len(jd_keywords)) * 100
        
        return min(100, score)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z][a-zA-Z+#\.]{2,}\b', text)
        
        # Filter out very common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'a', 'an'}
        keywords = [w for w in words if w.lower() not in stop_words]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _calculate_skills_match(self, resume_data: Dict, jd_text: str) -> float:
        """Calculate how many required skills are present"""
        if 'skills' not in resume_data:
            return 0.0
        
        # Get resume skills
        resume_skills = set()
        skills_data = resume_data['skills']
        resume_skills.update(s.lower() for s in skills_data.get('technical_skills', []))
        resume_skills.update(s.lower() for s in skills_data.get('soft_skills', []))
        
        # Extract skills mentioned in JD
        jd_lower = jd_text.lower()
        jd_skills = set()
        
        # Common skill patterns in JDs
        skill_keywords = ['python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker', 
                         'kubernetes', 'machine learning', 'data analysis', 'tensorflow']
        
        for skill in skill_keywords:
            if skill in jd_lower:
                jd_skills.add(skill)
        
        if not jd_skills:
            return 70.0  # Default if no specific skills detected
        
        # Calculate overlap
        matching_skills = resume_skills.intersection(jd_skills)
        score = (len(matching_skills) / len(jd_skills)) * 100
        
        return min(100, score)
    
    def _calculate_experience_score(self, resume_data: Dict, jd_text: str) -> float:
        """Score based on experience relevance"""
        if 'experience' not in resume_data or not resume_data['experience']:
            return 30.0
        
        # Extract years of experience required from JD
        required_years = self._extract_required_experience(jd_text)
        
        # Get total experience from resume
        total_years = resume_data.get('summary', {}).get('total_experience_years', 0)
        
        if required_years == 0:
            # No specific requirement, score based on having experience
            return min(100, 50 + (total_years * 10))
        
        # Score based on matching required experience
        if total_years >= required_years:
            return 100
        elif total_years >= required_years * 0.7:
            return 80
        elif total_years >= required_years * 0.5:
            return 60
        else:
            return 40
    
    def _extract_required_experience(self, jd_text: str) -> int:
        """Extract required years of experience from JD"""
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(?:minimum|at least)\s+(\d+)\s*years?',
            r'(\d+)-(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0
    
    def _calculate_semantic_score(self, resume_text: str, jd_text: str) -> float:
        """Calculate semantic similarity using embeddings"""
        try:
            resume_emb = self.embedding_model.encode(resume_text[:1000])  # Limit length
            jd_emb = self.embedding_model.encode(jd_text[:1000])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                resume_emb.reshape(1, -1),
                jd_emb.reshape(1, -1)
            )[0][0]
            
            return similarity * 100
        
        except Exception as e:
            logger.error(f"Error calculating semantic score: {e}")
            return 50.0
    
    def _calculate_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        """Fallback TF-IDF similarity calculation"""
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([jd_text, resume_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity * 100
        except:
            return 50.0
    
    def _calculate_format_score(self, resume_data: Dict) -> float:
        """Score based on ATS-friendly formatting"""
        score = 100
        
        # Check for essential sections
        if not resume_data.get('contact', {}).get('email'):
            score -= 15
        
        if not resume_data.get('experience'):
            score -= 20
        
        if not resume_data.get('education'):
            score -= 15
        
        if not resume_data.get('skills', {}).get('technical_skills'):
            score -= 20
        
        # Bonus for additional sections
        if resume_data.get('projects'):
            score += 5
        
        if resume_data.get('certifications'):
            score += 5
        
        return max(0, min(100, score))
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _get_match_status(self, score: float) -> str:
        """Get match status description"""
        if score >= 85:
            return 'Strong Match - Highly Recommended'
        elif score >= 70:
            return 'Good Match - Recommended'
        elif score >= 55:
            return 'Moderate Match - Consider'
        else:
            return 'Weak Match - Not Recommended'
