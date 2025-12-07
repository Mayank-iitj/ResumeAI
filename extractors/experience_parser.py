"""
Experience Parser Module
Extracts work experience, roles, companies, and duration from resume text
"""
import re
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExperienceParser:
    """Parse work experience from resume text"""
    
    def __init__(self):
        # Common job title keywords
        self.title_keywords = {
            'engineer', 'developer', 'analyst', 'manager', 'scientist', 'architect',
            'consultant', 'specialist', 'lead', 'director', 'coordinator', 'designer',
            'administrator', 'technician', 'associate', 'intern', 'fellow'
        }
        
        # Month patterns
        self.months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7,
            'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
    
    def extract(self, text: str) -> List[Dict]:
        """
        Extract work experience from resume text
        
        Args:
            text: Resume text
            
        Returns:
            List of experience dictionaries
        """
        experiences = []
        
        # Find experience section
        exp_section = self._extract_experience_section(text)
        
        if not exp_section:
            logger.warning("No experience section found")
            return experiences
        
        # Split into individual jobs
        jobs = self._split_jobs(exp_section)
        
        for job_text in jobs:
            experience = self._parse_job(job_text)
            if experience:
                experiences.append(experience)
        
        # Calculate total experience
        total_years = self._calculate_total_experience(experiences)
        
        logger.info(f"Extracted {len(experiences)} work experiences (Total: {total_years:.1f} years)")
        
        return experiences
    
    def _extract_experience_section(self, text: str) -> str:
        """Extract the work experience section"""
        patterns = [
            r'(?:work\s+)?experience[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\n\s*education|\Z)',
            r'(?:professional\s+)?(?:employment|history)[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\n\s*education|\Z)',
            r'career\s+(?:summary|history)[:\s]+(.+?)(?=\n\s*\n[A-Z][a-z]+:|\n\s*education|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        return ""
    
    def _split_jobs(self, section_text: str) -> List[str]:
        """Split experience section into individual jobs"""
        # Look for date patterns that typically indicate new job entries
        date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
        
        lines = section_text.split('\n')
        jobs = []
        current_job = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains a date (likely start of new job)
            if re.search(date_pattern, line, re.IGNORECASE):
                if current_job:
                    jobs.append('\n'.join(current_job))
                    current_job = []
            
            current_job.append(line)
        
        if current_job:
            jobs.append('\n'.join(current_job))
        
        return jobs
    
    def _parse_job(self, job_text: str) -> Optional[Dict]:
        """Parse a single job entry"""
        try:
            # Extract role/title
            role = self._extract_role(job_text)
            
            # Extract company
            company = self._extract_company(job_text)
            
            # Extract dates
            start_date, end_date = self._extract_dates(job_text)
            
            # Calculate duration
            duration_months = self._calculate_duration(start_date, end_date)
            
            # Extract description/responsibilities
            description = self._extract_description(job_text)
            
            if not role and not company:
                return None
            
            return {
                'role': role or 'Not specified',
                'company': company or 'Not specified',
                'start_date': start_date,
                'end_date': end_date or 'Present',
                'duration_months': duration_months,
                'duration_years': round(duration_months / 12, 1),
                'description': description,
                'is_current': end_date is None or 'present' in str(end_date).lower()
            }
        
        except Exception as e:
            logger.error(f"Error parsing job: {str(e)}")
            return None
    
    def _extract_role(self, text: str) -> Optional[str]:
        """Extract job role/title"""
        lines = text.split('\n')
        
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            # Check if line contains job title keywords
            if any(keyword in line.lower() for keyword in self.title_keywords):
                # Remove common prefixes
                role = re.sub(r'^(?:role|position|title):\s*', '', line, flags=re.IGNORECASE)
                return role.strip()
        
        # Return first non-empty line as fallback
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:
                return line
        
        return None
    
    def _extract_company(self, text: str) -> Optional[str]:
        """Extract company name"""
        # Look for common patterns
        patterns = [
            r'(?:at|@)\s+([A-Z][A-Za-z\s&,.]+?)(?:\n|,|\s+-|\s+\d{4})',
            r'(?:company|organization):\s*([A-Za-z\s&,.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                company = match.group(1).strip()
                # Clean up
                company = re.sub(r'\s*,\s*$', '', company)
                return company
        
        return None
    
    def _extract_dates(self, text: str) -> tuple:
        """Extract start and end dates"""
        # Pattern for date ranges
        date_pattern = r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\s*[-–—to]+\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current)'
        
        match = re.search(date_pattern, text, re.IGNORECASE)
        if match:
            start = self._normalize_date(match.group(1))
            end = self._normalize_date(match.group(2)) if 'present' not in match.group(2).lower() else None
            return start, end
        
        # Try to find just year ranges
        year_pattern = r'(\d{4})\s*[-–—to]+\s*(\d{4}|Present|Current)'
        match = re.search(year_pattern, text, re.IGNORECASE)
        if match:
            start = match.group(1)
            end = match.group(2) if 'present' not in match.group(2).lower() else None
            return start, end
        
        return None, None
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM format"""
        date_str = date_str.strip()
        
        # Parse month and year
        for month_name, month_num in self.months.items():
            if month_name in date_str.lower():
                year_match = re.search(r'\d{4}', date_str)
                if year_match:
                    year = year_match.group()
                    return f"{year}-{month_num:02d}"
        
        # Just year
        year_match = re.search(r'\d{4}', date_str)
        if year_match:
            return year_match.group()
        
        return date_str
    
    def _calculate_duration(self, start_date: Optional[str], end_date: Optional[str]) -> int:
        """Calculate duration in months"""
        if not start_date:
            return 0
        
        try:
            # Parse start date
            if '-' in start_date:
                start_year, start_month = map(int, start_date.split('-'))
            else:
                start_year = int(start_date)
                start_month = 1
            
            # Parse end date
            if end_date and '-' in str(end_date):
                end_year, end_month = map(int, str(end_date).split('-'))
            elif end_date:
                end_year = int(end_date)
                end_month = 12
            else:
                # Current date
                now = datetime.now()
                end_year, end_month = now.year, now.month
            
            # Calculate difference
            months = (end_year - start_year) * 12 + (end_month - start_month)
            return max(0, months)
        
        except:
            return 0
    
    def _extract_description(self, text: str) -> str:
        """Extract job description/responsibilities"""
        lines = text.split('\n')
        
        # Skip first few lines (typically role/company/dates)
        description_lines = []
        for line in lines[2:]:
            line = line.strip()
            if line and len(line) > 10:
                description_lines.append(line)
        
        return ' '.join(description_lines) if description_lines else ''
    
    def _calculate_total_experience(self, experiences: List[Dict]) -> float:
        """Calculate total years of experience"""
        total_months = sum(exp.get('duration_months', 0) for exp in experiences)
        return total_months / 12
