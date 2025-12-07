#!/bin/bash
# Bash script to run Streamlit app
# Resume Analyzer - Streamlit Launch Script

echo "================================================================================"
echo "Resume Analyzer - Streamlit Web App"
echo "================================================================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[INFO] Activating virtual environment..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "[OK] Virtual environment activated"
    else
        echo "[ERROR] Virtual environment not found. Run install.sh first."
        exit 1
    fi
fi

# Check if Streamlit is installed
echo "[INFO] Checking Streamlit installation..."
streamlit_version=$(python -c "import streamlit; print(streamlit.__version__)" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "[INFO] Streamlit not found. Installing..."
    pip install streamlit plotly kaleido
    if [ $? -eq 0 ]; then
        echo "[OK] Streamlit installed successfully"
    else
        echo "[ERROR] Failed to install Streamlit"
        exit 1
    fi
else
    echo "[OK] Streamlit $streamlit_version found"
fi

# Create output directory
if [ ! -d "output" ]; then
    mkdir -p output
    echo "[OK] Created output directory"
fi

echo ""
echo "================================================================================"
echo "Starting Streamlit App..."
echo "================================================================================"
echo ""
echo "The app will open in your browser at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
streamlit run app.py
