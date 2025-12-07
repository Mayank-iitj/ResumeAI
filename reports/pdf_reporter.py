"""
PDF Reporter
Generate PDF format reports
"""
from fpdf import FPDF
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PDFReporter(FPDF):
    """Generate PDF format reports"""
    
    def header(self):
        """PDF header"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Resume Analysis Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        """PDF footer"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title: str):
        """Add chapter title"""
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(2)
    
    def chapter_body(self, body: str):
        """Add chapter body text"""
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()


def generate_resume_report(resume_data: Dict, ats_score: Dict, 
                          feedback: Dict, output_path: str):
    """
    Generate comprehensive PDF report for a single resume
    
    Args:
        resume_data: Extracted resume data
        ats_score: ATS scoring results
        feedback: Optimization feedback
        output_path: Path to save PDF
    """
    try:
        pdf = PDFReporter()
        pdf.add_page()
        
        # Report metadata
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        pdf.ln(5)
        
        # Candidate Information
        pdf.chapter_title('1. Candidate Information')
        contact = resume_data.get('contact', {})
        info_text = f"""
Name: {contact.get('name', 'Not specified')}
Email: {contact.get('email', 'Not specified')}
Phone: {contact.get('phone', 'Not specified')}
LinkedIn: {contact.get('linkedin', 'Not specified')}
GitHub: {contact.get('github', 'Not specified')}
"""
        pdf.chapter_body(info_text.strip())
        
        # ATS Score
        pdf.chapter_title('2. ATS Score Summary')
        score_text = f"""
Overall Score: {ats_score.get('total_score', 0)}/100
Grade: {ats_score.get('grade', 'N/A')}
Match Status: {ats_score.get('match_status', 'N/A')}

Score Breakdown:
- Keyword Match: {ats_score.get('breakdown', {}).get('keyword_match', 0)}/100
- Skills Match: {ats_score.get('breakdown', {}).get('skills_match', 0)}/100
- Experience Relevance: {ats_score.get('breakdown', {}).get('experience_relevance', 0)}/100
- Semantic Similarity: {ats_score.get('breakdown', {}).get('semantic_similarity', 0)}/100
- Format Score: {ats_score.get('breakdown', {}).get('format_score', 0)}/100
"""
        pdf.chapter_body(score_text.strip())
        
        # Skills Summary
        pdf.chapter_title('3. Skills Overview')
        skills = resume_data.get('skills', {})
        tech_skills = ', '.join(skills.get('technical_skills', [])[:15])
        if len(skills.get('technical_skills', [])) > 15:
            tech_skills += '...'
        
        skills_text = f"""
Total Skills: {skills.get('total_count', 0)}
Technical Skills ({len(skills.get('technical_skills', []))}): {tech_skills or 'None listed'}
Soft Skills ({len(skills.get('soft_skills', []))}): {', '.join(skills.get('soft_skills', [])) or 'None listed'}
"""
        pdf.chapter_body(skills_text.strip())
        
        # Experience Summary
        pdf.chapter_title('4. Experience Summary')
        summary = resume_data.get('summary', {})
        exp_text = f"""
Total Experience: {summary.get('total_experience_years', 0):.1f} years
Number of Positions: {len(resume_data.get('experience', []))}
"""
        pdf.chapter_body(exp_text.strip())
        
        # Add each experience
        for i, exp in enumerate(resume_data.get('experience', [])[:3], 1):  # Limit to top 3
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 6, f"Position {i}: {exp.get('role', 'N/A')}", 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, f"Company: {exp.get('company', 'N/A')}\nDuration: {exp.get('duration_years', 0):.1f} years")
            pdf.ln(2)
        
        # Optimization Feedback
        pdf.add_page()
        pdf.chapter_title('5. Optimization Recommendations')
        
        # Critical Issues
        if feedback.get('critical_issues'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 6, 'Critical Issues:', 0, 1)
            pdf.set_font('Arial', '', 10)
            for issue in feedback['critical_issues']:
                pdf.multi_cell(0, 5, f"  {issue}")
            pdf.ln(3)
        
        # Improvements
        if feedback.get('improvements'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 6, 'Suggested Improvements:', 0, 1)
            pdf.set_font('Arial', '', 10)
            for improvement in feedback['improvements'][:10]:  # Limit to 10
                pdf.multi_cell(0, 5, f"  {improvement}")
            pdf.ln(3)
        
        # Strong Points
        if feedback.get('strong_points'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 6, 'Strong Points:', 0, 1)
            pdf.set_font('Arial', '', 10)
            for strength in feedback['strong_points']:
                pdf.multi_cell(0, 5, f"  {strength}")
        
        # Save PDF
        pdf.output(output_path)
        logger.info(f"PDF report saved to {output_path}")
    
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise


def generate_ranking_report(ranked_resumes: List[Dict], output_path: str):
    """
    Generate PDF report with ranked candidates
    
    Args:
        ranked_resumes: List of ranked resume dictionaries
        output_path: Path to save PDF
    """
    try:
        pdf = PDFReporter()
        pdf.add_page()
        
        # Report metadata
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Candidate Ranking Report", 0, 1)
        pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
        pdf.cell(0, 6, f"Total Candidates: {len(ranked_resumes)}", 0, 1)
        pdf.ln(10)
        
        # Rankings table
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(15, 8, 'Rank', 1, 0, 'C')
        pdf.cell(50, 8, 'Name', 1, 0, 'C')
        pdf.cell(30, 8, 'Score', 1, 0, 'C')
        pdf.cell(20, 8, 'Grade', 1, 0, 'C')
        pdf.cell(75, 8, 'Match Status', 1, 1, 'C')
        
        pdf.set_font('Arial', '', 10)
        for resume in ranked_resumes[:20]:  # Limit to top 20
            contact = resume.get('extracted_data', {}).get('contact', {})
            ats = resume.get('ats_score', {})
            
            pdf.cell(15, 7, str(resume.get('rank', '')), 1, 0, 'C')
            pdf.cell(50, 7, contact.get('name', 'N/A')[:25], 1, 0, 'L')
            pdf.cell(30, 7, f"{ats.get('total_score', 0):.1f}/100", 1, 0, 'C')
            pdf.cell(20, 7, ats.get('grade', 'N/A'), 1, 0, 'C')
            pdf.cell(75, 7, ats.get('match_status', 'N/A')[:30], 1, 1, 'L')
        
        pdf.output(output_path)
        logger.info(f"Ranking PDF report saved to {output_path}")
    
    except Exception as e:
        logger.error(f"Error generating ranking PDF: {e}")
        raise
