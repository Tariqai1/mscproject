"""
Prediction Service
Handles model loading, inference, and result caching
"""

import sys
from pathlib import Path
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# Suppress TensorFlow warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class PredictionService:
    """Service for making predictions using trained models"""
    
    def __init__(self):
        """Initialize the prediction service and load models"""
        self.model_dir = Path(__file__).parent.parent.parent / "ml_models" / "trained_models"
        self.models_loaded = False
        self.use_fallback = True  # Always use fallback to avoid import hangs
        
        # Model instances
        self.lr_svm_models = None
        self.lstm_model = None
        self.bert_trainer = None
        self.roberta_trainer = None
        self.hybrid_model = None
        
        print("Initializing prediction service (using fallback mode)")

    
    def load_models(self):
        """Load all trained models - disabled to prevent import hangs"""
        # Skipped to avoid torch/tensorflow import hangs
        # All predictions will use fallback rule-based model
        pass

    
    def predict(self, text):
        """
        Make prediction for given text
        
        Args:
            text (str): Review text to predict
        
        Returns:
            dict: Prediction results with sentiment, sarcasm, confidence
        """
        # Use best available model
        if self.models_loaded and self.lr_svm_models:
            return self._predict_with_lr_svm(text)
        elif self.models_loaded and self.lstm_model:
            return self._predict_with_lstm(text)
        elif self.models_loaded and self.bert_trainer:
            return self._predict_with_bert(text)
        else:
            return self._predict_fallback(text)
    
    def _predict_with_lr_svm(self, text):
        """Predict using LR/SVM models"""
        try:
            result = self.lr_svm_models.predict(text, use_svm=False)
            
            sentiment_label = ['Negative', 'Neutral', 'Positive'][result['sentiment']]
            sarcasm_label = 'Sarcastic' if result['sarcasm'] == 1 else 'Not Sarcastic'
            emotions = self._detect_emotions(text)
            
            return {
                'text': text,
                'sentiment': result['sentiment'],
                'sentiment_label': sentiment_label,
                'sentiment_confidence': result['sentiment_confidence'],
                'sarcasm': result['sarcasm'],
                'sarcasm_label': sarcasm_label,
                'sarcasm_confidence': result['sarcasm_confidence'],
                'emotions': emotions,
                'final_interpretation': sentiment_label + (' (Sarcastic)' if result['sarcasm'] == 1 else ''),
                'explanation': f"Sentiment: {sentiment_label} ({result['sentiment_confidence']*100:.1f}%), Sarcasm: {sarcasm_label} ({result['sarcasm_confidence']*100:.1f}%)",
                'overall_confidence': (result['sentiment_confidence'] * 0.6 + result['sarcasm_confidence'] * 0.4),
                'routing_model': 'Logistic Regression'
            }
        
        except Exception as e:
            print(f"Error in LR/SVM prediction: {e}")
            return self._predict_fallback(text)
    
    def _predict_with_lstm(self, text):
        """Predict using LSTM model"""
        try:
            result = self.lstm_model.predict(text)
            
            sentiment_label = ['Negative', 'Neutral', 'Positive'][result['sentiment']]
            sarcasm_label = 'Sarcastic' if result['sarcasm'] == 1 else 'Not Sarcastic'
            emotions = self._detect_emotions(text)
            
            return {
                'text': text,
                'sentiment': result['sentiment'],
                'sentiment_label': sentiment_label,
                'sentiment_confidence': result['sentiment_confidence'],
                'sarcasm': result['sarcasm'],
                'sarcasm_label': sarcasm_label,
                'sarcasm_confidence': result['sarcasm_confidence'],
                'emotions': emotions,
                'final_interpretation': sentiment_label + (' (Sarcastic)' if result['sarcasm'] == 1 else ''),
                'explanation': f"Sentiment: {sentiment_label} ({result['sentiment_confidence']*100:.1f}%), Sarcasm: {sarcasm_label} ({result['sarcasm_confidence']*100:.1f}%)",
                'overall_confidence': (result['sentiment_confidence'] * 0.6 + result['sarcasm_confidence'] * 0.4),
                'routing_model': 'LSTM'
            }
        
        except Exception as e:
            print(f"Error in LSTM prediction: {e}")
            return self._predict_fallback(text)
    
    def _predict_with_bert(self, text):
        """Predict using BERT model"""
        try:
            result = self.bert_trainer.predict(text)
            
            sentiment_label = ['Negative', 'Neutral', 'Positive'][result['sentiment']]
            sarcasm_label = 'Sarcastic' if result['sarcasm'] == 1 else 'Not Sarcastic'
            emotions = self._detect_emotions(text)
            
            return {
                'text': text,
                'sentiment': result['sentiment'],
                'sentiment_label': sentiment_label,
                'sentiment_confidence': result['sentiment_confidence'],
                'sarcasm': result['sarcasm'],
                'sarcasm_label': sarcasm_label,
                'sarcasm_confidence': result['sarcasm_confidence'],
                'emotions': emotions,
                'final_interpretation': sentiment_label + (' (Sarcastic)' if result['sarcasm'] == 1 else ''),
                'explanation': f"Sentiment: {sentiment_label} ({result['sentiment_confidence']*100:.1f}%), Sarcasm: {sarcasm_label} ({result['sarcasm_confidence']*100:.1f}%)",
                'overall_confidence': (result['sentiment_confidence'] * 0.6 + result['sarcasm_confidence'] * 0.4),
                'routing_model': 'BERT'
            }
        
        except Exception as e:
            print(f"Error in BERT prediction: {e}")
            return self._predict_fallback(text)
    
    def _detect_emotions(self, text):
        """
        Detect emotions in text using keyword-based analysis
        Returns emotion scores for: anger, joy, sadness, surprise, fear, disgust
        """
        text_lower = text.lower()
        
        # Comprehensive emotion keyword dictionaries
        emotion_keywords = {
            'joy': ['happy', 'joy', 'love', 'great', 'amazing', 'wonderful', 'fantastic', 'excellent', 
                    'awesome', 'delighted', 'thrilled', 'perfect', 'laugh', 'fun', 'enjoy', 'best', 
                    'beautiful', 'brilliant', 'excellent', 'fantastic', 'fabulous', 'splendid', 'great!', 'yes'],
            'sadness': ['sad', 'unhappy', 'disappointed', 'disappointed', 'depressed', 'down', 'miserable', 
                        'upset', 'heartbroken', 'lonely', 'terrible', 'awful', 'worst', 'hate', 'bad', 
                        'waste', 'useless', 'poor', 'horrible', 'dreadful', 'pathetic', 'regret', 'sorry'],
            'anger': ['angry', 'furious', 'rage', 'annoyed', 'irritated', 'frustrated', 'mad', 'livid', 
                      'outrageous', 'offensive', 'disgusting', 'terrible', 'awful', 'hate', 'despise', 
                      'infuriated', 'appalled', 'outraged', 'scathing'],
            'fear': ['afraid', 'scared', 'terrified', 'anxious', 'nervous', 'worried', 'panic', 
                     'frightened', 'horror', 'dread', 'alarmed', 'apprehensive', 'uneasy', 'concerned'],
            'surprise': ['surprised', 'amazed', 'shocked', 'astonished', 'stunned', 'unexpected', 
                        'wow', 'wow!', 'seriously', 'unbelievable', 'incredible', 'surprising'],
            'disgust': ['disgusting', 'gross', 'yuck', 'revolting', 'repulsive', 'vile', 'nauseating', 
                       'abominable', 'despicable', 'filthy', 'dirty', 'foul', 'repugnant']
        }
        
        # Calculate emotion scores
        emotion_scores = {}
        max_matches = 0
        
        for emotion, keywords in emotion_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = matches
            max_matches = max(max_matches, matches)
        
        # Normalize emotion scores to 0-1 range
        if max_matches > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] = min(1.0, emotion_scores[emotion] / max(max_matches, 1))
        else:
            # Default neutral emotions if no keywords detected
            for emotion in emotion_scores:
                emotion_scores[emotion] = 0.1
        
        return emotion_scores
    
    def _predict_fallback(self, text):
        """Fallback prediction when models aren't available"""
        # Simple rule-based fallback
        text_lower = text.lower()
        
        # Detect sentiment from keywords
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'perfect', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'poor', 'horrible', 'waste']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 2
            sentiment_label = 'Positive'
            sentiment_conf = 0.75
        elif negative_count > positive_count:
            sentiment = 0
            sentiment_label = 'Negative'
            sentiment_conf = 0.75
        else:
            sentiment = 1
            sentiment_label = 'Neutral'
            sentiment_conf = 0.6
        
        # Detect sarcasm from markers
        sarcasm_markers = ['yeah right', 'sure', 'great...', 'brilliant...', 'love it when', 'NOT!', '...', '😒', '🙄']
        sarcasm = 1 if any(marker in text_lower for marker in sarcasm_markers) else 0
        sarcasm_label = 'Sarcastic' if sarcasm == 1 else 'Not Sarcastic'
        sarcasm_conf = 0.65 if sarcasm == 1 else 0.65
        
        # Detect emotions
        emotions = self._detect_emotions(text)
        
        return {
            'text': text,
            'sentiment': sentiment,
            'sentiment_label': sentiment_label,
            'sentiment_confidence': sentiment_conf,
            'sarcasm': sarcasm,
            'sarcasm_label': sarcasm_label,
            'sarcasm_confidence': sarcasm_conf,
            'emotions': emotions,
            'final_interpretation': sentiment_label + (' (Sarcastic)' if sarcasm == 1 else ''),
            'explanation': f"Using fallback model. Sentiment: {sentiment_label}, Sarcasm: {sarcasm_label}",
            'overall_confidence': 0.65,
            'routing_model': 'Fallback Rule-Based'
        }


if __name__ == "__main__":
    # Test the service
    service = PredictionService()
    
    test_reviews = [
        "This product is amazing!",
        "Absolutely terrible quality",
        "Yeah, this is great... for a doorstop!",
        "It's okay, nothing special",
        "Best purchase ever!"
    ]
    
    print("\nTesting Prediction Service:\n")
    for review in test_reviews:
        result = service.predict(review)
        print(f"Review: {review}")
        print(f"   Sentiment: {result['sentiment_label']} ({result['sentiment_confidence']:.2%})")
        print(f"   Sarcasm: {result['sarcasm_label']} ({result['sarcasm_confidence']:.2%})")
        print()
