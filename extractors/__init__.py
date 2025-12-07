"""
Extractors Module Init
Combines all extraction modules
"""
from typing import Dict
import logging

from .skills_extractor import SkillsExtractor
from .experience_parser import ExperienceParser
from .education_parser import EducationParser
from .contact_extractor import ContactExtractor

logger = logging.getLogger(__name__)


class ResumeExtractor:
    """
    Main extractor class that combines all extraction modules
    """
    
    def __init__(self):
        self.skills_extractor = SkillsExtractor()
        self.experience_parser = ExperienceParser()
        self.education_parser = EducationParser()
        self.contact_extractor = ContactExtractor()
    
    def extract_all(self, text: str) -> Dict:
        """
        Extract all information from resume text
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary containing all extracted data
        """
        logger.info("Starting comprehensive extraction...")
        
        result = {}
        
        try:
            # Extract contact information
            result['contact'] = self.contact_extractor.extract(text)
            logger.info("Contact extraction completed")
            
            # Extract skills
            result['skills'] = self.skills_extractor.extract(text)
            logger.info("Skills extraction completed")
            
            # Extract experience
            result['experience'] = self.experience_parser.extract(text)
            logger.info("Experience extraction completed")
            
            # Extract education
            result['education'] = self.education_parser.extract(text)
            logger.info("Education extraction completed")
            
            # Extract projects (simplified)
            result['projects'] = self._extract_projects(text)
            
            # Extract certifications
            result['certifications'] = self._extract_certifications(text)
            
            # Summary statistics
            result['summary'] = {
                'total_experience_years': sum(exp.get('duration_years', 0) for exp in result['experience']),
                'total_skills': result['skills']['total_count'],
                'education_level': self._determine_education_level(result['education']),
                'has_projects': len(result['projects']) > 0,
                'has_certifications': len(result['certifications']) > 0
            }
            
            logger.info("All extractions completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during extraction: {str(e)}")
            raise
    
    def _extract_projects(self, text: str) -> list:
        """Extract projects section"""
        import re
        
        projects = []
        
        # Find projects section
        patterns = [
            r'projects?[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\Z)',
            r'(?:academic|personal)\s+projects?[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\Z)'
        ]
        
        project_section = ""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                project_section = match.group(1)
                break
        
        if project_section:
            # Split by bullets or double newlines
            items = re.split(r'\n\s*[•·-]\s*|\n\s*\n', project_section)
            
            for item in items:
                item = item.strip()
                if item and len(item) > 20:
                    # Extract project name (first line or up to colon)
                    lines = item.split('\n')
                    name = lines[0].split(':')[0].strip() if ':' in lines[0] else lines[0].strip()
                    
                    projects.append({
                        'name': name,
                        'description': item
                    })
        
        return projects
    
    def _extract_certifications(self, text: str) -> list:
        """Extract certifications"""
        import re
        
        certifications = []
        
        # Find certifications section
        patterns = [
            r'certifications?[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\Z)',
            r'licenses?\s+(?:and|&)\s+certifications?[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\Z)'
        ]
        
        cert_section = ""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                cert_section = match.group(1)
                break
        
        if cert_section:
            # Split by bullets or newlines
            items = re.split(r'\n\s*[•·-]\s*|\n', cert_section)
            
            for item in items:
                item = item.strip()
                if item and len(item) > 5:
                    certifications.append(item)
        
        return certifications
    
    def _determine_education_level(self, education: list) -> str:
        """Determine highest education level"""
        if not education:
            return "Not specified"
        
        levels = {
            'phd': 5, 'doctorate': 5,
            'master': 4, 'mba': 4,
            'bachelor': 3,
            'associate': 2,
            'diploma': 1
        }
        
        max_level = 0
        level_name = "Not specified"
        
        for edu in education:
            degree = edu.get('degree', '').lower()
            for key, value in levels.items():
                if key in degree:
                    if value > max_level:
                        max_level = value
                        level_name = key.title()
        
        return level_name


__all__ = ['ResumeExtractor', 'SkillsExtractor', 'ExperienceParser', 'EducationParser', 'ContactExtractor']
