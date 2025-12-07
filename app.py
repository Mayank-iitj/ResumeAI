"""
Resume Analyzer - Streamlit Web Application
Production-ready web interface for resume analysis and ATS scoring

Created by: MAYANK SHARMA
Website: https://mayankiitj.vercel.app
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json
import tempfile
import os
from datetime import datetime
import logging

# Import core modules
from parsers import ResumeParser
from extractors import ResumeExtractor
from scorer import ResumeScorer
from ranker import ResumeRanker
from optimizer import ResumeOptimizer
from reports.json_reporter import JSONReporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .score-value {
        font-size: 4rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .grade-badge {
        font-size: 2rem;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        background: rgba(255,255,255,0.2);
        display: inline-block;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .danger-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'batch_results' not in st.session_state:
        st.session_state.batch_results = []
    if 'scorer' not in st.session_state:
        st.session_state.scorer = ResumeScorer(use_embeddings=True)
    if 'extractor' not in st.session_state:
        st.session_state.extractor = ResumeExtractor()


def create_score_gauge(score: float, title: str = "ATS Score"):
    """Create an interactive gauge chart for score visualization"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        delta={'reference': 70, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffcccc'},
                {'range': [50, 70], 'color': '#fff4cc'},
                {'range': [70, 85], 'color': '#ccf2cc'},
                {'range': [85, 100], 'color': '#99e699'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig


def create_breakdown_chart(breakdown: dict):
    """Create a breakdown bar chart for scoring components"""
    components = list(breakdown.keys())
    values = list(breakdown.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=values,
            y=components,
            orientation='h',
            marker=dict(
                color=values,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Score")
            ),
            text=[f"{v:.1f}" for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Score Breakdown by Component",
        xaxis_title="Score",
        yaxis_title="Component",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_skills_chart(skills_data: dict):
    """Create skills distribution chart"""
    technical_skills = skills_data.get('technical_skills', [])
    soft_skills = skills_data.get('soft_skills', [])
    
    fig = go.Figure(data=[
        go.Pie(
            labels=['Technical Skills', 'Soft Skills'],
            values=[len(technical_skills), len(soft_skills)],
            hole=.3,
            marker_colors=['#1f77b4', '#ff7f0e']
        )
    ])
    
    fig.update_layout(
        title="Skills Distribution",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig


def analyze_single_resume(resume_file, jd_text: str):
    """Analyze a single resume file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(resume_file.name).suffix) as tmp_file:
            tmp_file.write(resume_file.getvalue())
            tmp_path = tmp_file.name
        
        # Parse resume
        with st.spinner("📄 Parsing resume..."):
            parser = ResumeParser()
            resume_text = parser.parse(tmp_path)
        
        # Extract data
        with st.spinner("🔍 Extracting structured data..."):
            resume_data = st.session_state.extractor.extract_all(resume_text, tmp_path)
        
        # Calculate score
        with st.spinner("📊 Calculating ATS score..."):
            score_result = st.session_state.scorer.score_resume(resume_data, jd_text)
        
        # Generate feedback
        with st.spinner("💡 Generating optimization suggestions..."):
            optimizer = ResumeOptimizer()
            feedback = optimizer.generate_feedback(resume_data, jd_text, score_result)
        
        # Clean up
        os.unlink(tmp_path)
        
        return {
            'resume_data': resume_data,
            'score_result': score_result,
            'feedback': feedback,
            'filename': resume_file.name
        }
        
    except Exception as e:
        st.error(f"❌ Error analyzing resume: {str(e)}")
        logger.error(f"Analysis error: {e}", exc_info=True)
        return None


def display_analysis_results(results: dict):
    """Display comprehensive analysis results"""
    resume_data = results['resume_data']
    score_result = results['score_result']
    feedback = results['feedback']
    
    # Header with candidate info
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👤 Candidate Information")
        st.write(f"**Name:** {resume_data.get('name', 'N/A')}")
        st.write(f"**Email:** {resume_data.get('email', 'N/A')}")
        st.write(f"**Phone:** {resume_data.get('phone', 'N/A')}")
    
    with col2:
        st.markdown("### 💼 Experience")
        experiences = resume_data.get('experience', [])
        total_years = sum([exp.get('duration_months', 0) for exp in experiences]) / 12
        st.write(f"**Total Experience:** {total_years:.1f} years")
        st.write(f"**Positions:** {len(experiences)}")
    
    with col3:
        st.markdown("### 🎓 Education")
        education = resume_data.get('education', [])
        st.write(f"**Highest Degree:** {resume_data.get('education_level', 'N/A')}")
        st.write(f"**Total Degrees:** {len(education)}")
    
    # ATS Score Section
    st.markdown("---")
    st.markdown("## 🎯 ATS Score Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Score card
        score = score_result['final_score']
        grade = score_result['grade']
        status = score_result['status']
        
        st.markdown(f"""
        <div class="score-card">
            <h2>ATS Score</h2>
            <div class="score-value">{score:.1f}</div>
            <div class="grade-badge">{grade}</div>
            <p style="margin-top: 1rem; font-size: 1.2rem;">{status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Score gauge
        st.plotly_chart(create_score_gauge(score), use_container_width=True)
    
    # Score breakdown
    st.markdown("### 📊 Score Breakdown")
    breakdown = score_result.get('breakdown', {})
    st.plotly_chart(create_breakdown_chart(breakdown), use_container_width=True)
    
    # Detailed metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🔑 Keyword Match</h4>
            <h2>{breakdown.get('keyword_score', 0):.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🛠️ Skills Match</h4>
            <h2>{breakdown.get('skills_score', 0):.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>💼 Experience</h4>
            <h2>{breakdown.get('experience_score', 0):.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Skills Analysis
    st.markdown("---")
    st.markdown("## 🛠️ Skills Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_skills_chart(resume_data), use_container_width=True)
    
    with col2:
        technical_skills = resume_data.get('technical_skills', [])
        soft_skills = resume_data.get('soft_skills', [])
        
        st.markdown("### Technical Skills")
        if technical_skills:
            skills_str = ", ".join(technical_skills[:20])
            st.write(skills_str)
            if len(technical_skills) > 20:
                st.write(f"*...and {len(technical_skills) - 20} more*")
        else:
            st.write("No technical skills detected")
        
        st.markdown("### Soft Skills")
        if soft_skills:
            st.write(", ".join(soft_skills))
        else:
            st.write("No soft skills detected")
    
    # Optimization Feedback
    st.markdown("---")
    st.markdown("## 💡 Optimization Feedback")
    
    # Critical Issues
    critical_issues = feedback.get('critical_issues', [])
    if critical_issues:
        st.markdown("### 🚨 Critical Issues")
        for issue in critical_issues:
            st.markdown(f"""
            <div class="danger-box">
                ❌ {issue}
            </div>
            """, unsafe_allow_html=True)
    
    # Improvements
    improvements = feedback.get('improvements', [])
    if improvements:
        st.markdown("### ⚠️ Recommended Improvements")
        for imp in improvements:
            st.markdown(f"""
            <div class="warning-box">
                ⚡ {imp}
            </div>
            """, unsafe_allow_html=True)
    
    # Suggestions
    suggestions = feedback.get('suggestions', [])
    if suggestions:
        st.markdown("### 💭 Suggestions")
        for sug in suggestions:
            st.markdown(f"""
            <div class="info-box">
                💡 {sug}
            </div>
            """, unsafe_allow_html=True)
    
    # Strong Points
    strong_points = feedback.get('strong_points', [])
    if strong_points:
        st.markdown("### ✅ Strong Points")
        for point in strong_points:
            st.markdown(f"""
            <div class="success-box">
                ✅ {point}
            </div>
            """, unsafe_allow_html=True)
    
    # Missing Keywords
    missing_keywords = feedback.get('missing_keywords', [])
    if missing_keywords:
        st.markdown("### 🔍 Missing Keywords from Job Description")
        st.write(f"**Keywords to add:** {', '.join(missing_keywords[:15])}")
        if len(missing_keywords) > 15:
            st.write(f"*...and {len(missing_keywords) - 15} more*")


def batch_analysis_tab():
    """Batch analysis tab content"""
    st.markdown("## 📚 Batch Resume Analysis")
    st.markdown("Upload multiple resumes to compare and rank candidates")
    
    # Job Description
    st.markdown("### Job Description")
    jd_text = st.text_area(
        "Paste the job description here:",
        height=200,
        placeholder="Enter the complete job description..."
    )
    
    # File upload
    st.markdown("### Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload multiple resume files (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True
    )
    
    if st.button("🚀 Analyze All Resumes", type="primary"):
        if not jd_text:
            st.error("⚠️ Please provide a job description")
            return
        
        if not uploaded_files:
            st.error("⚠️ Please upload at least one resume")
            return
        
        # Analyze all resumes
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, resume_file in enumerate(uploaded_files):
            status_text.text(f"Analyzing {resume_file.name}... ({idx + 1}/{len(uploaded_files)})")
            result = analyze_single_resume(resume_file, jd_text)
            if result:
                results.append(result)
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.empty()
        progress_bar.empty()
        
        if results:
            st.session_state.batch_results = results
            st.success(f"✅ Successfully analyzed {len(results)} resumes!")
            
            # Ranking
            st.markdown("---")
            st.markdown("## 🏆 Candidate Ranking")
            
            # Create ranking dataframe
            ranking_data = []
            for result in results:
                ranking_data.append({
                    'Candidate': result['resume_data'].get('name', 'N/A'),
                    'Filename': result['filename'],
                    'ATS Score': result['score_result']['final_score'],
                    'Grade': result['score_result']['grade'],
                    'Experience (Years)': sum([exp.get('duration_months', 0) for exp in result['resume_data'].get('experience', [])]) / 12,
                    'Skills Count': len(result['resume_data'].get('technical_skills', [])),
                    'Education': result['resume_data'].get('education_level', 'N/A')
                })
            
            df = pd.DataFrame(ranking_data)
            df = df.sort_values('ATS Score', ascending=False).reset_index(drop=True)
            df.index = df.index + 1
            
            # Display ranking table
            st.dataframe(
                df.style.background_gradient(subset=['ATS Score'], cmap='RdYlGn', vmin=0, vmax=100),
                use_container_width=True,
                height=400
            )
            
            # Ranking chart
            fig = px.bar(
                df,
                x='Candidate',
                y='ATS Score',
                color='Grade',
                title='Candidate Scores Comparison',
                text='ATS Score',
                color_discrete_map={
                    'A+': '#00b359', 'A': '#33cc33', 'A-': '#66ff66',
                    'B+': '#99ff99', 'B': '#ffff99', 'B-': '#ffcc66',
                    'C+': '#ff9933', 'C': '#ff6600', 'C-': '#ff3300',
                    'D': '#cc0000', 'F': '#990000'
                }
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Download results
            st.markdown("---")
            st.markdown("### 💾 Download Results")
            
            # Create CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Ranking (CSV)",
                data=csv,
                file_name=f"resume_ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Create JSON
            json_data = json.dumps([r['score_result'] for r in results], indent=2)
            st.download_button(
                label="📥 Download Detailed Results (JSON)",
                data=json_data,
                file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


def single_analysis_tab():
    """Single resume analysis tab content"""
    st.markdown("## 📄 Single Resume Analysis")
    st.markdown("Upload a resume and job description for detailed ATS analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Resume Upload")
        resume_file = st.file_uploader(
            "Upload resume file (PDF, DOCX, or TXT)",
            type=['pdf', 'docx', 'txt'],
            key="single_resume"
        )
    
    with col2:
        st.markdown("### Job Description")
        jd_text = st.text_area(
            "Paste the job description:",
            height=200,
            placeholder="Enter the complete job description...",
            key="single_jd"
        )
    
    if st.button("🎯 Analyze Resume", type="primary"):
        if not resume_file:
            st.error("⚠️ Please upload a resume")
            return
        
        if not jd_text:
            st.error("⚠️ Please provide a job description")
            return
        
        # Analyze
        with st.spinner("🔄 Analyzing resume..."):
            results = analyze_single_resume(resume_file, jd_text)
        
        if results:
            st.session_state.analysis_results = results
            st.success("✅ Analysis completed!")
            display_analysis_results(results)


def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📄 Resume Analyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered ATS Scoring & Resume Optimization Platform")
    st.markdown("*Created by [MAYANK SHARMA](https://mayankiitj.vercel.app)*")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/resume.png", width=100)
        st.markdown("## ⚙️ Settings")
        
        use_embeddings = st.checkbox("Use Advanced Embeddings", value=True, help="Use transformer-based embeddings for semantic similarity")
        
        if st.button("🔄 Reload Models"):
            st.session_state.scorer = ResumeScorer(use_embeddings=use_embeddings)
            st.session_state.extractor = ResumeExtractor()
            st.success("Models reloaded!")
        
        st.markdown("---")
        st.markdown("## 📊 About")
        st.markdown("""
        **Resume Analyzer Pro** uses advanced NLP and ML techniques to:
        - Parse PDF, DOCX, and TXT resumes
        - Extract structured data
        - Calculate ATS compatibility scores
        - Match candidates with job descriptions
        - Provide optimization feedback
        - Rank multiple candidates
        """)
        
        st.markdown("---")
        st.markdown("## 🚀 Features")
        st.markdown("""
        ✅ Multi-format parsing (98% accuracy)  
        ✅ ATS scoring (0-100)  
        ✅ Keyword extraction  
        ✅ Skills matching  
        ✅ Semantic similarity  
        ✅ Batch processing  
        ✅ Candidate ranking  
        ✅ Export reports (CSV/JSON)  
        """)
        
        st.markdown("---")
        st.markdown("## 👨‍💻 Created By")
        st.markdown("""
        **MAYANK SHARMA**
        
        🌐 [Portfolio](https://mayankiitj.vercel.app)  
        💼 [GitHub](https://github.com/Mayank-iitj)
        
        ---
        
        Made with ❤️ by [MAYANK SHARMA](https://mayankiitj.vercel.app)
        """)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📄 Single Analysis", "📚 Batch Analysis", "ℹ️ Help"])
    
    with tab1:
        single_analysis_tab()
    
    with tab2:
        batch_analysis_tab()
    
    with tab3:
        st.markdown("## 📖 How to Use")
        
        st.markdown("### Single Resume Analysis")
        st.markdown("""
        1. Upload a resume file (PDF, DOCX, or TXT)
        2. Paste the job description
        3. Click "Analyze Resume"
        4. Review the detailed analysis results
        """)
        
        st.markdown("### Batch Resume Analysis")
        st.markdown("""
        1. Paste the job description
        2. Upload multiple resume files
        3. Click "Analyze All Resumes"
        4. View the ranking and comparison
        5. Download results as CSV or JSON
        """)
        
        st.markdown("### Understanding ATS Scores")
        st.markdown("""
        - **90-100 (A+/A):** Excellent match - Highly recommended
        - **80-89 (A-/B+):** Very good match - Recommended
        - **70-79 (B/B-):** Good match - Consider
        - **60-69 (C+/C):** Fair match - Review carefully
        - **Below 60:** Poor match - Needs improvement
        """)
        
        st.markdown("### Score Components")
        st.markdown("""
        The ATS score is calculated using:
        - **Keyword Match (30%):** Resume-JD keyword overlap
        - **Skills Match (25%):** Technical skills alignment
        - **Experience Score (20%):** Years of relevant experience
        - **Semantic Similarity (15%):** Contextual meaning match
        - **Format Score (10%):** Resume structure and formatting
        """)


if __name__ == "__main__":
    main()
