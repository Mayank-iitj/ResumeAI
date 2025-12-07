"""
Skills Extractor Module
Extracts technical and soft skills from resume text using NLP and pattern matching
"""
import re
import nltk
from typing import List, Set, Dict
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class SkillsExtractor:
    """Extract skills from resume text"""
    
    def __init__(self):
        # Comprehensive skill database
        self.technical_skills = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
            'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash',
            
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask',
            'fastapi', 'spring', 'asp.net', 'jquery', 'bootstrap', 'tailwind',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'dynamodb',
            'oracle', 'sqlite', 'elasticsearch', 'neo4j',
            
            # ML/AI
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
            'pandas', 'numpy', 'nlp', 'computer vision', 'neural networks', 'transformers',
            'bert', 'gpt', 'llm', 'reinforcement learning', 'xgboost', 'lightgbm',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions',
            'terraform', 'ansible', 'ci/cd', 'devops', 'linux', 'unix',
            
            # Data Science
            'data analysis', 'data visualization', 'tableau', 'power bi', 'matplotlib',
            'seaborn', 'plotly', 'statistical analysis', 'hypothesis testing', 'a/b testing',
            
            # Tools & Frameworks
            'git', 'jira', 'confluence', 'postman', 'swagger', 'graphql', 'rest api',
            'microservices', 'agile', 'scrum', 'kafka', 'rabbitmq', 'spark', 'hadoop'
        }
        
        self.soft_skills = {
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'critical thinking', 'creativity', 'adaptability', 'time management',
            'project management', 'collaboration', 'presentation', 'negotiation'
        }
        
        # Skill variations and aliases
        self.skill_aliases = {
            'js': 'javascript',
            'ts': 'typescript',
            'k8s': 'kubernetes',
            'ml': 'machine learning',
            'dl': 'deep learning',
            'cv': 'computer vision',
            'tf': 'tensorflow',
            'sklearn': 'scikit-learn',
            'np': 'numpy',
            'pd': 'pandas'
        }
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills from text
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with technical_skills and soft_skills lists
        """
        text_lower = text.lower()
        
        # Find technical skills
        found_technical = set()
        for skill in self.technical_skills:
            # Use word boundaries for accurate matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_technical.add(skill)
        
        # Check for aliases
        for alias, skill in self.skill_aliases.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                found_technical.add(skill)
        
        # Find soft skills
        found_soft = set()
        for skill in self.soft_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_soft.add(skill)
        
        # Extract skills from common sections
        skills_section = self._extract_skills_section(text)
        if skills_section:
            additional_skills = self._parse_skills_section(skills_section)
            found_technical.update(additional_skills)
        
        result = {
            'technical_skills': sorted(list(found_technical)),
            'soft_skills': sorted(list(found_soft)),
            'total_count': len(found_technical) + len(found_soft)
        }
        
        logger.info(f"Extracted {result['total_count']} skills ({len(found_technical)} technical, {len(found_soft)} soft)")
        return result
    
    def _extract_skills_section(self, text: str) -> str:
        """Extract the skills section from resume"""
        # Common skills section headers
        patterns = [
            r'(?:technical\s+)?skills?[:\s]+(.+?)(?=\n\s*\n|\n[A-Z][a-z]+:|\Z)',
            r'(?:core\s+)?competencies[:\s]+(.+?)(?=\n\s*\n|\n[A-Z][a-z]+:|\Z)',
            r'expertise[:\s]+(.+?)(?=\n\s*\n|\n[A-Z][a-z]+:|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        return ""
    
    def _parse_skills_section(self, section_text: str) -> Set[str]:
        """Parse skills from a dedicated skills section"""
        skills = set()
        
        # Split by common delimiters
        items = re.split(r'[,;|\n•·]', section_text)
        
        for item in items:
            item = item.strip().lower()
            if item and len(item) > 1:
                # Check if it's a known skill
                if item in self.technical_skills:
                    skills.add(item)
                # Check multi-word skills
                for skill in self.technical_skills:
                    if ' ' in skill and skill in item:
                        skills.add(skill)
        
        return skills
    
    def get_skill_categories(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize skills into groups
        
        Args:
            skills: List of skills
            
        Returns:
            Dictionary mapping categories to skills
        """
        categories = {
            'programming': [],
            'frameworks': [],
            'databases': [],
            'cloud': [],
            'ml_ai': [],
            'tools': [],
            'other': []
        }
        
        programming = {'python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'ruby'}
        frameworks = {'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express'}
        databases = {'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra'}
        cloud = {'aws', 'azure', 'gcp', 'docker', 'kubernetes'}
        ml_ai = {'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp'}
        
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower in programming:
                categories['programming'].append(skill)
            elif skill_lower in frameworks:
                categories['frameworks'].append(skill)
            elif skill_lower in databases:
                categories['databases'].append(skill)
            elif skill_lower in cloud:
                categories['cloud'].append(skill)
            elif skill_lower in ml_ai:
                categories['ml_ai'].append(skill)
            elif skill_lower in self.technical_skills:
                categories['tools'].append(skill)
            else:
                categories['other'].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
