# scripts/data_preprocessing.py
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_PATHS

def preprocess_reviews():
    """
    Clean and preprocess the scraped reviews
    Even though data is clean, this ensures consistency
    """
    print("🧹 Preprocessing and cleaning review data...")
    
    # Read raw data
    df = pd.read_csv(DATA_PATHS['raw_data'])
    
    print(f"Initial data shape: {df.shape}")
    
    # 1. Remove duplicates (even though likely none)
    initial_count = len(df)
    df = df.drop_duplicates(subset=['review_id'], keep='first')
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate reviews")
    
    # 2. Data type validation
    df['rating'] = df['rating'].astype(int)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    # 3. Text cleaning preparation
    df['review_length'] = df['review_text'].str.len()
    
    # 4. Remove extremely short reviews (potential spam)
    short_reviews_before = len(df)
    df = df[df['review_length'] >= 5]  # At least 5 characters
    short_reviews_removed = short_reviews_before - len(df)
    if short_reviews_removed > 0:
        print(f"Removed {short_reviews_removed} very short reviews")
    
    # 5. Final data quality check
    print(f"Final data shape: {df.shape}")
    print(f"Missing values after cleaning:")
    print(df.isnull().sum())
    
    # Save cleaned data
    os.makedirs(os.path.dirname(DATA_PATHS['cleaned_data']), exist_ok=True)
    df.to_csv(DATA_PATHS['cleaned_data'], index=False)
    print(f"✅ Cleaned data saved to: {DATA_PATHS['cleaned_data']}")
    
    return df

def generate_quality_report(df):
    """Generate a comprehensive data quality report"""
    print("\n" + "="*60)
    print("📊 DATA QUALITY REPORT")
    print("="*60)
    
    print(f"Total reviews: {len(df)}")
    print(f"Reviews per bank:")
    print(df['bank'].value_counts())
    
    print(f"\nRating distribution:")
    rating_dist = df['rating'].value_counts().sort_index()
    for rating, count in rating_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  {rating} stars: {count} reviews ({percentage:.1f}%)")
    
    print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")
    
    # Review length statistics
    print(f"\nReview length statistics:")
    print(f"  Average length: {df['review_length'].mean():.1f} characters")
    print(f"  Shortest review: {df['review_length'].min()} characters")
    print(f"  Longest review: {df['review_length'].max()} characters")
    
    # Missing data percentage
    missing_pct = (df.isnull().sum() / len(df)) * 100
    print(f"\nMissing data percentage:")
    for col, pct in missing_pct.items():
        print(f"  {col}: {pct:.2f}%")
    
    print(f"  Total reviews: {len(df)}/1200 - {'✅ MET' if len(df) >= 1200 else '❌ NOT MET'}")
    max_missing = missing_pct.max()
    print(f"  Missing data: {max_missing:.2f}%/<5% - {'✅ MET' if max_missing < 5 else '❌ NOT MET'}")
    
    return missing_pct

if __name__ == "__main__":
    # Preprocess the data
    cleaned_df = preprocess_reviews()
    
    # Generate quality report
    generate_quality_report(cleaned_df)