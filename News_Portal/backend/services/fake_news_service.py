"""
Fake News Detection System using ML models
Supports: Logistic Regression, Naive Bayes, Random Forest
"""
import pickle
import os
import re
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

from config import Config


class FakeNewsDetector:
    """Fake news detection using multiple ML models"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        self.models = {
            'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
            'naive_bayes': MultinomialNB(),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        }
        self.trained_model = None
        self.model_type = 'logistic_regression'  # Default model
        self.load_model()
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for model"""
        if not text:
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def prepare_features(self, article: Dict[str, Any]) -> str:
        """Prepare text features from article"""
        title = article.get('title', '') or ''
        description = article.get('description', '') or ''
        content = article.get('content', '') or ''
        text = f"{title} {description} {content}".strip()
        return self.preprocess_text(text)
    
    def train_model(
        self,
        texts: List[str],
        labels: List[int],
        model_type: str = 'logistic_regression',
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """
        Train a fake news detection model
        labels: 0 = real, 1 = fake
        """
        if not texts or not labels:
            raise ValueError("Texts and labels cannot be empty")
        
        if model_type not in self.models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        try:
            # Preprocess texts
            processed_texts = [self.preprocess_text(text) for text in texts]
            
            # Vectorize
            X = self.vectorizer.fit_transform(processed_texts)
            y = np.array(labels)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # Train model
            self.model_type = model_type
            self.trained_model = self.models[model_type]
            self.trained_model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.trained_model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            # Save model
            self.save_model()
            
            return {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'model_type': model_type
            }
            
        except Exception as e:
            print(f"Error training model: {e}")
            raise
    
    def predict(self, article: Dict[str, Any]) -> Tuple[str, float]:
        """
        Predict if article is fake or real
        Returns: ('real' or 'fake', confidence_score)
        """
        if not self.trained_model:
            # Return default prediction if model not trained
            return ('unknown', 0.5)
        
        try:
            # Prepare text
            text = self.prepare_features(article)
            if not text:
                return ('unknown', 0.5)
            
            # Vectorize
            text_vector = self.vectorizer.transform([text])
            
            # Predict
            prediction = self.trained_model.predict(text_vector)[0]
            probabilities = self.trained_model.predict_proba(text_vector)[0]
            
            # Get confidence (probability of predicted class)
            confidence = float(max(probabilities))
            
            result = 'fake' if prediction == 1 else 'real'
            
            return (result, confidence)
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return ('unknown', 0.5)
    
    def predict_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict for multiple articles"""
        results = []
        for article in articles:
            prediction, confidence = self.predict(article)
            results.append({
                'article': article,
                'prediction': prediction,
                'confidence': confidence,
                'fake_news_score': confidence if prediction == 'fake' else (1 - confidence)
            })
        return results
    
    def save_model(self):
        """Save the trained model and vectorizer"""
        if not self.trained_model:
            return
        
        Config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.trained_model,
            'vectorizer': self.vectorizer,
            'model_type': self.model_type
        }
        
        with open(Config.FAKE_NEWS_MODEL_PATH, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self):
        """Load a saved model"""
        if os.path.exists(Config.FAKE_NEWS_MODEL_PATH):
            try:
                with open(Config.FAKE_NEWS_MODEL_PATH, 'rb') as f:
                    model_data = pickle.load(f)
                    self.trained_model = model_data['model']
                    self.vectorizer = model_data['vectorizer']
                    self.model_type = model_data.get('model_type', 'logistic_regression')
            except Exception as e:
                print(f"Error loading model: {e}")
                self.trained_model = None


# Global instance
fake_news_detector = FakeNewsDetector()


def create_sample_training_data():
    """
    Create sample training data for demonstration
    In production, use real dataset from Kaggle Fake News
    """
    # Sample real news (label = 0)
    real_samples = [
        "Scientists discover new planet in habitable zone with potential for life.",
        "Global economy shows steady growth in Q3 with positive indicators.",
        "New medical breakthrough in cancer treatment shows promising results.",
        "Tech company announces revolutionary AI technology for healthcare.",
        "International peace summit ends with historic agreement signed."
    ]
    
    # Sample fake news (label = 1) - exaggerated or false claims
    fake_samples = [
        "BREAKING: Aliens land in New York and take control of the government!",
        "Secret cure for all diseases discovered but hidden by pharmaceutical companies!",
        "Scientists prove that Earth is flat and NASA has been lying all along!",
        "One simple trick doctors don't want you to know cures cancer instantly!",
        "Government mind control chips hidden in vaccines exposed by whistleblower!"
    ]
    
    texts = real_samples + fake_samples
    labels = [0] * len(real_samples) + [1] * len(fake_samples)
    
    return texts, labels

