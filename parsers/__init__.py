"""
Parser Module Init
Main interface for parsing resumes in multiple formats
"""
from pathlib import Path
from typing import Dict, Optional
import logging

from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .txt_parser import TXTParser

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Main parser class that handles multiple file formats
    """
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.txt_parser = TXTParser()
        
        self.parsers = {
            '.pdf': self.pdf_parser,
            '.docx': self.docx_parser,
            '.doc': self.docx_parser,
            '.txt': self.txt_parser
        }
    
    def parse(self, file_path: str) -> Dict[str, any]:
        """
        Parse resume file and extract content
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Dictionary containing extracted data
            
        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension not in self.parsers:
            raise ValueError(f"Unsupported file format: {extension}. Supported: {list(self.parsers.keys())}")
        
        parser = self.parsers[extension]
        
        try:
            result = parser.parse(str(file_path))
            result['format'] = extension
            result['filename'] = file_path.name
            return result
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {str(e)}")
            raise
    
    def parse_batch(self, file_paths: list) -> Dict[str, Dict]:
        """
        Parse multiple resume files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Dictionary mapping file paths to parsed results
        """
        results = {}
        for file_path in file_paths:
            try:
                results[file_path] = self.parse(file_path)
            except Exception as e:
                logger.error(f"Error parsing {file_path}: {str(e)}")
                results[file_path] = {'error': str(e)}
        
        return results
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract raw text from resume file
        
        Args:
            file_path: Path to resume file
            
        Returns:
            Extracted text as string
        """
        result = self.parse(file_path)
        return result.get('text', '')
    
    @staticmethod
    def get_supported_formats() -> list:
        """
        Get list of supported file formats
        
        Returns:
            List of supported extensions
        """
        return ['.pdf', '.docx', '.doc', '.txt']


__all__ = ['ResumeParser', 'PDFParser', 'DOCXParser', 'TXTParser']
