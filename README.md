# 🏦 Fintech Review Analytics - Ethiopian Banking Apps

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Completed-success.svg)

A comprehensive data engineering and analytics project analyzing **1,200+ Google Play Store reviews** for three Ethiopian banks to identify customer satisfaction drivers, pain points, and provide actionable recommendations.

## 📋 Project Overview

**Business Context**: Omega Consultancy is advising Ethiopian banks to improve their mobile apps for better customer retention and satisfaction.

**Banks Analyzed**:
- 🏛️ Commercial Bank of Ethiopia (CBE)
- 🏦 Bank of Abyssinia (BOA)
- 🚀 Dashen Bank

**Key Deliverables**:
- Web scraping pipeline for Google Play Store reviews
- Sentiment analysis using DistilBERT transformer model
- Thematic analysis with TF-IDF keyword extraction
- PostgreSQL database with 1,200+ reviews
- 5 professional visualizations
- Actionable business recommendations

## 🎯 Key Findings

### 📊 Performance Rankings
| Rank | Bank | Positive Sentiment | Avg Rating | Key Strength | Key Issue |
|------|------|-------------------:|-----------:|--------------|-----------|
| 🥇 **1** | **Dashen Bank** | **66.3%** | **3.96/5** | User Experience | Minor Bugs |
| 🥈 **2** | **CBE** | 20.8% | 2.66/5 | Brand Trust | Transaction Problems |
| 🥉 **3** | **BOA** | 15.3% | 2.02/5 | Mobile Focus | App Stability |

### 🔥 Critical Insights
1. **BOA** has severe app stability issues (175+ complaints about crashes)
2. **CBE** struggles with transaction reliability (188+ failed transfer complaints)
3. **Dashen** leads in customer satisfaction but needs minor optimizations

## 📁 Project Structure

```
fintech-review-analytics/
├── config.py                # Configuration file
├── requirements.txt         # Dependencies
├── README.md                # This file
│
├── scripts/                 # Main Python scripts
│   ├── data_collection.py   # Scrape Google Play reviews
│   ├── data_preprocessing.py# Clean and validate data
│   ├── sentiment_analysis.py# DistilBERT sentiment analysis
│   ├── thematic_analysis.py # TF-IDF keyword extraction
│   ├── database_schema.py   # PostgreSQL setup
│   ├── database_insert.py   # Data insertion
│   ├── database_queries.py  # Business SQL queries
│   └── visualizations.py    # Generate charts
│
├── data/                    # Data files
│   ├── raw/                 # Raw scraped data
│   └── processed/           # Cleaned & analyzed data
│
├── visualizations/          # Generated plots
│   ├── sentiment_comparison.png
│   ├── pain_points_analysis.png
│   ├── rating_distribution.png
│   ├── word_clouds.png
│   └── monthly_trends.png
│
└── database/                # Database files
    └── schema.sql           # PostgreSQL schema
```

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database
createdb bank_reviews
```

### 2. Configuration
Update `config.py` with your PostgreSQL credentials:

```python
DATABASE_CONFIG = {
    'dbname': 'bank_reviews',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}
```

### 3. Run the Pipeline
Execute scripts in order:

```bash
# 1. Collect data
python scripts/data_collection.py

# 2. Clean data
python scripts/data_preprocessing.py

# 3. Analyze sentiment
python scripts/sentiment_analysis.py

# 4. Extract themes
python scripts/thematic_analysis.py

# 5. Setup database
python scripts/database_schema.py

# 6. Insert data
python scripts/database_insert.py

# 7. Generate visuals
python scripts/visualizations.py
```

## 🔧 Technical Stack

**Data Collection & Processing**
- `google-play-scraper` - Web scraping Google Play Store
- `pandas` - Data manipulation and cleaning
- `numpy` - Numerical operations

**Natural Language Processing**
- `transformers` - Hugging Face DistilBERT model
- `scikit-learn` - TF-IDF vectorization
- `regex` - Text pattern matching

**Database & Storage**
- `PostgreSQL` - Relational database
- `psycopg2` - PostgreSQL adapter for Python
- `SQLAlchemy` - Database ORM

**Visualization**
- `matplotlib` - Static visualizations
- `seaborn` - Statistical graphics
- `wordcloud` - Keyword visualization

**DevOps**
- `git` - Version control
- `Python 3.8+` - Core programming language

## 📈 Business Scenarios Addressed

**Scenario 1: User Retention**  
**Problem:** Slow transfer speeds causing user frustration  
**Solution:** Priority fix for transaction processing with progress indicators

**Scenario 2: Feature Enhancement**  
**Problem:** Identifying most-requested features  
**Solution:** Biometric login, offline mode, budgeting tools roadmap

**Scenario 3: Complaint Management**  
**Problem:** Efficient complaint resolution  
**Solution:** AI chatbot implementation for top 3 complaint categories

## 📊 Database Schema

**banks Table**
```sql
bank_id SERIAL PRIMARY KEY
bank_name VARCHAR(50) NOT NULL
app_name VARCHAR(100)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**reviews Table**
```sql
review_id VARCHAR(100) PRIMARY KEY
bank_id INTEGER REFERENCES banks(bank_id)
review_text TEXT NOT NULL
rating INTEGER CHECK (rating >= 1 AND rating <= 5)
review_date DATE
sentiment_label VARCHAR(10)
sentiment_score DECIMAL(5,4)
themes TEXT
source VARCHAR(50)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

## 🎨 Visualizations Generated
- **Sentiment Comparison:** Bank-wise sentiment and rating comparison
- **Pain Points Analysis:** Top complaints per bank (horizontal bar charts)
- **Rating Distribution:** Donut charts showing star rating breakdown
- **Word Clouds:** Keyword frequency visualization per bank
- **Monthly Trends:** Positive sentiment trends over time

---

*Prepared by Omega Consultancy — December 2025*
