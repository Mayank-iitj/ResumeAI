"""
TXT Parser Module
Extracts text from plain text resumes
"""
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class TXTParser:
    """Parse TXT files and extract text content"""
    
    def __init__(self):
        self.supported_extensions = ['.txt']
        self.encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    def parse(self, file_path: str) -> Dict[str, any]:
        """
        Parse TXT file and extract text
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            result = {
                'text': '',
                'lines': 0,
                'encoding': None,
                'file_path': str(file_path)
            }
            
            # Try different encodings
            text = None
            for encoding in self.encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    result['encoding'] = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                raise ValueError(f"Could not decode file with any supported encoding")
            
            result['text'] = text
            result['lines'] = len(text.split('\n'))
            
            logger.info(f"Successfully parsed TXT: {file_path.name} ({result['lines']} lines)")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing TXT {file_path}: {str(e)}")
            raise
    
    def extract_text_only(self, file_path: str) -> str:
        """
        Extract text from TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Extracted text as string
        """
        result = self.parse(file_path)
        return result['text']
