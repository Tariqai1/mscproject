"""
Advanced Text Preprocessing with Sarcasm-Aware Features
Handles: tokenization, lemmatization, emoji detection, contradiction detection, sarcasm markers
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

# NLP imports
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import emoji

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)


class SarcasmAwarePreprocessor:
    """
    Advanced text preprocessor with sarcasm detection features
    """
    
    def __init__(self):
        """Initialize preprocessor with lemmatizer and stopwords"""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Sarcasm keyword indicators
        self.sarcasm_keywords = {
            'yeah_right': ['yeah right', 'sure', 'yeah okay'],
            'emotional_exaggeration': ['so bad', 'worst ever', 'best ever', 'love it', 'hate it'],
            'contradiction_markers': ['though', 'but', 'however', 'surprisingly', 'ironically', 'actually', 'never mind'],
            'emoji_contradiction': ['😍', '❤️', '💕', '😊', '👍'],  # Positive emojis with negative text = sarcasm
        }
        
        # Contradiction word pairs (word1 = positive, word2 = negative)
        self.contradiction_pairs = {
            'great': ['bad', 'terrible', 'awful', 'worst', 'garbage', 'trash'],
            'love': ['hate', 'despise', 'dislike', 'can\'t stand'],
            'best': ['worst', 'terrible', 'awful', 'horrible'],
            'amazing': ['terrible', 'awful', 'horrible', 'disastrous'],
            'excellent': ['poor', 'bad', 'terrible', 'awful'],
            'perfect': ['broken', 'useless', 'worthless', 'damaged'],
            'wonderful': ['horrible', 'dreadful', 'terrible', 'awful'],
            'fantastic': ['awful', 'useless', 'garbage', 'terrible'],
            'brilliant': ['stupid', 'dumb', 'idiotic', 'terrible'],
            'fantastic': ['appalling', 'terrible', 'disastrous', 'horrible'],
        }
    
    def extract_emojis(self, text: str) -> Dict[str, List[str]]:
        """
        Extract emojis and categorize by sentiment
        
        Returns:
            Dict with keys: 'positive_emoji', 'negative_emoji', 'neutral_emoji'
        """
        extracted_emojis = {'positive': [], 'negative': [], 'neutral': []}
        
        for char in text:
            if char in emoji.EMOJI_DATA:
                emoji_obj = emoji.EMOJI_DATA[char]
                category = emoji_obj.get('category', 'neutral')
                
                # Classify emojis by sentiment
                if 'smiling' in category or 'heart' in category or 'celebration' in category or 'fire' in category:
                    extracted_emojis['positive'].append(char)
                elif 'sad' in category or 'angry' in category or 'skull' in category or 'cross' in category:
                    extracted_emojis['negative'].append(char)
                else:
                    extracted_emojis['neutral'].append(char)
        
        return extracted_emojis
    
    def detect_contradictions(self, tokens: List[str]) -> Tuple[bool, float]:
        """
        Detect contradictory word pairs in tokens
        e.g., 'great' and 'terrible' in same review
        
        Returns:
            (has_contradiction, contradiction_score)
        """
        token_set = set(tokens)
        contradiction_count = 0
        
        for positive_word, negative_words in self.contradiction_pairs.items():
            if positive_word in token_set:
                for negative_word in negative_words:
                    if negative_word in token_set:
                        contradiction_count += 1
        
        has_contradiction = contradiction_count > 0
        contradiction_score = min(contradiction_count / 2.0, 1.0)  # Normalize to [0, 1]
        
        return has_contradiction, contradiction_score
    
    def detect_sarcasm_keywords(self, text: str) -> Tuple[bool, float]:
        """
        Detect known sarcasm marker keywords
        
        Returns:
            (has_sarcasm_keyword, keyword_sarcasm_score)
        """
        text_lower = text.lower()
        sarcasm_score = 0.0
        found_keyword = False
        
        for category, keywords in self.sarcasm_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keyword = True
                    sarcasm_score += 0.2
        
        sarcasm_score = min(sarcasm_score, 1.0)  # Normalize to [0, 1]
        
        return found_keyword, sarcasm_score
    
    def detect_emoji_mismatch(self, text: str, sentiment_label: int = None) -> float:
        """
        Detect emoji sentiment vs text sentiment mismatch
        High score = likely sarcasm
        
        sentiment_label: 0=negative, 1=neutral, 2=positive
        """
        emojis = self.extract_emojis(text)
        
        # Count positive and negative emojis
        positive_emoji_count = len(emojis['positive'])
        negative_emoji_count = len(emojis['negative'])
        
        if positive_emoji_count == 0 and negative_emoji_count == 0:
            return 0.0
        
        # Detect mismatch
        emoji_sentiment = None
        if positive_emoji_count > negative_emoji_count:
            emoji_sentiment = 2  # Positive
        elif negative_emoji_count > positive_emoji_count:
            emoji_sentiment = 0  # Negative
        else:
            return 0.0
        
        # If we have a true sentiment label, check mismatch
        if sentiment_label is not None:
            if emoji_sentiment != sentiment_label:
                return 1.0  # Strong mismatch = sarcasm indicator
        
        return 0.5  # Weak indicator without sentiment label
    
    def basic_preprocessing(self, text: str) -> str:
        """
        Basic text cleaning: lowercase, URLs, special chars, extra spaces
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep emoji
        # Keep letters, numbers, spaces, and emoji
        text = re.sub(r'[^a-zA-Z0-9\s\U0001F300-\U0001F9FF]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize_and_lemmatize(self, text: str) -> List[str]:
        """
        Tokenize and lemmatize text
        """
        tokens = word_tokenize(text)
        
        # Lemmatize and remove stopwords
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                lemma = self.lemmatizer.lemmatize(token)
                processed_tokens.append(lemma)
        
        return processed_tokens
    
    def preprocess(self, text: str, sentiment_label: int = None) -> Dict:
        """
        Complete preprocessing pipeline with sarcasm-aware features
        
        Returns:
            Dict with keys:
            - text_original: Original text
            - text_cleaned: Cleaned text
            - tokens: Processed tokens
            - emojis: Extracted emojis
            - has_contradiction: Boolean
            - contradiction_score: Float [0, 1]
            - has_sarcasm_keyword: Boolean
            - sarcasm_keyword_score: Float [0, 1]
            - emoji_mismatch_score: Float [0, 1]
            - sarcasm_score: Combined sarcasm indicator [0, 1]
        """
        # Basic cleaning
        text_cleaned = self.basic_preprocessing(text)
        
        # Tokenization and lemmatization
        tokens = self.tokenize_and_lemmatize(text_cleaned)
        
        # Extract emojis
        emojis = self.extract_emojis(text)
        
        # Detect contradictions
        has_contradiction, contradiction_score = self.detect_contradictions(tokens)
        
        # Detect sarcasm keywords
        has_sarcasm_keyword, keyword_score = self.detect_sarcasm_keywords(text)
        
        # Detect emoji mismatch
        emoji_mismatch_score = self.detect_emoji_mismatch(text, sentiment_label)
        
        # Combined sarcasm score (weighted average)
        sarcasm_score = (
            contradiction_score * 0.3 +
            keyword_score * 0.3 +
            emoji_mismatch_score * 0.4
        )
        
        return {
            'text_original': text,
            'text_cleaned': text_cleaned,
            'tokens': tokens,
            'emojis': emojis,
            'has_contradiction': has_contradiction,
            'contradiction_score': contradiction_score,
            'has_sarcasm_keyword': has_sarcasm_keyword,
            'sarcasm_keyword_score': keyword_score,
            'emoji_mismatch_score': emoji_mismatch_score,
            'sarcasm_score': sarcasm_score,  # Combined indicator [0, 1]
        }
    
    def preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess entire dataframe
        
        Expects columns: text, sentiment (optional)
        Returns: DataFrame with additional preprocessed columns
        """
        results = []
        
        for idx, row in df.iterrows():
            text = row['text']
            sentiment_label = row.get('sentiment', None)
            
            # Preprocess
            processed = self.preprocess(text, sentiment_label)
            
            # Add to results
            result_row = {
                'text_original': processed['text_original'],
                'text_cleaned': processed['text_cleaned'],
                'tokens': ' '.join(processed['tokens']),  # Convert to string for CSV
                'tokens_list': processed['tokens'],  # Keep list for later use
                'positive_emojis': len(processed['emojis']['positive']),
                'negative_emojis': len(processed['emojis']['negative']),
                'neutral_emojis': len(processed['emojis']['neutral']),
                'has_contradiction': processed['has_contradiction'],
                'contradiction_score': processed['contradiction_score'],
                'has_sarcasm_keyword': processed['has_sarcasm_keyword'],
                'sarcasm_keyword_score': processed['sarcasm_keyword_score'],
                'emoji_mismatch_score': processed['emoji_mismatch_score'],
                'sarcasm_score': processed['sarcasm_score'],
            }
            
            # Add original columns
            for col in df.columns:
                if col != 'text':
                    result_row[col] = row[col]
            
            results.append(result_row)
        
        result_df = pd.DataFrame(results)
        return result_df


def main():
    """
    Main function to preprocess train and test datasets
    """
    print("🔄 Preprocessing datasets with sarcasm-aware features...\n")
    
    # Initialize preprocessor
    preprocessor = SarcasmAwarePreprocessor()
    
    # Define paths
    data_dir = Path(__file__).parent.parent / "data"
    train_path = data_dir / "processed" / "train.csv"
    test_path = data_dir / "processed" / "test.csv"
    
    # Check if data exists
    if not train_path.exists():
        print(f"❌ Train dataset not found: {train_path}")
        print("   Please run data_generation.py first")
        return
    
    # Load datasets
    print(f"📂 Loading datasets...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    print(f"  ✓ Train: {len(train_df)} samples")
    print(f"  ✓ Test: {len(test_df)} samples")
    
    # Preprocess train set
    print(f"\n🔄 Preprocessing training set...")
    train_preprocessed = preprocessor.preprocess_dataframe(train_df)
    train_preprocessed.to_csv(data_dir / "processed" / "train_preprocessed.csv", index=False)
    print(f"  ✓ Train preprocessed: {len(train_preprocessed)} samples")
    print(f"  ✓ Saved to: {data_dir / 'processed' / 'train_preprocessed.csv'}")
    
    # Preprocess test set
    print(f"\n🔄 Preprocessing test set...")
    test_preprocessed = preprocessor.preprocess_dataframe(test_df)
    test_preprocessed.to_csv(data_dir / "processed" / "test_preprocessed.csv", index=False)
    print(f"  ✓ Test preprocessed: {len(test_preprocessed)} samples")
    print(f"  ✓ Saved to: {data_dir / 'processed' / 'test_preprocessed.csv'}")
    
    # Display statistics
    print(f"\n📊 Sarcasm Feature Statistics:")
    print(f"\n  Training Set:")
    print(f"    Avg sarcasm_score: {train_preprocessed['sarcasm_score'].mean():.3f}")
    print(f"    Avg contradiction_score: {train_preprocessed['contradiction_score'].mean():.3f}")
    print(f"    Avg emoji_mismatch_score: {train_preprocessed['emoji_mismatch_score'].mean():.3f}")
    print(f"    Reviews with sarcasm keywords: {train_preprocessed['has_sarcasm_keyword'].sum()} ({train_preprocessed['has_sarcasm_keyword'].mean() * 100:.1f}%)")
    
    print(f"\n  Test Set:")
    print(f"    Avg sarcasm_score: {test_preprocessed['sarcasm_score'].mean():.3f}")
    print(f"    Avg contradiction_score: {test_preprocessed['contradiction_score'].mean():.3f}")
    print(f"    Avg emoji_mismatch_score: {test_preprocessed['emoji_mismatch_score'].mean():.3f}")
    print(f"    Reviews with sarcasm keywords: {test_preprocessed['has_sarcasm_keyword'].sum()} ({test_preprocessed['has_sarcasm_keyword'].mean() * 100:.1f}%)")
    
    # Display sample
    print(f"\n📝 Sample Preprocessed Review:")
    sample_idx = 0
    sample = train_preprocessed.iloc[sample_idx]
    print(f"\n  Original: {sample['text_original']}")
    print(f"  Cleaned: {sample['text_cleaned']}")
    print(f"  Tokens: {sample['tokens'][:50]}...")  # First 50 chars
    print(f"  Sarcasm Score: {sample['sarcasm_score']:.3f}")
    print(f"  Contradiction: {sample['has_contradiction']} (score: {sample['contradiction_score']:.3f})")
    print(f"  Emoji Mismatch: {sample['emoji_mismatch_score']:.3f}")
    
    print(f"\n✅ Preprocessing complete!")
    
    return train_preprocessed, test_preprocessed


if __name__ == "__main__":
    train_preprocessed, test_preprocessed = main()
