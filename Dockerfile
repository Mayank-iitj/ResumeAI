FROM python:3.11-slim

# Core env + fast startup toggle (set FAST_MODE=false for full features)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FAST_MODE=true

WORKDIR /app

# Install deps separately for better Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm \
    && python -c "try:\n from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')\nexcept Exception as e: print(e)"

# Copy source after deps to avoid invalidating heavy layers on code change
COPY . .

EXPOSE 8501

# Streamlit performance flags: disable stats & watcher for leaner runtime
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.headless=true", "--server.fileWatcherType=none", "--browser.gatherUsageStats=false"]
