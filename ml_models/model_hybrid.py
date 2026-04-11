"""
Hybrid Two-Stage Model for Advanced Sarcasm-Aware Sentiment Analysis
Stage 1: BERT detects sarcasm (binary classification)
Stage 2: Routes to appropriate sentiment model based on sarcasm detection
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import torch

# Import model classes
try:
    from model_bert import BERTTrainer
except ImportError:
    print("⚠️ Warning: Could not import BERT model")

try:
    from model_lr_svm import SentimentSarcasmModels
except ImportError:
    print("⚠️ Warning: Could not import LR/SVM models")

try:
    from model_lstm import LSTMSentimentSarcasmModel
except ImportError:
    print("⚠️ Warning: Could not import LSTM model")


class HybridTwoStageModel:
    """
    Hybrid Two-Stage Sarcasm-Aware Sentiment Analysis System
    
    Stage 1: Sarcasm Detection (using BERT)
    - Binary classification: is_sarcastic (0/1)
    
    Stage 2a: If NO SARCASM detected → Use Logistic Regression (fast, sufficient)
    Stage 2b: If SARCASM detected → Use RoBERTa (more accurate for complex cases)
    """
    
    def __init__(self, sarcasm_model=None, sentiment_model_no_sarcasm=None, 
                 sentiment_model_sarcasm=None):
        """
        Initialize hybrid model with component models
        
        Args:
            sarcasm_model: BERT-based sarcasm detector
            sentiment_model_no_sarcasm: LR/SVM for non-sarcastic reviews
            sentiment_model_sarcasm: LSTM/RoBERTa for sarcastic reviews
        """
        self.sarcasm_model = sarcasm_model
        self.sentiment_model_no_sarcasm = sentiment_model_no_sarcasm
        self.sentiment_model_sarcasm = sentiment_model_sarcasm
        
        self.stats = {
            'total_predictions': 0,
            'sarcasm_detected': 0,
            'non_sarcasm_detected': 0,
            'avg_confidence': 0.0
        }
    
    def predict(self, text):
        """
        Predict sentiment and sarcasm using hybrid approach
        
        Args:
            text (str): Review text
        
        Returns:
            Dict with sentiment, sarcasm, confidence, explanation, routing_info
        """
        self.stats['total_predictions'] += 1
        
        # ===== STAGE 1: Sarcasm Detection =====
        sarcasm_pred = self.sarcasm_model.predict(text)
        sarcasm_label = sarcasm_pred['sarcasm']
        sarcasm_confidence = sarcasm_pred['sarcasm_confidence']
        
        # ===== STAGE 2: Route to appropriate sentiment model =====
        if sarcasm_label == 1:  # Sarcasm detected
            self.stats['sarcasm_detected'] += 1
            
            # Use specialized sarcasm-aware model (RoBERTa)
            if self.sentiment_model_sarcasm:
                sentiment_pred = self.sentiment_model_sarcasm.predict(text)
                routing = "RoBERTa (Sarcasm-specialized)"
            else:
                sentiment_pred = self.sentiment_model_no_sarcasm.predict(text)
                routing = "LR (Fallback - no sarcasm model available)"
        
        else:  # No sarcasm
            self.stats['non_sarcasm_detected'] += 1
            
            # Use fast, sufficient model (LR)
            sentiment_pred = self.sentiment_model_no_sarcasm.predict(text)
            routing = "Logistic Regression (Fast)"
        
        # ===== Combine results =====
        sentiment_label = sentiment_pred['sentiment']
        sentiment_confidence = sentiment_pred['sentiment_confidence']
        
        # Adjust sentiment interpretation if sarcasm detected
        interpretation = self._interpret_prediction(
            sentiment_label,
            sarcasm_label,
            sentiment_confidence,
            sarcasm_confidence
        )
        
        result = {
            'text': text,
            'sentiment': sentiment_label,  # 0=negative, 1=neutral, 2=positive
            'sentiment_label': ['Negative', 'Neutral', 'Positive'][sentiment_label],
            'sentiment_confidence': float(sentiment_confidence),
            'sarcasm': sarcasm_label,  # 0=no sarcasm, 1=sarcasm
            'sarcasm_label': 'Sarcastic' if sarcasm_label == 1 else 'Not Sarcastic',
            'sarcasm_confidence': float(sarcasm_confidence),
            'final_interpretation': interpretation,
            'routing_model': routing,
            'overall_confidence': float(
                (sentiment_confidence * 0.6 + sarcasm_confidence * 0.4)
            ),
            'explanation': self._generate_explanation(
                sentiment_label, sarcasm_label, sentiment_confidence, sarcasm_confidence
            )
        }
        
        return result
    
    def _interpret_prediction(self, sentiment, sarcasm, sent_conf, sarc_conf):
        """
        Interpret prediction considering sarcasm
        """
        if sarcasm == 0:  # No sarcasm
            return ['Negative', 'Neutral', 'Positive'][sentiment]
        else:  # Sarcasm detected
            # When sarcasm is high confidence, likely opposite meaning
            if sarc_conf > 0.7:
                if sentiment == 0:  # Predicted negative but sarcastic → actually positive
                    return 'Positive (Sarcastic)'
                elif sentiment == 2:  # Predicted positive but sarcastic → actually negative
                    return 'Negative (Sarcastic)'
                else:
                    return 'Unclear (Sarcastic Neutral)'
            else:
                return ['Negative', 'Neutral', 'Positive'][sentiment]
    
    def _generate_explanation(self, sentiment, sarcasm, sent_conf, sarc_conf):
        """Generate human-readable explanation"""
        explanations = []
        
        # Sentiment explanation
        sentiment_text = ['negative', 'neutral', 'positive'][sentiment]
        explanations.append(f"Predicted sentiment: {sentiment_text} ({sent_conf*100:.1f}%)")
        
        # Sarcasm explanation
        if sarcasm == 1:
            explanations.append(f"⚠️ Sarcasm detected ({sarc_conf*100:.1f}%)")
            if sarc_conf > 0.7:
                opposite = ['positive', 'neutral', 'negative'][sentiment]
                explanations.append(f"→ Likely actual sentiment: {opposite}")
        else:
            explanations.append(f"No sarcasm detected ({(1-sarc_conf)*100:.1f}% confidence)")
        
        return " | ".join(explanations)
    
    def batch_predict(self, texts):
        """
        Predict for multiple texts
        
        Args:
            texts (list): List of review texts
        
        Returns:
            List of prediction dictionaries
        """
        predictions = []
        for text in texts:
            pred = self.predict(text)
            predictions.append(pred)
        
        return predictions
    
    def evaluate(self, texts, true_sentiments, true_sarcasms, set_name="Test"):
        """
        Evaluate hybrid model
        """
        print(f"\n📊 Evaluation on {set_name} Set (Hybrid Model):")
        print("=" * 70)
        
        predictions = self.batch_predict(texts)
        
        pred_sentiments = [p['sentiment'] for p in predictions]
        pred_sarcasms = [p['sarcasm'] for p in predictions]
        
        # ===== SENTIMENT METRICS =====
        print("\n🎯 SENTIMENT DETECTION:")
        sent_acc = accuracy_score(true_sentiments, pred_sentiments)
        sent_prec = precision_score(true_sentiments, pred_sentiments, average='weighted', zero_division=0)
        sent_rec = recall_score(true_sentiments, pred_sentiments, average='weighted', zero_division=0)
        sent_f1 = f1_score(true_sentiments, pred_sentiments, average='weighted', zero_division=0)
        
        print(f"  Accuracy: {sent_acc:.4f}")
        print(f"  Precision: {sent_prec:.4f}")
        print(f"  Recall: {sent_rec:.4f}")
        print(f"  F1-Score: {sent_f1:.4f}")
        
        # ===== SARCASM METRICS =====
        print("\n🎭 SARCASM DETECTION:")
        sarc_acc = accuracy_score(true_sarcasms, pred_sarcasms)
        sarc_prec = precision_score(true_sarcasms, pred_sarcasms, average='weighted', zero_division=0)
        sarc_rec = recall_score(true_sarcasms, pred_sarcasms, average='weighted', zero_division=0)
        sarc_f1 = f1_score(true_sarcasms, pred_sarcasms, average='weighted', zero_division=0)
        
        print(f"  Accuracy: {sarc_acc:.4f}")
        print(f"  Precision: {sarc_prec:.4f}")
        print(f"  Recall: {sarc_rec:.4f}")
        print(f"  F1-Score: {sarc_f1:.4f}")
        
        # Statistics
        print("\n📈 ROUTING STATISTICS:")
        print(f"  Sarcasm Detected: {self.stats['sarcasm_detected']} ({self.stats['sarcasm_detected']/self.stats['total_predictions']*100:.1f}%)")
        print(f"  Non-sarcasm: {self.stats['non_sarcasm_detected']} ({self.stats['non_sarcasm_detected']/self.stats['total_predictions']*100:.1f}%)")
        
        print("\n" + "=" * 70)
        
        results = {
            'sentiment': {
                'accuracy': float(sent_acc),
                'precision': float(sent_prec),
                'recall': float(sent_rec),
                'f1': float(sent_f1)
            },
            'sarcasm': {
                'accuracy': float(sarc_acc),
                'precision': float(sarc_prec),
                'recall': float(sarc_rec),
                'f1': float(sarc_f1)
            },
            'routing_stats': {
                'sarcasm_detected': int(self.stats['sarcasm_detected']),
                'non_sarcasm': int(self.stats['non_sarcasm_detected'])
            }
        }
        
        return results
    
    def save_config(self, model_dir):
        """Save hybrid model configuration"""
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'model_type': 'hybrid_two_stage',
            'description': 'Stage 1: BERT sarcasm detection → Stage 2: Route to LR (no sarcasm) or RoBERTa (sarcasm)',
            'components': {
                'stage_1': 'BERT (Sarcasm Detection)',
                'stage_2a': 'Logistic Regression (Non-sarcastic reviews)',
                'stage_2b': 'RoBERTa/LSTM (Sarcastic reviews)'
            }
        }
        
        with open(model_dir / 'hybrid_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Hybrid config saved to {model_dir / 'hybrid_config.json'}")


def main():
    """
    Main function: Demo hybrid model (architecture only, requires trained components)
    """
    print("🚀 Hybrid Two-Stage Sarcasm-Aware Sentiment Analysis Model\n")
    print("=" * 70)
    print("Architecture:")
    print("  Stage 1: BERT → Sarcasm Detection (Binary)")
    print("  Stage 2a: Logistic Regression → Sentiment (if NO sarcasm)")
    print("  Stage 2b: RoBERTa → Sentiment (if SARCASM detected)")
    print("=" * 70)
    
    print("\n⚠️ Note: This is the hybrid model architecture.")
    print("   To use it, train individual models first:")
    print("   1. python model_bert.py")
    print("   2. python model_lr_svm.py")
    print("   3. python model_roberta.py")
    print("   Then load all components and create HybridTwoStageModel instance.")
    
    # Example (pseudocode - requires trained models):
    # hybrid = HybridTwoStageModel(
    #     sarcasm_model=bert_sarcasm,
    #     sentiment_model_no_sarcasm=lr_model,
    #     sentiment_model_sarcasm=roberta_model
    # )
    # result = hybrid.predict("This product is great... for a doorstop!")
    # print(result)


if __name__ == "__main__":
    main()
