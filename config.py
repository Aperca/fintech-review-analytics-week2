
# Google Play Store app IDs for Ethiopian banks
BANK_APPS = {
    "CBE": "com.combanketh.mobilebanking",
    "BOA": "com.boa.boaMobileBanking",
    "Dashen": "com.dashen.dashensuperapp"
}
# Scraping settings
SCRAPING_CONFIG = {
    'reviews_per_bank': 400,  # Target number of reviews per bank
    'language': 'en',  # Language for reviews
    'country': 'et',  # Country (Ethiopia)
    'sort_by': 'MOST_RELEVANT',  # Sort method: MOST_RELEVANT or NEWEST
}

# File paths
DATA_PATHS = {
    'raw_data': 'data/raw/bank_reviews_raw.csv',
    'cleaned_data': 'data/processed/bank_reviews_cleaned.csv'
}

# Database configuration
DATABASE_CONFIG = {
    'dbname': 'bank_reviews',
    'user': 'liluebuy',  
    'password': '', 
    'host': 'localhost',
    'port': '5432'
}

# Alternative: Use environment variables for security
import os
DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'bank_reviews'),
    'user': os.getenv('DB_USER', 'liluebuy'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}