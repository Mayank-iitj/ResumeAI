"""
CSV Reporter
Generate CSV format reports
"""
import csv
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CSVReporter:
    """Generate CSV format reports"""
    
    @staticmethod
    def generate_ranking_report(ranked_resumes: List[Dict], output_path: str):
        """
        Generate CSV report with ranked resumes
        
        Args:
            ranked_resumes: List of ranked resume dictionaries
            output_path: Path to save CSV file
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Rank', 'Name', 'Email', 'Phone', 
                    'Total Score', 'Skills Match', 'Experience Score',
                    'Total Experience (Years)', 'Total Skills', 'Education Level',
                    'Match Status', 'Grade'
                ])
                
                # Data rows
                for resume in ranked_resumes:
                    contact = resume.get('extracted_data', {}).get('contact', {})
                    ats_score = resume.get('ats_score', {})
                    summary = resume.get('extracted_data', {}).get('summary', {})
                    
                    writer.writerow([
                        resume.get('rank', 0),
                        contact.get('name', 'N/A'),
                        contact.get('email', 'N/A'),
                        contact.get('phone', 'N/A'),
                        ats_score.get('total_score', 0),
                        ats_score.get('breakdown', {}).get('skills_match', 0),
                        ats_score.get('breakdown', {}).get('experience_relevance', 0),
                        summary.get('total_experience_years', 0),
                        summary.get('total_skills', 0),
                        summary.get('education_level', 'N/A'),
                        ats_score.get('match_status', 'N/A'),
                        ats_score.get('grade', 'N/A')
                    ])
            
            logger.info(f"CSV ranking report saved to {output_path}")
        
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            raise
    
    @staticmethod
    def generate_skills_comparison(resumes: List[Dict], output_path: str):
        """
        Generate CSV comparing skills across resumes
        
        Args:
            resumes: List of resume dictionaries
            output_path: Path to save CSV file
        """
        try:
            # Collect all unique skills
            all_skills = set()
            for resume in resumes:
                skills_data = resume.get('extracted_data', {}).get('skills', {})
                all_skills.update(skills_data.get('technical_skills', []))
            
            all_skills = sorted(list(all_skills))
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                names = [resume.get('extracted_data', {}).get('contact', {}).get('name', f'Candidate {i+1}') 
                        for i, resume in enumerate(resumes)]
                writer.writerow(['Skill'] + names)
                
                # Data rows
                for skill in all_skills:
                    row = [skill]
                    for resume in resumes:
                        skills_data = resume.get('extracted_data', {}).get('skills', {})
                        has_skill = skill in skills_data.get('technical_skills', [])
                        row.append('✓' if has_skill else '✗')
                    writer.writerow(row)
            
            logger.info(f"Skills comparison CSV saved to {output_path}")
        
        except Exception as e:
            logger.error(f"Error generating skills comparison CSV: {e}")
            raise
