"""
Logistic Regression and SVM Models for Sentiment and Sarcasm Detection
Using sklearn with TF-IDF vectorizer
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
import pickle
import json

class SentimentSarcasmModels:
    """
    Logistic Regression and SVM models for dual task: sentiment + sarcasm detection
    """
    
    def __init__(self):
        self.vectorizer_sentiment = None
        self.vectorizer_sarcasm = None
        self.lr_sentiment = None
        self.lr_sarcasm = None
        self.svm_sentiment = None
        self.svm_sarcasm = None
        self.results = {}
    
    def train_models(self, X_text, y_sentiment, y_sarcasm):
        """
        Train both sentiment and sarcasm models
        
        Args:
            X_text: Text samples (Series or list)
            y_sentiment: Sentiment labels (0=neg, 1=neutral, 2=pos)
            y_sarcasm: Sarcasm labels (0=no sarcasm, 1=sarcasm)
        """
        print("🔄 Training Logistic Regression and SVM models...\n")
        
        # Convert to strings if needed
        X_text = [str(x) for x in X_text]
        
        # ===== SENTIMENT MODELS =====
        print("📊 Training Sentiment Models...")
        
        # Vectorize for sentiment
        self.vectorizer_sentiment = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        X_tfidf_sentiment = self.vectorizer_sentiment.fit_transform(X_text)
        print(f"  ✓ TF-IDF features for sentiment: {X_tfidf_sentiment.shape[1]}")
        
        # Train Logistic Regression for sentiment
        print(f"  Training Logistic Regression...")
        self.lr_sentiment = LogisticRegression(
            max_iter=1000,
            random_state=42,
            multi_class='multinomial',
            solver='lbfgs'
        )
        self.lr_sentiment.fit(X_tfidf_sentiment, y_sentiment)
        print(f"  ✓ LR Sentiment trained")
        
        # Train SVM for sentiment
        print(f"  Training SVM...")
        self.svm_sentiment = SVC(
            kernel='rbf',
            probability=True,
            random_state=42
        )
        self.svm_sentiment.fit(X_tfidf_sentiment, y_sentiment)
        print(f"  ✓ SVM Sentiment trained")
        
        # ===== SARCASM MODELS =====
        print(f"\n📊 Training Sarcasm Models...")
        
        # Vectorize for sarcasm
        self.vectorizer_sarcasm = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        X_tfidf_sarcasm = self.vectorizer_sarcasm.fit_transform(X_text)
        print(f"  ✓ TF-IDF features for sarcasm: {X_tfidf_sarcasm.shape[1]}")
        
        # Train Logistic Regression for sarcasm
        print(f"  Training Logistic Regression...")
        self.lr_sarcasm = LogisticRegression(
            max_iter=1000,
            random_state=42
        )
        self.lr_sarcasm.fit(X_tfidf_sarcasm, y_sarcasm)
        print(f"  ✓ LR Sarcasm trained")
        
        # Train SVM for sarcasm
        print(f"  Training SVM...")
        self.svm_sarcasm = SVC(
            kernel='rbf',
            probability=True,
            random_state=42
        )
        self.svm_sarcasm.fit(X_tfidf_sarcasm, y_sarcasm)
        print(f"  ✓ SVM Sarcasm trained")
        
        print(f"\n✅ All models trained!")
    
    def evaluate(self, X_text, y_sentiment, y_sarcasm, model_name="Test"):
        """
        Evaluate all models
        """
        X_text = [str(x) for x in X_text]
        
        print(f"\n📊 Evaluation on {model_name} Set:")
        print("=" * 60)
        
        # Sentiment predictions
        X_tfidf_sentiment = self.vectorizer_sentiment.transform(X_text)
        y_pred_lr_sentiment = self.lr_sentiment.predict(X_tfidf_sentiment)
        y_pred_svm_sentiment = self.svm_sentiment.predict(X_tfidf_sentiment)
        
        # Sarcasm predictions
        X_tfidf_sarcasm = self.vectorizer_sarcasm.transform(X_text)
        y_pred_lr_sarcasm = self.lr_sarcasm.predict(X_tfidf_sarcasm)
        y_pred_svm_sarcasm = self.svm_sarcasm.predict(X_tfidf_sarcasm)
        
        results = {}
        
        # ===== SENTIMENT RESULTS =====
        print("\n🎯 SENTIMENT DETECTION:")
        print("-" * 60)
        
        # LR Sentiment
        print("\n📈 Logistic Regression (Sentiment):")
        lr_sentiment_acc = accuracy_score(y_sentiment, y_pred_lr_sentiment)
        print(f"  Accuracy: {lr_sentiment_acc:.4f}")
        print(f"  Precision: {precision_score(y_sentiment, y_pred_lr_sentiment, average='weighted'):.4f}")
        print(f"  Recall: {recall_score(y_sentiment, y_pred_lr_sentiment, average='weighted'):.4f}")
        print(f"  F1-Score: {f1_score(y_sentiment, y_pred_lr_sentiment, average='weighted'):.4f}")
        
        results['lr_sentiment'] = {
            'accuracy': float(lr_sentiment_acc),
            'precision': float(precision_score(y_sentiment, y_pred_lr_sentiment, average='weighted')),
            'recall': float(recall_score(y_sentiment, y_pred_lr_sentiment, average='weighted')),
            'f1': float(f1_score(y_sentiment, y_pred_lr_sentiment, average='weighted'))
        }
        
        # SVM Sentiment
        print("\n🎯 SVM (Sentiment):")
        svm_sentiment_acc = accuracy_score(y_sentiment, y_pred_svm_sentiment)
        print(f"  Accuracy: {svm_sentiment_acc:.4f}")
        print(f"  Precision: {precision_score(y_sentiment, y_pred_svm_sentiment, average='weighted'):.4f}")
        print(f"  Recall: {recall_score(y_sentiment, y_pred_svm_sentiment, average='weighted'):.4f}")
        print(f"  F1-Score: {f1_score(y_sentiment, y_pred_svm_sentiment, average='weighted'):.4f}")
        
        results['svm_sentiment'] = {
            'accuracy': float(svm_sentiment_acc),
            'precision': float(precision_score(y_sentiment, y_pred_svm_sentiment, average='weighted')),
            'recall': float(recall_score(y_sentiment, y_pred_svm_sentiment, average='weighted')),
            'f1': float(f1_score(y_sentiment, y_pred_svm_sentiment, average='weighted'))
        }
        
        # ===== SARCASM RESULTS =====
        print("\n\n🎯 SARCASM DETECTION:")
        print("-" * 60)
        
        # LR Sarcasm
        print("\n📈 Logistic Regression (Sarcasm):")
        lr_sarcasm_acc = accuracy_score(y_sarcasm, y_pred_lr_sarcasm)
        print(f"  Accuracy: {lr_sarcasm_acc:.4f}")
        print(f"  Precision: {precision_score(y_sarcasm, y_pred_lr_sarcasm, average='weighted'):.4f}")
        print(f"  Recall: {recall_score(y_sarcasm, y_pred_lr_sarcasm, average='weighted'):.4f}")
        print(f"  F1-Score: {f1_score(y_sarcasm, y_pred_lr_sarcasm, average='weighted'):.4f}")
        
        results['lr_sarcasm'] = {
            'accuracy': float(lr_sarcasm_acc),
            'precision': float(precision_score(y_sarcasm, y_pred_lr_sarcasm, average='weighted')),
            'recall': float(recall_score(y_sarcasm, y_pred_lr_sarcasm, average='weighted')),
            'f1': float(f1_score(y_sarcasm, y_pred_lr_sarcasm, average='weighted'))
        }
        
        # SVM Sarcasm
        print("\n🎯 SVM (Sarcasm):")
        svm_sarcasm_acc = accuracy_score(y_sarcasm, y_pred_svm_sarcasm)
        print(f"  Accuracy: {svm_sarcasm_acc:.4f}")
        print(f"  Precision: {precision_score(y_sarcasm, y_pred_svm_sarcasm, average='weighted'):.4f}")
        print(f"  Recall: {recall_score(y_sarcasm, y_pred_svm_sarcasm, average='weighted'):.4f}")
        print(f"  F1-Score: {f1_score(y_sarcasm, y_pred_svm_sarcasm, average='weighted'):.4f}")
        
        results['svm_sarcasm'] = {
            'accuracy': float(svm_sarcasm_acc),
            'precision': float(precision_score(y_sarcasm, y_pred_svm_sarcasm, average='weighted')),
            'recall': float(recall_score(y_sarcasm, y_pred_svm_sarcasm, average='weighted')),
            'f1': float(f1_score(y_sarcasm, y_pred_svm_sarcasm, average='weighted'))
        }
        
        print("\n" + "=" * 60)
        
        return results
    
    def save_models(self, model_dir):
        """
        Save all trained models
        """
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save models
        joblib.dump(self.lr_sentiment, model_dir / "lr_sentiment.joblib")
        joblib.dump(self.svm_sentiment, model_dir / "svm_sentiment.joblib")
        joblib.dump(self.lr_sarcasm, model_dir / "lr_sarcasm.joblib")
        joblib.dump(self.svm_sarcasm, model_dir / "svm_sarcasm.joblib")
        
        # Save vectorizers
        joblib.dump(self.vectorizer_sentiment, model_dir / "vectorizer_sentiment.joblib")
        joblib.dump(self.vectorizer_sarcasm, model_dir / "vectorizer_sarcasm.joblib")
        
        print(f"✅ Models saved to {model_dir}")
    
    @staticmethod
    def load_models(model_dir):
        """
        Load trained models
        """
        model_dir = Path(model_dir)
        
        obj = SentimentSarcasmModels()
        
        obj.lr_sentiment = joblib.load(model_dir / "lr_sentiment.joblib")
        obj.svm_sentiment = joblib.load(model_dir / "svm_sentiment.joblib")
        obj.lr_sarcasm = joblib.load(model_dir / "lr_sarcasm.joblib")
        obj.svm_sarcasm = joblib.load(model_dir / "svm_sarcasm.joblib")
        
        obj.vectorizer_sentiment = joblib.load(model_dir / "vectorizer_sentiment.joblib")
        obj.vectorizer_sarcasm = joblib.load(model_dir / "vectorizer_sarcasm.joblib")
        
        return obj
    
    def predict(self, text, use_svm=False):
        """
        Predict sentiment and sarcasm for a single text
        """
        X_text = [str(text)]
        
        # Sentiment
        X_sentiment = self.vectorizer_sentiment.transform(X_text)
        if use_svm:
            sentiment_pred = self.svm_sentiment.predict(X_text)[0]
            sentiment_proba = self.svm_sentiment.predict_proba(X_text)[0]
        else:
            sentiment_pred = self.lr_sentiment.predict(X_sentiment)[0]
            sentiment_proba = self.lr_sentiment.predict_proba(X_sentiment)[0]
        
        # Sarcasm
        X_sarcasm = self.vectorizer_sarcasm.transform(X_text)
        if use_svm:
            sarcasm_pred = self.svm_sarcasm.predict(X_text)[0]
            sarcasm_proba = self.svm_sarcasm.predict_proba(X_text)[0]
        else:
            sarcasm_pred = self.lr_sarcasm.predict(X_sarcasm)[0]
            sarcasm_proba = self.lr_sarcasm.predict_proba(X_sarcasm)[0]
        
        return {
            'sentiment': sentiment_pred,
            'sentiment_confidence': float(max(sentiment_proba)),
            'sarcasm': sarcasm_pred,
            'sarcasm_confidence': float(max(sarcasm_proba))
        }


def main():
    """
    Main function to train and evaluate LR and SVM models
    """
    print("🚀 Training Logistic Regression and SVM Models\n")
    
    # Define paths
    data_dir = Path(__file__).parent.parent / "data"
    train_path = data_dir / "processed" / "train.csv"
    test_path = data_dir / "processed" / "test.csv"
    model_dir = Path(__file__).parent / "trained_models"
    
    # Check if data exists
    if not train_path.exists():
        print(f"❌ Training data not found: {train_path}")
        print("   Please run data_generation.py first")
        return
    
    # Load datasets
    print(f"📂 Loading datasets...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    print(f"  ✓ Train: {len(train_df)} samples")
    print(f"  ✓ Test: {len(test_df)} samples")
    
    # Initialize models
    models = SentimentSarcasmModels()
    
    # Train models
    print(f"\n🔄 Training models on training set...")
    models.train_models(
        train_df['text'],
        train_df['sentiment'],
        train_df['has_sarcasm']
    )
    
    # Evaluate on training set
    train_results = models.evaluate(
        train_df['text'],
        train_df['sentiment'],
        train_df['has_sarcasm'],
        "Training"
    )
    
    # Evaluate on test set
    test_results = models.evaluate(
        test_df['text'],
        test_df['sentiment'],
        test_df['has_sarcasm'],
        "Test"
    )
    
    # Save models
    models.save_models(model_dir)
    
    # Save results
    all_results = {
        'train': train_results,
        'test': test_results
    }
    
    with open(model_dir / "lr_svm_results.json", 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✅ Training complete!")
    print(f"   Models saved in: {model_dir}")
    print(f"   Results saved in: {model_dir / 'lr_svm_results.json'}")
    
    return models


if __name__ == "__main__":
    models = main()
