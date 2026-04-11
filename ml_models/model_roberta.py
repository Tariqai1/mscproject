"""
RoBERTa Model for Sentiment and Sarcasm Detection
Uses Hugging Face Transformers (RoBERTa for better performance)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel, AdamW
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

import warnings
warnings.filterwarnings('ignore')


class RobertaDataset(Dataset):
    """Custom Dataset for RoBERTa model"""
    
    def __init__(self, texts, sentiments, sarcasms, tokenizer, max_length=128):
        self.texts = texts
        self.sentiments = sentiments
        self.sarcasms = sarcasms
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts.iloc[idx]) if hasattr(self.texts, 'iloc') else str(self.texts[idx])
        
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'sentiment': torch.tensor(self.sentiments[idx], dtype=torch.long),
            'sarcasm': torch.tensor(self.sarcasms[idx], dtype=torch.long)
        }


class RoBERTaSentimentSarcasmModel(nn.Module):
    """RoBERTa model with dual outputs for sentiment and sarcasm"""
    
    def __init__(self, model_name='roberta-base'):
        super().__init__()
        
        self.roberta = AutoModel.from_pretrained(model_name)
        hidden_size = self.roberta.config.hidden_size
        
        # Sentiment classifier
        self.sentiment_classifier = nn.Sequential(
            nn.Linear(hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 3)  # 3 sentiment classes
        )
        
        # Sarcasm classifier
        self.sarcasm_classifier = nn.Sequential(
            nn.Linear(hidden_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 2)  # Binary sarcasm classification
        )
    
    def forward(self, input_ids, attention_mask):
        outputs = self.roberta(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Use [CLS] token representation
        cls_output = outputs.last_hidden_state[:, 0, :]
        
        # Sentiment prediction
        sentiment_logits = self.sentiment_classifier(cls_output)
        
        # Sarcasm prediction
        sarcasm_logits = self.sarcasm_classifier(cls_output)
        
        return sentiment_logits, sarcasm_logits


class RoBERTATrainer:
    """Trainer for RoBERTa model"""
    
    def __init__(self, model_name='roberta-base', device='cpu'):
        self.model_name = model_name
        self.device = device
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = RoBERTaSentimentSarcasmModel(model_name).to(device)
        
        print(f"✅ RoBERTa Model initialized: {model_name}")
        print(f"   Device: {device}")
    
    def prepare_dataloader(self, texts, sentiments, sarcasms, batch_size=16, shuffle=True):
        """Prepare DataLoader"""
        dataset = RobertaDataset(
            texts, sentiments, sarcasms,
            self.tokenizer,
            max_length=128
        )
        
        return DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=0
        )
    
    def train_epoch(self, train_loader, optimizer, sentiment_loss_fn, sarcasm_loss_fn):
        """Train one epoch"""
        self.model.train()
        total_loss = 0
        
        for batch in tqdm(train_loader, desc="Training"):
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            sentiments = batch['sentiment'].to(self.device)
            sarcasms = batch['sarcasm'].to(self.device)
            
            sentiment_logits, sarcasm_logits = self.model(input_ids, attention_mask)
            
            loss_sentiment = sentiment_loss_fn(sentiment_logits, sentiments)
            loss_sarcasm = sarcasm_loss_fn(sarcasm_logits, sarcasms)
            
            loss = loss_sentiment * 0.6 + loss_sarcasm * 0.4
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def evaluate(self, val_loader):
        """Evaluate model"""
        self.model.eval()
        
        sentiment_preds = []
        sarcasm_preds = []
        sentiment_trues = []
        sarcasm_trues = []
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Evaluating"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                sentiment_logits, sarcasm_logits = self.model(input_ids, attention_mask)
                
                sentiment_preds.extend(sentiment_logits.argmax(dim=1).cpu().numpy())
                sarcasm_preds.extend(sarcasm_logits.argmax(dim=1).cpu().numpy())
                sentiment_trues.extend(batch['sentiment'].numpy())
                sarcasm_trues.extend(batch['sarcasm'].numpy())
        
        return sentiment_preds, sarcasm_preds, sentiment_trues, sarcasm_trues
    
    def train(self, train_texts, train_sentiments, train_sarcasms,
              val_texts=None, val_sentiments=None, val_sarcasms=None,
              epochs=2, batch_size=16, learning_rate=2e-5):
        """Train the model"""
        print(f"\n🔄 Training RoBERTa Model...")
        print(f"  Epochs: {epochs}, Batch size: {batch_size}, LR: {learning_rate}\n")
        
        train_loader = self.prepare_dataloader(
            train_texts, train_sentiments, train_sarcasms,
            batch_size=batch_size
        )
        
        val_loader = None
        if val_texts is not None:
            val_loader = self.prepare_dataloader(
                val_texts, val_sentiments, val_sarcasms,
                batch_size=batch_size, shuffle=False
            )
        
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        sentiment_loss_fn = nn.CrossEntropyLoss()
        sarcasm_loss_fn = nn.CrossEntropyLoss()
        
        for epoch in range(epochs):
            print(f"\nEpoch {epoch + 1}/{epochs}")
            
            train_loss = self.train_epoch(
                train_loader, optimizer,
                sentiment_loss_fn, sarcasm_loss_fn
            )
            
            print(f"  Training Loss: {train_loss:.4f}")
            
            if val_loader:
                sent_preds, sarc_preds, sent_trues, sarc_trues = self.evaluate(val_loader)
                
                sent_acc = accuracy_score(sent_trues, sent_preds)
                sarc_acc = accuracy_score(sarc_trues, sarc_preds)
                
                print(f"  Val Sentiment Accuracy: {sent_acc:.4f}")
                print(f"  Val Sarcasm Accuracy: {sarc_acc:.4f}")
        
        print(f"\n✅ Training complete!")
    
    def save_model(self, model_dir):
        """Save model and tokenizer"""
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        self.model.roberta.save_pretrained(model_dir / "roberta_sentiment_sarcasm")
        self.tokenizer.save_pretrained(model_dir / "roberta_sentiment_sarcasm")
        torch.save(self.model.state_dict(), model_dir / "roberta_full_state.pt")
        
        print(f"✅ Model saved to {model_dir}")
    
    def predict(self, text):
        """Predict sentiment and sarcasm"""
        self.model.eval()
        
        encoding = self.tokenizer(
            text,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        ).to(self.device)
        
        with torch.no_grad():
            sent_logits, sarc_logits = self.model(
                encoding['input_ids'],
                encoding['attention_mask']
            )
        
        sentiment_pred = sent_logits.argmax(dim=1).item()
        sentiment_conf = torch.softmax(sent_logits, dim=1).max().item()
        
        sarcasm_pred = sarc_logits.argmax(dim=1).item()
        sarcasm_conf = torch.softmax(sarc_logits, dim=1).max().item()
        
        return {
            'sentiment': sentiment_pred,
            'sentiment_confidence': float(sentiment_conf),
            'sarcasm': sarcasm_pred,
            'sarcasm_confidence': float(sarcasm_conf)
        }


def main():
    """Main function"""
    print("🚀 Training RoBERTa Model\n")
    
    data_dir = Path(__file__).parent.parent / "data"
    train_path = data_dir / "processed" / "train.csv"
    test_path = data_dir / "processed" / "test.csv"
    model_dir = Path(__file__).parent / "trained_models"
    
    if not train_path.exists():
        print(f"❌ Training data not found: {train_path}")
        return
    
    # Check for GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}\n")
    
    # Load data
    print("📂 Loading datasets...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    print(f"  ✓ Train: {len(train_df)} samples")
    print(f"  ✓ Test: {len(test_df)} samples")
    
    # Train
    trainer = RoBERTATrainer(model_name='roberta-base', device=device)
    
    trainer.train(
        train_df['text'].values,
        train_df['sentiment'].values,
        train_df['has_sarcasm'].values,
        epochs=2,
        batch_size=16
    )
    
    # Evaluate
    print("\n📊 Evaluating on test set...")
    test_loader = trainer.prepare_dataloader(
        test_df['text'].values,
        test_df['sentiment'].values,
        test_df['has_sarcasm'].values,
        batch_size=32,
        shuffle=False
    )
    
    sent_preds, sarc_preds, sent_trues, sarc_trues = trainer.evaluate(test_loader)
    
    print("\n🎯 SENTIMENT DETECTION:")
    print(f"  Accuracy: {accuracy_score(sent_trues, sent_preds):.4f}")
    print(f"  F1-Score: {f1_score(sent_trues, sent_preds, average='weighted', zero_division=0):.4f}")
    
    print("\n🎭 SARCASM DETECTION:")
    print(f"  Accuracy: {accuracy_score(sarc_trues, sarc_preds):.4f}")
    print(f"  F1-Score: {f1_score(sarc_trues, sarc_preds, average='weighted', zero_division=0):.4f}")
    
    # Save
    trainer.save_model(model_dir)
    
    print(f"\n✅ Complete!")
    
    return trainer


if __name__ == "__main__":
    trainer = main()
