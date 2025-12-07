"""
Test Parsers Module
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers import ResumeParser, PDFParser, DOCXParser, TXTParser


class TestResumeParser:
    """Test main resume parser"""
    
    def test_initialization(self):
        """Test parser initialization"""
        parser = ResumeParser()
        assert parser is not None
        assert parser.pdf_parser is not None
        assert parser.docx_parser is not None
        assert parser.txt_parser is not None
    
    def test_supported_formats(self):
        """Test supported formats"""
        formats = ResumeParser.get_supported_formats()
        assert '.pdf' in formats
        assert '.docx' in formats
        assert '.txt' in formats
    
    def test_txt_parsing(self, tmp_path):
        """Test TXT file parsing"""
        # Create temporary TXT file
        txt_file = tmp_path / "test_resume.txt"
        txt_content = """
John Doe
john.doe@email.com
+1-234-567-8900

EXPERIENCE
Software Engineer at Tech Corp
2020 - 2023

SKILLS
Python, Java, Machine Learning
"""
        txt_file.write_text(txt_content)
        
        parser = ResumeParser()
        result = parser.parse(str(txt_file))
        
        assert result is not None
        assert 'text' in result
        assert 'John Doe' in result['text']
        assert result['format'] == '.txt'


class TestPDFParser:
    """Test PDF parser"""
    
    def test_initialization(self):
        """Test PDF parser initialization"""
        parser = PDFParser()
        assert parser is not None
        assert '.pdf' in parser.supported_extensions


class TestDOCXParser:
    """Test DOCX parser"""
    
    def test_initialization(self):
        """Test DOCX parser initialization"""
        parser = DOCXParser()
        assert parser is not None
        assert '.docx' in parser.supported_extensions


class TestTXTParser:
    """Test TXT parser"""
    
    def test_initialization(self):
        """Test TXT parser initialization"""
        parser = TXTParser()
        assert parser is not None
        assert '.txt' in parser.supported_extensions
    
    def test_txt_parsing(self, tmp_path):
        """Test TXT parsing"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Test content")
        
        parser = TXTParser()
        result = parser.parse(str(txt_file))
        
        assert result is not None
        assert result['text'] == "Test content"
        assert result['lines'] > 0
