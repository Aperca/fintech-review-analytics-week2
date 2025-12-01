

# Fintech Review Analytics - Week 2 Challenge

## Task 1: Data Collection and Preprocessing ✅ COMPLETED

### Data Collected:
- **Total Reviews**: 1,200 (400 per bank)
- **Banks**: CBE, BOA, Dashen
- **Data Quality**: 0% missing data
- **Source**: Google Play Store

### Files Structure:
fintech-review-analytics-week2/
├── config.py # App IDs and settings
├── scripts/
│ ├── data_collection.py # Scraping script
│ ├── data_preprocessing.py # Cleaning script
│ └── check_data.py # Data validation
├── data/
│ ├── raw/ # Raw scraped data
│ └── processed/ # Cleaned data
└── requirements.txt


### Usage:
```bash
# Scrape new data
python scripts/data_collection.py

# Preprocess and clean
python scripts/data_preprocessing.py

# Check data quality
python scripts/data_check.py

# Create database directory
mkdir -p database

# Create README for database setup
cat > database/README.md << 'EOF'
# Database Setup Guide

## PostgreSQL Installation

### macOS (using Homebrew):
```bash
brew install postgresql
brew services start postgresql