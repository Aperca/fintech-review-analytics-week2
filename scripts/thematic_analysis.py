# scripts/thematic_analysis.py
import pandas as pd
import numpy as np
import re
from collections import Counter
import sys
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import _stop_words

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BANK_APPS

class ThematicAnalyzer:
    def __init__(self):
        # Expanded theme keywords based on common banking app issues
        self.theme_keywords = {
            'Login & Access Issues': [
                'login', 'log in', 'password', 'forgot', 'account', 'access', 'verification',
                'authenticate', 'biometric', 'fingerprint', 'face id', 'locked', 'blocked',
                'security', 'pin', 'code', 'verify', 'registered', 'registration'
            ],
            'Transaction Problems': [
                'transfer', 'transaction', 'payment', 'send money', 'failed', 'fail',
                'pending', 'stuck', 'complete', 'process', 'send', 'receive', 'money',
                'amount', 'balance', 'deduct', 'charge', 'fee', 'bill', 'payment'
            ],
            'App Performance & Bugs': [
                'crash', 'freeze', 'frozen', 'slow', 'lag', 'bug', 'error', 'not working',
                'close', 'stop', 'hang', 'loading', 'response', 'speed', 'fast', 'quick',
                'update', 'version', 'install', 'download', 'technical', 'problem', 'issue'
            ],
            'User Interface & Experience': [
                'interface', 'ui', 'ux', 'design', 'layout', 'navigation', 'menu',
                'complicated', 'confusing', 'hard to use', 'complex', 'simple', 'easy',
                'intuitive', 'beautiful', 'ugly', 'modern', 'old', 'outdated'
            ],
            'Customer Support': [
                'support', 'help', 'service', 'assistance', 'contact', 'call', 'phone',
                'email', 'response', 'complain', 'complaint', 'issue', 'resolve',
                'customer care', 'helpline', 'assist'
            ],
            'Features & Functionality': [
                'feature', 'function', 'add', 'missing', 'should have', 'need',
                'improve', 'update', 'version', 'new', 'option', 'setting',
                'notification', 'alert', 'reminder', 'history', 'statement'
            ],
            'Network & Connectivity': [
                'network', 'internet', 'connection', 'connect', 'online', 'offline',
                'wifi', 'data', 'signal', 'server', 'maintenance', 'down'
            ]
        }
    
    def preprocess_text(self, text):
        """Basic text preprocessing without spaCy"""
        if pd.isna(text):
            return ""
        text = str(text).lower()
        # Remove special characters but keep words
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_keywords_tfidf(self, texts, max_features=50):
        """Extract keywords using TF-IDF"""
        # Preprocess all texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 3),  # Include single words, bigrams, and trigrams
            min_df=2  # Ignore terms that appear in only 1 document
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top keywords by average TF-IDF score
            scores = np.array(tfidf_matrix.mean(axis=0)).flatten()
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:30]  # Return top 30
        except Exception as e:
            print(f"TF-IDF error: {e}")
            return []
    
    def categorize_review_themes(self, review_text):
        """Categorize review into themes based on keyword matching"""
        text_lower = self.preprocess_text(review_text)
        matched_themes = []
        
        for theme, keywords in self.theme_keywords.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    matched_themes.append(theme)
                    break  # Avoid duplicate themes for same review
        
        return ', '.join(matched_themes) if matched_themes else 'Other'
    
    def analyze_bank_themes(self, df, bank_name):
        """Analyze themes for a specific bank"""
        bank_reviews = df[df['bank'] == bank_name]
        
        print(f"\n🏦 {bank_name} - THEMATIC ANALYSIS")
        print("=" * 50)
        
        # Analyze negative reviews (pain points)
        negative_reviews = bank_reviews[bank_reviews['sentiment_label'] == 'NEGATIVE']
        positive_reviews = bank_reviews[bank_reviews['sentiment_label'] == 'POSITIVE']
        
        print(f"Total reviews: {len(bank_reviews)}")
        print(f"Negative reviews: {len(negative_reviews)}")
        print(f"Positive reviews: {len(positive_reviews)}")
        
        if len(negative_reviews) == 0:
            print("No negative reviews to analyze.")
            return Counter()
        
        # Extract themes for negative reviews
        print("\n🔍 Analyzing pain points...")
        negative_reviews['themes'] = negative_reviews['review_text'].apply(
            self.categorize_review_themes
        )
        
        # Count theme frequency
        all_themes = []
        for themes in negative_reviews['themes']:
            if themes != 'Other':
                all_themes.extend([theme.strip() for theme in themes.split(',')])
        
        theme_counts = Counter(all_themes)
        
        print(f"\n📊 TOP PAIN POINTS ({bank_name}):")
        if theme_counts:
            for theme, count in theme_counts.most_common(5):
                percentage = (count / len(negative_reviews)) * 100
                print(f"  {theme}: {count} reviews ({percentage:.1f}%)")
        else:
            print("  No specific themes identified")
        
        # Extract keywords from negative reviews
        print(f"\n🔑 TOP KEYWORDS FROM NEGATIVE REVIEWS:")
        negative_texts = negative_reviews['review_text'].tolist()
        top_keywords = self.extract_keywords_tfidf(negative_texts)
        
        if top_keywords:
            for keyword, score in top_keywords[:10]:
                print(f"  '{keyword}': {score:.3f}")
        else:
            print("  No keywords extracted")
        
        # Analyze positive reviews for strengths
        if len(positive_reviews) > 0:
            print(f"\n⭐ POSITIVE FEEDBACK KEYWORDS:")
            positive_texts = positive_reviews['review_text'].tolist()
            positive_keywords = self.extract_keywords_tfidf(positive_texts)
            
            if positive_keywords:
                for keyword, score in positive_keywords[:5]:
                    print(f"  '{keyword}': {score:.3f}")
        
        return theme_counts

def generate_thematic_report(df):
    """Generate comprehensive thematic analysis report"""
    print("🚀 Starting Thematic Analysis...")
    analyzer = ThematicAnalyzer()
    
    print("=" * 60)
    print("📊 COMPREHENSIVE THEMATIC ANALYSIS")
    print("=" * 60)
    
    # Analyze each bank
    bank_themes = {}
    for bank in df['bank'].unique():
        bank_themes[bank] = analyzer.analyze_bank_themes(df, bank)
    
    # Comparative analysis
    print("\n" + "=" * 60)
    print("🏆 COMPARATIVE ANALYSIS - TOP PAIN POINTS")
    print("=" * 60)
    
    # Find top pain points across banks
    all_pain_points = []
    for bank, themes in bank_themes.items():
        top_theme = themes.most_common(1)
        if top_theme:
            all_pain_points.append((bank, top_theme[0][0], top_theme[0][1]))
    
    print("\nMOST FREQUENT PAIN POINT PER BANK:")
    for bank, theme, count in sorted(all_pain_points, key=lambda x: x[2], reverse=True):
        print(f"  {bank}: {theme} ({count} complaints)")
    
    return bank_themes

if __name__ == "__main__":
    # Load data with sentiment
    df = pd.read_csv('data/processed/reviews_with_sentiment.csv')
    
    # Generate thematic report
    bank_themes = generate_thematic_report(df)
    
    # Save results with themes
    analyzer = ThematicAnalyzer()
    df['themes'] = df['review_text'].apply(analyzer.categorize_review_themes)
    df.to_csv('data/processed/reviews_with_sentiment_themes.csv', index=False)
    
    print(f"\n💾 Results saved to: data/processed/reviews_with_sentiment_themes.csv")
    print(f"\n✅ Thematic analysis completed! Ready for database storage and visualization.")