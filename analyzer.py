#!/usr/bin/env python3
"""
Resume Analyzer CLI - Main Entry Point
Production-ready ATS resume analyzer and scorer
"""
import argparse
import sys
import os
import logging
from pathlib import Path
from typing import List, Dict
import json
from colorama import init, Fore, Style
from tqdm import tqdm

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Import modules
from parsers import ResumeParser
from extractors import ResumeExtractor
from scorer import ResumeScorer
from ranker import ResumeRanker
from optimizer import ResumeOptimizer
from reports.json_reporter import JSONReporter
from reports.csv_reporter import CSVReporter
from reports import generate_resume_report, generate_ranking_report
from utils.metrics import MetricsCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resume_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ResumeAnalyzerCLI:
    """Main CLI application for resume analysis"""
    
    def __init__(self):
        self.parser = ResumeParser()
        self.extractor = ResumeExtractor()
        self.scorer = ResumeScorer(use_embeddings=True)
        self.ranker = ResumeRanker()
        self.optimizer = ResumeOptimizer()
        self.json_reporter = JSONReporter()
        self.csv_reporter = CSVReporter()
    
    def analyze_single_resume(self, resume_path: str, jd_path: str = None, 
                             output_dir: str = None, report_format: str = None):
        """
        Analyze a single resume
        
        Args:
            resume_path: Path to resume file
            jd_path: Path to job description file
            output_dir: Directory to save outputs
            report_format: Report format (json/csv/pdf)
        """
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}Resume Analyzer - Single Resume Analysis")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        try:
            # Parse resume
            print(f"{Fore.YELLOW}[1/5] Parsing resume: {Path(resume_path).name}")
            parsed_data = self.parser.parse(resume_path)
            resume_text = parsed_data['text']
            
            # Extract data
            print(f"{Fore.YELLOW}[2/5] Extracting structured data...")
            extracted_data = self.extractor.extract_all(resume_text)
            
            # Load job description if provided
            jd_text = ""
            if jd_path:
                print(f"{Fore.YELLOW}[3/5] Loading job description...")
                with open(jd_path, 'r', encoding='utf-8') as f:
                    jd_text = f.read()
                
                # Score resume
                print(f"{Fore.YELLOW}[4/5] Calculating ATS score...")
                ats_score = self.scorer.score_resume(extracted_data, jd_text)
            else:
                print(f"{Fore.YELLOW}[3/5] No job description provided")
                ats_score = {'total_score': 0, 'breakdown': {}, 'grade': 'N/A', 'match_status': 'N/A'}
            
            # Generate feedback
            print(f"{Fore.YELLOW}[5/5] Generating optimization feedback...")
            feedback = self.optimizer.generate_feedback(extracted_data, jd_text, ats_score)
            
            # Display results
            self._display_results(extracted_data, ats_score, feedback)
            
            # Save reports
            if output_dir:
                self._save_reports(
                    extracted_data, ats_score, feedback,
                    output_dir, Path(resume_path).stem, report_format
                )
            
            print(f"\n{Fore.GREEN}✓ Analysis completed successfully!\n")
            
        except Exception as e:
            print(f"\n{Fore.RED}✗ Error: {str(e)}\n")
            logger.error(f"Error analyzing resume: {e}", exc_info=True)
            sys.exit(1)
    
    def analyze_batch(self, resumes_dir: str, jd_path: str, output_dir: str, 
                     topk: int = 5, report_format: str = 'csv'):
        """
        Analyze multiple resumes and rank them
        
        Args:
            resumes_dir: Directory containing resume files
            jd_path: Path to job description file
            output_dir: Directory to save outputs
            topk: Number of top candidates to highlight
            report_format: Report format
        """
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}Resume Analyzer - Batch Mode")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        try:
            # Get resume files
            resume_files = self._get_resume_files(resumes_dir)
            
            if not resume_files:
                print(f"{Fore.RED}No resume files found in {resumes_dir}")
                return
            
            print(f"{Fore.GREEN}Found {len(resume_files)} resume(s) to analyze\n")
            
            # Load job description
            with open(jd_path, 'r', encoding='utf-8') as f:
                jd_text = f.read()
            
            # Analyze each resume
            results = []
            
            for resume_path in tqdm(resume_files, desc="Analyzing resumes", ncols=80):
                try:
                    # Parse and extract
                    parsed_data = self.parser.parse(str(resume_path))
                    extracted_data = self.extractor.extract_all(parsed_data['text'])
                    
                    # Score
                    ats_score = self.scorer.score_resume(extracted_data, jd_text)
                    
                    # Generate feedback
                    feedback = self.optimizer.generate_feedback(extracted_data, jd_text, ats_score)
                    
                    results.append({
                        'file_path': str(resume_path),
                        'file_name': resume_path.name,
                        'extracted_data': extracted_data,
                        'ats_score': ats_score,
                        'feedback': feedback
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing {resume_path}: {e}")
                    continue
            
            # Rank resumes
            print(f"\n{Fore.YELLOW}Ranking candidates...")
            ranked_resumes = self.ranker.rank_resumes(results, jd_text)
            
            # Display rankings
            self._display_rankings(ranked_resumes, topk)
            
            # Save reports
            self._save_batch_reports(ranked_resumes, output_dir, report_format)
            
            print(f"\n{Fore.GREEN}✓ Batch analysis completed!\n")
            
        except Exception as e:
            print(f"\n{Fore.RED}✗ Error: {str(e)}\n")
            logger.error(f"Error in batch analysis: {e}", exc_info=True)
            sys.exit(1)
    
    def _get_resume_files(self, directory: str) -> List[Path]:
        """Get all resume files from directory"""
        directory = Path(directory)
        supported_formats = ['.pdf', '.docx', '.doc', '.txt']
        
        resume_files = []
        for ext in supported_formats:
            resume_files.extend(directory.glob(f'*{ext}'))
        
        return sorted(resume_files)
    
    def _display_results(self, extracted_data: Dict, ats_score: Dict, feedback: Dict):
        """Display analysis results in terminal"""
        print(f"\n{Fore.CYAN}{'─'*80}")
        print(f"{Fore.CYAN}ANALYSIS RESULTS")
        print(f"{Fore.CYAN}{'─'*80}\n")
        
        # Contact Info
        contact = extracted_data.get('contact', {})
        print(f"{Fore.WHITE}📋 Candidate: {Style.BRIGHT}{contact.get('name', 'N/A')}")
        print(f"{Fore.WHITE}📧 Email: {contact.get('email', 'N/A')}")
        print(f"{Fore.WHITE}📱 Phone: {contact.get('phone', 'N/A')}\n")
        
        # ATS Score
        total_score = ats_score.get('total_score', 0)
        grade = ats_score.get('grade', 'N/A')
        
        score_color = Fore.GREEN if total_score >= 70 else Fore.YELLOW if total_score >= 50 else Fore.RED
        
        print(f"{Fore.CYAN}🎯 ATS SCORE: {score_color}{Style.BRIGHT}{total_score}/100 ({grade})")
        print(f"{Fore.WHITE}Status: {ats_score.get('match_status', 'N/A')}\n")
        
        # Score Breakdown
        if 'breakdown' in ats_score:
            print(f"{Fore.CYAN}Score Breakdown:")
            breakdown = ats_score['breakdown']
            for key, value in breakdown.items():
                print(f"  • {key.replace('_', ' ').title()}: {value:.1f}/100")
            print()
        
        # Skills Summary
        skills = extracted_data.get('skills', {})
        print(f"{Fore.CYAN}💼 Skills: {skills.get('total_count', 0)} total")
        print(f"  • Technical: {len(skills.get('technical_skills', []))}")
        print(f"  • Soft: {len(skills.get('soft_skills', []))}\n")
        
        # Experience Summary
        summary = extracted_data.get('summary', {})
        print(f"{Fore.CYAN}🏢 Experience: {summary.get('total_experience_years', 0):.1f} years")
        print(f"  • Positions: {len(extracted_data.get('experience', []))}\n")
        
        # Education
        print(f"{Fore.CYAN}🎓 Education: {summary.get('education_level', 'Not specified')}\n")
        
        # Feedback
        print(f"{Fore.CYAN}{'─'*80}")
        print(f"{Fore.CYAN}OPTIMIZATION FEEDBACK")
        print(f"{Fore.CYAN}{'─'*80}\n")
        
        if feedback.get('critical_issues'):
            print(f"{Fore.RED}Critical Issues:")
            for issue in feedback['critical_issues']:
                print(f"  {issue}")
            print()
        
        if feedback.get('strong_points'):
            print(f"{Fore.GREEN}Strong Points:")
            for strength in feedback['strong_points'][:5]:
                print(f"  {strength}")
            print()
        
        if feedback.get('improvements'):
            print(f"{Fore.YELLOW}Improvements:")
            for improvement in feedback['improvements'][:5]:
                print(f"  {improvement}")
            print()
    
    def _display_rankings(self, ranked_resumes: List[Dict], topk: int):
        """Display candidate rankings"""
        print(f"\n{Fore.CYAN}{'─'*80}")
        print(f"{Fore.CYAN}CANDIDATE RANKINGS")
        print(f"{Fore.CYAN}{'─'*80}\n")
        
        print(f"{'Rank':<6} {'Name':<25} {'Score':<12} {'Grade':<8} {'Status':<20}")
        print(f"{'-'*80}")
        
        for resume in ranked_resumes[:topk]:
            rank = resume.get('rank', 0)
            contact = resume.get('extracted_data', {}).get('contact', {})
            name = contact.get('name', 'N/A')[:24]
            ats = resume.get('ats_score', {})
            score = ats.get('total_score', 0)
            grade = ats.get('grade', 'N/A')
            status = ats.get('match_status', 'N/A')[:19]
            
            rank_color = Fore.GREEN if rank <= 3 else Fore.YELLOW if rank <= 5 else Fore.WHITE
            
            print(f"{rank_color}{rank:<6} {name:<25} {score:<12.1f} {grade:<8} {status:<20}")
    
    def _save_reports(self, extracted_data: Dict, ats_score: Dict, feedback: Dict,
                     output_dir: str, filename: str, report_format: str = None):
        """Save analysis reports"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Always save JSON
        json_path = output_path / f"{filename}_analysis.json"
        self.json_reporter.generate_single_resume_report(
            extracted_data, ats_score, feedback, str(json_path)
        )
        
        # Save additional format if requested
        if report_format == 'pdf':
            pdf_path = output_path / f"{filename}_report.pdf"
            generate_resume_report(extracted_data, ats_score, feedback, str(pdf_path))
            print(f"{Fore.GREEN}✓ PDF report saved: {pdf_path}")
        
        print(f"{Fore.GREEN}✓ JSON report saved: {json_path}")
    
    def _save_batch_reports(self, ranked_resumes: List[Dict], output_dir: str, 
                           report_format: str):
        """Save batch analysis reports"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = output_path / "batch_analysis.json"
        self.json_reporter.generate_batch_report(ranked_resumes, str(json_path))
        
        # Save CSV ranking
        csv_path = output_path / "candidate_rankings.csv"
        self.csv_reporter.generate_ranking_report(ranked_resumes, str(csv_path))
        
        # Save PDF if requested
        if report_format == 'pdf':
            pdf_path = output_path / "ranking_report.pdf"
            generate_ranking_report(ranked_resumes, str(pdf_path))
            print(f"{Fore.GREEN}✓ PDF report saved: {pdf_path}")
        
        print(f"{Fore.GREEN}✓ JSON report saved: {json_path}")
        print(f"{Fore.GREEN}✓ CSV report saved: {csv_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Resume Analyzer CLI - Production-ready ATS scoring and analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single resume
  python analyzer.py --resume resume.pdf --jd job_desc.txt --output results/

  # Batch mode - rank candidates
  python analyzer.py --resumes data/resumes/ --jd job_desc.txt --output results/ --topk 5

  # Generate PDF report
  python analyzer.py --resume resume.pdf --jd job_desc.txt --report pdf
        """
    )
    
    parser.add_argument('--resume', help='Path to single resume file')
    parser.add_argument('--resumes', help='Directory containing multiple resumes (batch mode)')
    parser.add_argument('--jd', required=True, help='Path to job description file')
    parser.add_argument('--output', default='./output', help='Output directory (default: ./output)')
    parser.add_argument('--topk', type=int, default=5, help='Number of top candidates to show (default: 5)')
    parser.add_argument('--report', choices=['json', 'csv', 'pdf'], help='Report format')
    parser.add_argument('--batch', action='store_true', help='Enable batch mode')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate arguments
    if not args.resume and not args.resumes:
        parser.error("Either --resume or --resumes must be specified")
    
    if args.resume and args.resumes:
        parser.error("Cannot use both --resume and --resumes")
    
    # Initialize CLI
    cli = ResumeAnalyzerCLI()
    
    # Run analysis
    if args.resume:
        cli.analyze_single_resume(args.resume, args.jd, args.output, args.report)
    elif args.resumes or args.batch:
        resumes_dir = args.resumes if args.resumes else args.resume
        cli.analyze_batch(resumes_dir, args.jd, args.output, args.topk, args.report or 'csv')


if __name__ == '__main__':
    main()
