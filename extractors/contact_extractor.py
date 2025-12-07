"""
Contact Extractor Module
Extracts contact information (email, phone, name) from resume text
"""
import re
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class ContactExtractor:
    """Extract contact information from resume text"""
    
    def __init__(self):
        # Email pattern
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Phone patterns (various formats)
        self.phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-234-567-8900
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (234) 567-8900
            r'\d{10}',  # 2345678900
            r'\+?\d{1,3}\s?\d{9,10}'  # +91 9876543210
        ]
        
        # LinkedIn pattern
        self.linkedin_pattern = r'(?:linkedin\.com/in/|linkedin:)\s*([a-zA-Z0-9-]+)'
        
        # GitHub pattern
        self.github_pattern = r'(?:github\.com/|github:)\s*([a-zA-Z0-9-]+)'
    
    def extract(self, text: str) -> Dict[str, any]:
        """
        Extract contact information from text
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with contact information
        """
        return {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'linkedin': self._extract_linkedin(text),
            'github': self._extract_github(text),
            'location': self._extract_location(text)
        }
    
    def _extract_name(self, text: str) -> Optional[str]:
        """
        Extract candidate name (typically in first few lines)
        """
        lines = text.split('\n')
        
        for i, line in enumerate(lines[:5]):  # Check first 5 lines
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines with email or phone
            if re.search(self.email_pattern, line) or any(re.search(p, line) for p in self.phone_patterns):
                continue
            
            # Name is likely 2-4 words, mostly alphabetic, capitalized
            words = line.split()
            if 2 <= len(words) <= 4:
                if all(word[0].isupper() and word.isalpha() for word in words if len(word) > 1):
                    return line
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        match = re.search(self.email_pattern, text)
        if match:
            return match.group()
        return None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        for pattern in self.phone_patterns:
            match = re.search(pattern, text)
            if match:
                phone = match.group()
                # Clean up
                phone = re.sub(r'[^\d+]', '', phone)
                if len(phone) >= 10:
                    return phone
        return None
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile"""
        match = re.search(self.linkedin_pattern, text, re.IGNORECASE)
        if match:
            return f"linkedin.com/in/{match.group(1)}"
        
        # Also check for full URLs
        url_match = re.search(r'linkedin\.com/in/([a-zA-Z0-9-]+)', text, re.IGNORECASE)
        if url_match:
            return f"linkedin.com/in/{url_match.group(1)}"
        
        return None
    
    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub profile"""
        match = re.search(self.github_pattern, text, re.IGNORECASE)
        if match:
            return f"github.com/{match.group(1)}"
        
        # Also check for full URLs
        url_match = re.search(r'github\.com/([a-zA-Z0-9-]+)', text, re.IGNORECASE)
        if url_match:
            return f"github.com/{url_match.group(1)}"
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location/address"""
        # Look for common location patterns
        patterns = [
            r'(?:location|address|based in)[:\s]+([A-Za-z\s,]+(?:USA|India|UK|Canada))',
            r'([A-Z][a-z]+,\s*[A-Z]{2}(?:\s+\d{5})?)',  # City, State ZIP
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+)'  # City, Country
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
