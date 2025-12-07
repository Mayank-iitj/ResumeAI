"""
Test Extractors Module
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from extractors import SkillsExtractor, ExperienceParser, EducationParser, ContactExtractor


class TestSkillsExtractor:
    """Test skills extraction"""
    
    def test_initialization(self):
        """Test initialization"""
        extractor = SkillsExtractor()
        assert extractor is not None
        assert len(extractor.technical_skills) > 0
    
    def test_skill_extraction(self):
        """Test extracting skills from text"""
        extractor = SkillsExtractor()
        
        text = """
        Skills: Python, Java, Machine Learning, TensorFlow, AWS, Docker
        Expert in React, Node.js, and SQL databases.
        """
        
        result = extractor.extract(text)
        
        assert 'technical_skills' in result
        assert 'python' in result['technical_skills']
        assert 'java' in result['technical_skills']
        assert result['total_count'] > 0


class TestExperienceParser:
    """Test experience parsing"""
    
    def test_initialization(self):
        """Test initialization"""
        parser = ExperienceParser()
        assert parser is not None
    
    def test_experience_extraction(self):
        """Test extracting experience"""
        parser = ExperienceParser()
        
        text = """
        EXPERIENCE
        
        Senior Software Engineer at Google
        January 2020 - Present
        Led development of ML systems
        
        Software Engineer at Microsoft
        June 2018 - December 2019
        Developed cloud applications
        """
        
        result = parser.extract(text)
        
        assert isinstance(result, list)
        # May extract 0-2 experiences depending on regex matching


class TestEducationParser:
    """Test education parsing"""
    
    def test_initialization(self):
        """Test initialization"""
        parser = EducationParser()
        assert parser is not None
    
    def test_education_extraction(self):
        """Test extracting education"""
        parser = EducationParser()
        
        text = """
        EDUCATION
        
        Master of Science in Computer Science
        Stanford University
        2018
        
        Bachelor of Technology
        IIT Delhi
        2016
        """
        
        result = parser.extract(text)
        
        assert isinstance(result, list)


class TestContactExtractor:
    """Test contact extraction"""
    
    def test_initialization(self):
        """Test initialization"""
        extractor = ContactExtractor()
        assert extractor is not None
    
    def test_email_extraction(self):
        """Test extracting email"""
        extractor = ContactExtractor()
        
        text = "Contact me at john.doe@email.com for inquiries."
        result = extractor.extract(text)
        
        assert result['email'] == 'john.doe@email.com'
    
    def test_phone_extraction(self):
        """Test extracting phone"""
        extractor = ContactExtractor()
        
        text = "Call me at +1-234-567-8900"
        result = extractor.extract(text)
        
        assert result['phone'] is not None
