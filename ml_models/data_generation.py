"""
Synthetic E-commerce Review Dataset Generator
Generates 2000+ reviews with sentiment and sarcasm labels
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

# Set random seed for reproducibility
np.random.seed(42)

# Positive reviews (non-sarcastic)
POSITIVE_REVIEWS = [
    "This product is excellent! I love it so much.",
    "Amazing quality and fast delivery. Highly recommended!",
    "Best purchase I've made in years. Worth every penny.",
    "Perfect for my needs. Great value for money.",
    "Fantastic product! Works as described. Very satisfied.",
    "Absolutely love this! Top-notch quality.",
    "Exceeded my expectations. Would buy again.",
    "Great product at an affordable price.",
    "Wonderful experience. Customer service is excellent.",
    "This is exactly what I was looking for!",
    "Outstanding quality and design. Highly impressed.",
    "Super happy with this purchase!",
    "Best investment I've made recently.",
    "Love everything about this product!",
    "Fantastic find! Great quality for the price.",
]

# Negative reviews (non-sarcastic)
NEGATIVE_REVIEWS = [
    "Terrible quality. Broke within a week.",
    "Worst purchase ever. Complete waste of money.",
    "Poor quality and bad customer service.",
    "Does not work as advertised. Very disappointed.",
    "Arrived damaged and unusable.",
    "This product is absolute garbage.",
    "Extremely disappointed with this purchase.",
    "Bad quality, bad service, bad experience.",
    "Total disappointment. Do not recommend.",
    "Waste of time and money.",
    "Product fell apart immediately.",
    "Very poor quality. Not worth it.",
    "Don't buy this. You'll regret it.",
    "Horrible experience from start to finish.",
    "Clearly poorly made and overpriced.",
]

# Neutral reviews (balanced sentiment)
NEUTRAL_REVIEWS = [
    "It's okay. Does the job, nothing special.",
    "Average product. Works fine for the price.",
    "Decent quality. No complaints.",
    "It's alright. Nothing to complain about.",
    "Standard product. Nothing remarkable.",
    "Good enough for everyday use.",
    "Meets expectations. Not exceptional though.",
    "Fair quality for the price point.",
    "Does what it's supposed to do.",
    "Acceptable product with decent features.",
]

# Sarcastic positive reviews (actually negative)
SARCASTIC_POSITIVE_REVIEWS = [
    "Oh, this is absolutely amazing... for a doorstop!",
    "Love it! Really great for a piece of junk.",
    "Best product ever... to use as a paperweight.",
    "Fantastic! Perfect for everyone who loves disappointment.",
    "So good... if you enjoy throwing money away!",
    "Wonderful quality... for something from 1995.",
    "Yeah, this is exactly what I wanted... NOT!",
    "Sure, brilliant design... if you hate functionality.",
    "Perfect! Just what I needed... a useless brick.",
    "Outstanding... at being totally useless.",
    "Love how it breaks so easily! Manufacturing excellence!",
    "Fantastic! Nothing says quality like instant failure.",
    "Best money ever spent... on regret.",
    "Absolutely thrilled with this pile of garbage.",
    "What a steal! For stealing your money, that is.",
]

# Sarcastic negative reviews (actually positive)
SARCASTIC_NEGATIVE_REVIEWS = [
    "It's so bad, you'll want to buy ten more!",
    "Terrible quality. I've already ordered five more!",
    "Worst thing ever... said no one who actually bought it!",
    "Hate it so much I bought it for all my friends!",
    "Broke in one day... of continuous heavy use, still works!",
    "The price is insane... for such an incredible product!",
    "Customer service is non-existent... except they're super helpful!",
    "Absolutely disappointing... if disappointment means being amazed!",
    "Poor quality... best purchase of my life!",
    "Don't waste your money... just kidding, totally worth it!",
    "If you hate value, then avoid this!",
    "Would not recommend... to my worst enemy, it's too good!",
    "Garbage product... that I use every single day!",
    "Save your money... NOT. This is essential!",
    "Regret every penny... spent on this masterpiece!",
]

# Emoji sentiments
POSITIVE_EMOJIS = ["😍", "🎉", "👍", "💯", "✨", "🔥", "😊", "💝", "⭐"]
NEGATIVE_EMOJIS = ["😒", "😠", "💔", "😤", "🤦", "😡", "👎", "💩", "😞"]
NEUTRAL_EMOJIS = ["😐", "🤷", "😑", "📦", "🛍️"]

# Contradictory phrase pairs (for sarcasm detection)
CONTRADICTION_PAIRS = [
    ("great", "worst"),
    ("love", "hate"),
    ("best", "terrible"),
    ("amazing", "awful"),
    ("perfect", "broken"),
    ("excellent", "garbage"),
    ("fantastic", "useless"),
    ("wonderful", "horrible"),
]


def generate_synthetic_reviews(num_reviews=2000):
    """
    Generate synthetic e-commerce reviews with sentiment and sarcasm labels
    
    Returns:
        DataFrame with columns: text, sentiment, has_sarcasm
        sentiment: 0=negative, 1=neutral, 2=positive
        has_sarcasm: 0=no sarcasm, 1=sarcasm
    """
    reviews = []
    
    # Distribution: 40% positive, 35% negative, 25% neutral
    # Within reviews: ~30% contain sarcasm
    num_positive = int(num_reviews * 0.40)
    num_negative = int(num_reviews * 0.35)
    num_neutral = int(num_reviews * 0.25)
    
    # POSITIVE SENTIMENT (label=2)
    for i in range(num_positive):
        is_sarcastic = np.random.random() < 0.30
        
        if is_sarcastic:
            text = np.random.choice(SARCASTIC_POSITIVE_REVIEWS)
            # Add emoji mismatch for sarcasm indicator
            if np.random.random() > 0.5:
                text += " " + np.random.choice(NEGATIVE_EMOJIS)
        else:
            text = np.random.choice(POSITIVE_REVIEWS)
            if np.random.random() > 0.7:
                text += " " + np.random.choice(POSITIVE_EMOJIS)
        
        reviews.append({
            "text": text,
            "sentiment": 2,  # Positive
            "has_sarcasm": 1 if is_sarcastic else 0
        })
    
    # NEGATIVE SENTIMENT (label=0)
    for i in range(num_negative):
        is_sarcastic = np.random.random() < 0.30
        
        if is_sarcastic:
            text = np.random.choice(SARCASTIC_NEGATIVE_REVIEWS)
            # Add emoji mismatch for sarcasm indicator
            if np.random.random() > 0.5:
                text += " " + np.random.choice(POSITIVE_EMOJIS)
        else:
            text = np.random.choice(NEGATIVE_REVIEWS)
            if np.random.random() > 0.7:
                text += " " + np.random.choice(NEGATIVE_EMOJIS)
        
        reviews.append({
            "text": text,
            "sentiment": 0,  # Negative
            "has_sarcasm": 1 if is_sarcastic else 0
        })
    
    # NEUTRAL SENTIMENT (label=1)
    for i in range(num_neutral):
        # Lower sarcasm rate for neutral reviews
        is_sarcastic = np.random.random() < 0.15
        
        if is_sarcastic:
            text = np.random.choice(SARCASTIC_POSITIVE_REVIEWS + SARCASTIC_NEGATIVE_REVIEWS)
        else:
            text = np.random.choice(NEUTRAL_REVIEWS)
            if np.random.random() > 0.8:
                text += " " + np.random.choice(NEUTRAL_EMOJIS)
        
        reviews.append({
            "text": text,
            "sentiment": 1,  # Neutral
            "has_sarcasm": 1 if is_sarcastic else 0
        })
    
    # Add some variation by duplicating with slight modifications
    base_df = pd.DataFrame(reviews)
    
    # Shuffle and return
    df = base_df.sample(frac=1).reset_index(drop=True)
    
    return df


def split_train_test(df, train_ratio=0.8, random_state=42):
    """
    Split dataset into train and test sets, stratified by sentiment and sarcasm
    """
    # Stratified split by sentiment and sarcasm
    from sklearn.model_selection import train_test_split
    
    train_df, test_df = train_test_split(
        df,
        test_size=1-train_ratio,
        random_state=random_state,
        stratify=df[['sentiment', 'has_sarcasm']]
    )
    
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def main():
    """
    Main function to generate and save dataset
    """
    print("🚀 Generating synthetic e-commerce review dataset...")
    
    # Create data directory
    data_dir = Path(__file__).parent.parent / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    
    # Create directories if they don't exist
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate dataset
    print(f"  Generating 2000 reviews...")
    df = generate_synthetic_reviews(2000)
    
    # Display statistics
    print(f"\n📊 Dataset Statistics:")
    print(f"  Total reviews: {len(df)}")
    print(f"  Sentiment distribution:")
    print(f"    - Positive (2): {(df['sentiment'] == 2).sum()} ({(df['sentiment'] == 2).sum() / len(df) * 100:.1f}%)")
    print(f"    - Neutral (1): {(df['sentiment'] == 1).sum()} ({(df['sentiment'] == 1).sum() / len(df) * 100:.1f}%)")
    print(f"    - Negative (0): {(df['sentiment'] == 0).sum()} ({(df['sentiment'] == 0).sum() / len(df) * 100:.1f}%)")
    print(f"\n  Sarcasm distribution:")
    print(f"    - With sarcasm: {(df['has_sarcasm'] == 1).sum()} ({(df['has_sarcasm'] == 1).sum() / len(df) * 100:.1f}%)")
    print(f"    - Without sarcasm: {(df['has_sarcasm'] == 0).sum()} ({(df['has_sarcasm'] == 0).sum() / len(df) * 100:.1f}%)")
    
    # Save full dataset
    full_dataset_path = raw_dir / "reviews.csv"
    df.to_csv(full_dataset_path, index=False)
    print(f"\n✅ Full dataset saved: {full_dataset_path}")
    
    # Split into train and test
    print(f"\n  Splitting into train (80%) and test (20%)...")
    train_df, test_df = split_train_test(df)
    
    # Save train and test sets
    train_path = processed_dir / "train.csv"
    test_path = processed_dir / "test.csv"
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"✅ Train set saved ({len(train_df)} samples): {train_path}")
    print(f"✅ Test set saved ({len(test_df)} samples): {test_path}")
    
    # Print sample reviews
    print(f"\n📝 Sample Reviews:")
    print("\n--- Positive, Non-sarcastic ---")
    print(df[(df['sentiment'] == 2) & (df['has_sarcasm'] == 0)]['text'].iloc[0])
    print("\n--- Negative, Non-sarcastic ---")
    print(df[(df['sentiment'] == 0) & (df['has_sarcasm'] == 0)]['text'].iloc[0])
    print("\n--- Sarcastic (appears positive, actually negative) ---")
    print(df[(df['sentiment'] == 2) & (df['has_sarcasm'] == 1)]['text'].iloc[0])
    print("\n--- Sarcastic (appears negative, actually positive) ---")
    print(df[(df['sentiment'] == 0) & (df['has_sarcasm'] == 1)]['text'].iloc[0])
    
    print("\n✅ Dataset generation complete!")
    
    return df


if __name__ == "__main__":
    df = main()
