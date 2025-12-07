"""
Machine Learning Model for Resume Analysis
Train and use ML models for improved resume scoring and classification
"""
import os
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

logger = logging.getLogger(__name__)


class ResumeMLModel:
    """
    Machine Learning model for resume classification and scoring
    """
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.classifier = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        
        self.is_trained = False
        self.model_path = self.model_dir / "resume_classifier.pkl"
        self.scaler_path = self.model_dir / "scaler.pkl"
        self.encoder_path = self.model_dir / "label_encoder.pkl"
        self.vectorizer_path = self.model_dir / "tfidf_vectorizer.pkl"
    
    def extract_features(self, resume_data: Dict, jd_text: str = "") -> np.ndarray:
        """
        Extract numerical features from resume data for ML model
        
        Args:
            resume_data: Extracted resume data
            jd_text: Job description text (optional)
        
        Returns:
            Feature array
        """
        features = []
        
        # Basic features
        features.append(len(resume_data.get('technical_skills', [])))  # Technical skills count
        features.append(len(resume_data.get('soft_skills', [])))  # Soft skills count
        
        # Experience features
        experiences = resume_data.get('experience', [])
        total_months = sum([exp.get('duration_months', 0) for exp in experiences])
        features.append(total_months / 12)  # Total years of experience
        features.append(len(experiences))  # Number of positions
        
        # Education features
        education = resume_data.get('education', [])
        features.append(len(education))  # Number of degrees
        
        # Education level encoding
        education_level = resume_data.get('education_level', 'Bachelor')
        education_encoding = {
            'High School': 1,
            'Associate': 2,
            'Bachelor': 3,
            'Master': 4,
            'PhD': 5,
            'Doctorate': 5
        }
        features.append(education_encoding.get(education_level, 3))
        
        # Projects and certifications
        features.append(len(resume_data.get('projects', [])))
        features.append(len(resume_data.get('certifications', [])))
        
        # Contact info completeness
        contact_score = 0
        if resume_data.get('email'): contact_score += 1
        if resume_data.get('phone'): contact_score += 1
        if resume_data.get('linkedin'): contact_score += 1
        if resume_data.get('github'): contact_score += 1
        features.append(contact_score)
        
        # Resume length (character count)
        resume_text = resume_data.get('raw_text', '')
        features.append(len(resume_text))
        
        # Word count
        features.append(len(resume_text.split()))
        
        # If JD provided, add matching features
        if jd_text:
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Simple keyword overlap
            resume_words = set(resume_text.lower().split())
            jd_words = set(jd_text.lower().split())
            overlap = len(resume_words & jd_words)
            features.append(overlap)
            
            # Skills match with JD
            all_skills = resume_data.get('technical_skills', []) + resume_data.get('soft_skills', [])
            jd_lower = jd_text.lower()
            skills_in_jd = sum([1 for skill in all_skills if skill.lower() in jd_lower])
            features.append(skills_in_jd)
        else:
            features.append(0)  # No JD overlap
            features.append(0)  # No skills match
        
        return np.array(features).reshape(1, -1)
    
    def prepare_training_data(self, resumes_data: List[Dict], labels: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from resume datasets
        
        Args:
            resumes_data: List of extracted resume data dictionaries
            labels: List of labels (e.g., 'hire', 'reject', 'A', 'B', 'C')
        
        Returns:
            X (features), y (encoded labels)
        """
        X_list = []
        
        for resume_data in resumes_data:
            features = self.extract_features(resume_data)
            X_list.append(features.flatten())
        
        X = np.array(X_list)
        y = self.label_encoder.fit_transform(labels)
        
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray, model_type: str = "random_forest"):
        """
        Train the ML model
        
        Args:
            X: Feature matrix
            y: Labels
            model_type: Type of model ('random_forest', 'gradient_boosting', 'logistic')
        """
        logger.info(f"Training {model_type} model with {len(X)} samples...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Select and train model
        if model_type == "random_forest":
            self.classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "gradient_boosting":
            self.classifier = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == "logistic":
            self.classifier = LogisticRegression(
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train
        self.classifier.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        logger.info(f"Model trained! Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred, target_names=self.label_encoder.classes_))
        
        # Cross-validation
        cv_scores = cross_val_score(self.classifier, X_train_scaled, y_train, cv=5, scoring='f1_weighted')
        logger.info(f"Cross-validation F1 scores: {cv_scores}")
        logger.info(f"Mean CV F1: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        self.is_trained = True
        
        return {
            'accuracy': accuracy,
            'f1_score': f1,
            'cv_scores': cv_scores,
            'classification_report': classification_report(y_test, y_pred, target_names=self.label_encoder.classes_, output_dict=True)
        }
    
    def predict(self, resume_data: Dict, jd_text: str = "") -> Dict:
        """
        Predict resume class and probability
        
        Args:
            resume_data: Extracted resume data
            jd_text: Job description (optional)
        
        Returns:
            Dictionary with prediction and probabilities
        """
        if not self.is_trained and not self.load_model():
            raise RuntimeError("Model not trained. Please train or load a model first.")
        
        # Extract features
        features = self.extract_features(resume_data, jd_text)
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.classifier.predict(features_scaled)[0]
        probabilities = self.classifier.predict_proba(features_scaled)[0]
        
        # Decode prediction
        predicted_class = self.label_encoder.inverse_transform([prediction])[0]
        
        # Create probability dictionary
        prob_dict = {}
        for idx, class_name in enumerate(self.label_encoder.classes_):
            prob_dict[class_name] = float(probabilities[idx])
        
        return {
            'predicted_class': predicted_class,
            'confidence': float(max(probabilities)),
            'probabilities': prob_dict
        }
    
    def save_model(self):
        """Save trained model and preprocessing objects"""
        if not self.is_trained:
            logger.warning("Model not trained yet. Nothing to save.")
            return
        
        joblib.dump(self.classifier, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        joblib.dump(self.label_encoder, self.encoder_path)
        
        logger.info(f"Model saved to {self.model_dir}")
    
    def load_model(self) -> bool:
        """Load trained model and preprocessing objects"""
        try:
            if not self.model_path.exists():
                logger.warning(f"Model file not found: {self.model_path}")
                return False
            
            self.classifier = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            self.label_encoder = joblib.load(self.encoder_path)
            
            self.is_trained = True
            logger.info(f"Model loaded from {self.model_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


class SyntheticDataGenerator:
    """
    Generate synthetic training data for resume classification
    """
    
    @staticmethod
    def generate_synthetic_resumes(n_samples: int = 1000) -> Tuple[List[Dict], List[str]]:
        """
        Generate synthetic resume data for training
        
        Args:
            n_samples: Number of samples to generate
        
        Returns:
            List of resume data dictionaries and labels
        """
        np.random.seed(42)
        
        resumes_data = []
        labels = []
        
        education_levels = ['Bachelor', 'Master', 'PhD', 'Associate']
        education_weights = [0.5, 0.3, 0.1, 0.1]
        
        for i in range(n_samples):
            # Generate random features
            num_technical_skills = np.random.randint(5, 50)
            num_soft_skills = np.random.randint(0, 10)
            years_experience = np.random.uniform(0, 20)
            num_positions = max(1, int(years_experience / 2.5) + np.random.randint(-1, 2))
            education_level = np.random.choice(education_levels, p=education_weights)
            num_projects = np.random.randint(0, 25)
            num_certifications = np.random.randint(0, 15)
            
            # Create resume data
            resume_data = {
                'name': f'Candidate {i}',
                'email': f'candidate{i}@email.com',
                'phone': '+1234567890',
                'linkedin': 'linkedin.com/in/candidate' if np.random.random() > 0.3 else '',
                'github': 'github.com/candidate' if np.random.random() > 0.5 else '',
                'technical_skills': [f'Skill{j}' for j in range(num_technical_skills)],
                'soft_skills': [f'SoftSkill{j}' for j in range(num_soft_skills)],
                'experience': [
                    {'duration_months': int(years_experience * 12 / max(1, num_positions))}
                    for _ in range(num_positions)
                ],
                'education': [{'degree': education_level}],
                'education_level': education_level,
                'projects': [f'Project{j}' for j in range(num_projects)],
                'certifications': [f'Cert{j}' for j in range(num_certifications)],
                'raw_text': f'Resume text with {np.random.randint(500, 2000)} characters'
            }
            
            # Determine label based on features (create realistic distribution)
            score = 0
            score += min(num_technical_skills / 30, 1) * 25  # Skills contribution
            score += min(years_experience / 10, 1) * 25  # Experience contribution
            score += {'Associate': 0.5, 'Bachelor': 0.7, 'Master': 0.9, 'PhD': 1.0}[education_level] * 20  # Education
            score += min(num_projects / 15, 1) * 15  # Projects
            score += min(num_certifications / 10, 1) * 15  # Certifications
            
            # Add some randomness
            score += np.random.normal(0, 10)
            score = max(0, min(100, score))
            
            # Assign grade
            if score >= 85:
                label = 'A'
            elif score >= 70:
                label = 'B'
            elif score >= 55:
                label = 'C'
            else:
                label = 'D'
            
            resumes_data.append(resume_data)
            labels.append(label)
        
        logger.info(f"Generated {n_samples} synthetic resumes")
        logger.info(f"Label distribution: {pd.Series(labels).value_counts().to_dict()}")
        
        return resumes_data, labels


def train_resume_model(n_samples: int = 1000, model_type: str = "random_forest"):
    """
    Train a resume classification model with synthetic data
    
    Args:
        n_samples: Number of synthetic samples to generate
        model_type: Type of model to train
    """
    logger.info("=" * 80)
    logger.info("Resume ML Model Training")
    logger.info("=" * 80)
    
    # Generate synthetic data
    logger.info(f"\n[1/4] Generating {n_samples} synthetic resumes...")
    generator = SyntheticDataGenerator()
    resumes_data, labels = generator.generate_synthetic_resumes(n_samples)
    
    # Initialize model
    logger.info("\n[2/4] Initializing ML model...")
    model = ResumeMLModel()
    
    # Prepare data
    logger.info("\n[3/4] Preparing training data...")
    X, y = model.prepare_training_data(resumes_data, labels)
    logger.info(f"Feature matrix shape: {X.shape}")
    logger.info(f"Labels shape: {y.shape}")
    
    # Train model
    logger.info(f"\n[4/4] Training {model_type} model...")
    results = model.train(X, y, model_type=model_type)
    
    # Save model
    model.save_model()
    
    logger.info("\n" + "=" * 80)
    logger.info("Training Complete!")
    logger.info("=" * 80)
    logger.info(f"Final Accuracy: {results['accuracy']:.3f}")
    logger.info(f"Final F1 Score: {results['f1_score']:.3f}")
    logger.info(f"Model saved to: {model.model_dir}")
    
    return model, results


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Train model with different configurations
    print("\nTraining Random Forest Model...")
    train_resume_model(n_samples=1000, model_type="random_forest")
    
    print("\n" + "="*80)
    print("Training complete! Model ready for use.")
    print("="*80)
