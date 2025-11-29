# scripts/sentiment_analysis.py
import pandas as pd
import numpy as np
import sys
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_PATHS

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the sentiment analysis pipeline with DistilBERT"""
        print("🔄 Loading DistilBERT sentiment model...")
        self.model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=self.model_name,
            tokenizer=self.model_name,
            truncation=True,
            max_length=512
        )
        print("✅ Sentiment model loaded successfully!")
    
    def analyze_sentiment_batch(self, texts):
        """Analyze sentiment for a batch of texts"""
        try:
            results = self.sentiment_pipeline(texts)
            return results
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return [{"label": "NEUTRAL", "score": 0.0}] * len(texts)
    
    def analyze_reviews(self, df, batch_size=32):
        """Analyze sentiment for all reviews in batches"""
        print(f"🔍 Analyzing sentiment for {len(df)} reviews...")
        
        sentiments = []
        confidence_scores = []
        
        # Process in batches to avoid memory issues
        for i in range(0, len(df), batch_size):
            batch_texts = df['review_text'].iloc[i:i+batch_size].tolist()
            batch_results = self.analyze_sentiment_batch(batch_texts)
            
            for result in batch_results:
                sentiments.append(result['label'])
                confidence_scores.append(result['score'])
            
            if (i // batch_size) % 10 == 0:  # Progress update every 10 batches
                print(f"   Processed {min(i + batch_size, len(df))}/{len(df)} reviews")
        
        # Add results to dataframe
        df['sentiment_label'] = sentiments
        df['sentiment_score'] = confidence_scores
        
        # Convert labels to standard format
        df['sentiment_label'] = df['sentiment_label'].str.upper()
        
        print("✅ Sentiment analysis completed!")
        return df

def generate_sentiment_report(df):
    """Generate comprehensive sentiment analysis report"""
    print("\n" + "="*60)
    print("📊 SENTIMENT ANALYSIS REPORT")
    print("="*60)
    
    # Overall sentiment distribution
    print("\nOverall Sentiment Distribution:")
    sentiment_counts = df['sentiment_label'].value_counts()
    for sentiment, count in sentiment_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {sentiment}: {count} reviews ({percentage:.1f}%)")
    
    # Sentiment by bank
    print("\nSentiment by Bank:")
    bank_sentiment = pd.crosstab(df['bank'], df['sentiment_label'], normalize='index') * 100
    print(bank_sentiment.round(1))
    
    # Sentiment by rating
    print("\nSentiment by Star Rating:")
    rating_sentiment = pd.crosstab(df['rating'], df['sentiment_label'])
    print(rating_sentiment)
    
    # Average sentiment score by bank
    print("\nAverage Sentiment Confidence by Bank:")
    avg_confidence = df.groupby('bank')['sentiment_score'].mean().round(3)
    print(avg_confidence)
    
    return df

if __name__ == "__main__":
    # Load cleaned data
    print("🚀 Starting Sentiment Analysis...")
    df = pd.read_csv(DATA_PATHS['cleaned_data'])
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    
    # Analyze sentiment
    df_with_sentiment = analyzer.analyze_reviews(df)
    
    # Generate report
    df_with_sentiment = generate_sentiment_report(df_with_sentiment)
    
    # Save results
    output_path = 'data/processed/reviews_with_sentiment.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_with_sentiment.to_csv(output_path, index=False)
    print(f"\n💾 Results saved to: {output_path}")