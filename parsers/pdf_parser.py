"""
PDF Parser Module
Extracts text and tables from PDF resumes using pdfplumber
"""
import pdfplumber
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """Parse PDF files and extract text content"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def parse(self, file_path: str) -> Dict[str, any]:
        """
        Parse PDF file and extract text, tables, and metadata
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary containing extracted text, tables, and metadata
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            result = {
                'text': '',
                'tables': [],
                'pages': 0,
                'metadata': {},
                'file_path': str(file_path)
            }
            
            with pdfplumber.open(file_path) as pdf:
                result['pages'] = len(pdf.pages)
                result['metadata'] = pdf.metadata or {}
                
                all_text = []
                all_tables = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(page_text)
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            all_tables.append({
                                'page': page_num,
                                'data': table
                            })
                
                result['text'] = '\n'.join(all_text)
                result['tables'] = all_tables
            
            logger.info(f"Successfully parsed PDF: {file_path.name} ({result['pages']} pages)")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {str(e)}")
            raise
    
    def extract_text_only(self, file_path: str) -> str:
        """
        Quick extraction of text only (no tables)
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        result = self.parse(file_path)
        return result['text']
    
    def is_valid_pdf(self, file_path: str) -> bool:
        """
        Check if file is a valid PDF
        
        Args:
            file_path: Path to check
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages) > 0
        except:
            return False
