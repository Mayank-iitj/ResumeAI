"""
Training Script for Resume ML Model
Run this script to train the machine learning model
"""
import logging
from ml_model import train_resume_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    print("""
================================================================================
Resume Analyzer - ML Model Training
================================================================================

This script will train a machine learning model for resume classification.
The model will be trained on synthetic data to classify resumes into grades:
- A: Excellent (85-100)
- B: Good (70-84)
- C: Fair (55-69)
- D: Poor (0-54)

Training Configuration:
- Samples: 1000 synthetic resumes
- Model: Random Forest Classifier
- Features: 13 extracted features
- Cross-validation: 5-fold

Starting training...
""")
    
    # Train the model
    model, results = train_resume_model(n_samples=1000, model_type="random_forest")
    
    print(f"""
================================================================================
Training Summary
================================================================================

Model Performance:
  • Accuracy: {results['accuracy']:.1%}
  • F1 Score: {results['f1_score']:.3f}
  • CV Mean F1: {results['cv_scores'].mean():.3f}
  • CV Std: {results['cv_scores'].std():.3f}

Model saved to: models/

The trained model can now be used in the Streamlit app and CLI tool.

To use the model:
  1. Run the Streamlit app: streamlit run app.py
  2. Or use the CLI: python analyzer.py --resume <file> --jd <file> --use-ml

Next steps:
  • Test the model with real resumes
  • Fine-tune hyperparameters if needed
  • Collect real training data for improved accuracy

================================================================================
""")
