# Streamlit Deployment Configuration

This Resume Analyzer app is **completely standalone** and does NOT require:
- ❌ MySQL or any database
- ❌ External API keys
- ❌ Authentication systems
- ❌ Environment variables

## ✅ What You Need to Deploy

1. **Just the code** - Upload this entire repository to GitHub
2. **Streamlit Cloud** - Connect your GitHub repo
3. **Python 3.8+** - That's it!

## 🚀 Deploy to Streamlit Cloud

### Step 1: Ensure Correct Repository

Make sure you're deploying from:
```
https://github.com/Mayank-iitj/ResumeAI
```

**NOT** from any other repository like `ai-resume-analyzer`

### Step 2: Configure Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select repository: `Mayank-iitj/ResumeAI`
4. Set main file path: `app.py`
5. Click "Deploy"

### Step 3: That's It!

No additional configuration needed. The app will:
- ✅ Install dependencies from `requirements.txt`
- ✅ Download ML models automatically
- ✅ Run completely in-memory (no database)

## ❌ Common Deployment Errors

### Error: "pymysql.err.OperationalError: localhost connection failed"

**Cause:** You deployed the wrong repository that has database code

**Solution:** 
1. Delete the current deployment
2. Deploy from `Mayank-iitj/ResumeAI` instead
3. Make sure `app.py` is the main file (not `App/App.py`)

### Error: "No module named 'streamlit'"

**Cause:** Dependencies not installed

**Solution:** Ensure `requirements.txt` exists and is correctly formatted

### Error: Models downloading too slowly

**Cause:** Sentence transformers model is large (~80MB)

**Solution:** 
- First deploy will take 2-3 minutes
- Subsequent starts will be faster (cached)
- Optionally disable embeddings in sidebar to skip model download

## 🔒 Privacy & Security

This app:
- ✅ Processes all data **locally** (in Streamlit Cloud's container)
- ✅ Does NOT store any resumes or data
- ✅ Does NOT send data to external APIs
- ✅ Automatically clears uploaded files after processing
- ✅ No user data persistence between sessions

## 📊 Resource Requirements

**Streamlit Cloud Free Tier:**
- ✅ CPU: Sufficient (single-threaded processing)
- ✅ Memory: ~1GB needed (should work on free tier)
- ✅ Storage: Minimal (~200MB with models)

**Tips for Free Tier:**
- Disable embeddings to reduce memory usage
- Process one resume at a time
- Limit batch analysis to <5 resumes

## 🐛 Troubleshooting

### App crashes or runs out of memory

1. In Streamlit Cloud dashboard:
   - Click "Manage app"
   - Restart the app
   - Check resource usage

2. In the app sidebar:
   - Uncheck "Use Advanced Embeddings"
   - This reduces memory by ~500MB

### Slow performance

- First upload is slow (downloading models)
- Subsequent requests are faster
- Consider upgrading to Streamlit Cloud paid tier for better performance

## 🔄 Updating the App

After pushing changes to GitHub:
1. Streamlit Cloud auto-detects changes
2. App redeploys automatically (~2-3 minutes)
3. No manual steps needed!

## 📞 Support

If you encounter issues not listed here:
1. Check Streamlit Cloud logs ("Manage app" → "Logs")
2. Ensure you're using Python 3.8+
3. Verify all files from this repository are deployed
4. Contact: https://mayankiitj.vercel.app

---

**Made by [MAYANK SHARMA](https://mayankiitj.vercel.app)**
