# Resume Analyzer - Streamlit Web Application

## 🌟 Overview

The Resume Analyzer is now available as a **Streamlit web application** with a modern, interactive UI for ATS scoring, resume analysis, and candidate ranking.

## 🚀 Quick Start

### Windows (PowerShell)

```powershell
# Run the Streamlit app
.\run_streamlit.ps1
```

### Linux/Mac (Bash)

```bash
# Make the script executable
chmod +x run_streamlit.sh

# Run the Streamlit app
./run_streamlit.sh
```

### Manual Start

```bash
# Activate virtual environment
# Windows
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Install Streamlit dependencies (if not already installed)
pip install streamlit plotly kaleido

# Run the app
streamlit run app.py
```

The app will automatically open in your browser at: **http://localhost:8501**

## 📱 Features

### 1. **Single Resume Analysis**
- Upload one resume (PDF, DOCX, TXT)
- Paste job description
- Get detailed ATS score with interactive visualizations
- View score breakdown by component
- Get optimization feedback and suggestions
- See strong points and areas for improvement

### 2. **Batch Resume Analysis**
- Upload multiple resumes at once
- Compare and rank candidates
- Interactive ranking table with color-coded grades
- Export results as CSV or JSON
- Visual comparison charts

### 3. **Interactive Visualizations**
- **Score Gauge**: Real-time ATS score display
- **Component Breakdown**: Bar chart showing score components
- **Skills Distribution**: Pie chart of technical vs soft skills
- **Candidate Comparison**: Interactive ranking charts
- **Color-coded Metrics**: Easy-to-read performance indicators

## 🎯 Using the Web App

### Single Analysis Workflow

1. **Navigate to "Single Analysis" tab**
2. **Upload Resume**: Click "Browse files" and select your resume (PDF/DOCX/TXT)
3. **Paste Job Description**: Copy and paste the complete job description
4. **Click "Analyze Resume"**: Wait for processing (5-10 seconds)
5. **Review Results**:
   - ATS Score (0-100 with letter grade)
   - Score breakdown by component
   - Candidate information (name, email, experience)
   - Skills analysis
   - Optimization feedback
   - Missing keywords from JD

### Batch Analysis Workflow

1. **Navigate to "Batch Analysis" tab**
2. **Paste Job Description**: Enter the job description first
3. **Upload Multiple Resumes**: Select 2+ resume files
4. **Click "Analyze All Resumes"**: Wait for batch processing
5. **View Rankings**:
   - Sortable ranking table
   - Interactive comparison charts
   - Download results as CSV/JSON

## 📊 Understanding the Results

### ATS Score Ranges

| Score | Grade | Status | Recommendation |
|-------|-------|--------|----------------|
| 90-100 | A+/A | Excellent Match | Highly Recommended |
| 80-89 | A-/B+ | Very Good Match | Recommended |
| 70-79 | B/B- | Good Match | Consider |
| 60-69 | C+/C | Fair Match | Review Carefully |
| 0-59 | D/F | Poor Match | Needs Improvement |

### Score Components

The ATS score is calculated from 5 weighted components:

1. **Keyword Match (30%)**: Resume-JD keyword overlap using TF-IDF
2. **Skills Match (25%)**: Technical and soft skills alignment
3. **Experience Score (20%)**: Years of relevant experience
4. **Semantic Similarity (15%)**: Contextual meaning match (using embeddings)
5. **Format Score (10%)**: Resume structure and formatting quality

### Optimization Feedback Categories

- **🚨 Critical Issues**: Must-fix problems (missing contact info, no experience, etc.)
- **⚠️ Improvements**: Important enhancements (add metrics, action verbs, etc.)
- **💡 Suggestions**: Nice-to-have additions (certifications, GitHub, etc.)
- **✅ Strong Points**: What's already working well
- **🔍 Missing Keywords**: Important terms from JD not in resume

## 🎨 UI Features

### Interactive Elements

- **Score Gauge**: Live needle showing your ATS score
- **Color-coded Cards**: Visual hierarchy of information
- **Expandable Sections**: Organize detailed information
- **Download Buttons**: Export analysis as CSV/JSON
- **Progress Bars**: Real-time processing feedback
- **Sortable Tables**: Click column headers to sort rankings

### Responsive Design

- Works on desktop, tablet, and mobile
- Adaptive layouts for different screen sizes
- Touch-friendly buttons and controls

## 🔧 Configuration

### Streamlit Settings

Edit `.streamlit/config.toml` to customize:

```toml
[theme]
primaryColor = "#1f77b4"  # Main accent color
backgroundColor = "#ffffff"  # Page background
secondaryBackgroundColor = "#f0f2f6"  # Sidebar/card background
textColor = "#262730"  # Text color
font = "sans serif"  # Font family

[server]
port = 8501  # Port number
enableCORS = false  # CORS settings
```

### Model Settings

In the sidebar:
- **Use Advanced Embeddings**: Toggle semantic similarity (requires more RAM)
- **Reload Models**: Refresh ML models without restarting

## 🧠 Machine Learning Integration

### Training the ML Model

The app includes an optional ML model for enhanced resume classification:

```powershell
# Train the model
python train_model.py
```

This creates a Random Forest classifier trained on 1000 synthetic resumes, achieving ~85% accuracy.

### Using the ML Model

The ML model provides:
- **Resume Classification**: A/B/C/D grade prediction
- **Confidence Scores**: Probability for each class
- **Feature Importance**: Which factors matter most

To use in the app, the model will be automatically loaded if available in the `models/` directory.

## 📦 Dependencies

The Streamlit app requires these additional packages:

```txt
streamlit==1.29.0
plotly==5.18.0
kaleido==0.2.1
```

All other dependencies are already installed from the main `requirements.txt`.

## 🐛 Troubleshooting

### App Won't Start

```powershell
# Reinstall Streamlit
pip uninstall streamlit
pip install streamlit==1.29.0

# Clear Streamlit cache
streamlit cache clear
```

### Import Errors

```powershell
# Ensure all dependencies are installed
pip install -r requirements.txt

# Reinstall specific packages
pip install --upgrade plotly kaleido
```

### Port Already in Use

```powershell
# Use a different port
streamlit run app.py --server.port 8502
```

### Slow Performance

- Disable embeddings in the sidebar (uses less memory)
- Reduce batch size (analyze fewer resumes at once)
- Close other browser tabs

### Browser Doesn't Open

```powershell
# Manually open browser to:
http://localhost:8501
```

## 💾 Data Export

### Single Analysis Export

After analyzing a resume, download:
- **JSON**: Complete analysis data with all fields
- **PDF**: Formatted report (via CLI tool)

### Batch Analysis Export

After batch analysis, download:
- **CSV**: Ranking table with scores and metadata
- **JSON**: Detailed results for all candidates

## 🔒 Privacy & Security

- All processing is **local** - no data sent to external APIs
- Uploaded files are stored in **temporary memory** only
- Files are **automatically deleted** after processing
- No user data is logged or persisted

## 🎓 Best Practices

### For Best Results

1. **Use complete job descriptions** (500+ words)
2. **Upload high-quality PDFs** (not scanned images)
3. **Ensure resumes have clear structure** (sections, headings)
4. **Include all keywords from JD** in resume
5. **Review optimization feedback** and apply suggestions

### Performance Tips

1. **Single analysis** is faster than batch for 1-2 resumes
2. **Batch analysis** is efficient for 3+ resumes
3. **Disable embeddings** if you don't need semantic similarity
4. **Use smaller file sizes** for faster uploads

## 📚 Additional Resources

- **CLI Documentation**: See `README.md` for command-line usage
- **Architecture**: See `ARCHITECTURE.md` for system design
- **Quick Start**: See `QUICKSTART.md` for setup guide
- **API Reference**: See source code docstrings

## 🆘 Support

If you encounter issues:

1. Check the **console output** for error messages
2. Review this **README** for common solutions
3. Check **logs** in the Streamlit terminal
4. Verify all **dependencies** are installed
5. Try **restarting** the app

## 🚀 Next Steps

After setting up the Streamlit app:

1. **Train the ML model**: `python train_model.py`
2. **Test with sample data**: Use files in `data/sample_resumes/`
3. **Analyze your resumes**: Upload your own files
4. **Export results**: Download CSV/JSON reports
5. **Customize theme**: Edit `.streamlit/config.toml`

---

**Enjoy analyzing resumes with the modern web interface! 🎉**
