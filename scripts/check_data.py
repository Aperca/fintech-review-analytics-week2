# scripts/check_data.py
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_PATHS

def check_raw_data():
    """Quick check of the scraped data"""
    print("🔍 Checking raw data quality...")
    
    df = pd.read_csv(DATA_PATHS['raw_data'])
    
    print(f"Total reviews: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nSample of reviews:")
    print(df[['bank', 'rating', 'review_text']].head(3))
    
    print(f"\nRating distribution:")
    print(df['rating'].value_counts().sort_index())
    
    print(f"\nMissing values per column:")
    print(df.isnull().sum())

if __name__ == "__main__":
    check_raw_data()