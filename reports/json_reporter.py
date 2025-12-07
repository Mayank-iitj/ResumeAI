"""
JSON Reporter
Generate JSON format reports
"""
import json
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JSONReporter:
    """Generate JSON format reports"""
    
    @staticmethod
    def generate_single_resume_report(resume_data: Dict, ats_score: Dict, 
                                     feedback: Dict, output_path: str = None) -> str:
        """
        Generate JSON report for single resume
        
        Args:
            resume_data: Extracted resume data
            ats_score: ATS scoring results
            feedback: Optimization feedback
            output_path: Optional path to save report
            
        Returns:
            JSON string
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'resume_analysis': {
                'contact': resume_data.get('contact', {}),
                'summary': resume_data.get('summary', {}),
                'skills': resume_data.get('skills', {}),
                'experience': resume_data.get('experience', []),
                'education': resume_data.get('education', []),
                'projects': resume_data.get('projects', []),
                'certifications': resume_data.get('certifications', [])
            },
            'ats_score': ats_score,
            'optimization_feedback': feedback
        }
        
        json_str = json.dumps(report, indent=2, ensure_ascii=False)
        
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                logger.info(f"JSON report saved to {output_path}")
            except Exception as e:
                logger.error(f"Error saving JSON report: {e}")
        
        return json_str
    
    @staticmethod
    def generate_batch_report(results: List[Dict], output_path: str = None) -> str:
        """
        Generate JSON report for multiple resumes
        
        Args:
            results: List of resume analysis results
            output_path: Optional path to save report
            
        Returns:
            JSON string
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_resumes': len(results),
            'results': results,
            'summary': {
                'average_score': sum(r.get('ats_score', {}).get('total_score', 0) for r in results) / len(results) if results else 0,
                'top_score': max((r.get('ats_score', {}).get('total_score', 0) for r in results), default=0),
                'low_score': min((r.get('ats_score', {}).get('total_score', 0) for r in results), default=0)
            }
        }
        
        json_str = json.dumps(report, indent=2, ensure_ascii=False)
        
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
                logger.info(f"Batch JSON report saved to {output_path}")
            except Exception as e:
                logger.error(f"Error saving batch JSON report: {e}")
        
        return json_str
