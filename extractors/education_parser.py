"""
Education Parser Module
Extracts educational qualifications from resume text
"""
import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class EducationParser:
    """Parse education information from resume text"""
    
    def __init__(self):
        # Common degrees
        self.degrees = {
            'phd', 'ph.d', 'doctorate', 'doctoral',
            'master', 'masters', 'm.s', 'ms', 'm.tech', 'mtech', 'mba', 'm.b.a',
            'bachelor', 'bachelors', 'b.s', 'bs', 'b.tech', 'btech', 'b.e', 'be', 'ba', 'b.a',
            'associate', 'diploma', 'certificate'
        }
        
        # Common fields of study
        self.fields = {
            'computer science', 'electrical engineering', 'mechanical engineering',
            'information technology', 'data science', 'artificial intelligence',
            'business administration', 'economics', 'mathematics', 'physics',
            'software engineering', 'civil engineering', 'chemical engineering'
        }
    
    def extract(self, text: str) -> List[Dict]:
        """
        Extract education from resume text
        
        Args:
            text: Resume text
            
        Returns:
            List of education dictionaries
        """
        educations = []
        
        # Find education section
        edu_section = self._extract_education_section(text)
        
        if not edu_section:
            logger.warning("No education section found")
            return educations
        
        # Split into individual education entries
        entries = self._split_education_entries(edu_section)
        
        for entry_text in entries:
            education = self._parse_education(entry_text)
            if education:
                educations.append(education)
        
        logger.info(f"Extracted {len(educations)} education entries")
        
        return educations
    
    def _extract_education_section(self, text: str) -> str:
        """Extract the education section"""
        patterns = [
            r'education[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\n\s*(?:experience|skills)|\Z)',
            r'(?:academic|educational)\s+(?:background|qualifications)[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\Z)',
            r'qualifications[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        return ""
    
    def _split_education_entries(self, section_text: str) -> List[str]:
        """Split education section into individual entries"""
        # Look for degree patterns or years
        lines = section_text.split('\n')
        entries = []
        current_entry = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts a new entry (contains degree or year)
            is_new_entry = False
            for degree in self.degrees:
                if degree in line.lower():
                    is_new_entry = True
                    break
            
            if not is_new_entry:
                # Check for year pattern
                if re.search(r'\b(19|20)\d{2}\b', line):
                    is_new_entry = True
            
            if is_new_entry and current_entry:
                entries.append('\n'.join(current_entry))
                current_entry = []
            
            current_entry.append(line)
        
        if current_entry:
            entries.append('\n'.join(current_entry))
        
        return entries
    
    def _parse_education(self, text: str) -> Optional[Dict]:
        """Parse a single education entry"""
        try:
            # Extract degree
            degree = self._extract_degree(text)
            
            # Extract field of study
            field = self._extract_field(text)
            
            # Extract institution
            institution = self._extract_institution(text)
            
            # Extract year/dates
            year = self._extract_year(text)
            
            # Extract GPA if present
            gpa = self._extract_gpa(text)
            
            if not degree and not institution:
                return None
            
            return {
                'degree': degree or 'Not specified',
                'field': field,
                'institution': institution or 'Not specified',
                'year': year,
                'gpa': gpa,
                'full_text': text
            }
        
        except Exception as e:
            logger.error(f"Error parsing education: {str(e)}")
            return None
    
    def _extract_degree(self, text: str) -> Optional[str]:
        """Extract degree name"""
        text_lower = text.lower()
        
        # Look for full degree names
        patterns = [
            r'((?:doctor|ph\.?d|doctorate)\s+(?:of|in)\s+[a-z\s]+)',
            r'((?:master|m\.?s\.?|m\.?tech|mba)\s+(?:of|in)\s+[a-z\s]+)',
            r'((?:bachelor|b\.?s\.?|b\.?tech|b\.?e\.?)\s+(?:of|in)\s+[a-z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).strip().title()
        
        # Look for short forms
        for degree in self.degrees:
            if re.search(r'\b' + re.escape(degree) + r'\b', text_lower):
                return degree.upper()
        
        return None
    
    def _extract_field(self, text: str) -> Optional[str]:
        """Extract field of study"""
        text_lower = text.lower()
        
        for field in self.fields:
            if field in text_lower:
                return field.title()
        
        # Try to extract from "in [field]" pattern
        match = re.search(r'\bin\s+([a-z\s]{5,30})', text_lower)
        if match:
            field = match.group(1).strip()
            if len(field) > 5:
                return field.title()
        
        return None
    
    def _extract_institution(self, text: str) -> Optional[str]:
        """Extract institution/university name"""
        # Look for common patterns
        patterns = [
            r'(?:from|at)\s+([A-Z][A-Za-z\s&,.]+?(?:University|Institute|College|School))',
            r'([A-Z][A-Za-z\s&,.]+?(?:University|Institute|College|School))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                institution = match.group(1).strip()
                # Clean up
                institution = re.sub(r'\s*,\s*$', '', institution)
                return institution
        
        # Look for capitalized institution names
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Check if line is mostly capitalized (likely institution name)
            if line and len(line) > 10 and sum(c.isupper() for c in line) > len(line) * 0.3:
                return line
        
        return None
    
    def _extract_year(self, text: str) -> Optional[str]:
        """Extract graduation year or date range"""
        # Look for year ranges
        range_pattern = r'(\d{4})\s*[-–—to]+\s*(\d{4})'
        match = re.search(range_pattern, text)
        if match:
            return f"{match.group(1)} - {match.group(2)}"
        
        # Look for single year
        year_pattern = r'\b(19|20)\d{2}\b'
        matches = re.findall(year_pattern, text)
        if matches:
            # Return the most recent year
            years = [int(y) for y in matches]
            return str(max(years))
        
        return None
    
    def _extract_gpa(self, text: str) -> Optional[str]:
        """Extract GPA if mentioned"""
        patterns = [
            r'gpa[:\s]+(\d+\.?\d*)\s*/?\s*(\d+\.?\d*)?',
            r'(?:grade|cgpa)[:\s]+(\d+\.?\d*)\s*/?\s*(\d+\.?\d*)?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gpa = match.group(1)
                if match.group(2):
                    return f"{gpa}/{match.group(2)}"
                return gpa
        
        return None
