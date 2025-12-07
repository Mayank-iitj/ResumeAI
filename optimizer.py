"""
Optimizer Module
Generates actionable feedback and optimization suggestions for resumes
"""
from typing import List, Dict
import re
import logging

logger = logging.getLogger(__name__)


class ResumeOptimizer:
    """
    Analyze resumes and provide optimization suggestions
    """
    
    def __init__(self):
        # High-value skills by domain
        self.trending_skills = {
            'software': ['python', 'java', 'javascript', 'react', 'aws', 'docker', 'kubernetes'],
            'data': ['machine learning', 'tensorflow', 'pytorch', 'sql', 'pandas', 'tableau'],
            'cloud': ['aws', 'azure', 'gcp', 'terraform', 'jenkins', 'ci/cd'],
            'general': ['git', 'agile', 'rest api', 'microservices']
        }
    
    def generate_feedback(self, resume_data: Dict, jd_text: str = None, 
                         ats_score: Dict = None) -> Dict:
        """
        Generate comprehensive optimization feedback
        
        Args:
            resume_data: Extracted resume data
            jd_text: Job description text (optional)
            ats_score: ATS scoring results (optional)
            
        Returns:
            Dictionary with suggestions and improvements
        """
        logger.info("Generating optimization feedback...")
        
        feedback = {
            'overall_rating': self._get_overall_rating(resume_data, ats_score),
            'critical_issues': [],
            'improvements': [],
            'suggestions': [],
            'missing_keywords': [],
            'strong_points': [],
            'optimization_score': 0
        }
        
        # Check critical issues
        feedback['critical_issues'] = self._identify_critical_issues(resume_data)
        
        # Check for missing sections
        feedback['improvements'] = self._suggest_improvements(resume_data)
        
        # Analyze content quality
        feedback['suggestions'] = self._analyze_content_quality(resume_data)
        
        # If JD provided, find missing keywords
        if jd_text:
            feedback['missing_keywords'] = self._find_missing_keywords(resume_data, jd_text)
        
        # Identify strong points
        feedback['strong_points'] = self._identify_strengths(resume_data)
        
        # Calculate optimization score
        feedback['optimization_score'] = self._calculate_optimization_score(feedback, ats_score)
        
        logger.info(f"Feedback generated: {len(feedback['improvements'])} improvements, "
                   f"{len(feedback['suggestions'])} suggestions")
        
        return feedback
    
    def _get_overall_rating(self, resume_data: Dict, ats_score: Dict) -> str:
        """Get overall resume rating"""
        if ats_score and 'total_score' in ats_score:
            score = ats_score['total_score']
            if score >= 85:
                return 'Excellent'
            elif score >= 70:
                return 'Good'
            elif score >= 55:
                return 'Average'
            else:
                return 'Needs Improvement'
        
        # Fallback rating based on completeness
        sections = 0
        if resume_data.get('contact', {}).get('email'):
            sections += 1
        if resume_data.get('skills', {}).get('technical_skills'):
            sections += 1
        if resume_data.get('experience'):
            sections += 1
        if resume_data.get('education'):
            sections += 1
        
        if sections >= 4:
            return 'Good'
        elif sections >= 3:
            return 'Average'
        else:
            return 'Needs Improvement'
    
    def _identify_critical_issues(self, resume_data: Dict) -> List[str]:
        """Identify critical issues that must be fixed"""
        issues = []
        
        contact = resume_data.get('contact', {})
        
        # Missing contact information
        if not contact.get('email'):
            issues.append("❌ Missing email address - Critical for contact")
        
        if not contact.get('phone'):
            issues.append("⚠️ Missing phone number - Recommended to add")
        
        # Missing essential sections
        if not resume_data.get('experience'):
            issues.append("❌ No work experience found - Add professional experience")
        
        if not resume_data.get('education'):
            issues.append("❌ No education information found - Add educational background")
        
        skills = resume_data.get('skills', {})
        if not skills.get('technical_skills'):
            issues.append("❌ No technical skills listed - Add relevant skills")
        
        return issues
    
    def _suggest_improvements(self, resume_data: Dict) -> List[str]:
        """Suggest improvements for missing or weak sections"""
        improvements = []
        
        # Skills section
        skills = resume_data.get('skills', {})
        tech_skills = skills.get('technical_skills', [])
        
        if len(tech_skills) < 10:
            improvements.append(
                f"📈 Add more technical skills (Current: {len(tech_skills)}, Recommended: 10-15)"
            )
        
        # Experience section
        experiences = resume_data.get('experience', [])
        
        if len(experiences) < 2:
            improvements.append(
                "💼 Add more work experience entries (minimum 2-3 for better ATS score)"
            )
        
        for exp in experiences:
            desc = exp.get('description', '')
            if len(desc) < 100:
                improvements.append(
                    f"📝 Expand description for '{exp.get('role', 'position')}' "
                    f"(add 3-5 bullet points with achievements)"
                )
        
        # Projects
        projects = resume_data.get('projects', [])
        if len(projects) == 0:
            improvements.append(
                "🚀 Add projects section to showcase practical experience"
            )
        elif len(projects) < 3:
            improvements.append(
                f"🚀 Add more projects (Current: {len(projects)}, Recommended: 3-5)"
            )
        
        # Certifications
        certs = resume_data.get('certifications', [])
        if len(certs) == 0:
            improvements.append(
                "🎓 Add certifications if you have any (AWS, Azure, Google, etc.)"
            )
        
        # LinkedIn/GitHub
        contact = resume_data.get('contact', {})
        if not contact.get('linkedin'):
            improvements.append(
                "🔗 Add LinkedIn profile URL for professional networking"
            )
        
        if not contact.get('github'):
            improvements.append(
                "💻 Add GitHub profile to showcase your code (especially for tech roles)"
            )
        
        return improvements
    
    def _analyze_content_quality(self, resume_data: Dict) -> List[str]:
        """Analyze content quality and provide suggestions"""
        suggestions = []
        
        # Check experience descriptions for quantifiable achievements
        experiences = resume_data.get('experience', [])
        has_metrics = False
        
        for exp in experiences:
            desc = exp.get('description', '')
            # Look for numbers/metrics
            if re.search(r'\d+%|\d+x|\$\d+|saved \d+|increased \d+', desc, re.IGNORECASE):
                has_metrics = True
                break
        
        if not has_metrics and experiences:
            suggestions.append(
                "📊 Quantify achievements with metrics (e.g., 'Improved performance by 40%', "
                "'Reduced costs by $50K', 'Led team of 5 engineers')"
            )
        
        # Check for action verbs
        weak_verbs = ['responsible for', 'worked on', 'helped with', 'assisted in']
        strong_verbs = ['Led', 'Developed', 'Implemented', 'Achieved', 'Optimized', 'Designed']
        
        for exp in experiences:
            desc = exp.get('description', '').lower()
            if any(verb in desc for verb in weak_verbs):
                suggestions.append(
                    f"💪 Use strong action verbs instead of passive phrases "
                    f"(Try: {', '.join(strong_verbs[:3])}...)"
                )
                break
        
        # Check description length
        for exp in experiences:
            desc = exp.get('description', '')
            bullet_count = desc.count('\n') + desc.count('•') + desc.count('-')
            
            if bullet_count < 3:
                suggestions.append(
                    "📋 Add 3-5 bullet points per job to fully describe your responsibilities"
                )
                break
        
        # Education details
        education = resume_data.get('education', [])
        for edu in education:
            if not edu.get('year'):
                suggestions.append(
                    "📅 Add graduation years to education entries"
                )
                break
        
        # Overall length check
        total_exp_years = resume_data.get('summary', {}).get('total_experience_years', 0)
        if total_exp_years > 5 and len(experiences) < 3:
            suggestions.append(
                "⏰ With 5+ years experience, include at least 3 recent positions"
            )
        
        return suggestions
    
    def _find_missing_keywords(self, resume_data: Dict, jd_text: str) -> List[str]:
        """Find important keywords from JD that are missing in resume"""
        # Extract skills from resume
        resume_skills = set()
        skills_data = resume_data.get('skills', {})
        resume_skills.update(s.lower() for s in skills_data.get('technical_skills', []))
        resume_skills.update(s.lower() for s in skills_data.get('soft_skills', []))
        
        # Prepare resume text
        resume_text = self._get_resume_text(resume_data).lower()
        
        # Extract keywords from JD
        jd_lower = jd_text.lower()
        jd_keywords = []
        
        # Check for common tech skills
        all_skills = []
        for domain_skills in self.trending_skills.values():
            all_skills.extend(domain_skills)
        
        for skill in all_skills:
            if skill in jd_lower and skill not in resume_text:
                jd_keywords.append(skill)
        
        # Also check for specific tools/technologies mentioned in JD
        tech_pattern = r'\b([A-Z][a-zA-Z+#]{2,}(?:\.[a-z]{2,})?)\b'
        potential_tech = re.findall(tech_pattern, jd_text)
        
        for tech in potential_tech[:10]:  # Limit to top 10
            if tech.lower() not in resume_text and len(tech) > 2:
                if tech not in jd_keywords:
                    jd_keywords.append(tech.lower())
        
        # Format as suggestions
        suggestions = []
        for keyword in jd_keywords[:5]:  # Top 5 missing keywords
            suggestions.append(
                f"🔑 Add '{keyword}' keyword (mentioned in job description)"
            )
        
        return suggestions
    
    def _identify_strengths(self, resume_data: Dict) -> List[str]:
        """Identify strong points in the resume"""
        strengths = []
        
        # Strong skills section
        skills = resume_data.get('skills', {})
        tech_count = len(skills.get('technical_skills', []))
        if tech_count >= 15:
            strengths.append(f"✅ Strong technical skills portfolio ({tech_count} skills)")
        
        # Good experience
        total_years = resume_data.get('summary', {}).get('total_experience_years', 0)
        if total_years >= 5:
            strengths.append(f"✅ Solid work experience ({total_years:.1f} years)")
        
        # Education level
        edu_level = resume_data.get('summary', {}).get('education_level', '')
        if edu_level in ['Phd', 'Doctorate', 'Master', 'Mba']:
            strengths.append(f"✅ Advanced degree ({edu_level})")
        
        # Projects
        projects = resume_data.get('projects', [])
        if len(projects) >= 3:
            strengths.append(f"✅ Good project portfolio ({len(projects)} projects)")
        
        # Certifications
        certs = resume_data.get('certifications', [])
        if len(certs) >= 2:
            strengths.append(f"✅ Professional certifications ({len(certs)})")
        
        # Complete contact info
        contact = resume_data.get('contact', {})
        if contact.get('email') and contact.get('phone') and contact.get('linkedin'):
            strengths.append("✅ Complete contact information")
        
        return strengths
    
    def _calculate_optimization_score(self, feedback: Dict, ats_score: Dict) -> int:
        """Calculate how optimized the resume is (0-100)"""
        score = 100
        
        # Deduct for critical issues
        score -= len(feedback['critical_issues']) * 15
        
        # Deduct for improvements needed
        score -= len(feedback['improvements']) * 5
        
        # Deduct for missing keywords
        score -= len(feedback['missing_keywords']) * 3
        
        # Bonus for strengths
        score += len(feedback['strong_points']) * 2
        
        return max(0, min(100, score))
    
    def _get_resume_text(self, resume_data: Dict) -> str:
        """Get all resume text for keyword matching"""
        parts = []
        
        if 'skills' in resume_data:
            skills = resume_data['skills']
            parts.extend(skills.get('technical_skills', []))
            parts.extend(skills.get('soft_skills', []))
        
        if 'experience' in resume_data:
            for exp in resume_data['experience']:
                parts.append(exp.get('role', ''))
                parts.append(exp.get('description', ''))
        
        return ' '.join(parts)
