# scripts/data_collection.py
import sys
import os
import pandas as pd
from datetime import datetime
import time

# Add the root directory to Python path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BANK_APPS, SCRAPING_CONFIG, DATA_PATHS

def scrape_bank_reviews():
    """
    Scrape reviews for Ethiopian banking apps from Google Play Store
    Uses app IDs from config.py
    """
    try:
        from google_play_scraper import app, reviews, Sort
    except ImportError:
        print("Error: google-play-scraper not installed. Run: pip install google-play-scraper")
        return []
    
    all_reviews = []
    
    for bank_name, app_id in BANK_APPS.items():
        print(f"Scraping reviews for {bank_name} (App ID: {app_id})...")
        
        try:
            # Try to get app info first (optional)
            try:
                app_info = app(app_id)
                print(f"  App Name: {app_info.get('title', 'Unknown')}")
            except:
                print(f"  Could not fetch app info, but will try to scrape reviews anyway")
            
            # Scrape reviews
            reviews_result, continuation_token = reviews(
                app_id,
                lang=SCRAPING_CONFIG['language'],
                country=SCRAPING_CONFIG['country'],
                sort=Sort.MOST_RELEVANT,
                count=SCRAPING_CONFIG['reviews_per_bank'],
                filter_score_with=None  # Get all ratings (1-5 stars)
            )
            
            # Process and store reviews
            for review in reviews_result:
                all_reviews.append({
                    'review_id': review['reviewId'],
                    'review_text': review['content'],
                    'rating': review['score'],
                    'date': review['at'].strftime('%Y-%m-%d'),
                    'bank': bank_name,
                    'app_name': BANK_APPS[bank_name],
                    'source': 'Google Play'
                })
            
            print(f"  ✅ Collected {len(reviews_result)} reviews for {bank_name}")
            
            # Small delay to be respectful to servers
            time.sleep(2)
            
        except Exception as e:
            print(f"  ❌ Error scraping {bank_name}: {str(e)}")
            continue
    
    return all_reviews

def save_reviews_to_csv(reviews_data, filename):
    """Save reviews data to CSV"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    df = pd.DataFrame(reviews_data)
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(df)} reviews to {filename}")
    return df

if __name__ == "__main__":
    print("🚀 Starting Bank Reviews Scraping...")
    print("=" * 50)
    
    # Scrape reviews
    reviews_data = scrape_bank_reviews()
    
    if reviews_data:
        # Save to CSV using path from config
        df = save_reviews_to_csv(reviews_data, DATA_PATHS['raw_data'])
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 SCRAPING SUMMARY:")
        print(f"Total reviews collected: {len(df)}")
        print("\nReviews per bank:")
        print(df['bank'].value_counts())
        print(f"\nTarget: {SCRAPING_CONFIG['reviews_per_bank']} per bank")
    else:
        print("❌ No reviews were collected. Please check the errors above.")