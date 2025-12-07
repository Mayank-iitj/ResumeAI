"""
Data Cleaner Utility
Clean and normalize text data from resumes
"""
import re
import string
from typing import List
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and normalize resume text data"""
    
    @staticmethod
    def clean_text(text: str, lowercase: bool = False) -> str:
        """
        Clean text by removing noise and normalizing
        
        Args:
            text: Input text
            lowercase: Whether to convert to lowercase
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric and basic punctuation
        # text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive punctuation
        text = re.sub(r'([.!?])\1+', r'\1', text)
        
        # Strip whitespace
        text = text.strip()
        
        if lowercase:
            text = text.lower()
        
        return text
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text)
    
    @staticmethod
    def remove_emails(text: str) -> str:
        """Remove email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '', text)
    
    @staticmethod
    def remove_phone_numbers(text: str) -> str:
        """Remove phone numbers from text"""
        phone_pattern = r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        return re.sub(phone_pattern, '', text)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace"""
        return ' '.join(text.split())
    
    @staticmethod
    def remove_stopwords(text: str, custom_stopwords: List[str] = None) -> str:
        """
        Remove common stopwords
        
        Args:
            text: Input text
            custom_stopwords: Optional list of additional stopwords
            
        Returns:
            Text with stopwords removed
        """
        try:
            import nltk
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words('english'))
        except:
            # Fallback stopwords
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                'could', 'should', 'may', 'might', 'can'
            }
        
        if custom_stopwords:
            stop_words.update(custom_stopwords)
        
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in stop_words]
        
        return ' '.join(filtered_words)
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Extract sentences from text"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def remove_extra_newlines(text: str) -> str:
        """Remove excessive newlines"""
        return re.sub(r'\n{3,}', '\n\n', text)
