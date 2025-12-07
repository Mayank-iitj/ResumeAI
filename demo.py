"""
Demo Script - Test Resume Analyzer with sample data
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from analyzer import ResumeAnalyzerCLI
from colorama import init, Fore, Style

init(autoreset=True)


def main():
    """Run demo analysis"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}Resume Analyzer - Demo Script")
    print(f"{Fore.CYAN}{'='*80}\n")
    
    # Initialize CLI
    cli = ResumeAnalyzerCLI()
    
    # Demo 1: Single resume analysis
    print(f"{Fore.YELLOW}Demo 1: Single Resume Analysis")
    print(f"{Fore.YELLOW}{'-'*80}\n")
    
    resume_path = "data/sample_resumes/sample_resume_ml.txt"
    jd_path = "data/sample_jds/ml_engineer_jd.txt"
    output_dir = "output/demo"
    
    if not Path(resume_path).exists():
        print(f"{Fore.RED}Sample resume not found: {resume_path}")
        print(f"{Fore.YELLOW}Please ensure sample data exists in data/ directory")
        return
    
    if not Path(jd_path).exists():
        print(f"{Fore.RED}Sample JD not found: {jd_path}")
        return
    
    try:
        cli.analyze_single_resume(
            resume_path=resume_path,
            jd_path=jd_path,
            output_dir=output_dir,
            report_format='json'
        )
        
        print(f"\n{Fore.GREEN}{'='*80}")
        print(f"{Fore.GREEN}Demo Completed Successfully!")
        print(f"{Fore.GREEN}{'='*80}\n")
        print(f"{Fore.WHITE}Output saved to: {output_dir}/")
        print(f"{Fore.WHITE}Check the JSON report for detailed analysis\n")
        
    except Exception as e:
        print(f"\n{Fore.RED}Demo failed: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
