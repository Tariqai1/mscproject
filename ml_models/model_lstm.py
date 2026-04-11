"""
LSTM Model for Sentiment and Sarcasm Detection
Using TensorFlow/Keras with embedding layer and bidirectional LSTM
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
import json

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib


class LSTMSentimentSarcasmModel:
    """
    Bidirectional LSTM model for dual task: sentiment + sarcasm detection
    Uses shared embedding layer with separate output heads
    """
    
    def __init__(self, vocab_size=10000, max_length=128, embedding_dim=100):
        self.vocab_size = vocab_size
        self.max_length = max_length
        self.embedding_dim = embedding_dim
        self.tokenizer = None
        self.model = None
        self.history = None
    
    def build_model(self):
        """
        Build LSTM model with dual outputs
        """
        # Input layer
        inputs = layers.Input(shape=(self.max_length,), dtype=tf.int32)
        
        # Embedding layer
        x = layers.Embedding(
            input_dim=self.vocab_size,
            output_dim=self.embedding_dim,
            name='embedding'
        )(inputs)
        
        # Dropout for regularization
        x = layers.Dropout(0.2)(x)
        
        # Bidirectional LSTM
        lstm_out = layers.Bidirectional(
            layers.LSTM(128, return_sequences=False, dropout=0.2)
        )(x)
        
        # Dense layer
        dense = layers.Dense(64, activation='relu')(lstm_out)
        dense = layers.Dropout(0.3)(dense)
        
        # ===== SENTIMENT OUTPUT HEAD =====
        sentiment_dense = layers.Dense(32, activation='relu')(dense)
        sentiment_output = layers.Dense(
            3,  # 3 classes: negative, neutral, positive
            activation='softmax',
            name='sentiment_output'
        )(sentiment_dense)
        
        # ===== SARCASM OUTPUT HEAD =====
        sarcasm_dense = layers.Dense(16, activation='relu')(dense)
        sarcasm_output = layers.Dense(
            1,  # Binary classification
            activation='sigmoid',
            name='sarcasm_output'
        )(sarcasm_dense)
        
        # Create model
        self.model = models.Model(
            inputs=inputs,
            outputs=[sentiment_output, sarcasm_output]
        )
        
        print(f"✅ Model built successfully")
        print(f"   Vocab size: {self.vocab_size}")
        print(f"   Max sequence length: {self.max_length}")
        print(f"   Embedding dim: {self.embedding_dim}")
        print(f"   LSTM units: 128 (bidirectional = 256)")
    
    def prepare_texts(self, texts):
        """
        Prepare texts using tokenizer
        """
        if self.tokenizer is None:
            self.tokenizer = Tokenizer(num_words=self.vocab_size)
            self.tokenizer.fit_on_texts(texts)
        
        sequences = self.tokenizer.texts_to_sequences(texts)
        padded = pad_sequences(sequences, maxlen=self.max_length, padding='post')
        
        return padded
    
    def compile_model(self):
        """
        Compile model with appropriate loss functions
        """
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss={
                'sentiment_output': 'categorical_crossentropy',
                'sarcasm_output': 'binary_crossentropy'
            },
            loss_weights={
                'sentiment_output': 1.0,
                'sarcasm_output': 0.8
            },
            metrics={
                'sentiment_output': 'accuracy',
                'sarcasm_output': 'accuracy'
            }
        )
        print(f"✅ Model compiled with dual losses")
    
    def train(self, X_train, y_sentiment_train, y_sarcasm_train,
              X_val=None, y_sentiment_val=None, y_sarcasm_val=None,
              epochs=10, batch_size=32):
        """
        Train the model
        """
        print(f"\n🔄 Training LSTM Model...")
        print(f"  Training samples: {len(X_train)}")
        if X_val is not None:
            print(f"  Validation samples: {len(X_val)}")
        print(f"  Epochs: {epochs}, Batch size: {batch_size}\n")
        
        # Prepare data
        X_train_padded = self.prepare_texts(X_train)
        
        # Convert sentiment to one-hot (3 classes)
        y_sentiment_train_encoded = keras.utils.to_categorical(y_sentiment_train, 3)
        
        # Reshape sarcasm to (n, 1) for binary crossentropy
        y_sarcasm_train_encoded = np.array(y_sarcasm_train).reshape(-1, 1)
        
        # Prepare validation data if provided
        validation_data = None
        if X_val is not None:
            X_val_padded = self.prepare_texts(X_val)
            y_sentiment_val_encoded = keras.utils.to_categorical(y_sentiment_val, 3)
            y_sarcasm_val_encoded = np.array(y_sarcasm_val).reshape(-1, 1)
            
            validation_data = (
                X_val_padded,
                {
                    'sentiment_output': y_sentiment_val_encoded,
                    'sarcasm_output': y_sarcasm_val_encoded
                }
            )
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss' if validation_data else 'loss',
            patience=3,
            restore_best_weights=True
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss' if validation_data else 'loss',
            factor=0.5,
            patience=2,
            min_lr=1e-5,
            verbose=1
        )
        
        # Train
        self.history = self.model.fit(
            X_train_padded,
            {
                'sentiment_output': y_sentiment_train_encoded,
                'sarcasm_output': y_sarcasm_train_encoded
            },
            batch_size=batch_size,
            epochs=epochs,
            validation_data=validation_data,
            callbacks=[early_stopping, reduce_lr],
            verbose=1
        )
        
        print(f"\n✅ Training complete!")
        
        return self.history
    
    def evaluate(self, X_test, y_sentiment_test, y_sarcasm_test, set_name="Test"):
        """
        Evaluate the model
        """
        print(f"\n📊 Evaluation on {set_name} Set:")
        print("=" * 60)
        
        X_test_padded = self.prepare_texts(X_test)
        
        # Predictions
        sentiment_probs, sarcasm_probs = self.model.predict(X_test_padded, verbose=0)
        y_sentiment_pred = np.argmax(sentiment_probs, axis=1)
        y_sarcasm_pred = (sarcasm_probs.flatten() > 0.5).astype(int)
        
        results = {}
        
        # ===== SENTIMENT METRICS =====
        print("\n🎯 SENTIMENT DETECTION:")
        sentiment_acc = accuracy_score(y_sentiment_test, y_sentiment_pred)
        print(f"  Accuracy: {sentiment_acc:.4f}")
        print(f"  Precision: {precision_score(y_sentiment_test, y_sentiment_pred, average='weighted', zero_division=0):.4f}")
        print(f"  Recall: {recall_score(y_sentiment_test, y_sentiment_pred, average='weighted', zero_division=0):.4f}")
        print(f"  F1-Score: {f1_score(y_sentiment_test, y_sentiment_pred, average='weighted', zero_division=0):.4f}")
        
        results['sentiment'] = {
            'accuracy': float(sentiment_acc),
            'precision': float(precision_score(y_sentiment_test, y_sentiment_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_sentiment_test, y_sentiment_pred, average='weighted', zero_division=0)),
            'f1': float(f1_score(y_sentiment_test, y_sentiment_pred, average='weighted', zero_division=0))
        }
        
        # ===== SARCASM METRICS =====
        print("\n🎭 SARCASM DETECTION:")
        sarcasm_acc = accuracy_score(y_sarcasm_test, y_sarcasm_pred)
        print(f"  Accuracy: {sarcasm_acc:.4f}")
        print(f"  Precision: {precision_score(y_sarcasm_test, y_sarcasm_pred, zero_division=0):.4f}")
        print(f"  Recall: {recall_score(y_sarcasm_test, y_sarcasm_pred, zero_division=0):.4f}")
        print(f"  F1-Score: {f1_score(y_sarcasm_test, y_sarcasm_pred, zero_division=0):.4f}")
        
        results['sarcasm'] = {
            'accuracy': float(sarcasm_acc),
            'precision': float(precision_score(y_sarcasm_test, y_sarcasm_pred, zero_division=0)),
            'recall': float(recall_score(y_sarcasm_test, y_sarcasm_pred, zero_division=0)),
            'f1': float(f1_score(y_sarcasm_test, y_sarcasm_pred, zero_division=0))
        }
        
        print("\n" + "=" * 60)
        
        return results
    
    def save_model(self, model_dir):
        """
        Save model and tokenizer
        """
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        self.model.save(model_dir / "lstm_model.h5")
        
        # Save tokenizer
        joblib.dump(self.tokenizer, model_dir / "lstm_tokenizer.joblib")
        
        # Save model config
        config = {
            'vocab_size': self.vocab_size,
            'max_length': self.max_length,
            'embedding_dim': self.embedding_dim
        }
        with open(model_dir / "lstm_config.json", 'w') as f:
            json.dump(config, f)
        
        print(f"✅ Model saved to {model_dir}")
    
    @staticmethod
    def load_model(model_dir):
        """
        Load saved model and tokenizer
        """
        model_dir = Path(model_dir)
        
        # Load config
        with open(model_dir / "lstm_config.json", 'r') as f:
            config = json.load(f)
        
        # Create and load model
        obj = LSTMSentimentSarcasmModel(
            vocab_size=config['vocab_size'],
            max_length=config['max_length'],
            embedding_dim=config['embedding_dim']
        )
        
        obj.model = keras.models.load_model(model_dir / "lstm_model.h5")
        obj.tokenizer = joblib.load(model_dir / "lstm_tokenizer.joblib")
        
        return obj
    
    def predict(self, text):
        """
        Predict sentiment and sarcasm for a single text
        """
        X_padded = self.prepare_texts([text])
        
        sentiment_probs, sarcasm_probs = self.model.predict(X_padded, verbose=0)
        
        sentiment_pred = np.argmax(sentiment_probs[0])
        sentiment_confidence = float(np.max(sentiment_probs[0]))
        
        sarcasm_pred = int(sarcasm_probs[0][0] > 0.5)
        sarcasm_confidence = float(sarcasm_probs[0][0])
        
        return {
            'sentiment': sentiment_pred,
            'sentiment_confidence': sentiment_confidence,
            'sarcasm': sarcasm_pred,
            'sarcasm_confidence': sarcasm_confidence
        }


def main():
    """
    Main function to train and evaluate LSTM model
    """
    print("🚀 Training LSTM Model\n")
    
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
    
    # Split train into train and validation (80-20)
    from sklearn.model_selection import train_test_split
    train_texts, val_texts, train_sentiments, val_sentiments, train_sarcasm, val_sarcasm = train_test_split(
        train_df['text'],
        train_df['sentiment'],
        train_df['has_sarcasm'],
        test_size=0.2,
        random_state=42,
        stratify=train_df[['sentiment', 'has_sarcasm']]
    )
    
    print(f"  ✓ Train split: {len(train_texts)} (train), {len(val_texts)} (val)")
    
    # Initialize model
    print(f"\n🔨 Building LSTM Model...")
    model = LSTMSentimentSarcasmModel(
        vocab_size=10000,
        max_length=128,
        embedding_dim=100
    )
    
    model.build_model()
    model.compile_model()
    
    # Train model
    print(f"\n📊 Model Architecture:")
    model.model.summary()
    
    model.train(
        train_texts.values,
        train_sentiments.values,
        train_sarcasm.values,
        X_val=val_texts.values,
        y_sentiment_val=val_sentiments.values,
        y_sarcasm_val=val_sarcasm.values,
        epochs=10,
        batch_size=32
    )
    
    # Evaluate on test set
    test_results = model.evaluate(
        test_df['text'].values,
        test_df['sentiment'].values,
        test_df['has_sarcasm'].values,
        "Test"
    )
    
    # Save model
    model.save_model(model_dir)
    
    # Save results
    with open(model_dir / "lstm_results.json", 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n✅ Training complete!")
    print(f"   Model saved in: {model_dir}")
    print(f"   Results saved in: {model_dir / 'lstm_results.json'}")
    
    return model


if __name__ == "__main__":
    model = main()
