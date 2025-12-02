# scripts/visualizations.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set style for professional plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class BankVisualizations:
    def __init__(self):
        # Load data directly from database or CSV
        self.data_file = 'data/processed/reviews_with_sentiment_themes.csv'
        self.df = pd.read_csv(self.data_file)
        
        # Bank color mapping
        self.bank_colors = {
            'CBE': '#2E86AB',  # Blue
            'BOA': '#A23B72',  # Purple
            'Dashen': '#F18F01'  # Orange
        }
    
    def plot_sentiment_comparison(self):
        """Plot 1: Sentiment comparison across banks"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Subplot 1: Sentiment distribution
        sentiment_counts = self.df.groupby(['bank', 'sentiment_label']).size().unstack()
        sentiment_counts.plot(kind='bar', ax=ax1, color=['#FF6B6B', '#4ECDC4'])
        ax1.set_title('Sentiment Distribution by Bank', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Bank', fontsize=12)
        ax1.set_ylabel('Number of Reviews', fontsize=12)
        ax1.legend(['Negative', 'Positive'], title='Sentiment')
        ax1.tick_params(axis='x', rotation=45)
        
        # Subplot 2: Average rating comparison
        avg_rating = self.df.groupby('bank')['rating'].mean().sort_values(ascending=False)
        bars = ax2.bar(avg_rating.index, avg_rating.values, 
                       color=[self.bank_colors[b] for b in avg_rating.index])
        ax2.set_title('Average Star Rating by Bank', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Bank', fontsize=12)
        ax2.set_ylabel('Average Rating (1-5 stars)', fontsize=12)
        ax2.set_ylim(0, 5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('visualizations/sentiment_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Saved: sentiment_comparison.png")
    
    def plot_pain_points_analysis(self):
        """Plot 2: Pain points analysis for each bank"""
        # Extract themes from negative reviews
        negative_reviews = self.df[self.df['sentiment_label'] == 'NEGATIVE']
        
        # Parse themes into list
        negative_reviews['theme_list'] = negative_reviews['themes'].apply(
            lambda x: [theme.strip() for theme in str(x).split(',') if theme.strip() != 'Other']
        )
        
        # Explode themes into separate rows
        exploded = negative_reviews.explode('theme_list')
        theme_counts = exploded.groupby(['bank', 'theme_list']).size().unstack(fill_value=0)
        
        # Plot
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for idx, (bank, color) in enumerate(self.bank_colors.items()):
            if bank in theme_counts.index:
                bank_themes = theme_counts.loc[bank]
                top_themes = bank_themes.nlargest(5)
                
                axes[idx].barh(range(len(top_themes)), top_themes.values, color=color)
                axes[idx].set_yticks(range(len(top_themes)))
                axes[idx].set_yticklabels(top_themes.index, fontsize=10)
                axes[idx].invert_yaxis()
                axes[idx].set_title(f'{bank} - Top 5 Pain Points', fontsize=12, fontweight='bold')
                axes[idx].set_xlabel('Number of Complaints', fontsize=10)
                
                # Add count labels
                for i, v in enumerate(top_themes.values):
                    axes[idx].text(v + 1, i, str(v), va='center', fontweight='bold')
        
        plt.suptitle('Top Pain Points by Bank (Negative Reviews)', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig('visualizations/pain_points_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Saved: pain_points_analysis.png")
    
    def plot_rating_distribution(self):
        """Plot 3: Detailed rating distribution"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for idx, bank in enumerate(self.bank_colors.keys()):
            bank_data = self.df[self.df['bank'] == bank]
            rating_counts = bank_data['rating'].value_counts().sort_index()
            
            # Create donut chart
            ax = axes[idx]
            colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, 5))  # Red to Green
            wedges, texts, autotexts = ax.pie(rating_counts.values, 
                                              labels=rating_counts.index,
                                              colors=colors,
                                              autopct='%1.1f%%',
                                              startangle=90,
                                              wedgeprops=dict(width=0.3))
            
            ax.set_title(f'{bank} - Rating Distribution', fontsize=12, fontweight='bold')
            
            # Make percentage text bold
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        plt.suptitle('Star Rating Distribution by Bank', fontsize=16, fontweight='bold', y=1.05)
        plt.tight_layout()
        plt.savefig('visualizations/rating_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Saved: rating_distribution.png")
    
    def create_word_clouds(self):
        """Plot 4: Word clouds for each bank"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for idx, (bank, color) in enumerate(self.bank_colors.items()):
            bank_reviews = self.df[self.df['bank'] == bank]
            negative_text = ' '.join(bank_reviews[bank_reviews['sentiment_label'] == 'NEGATIVE']['review_text'])
            positive_text = ' '.join(bank_reviews[bank_reviews['sentiment_label'] == 'POSITIVE']['review_text'])
            
            # Create word cloud
            wordcloud = WordCloud(
                width=400, height=300,
                background_color='white',
                colormap='Reds' if bank == 'BOA' else ('Blues' if bank == 'CBE' else 'Oranges'),
                max_words=50,
                contour_width=1,
                contour_color='steelblue'
            ).generate(negative_text if len(negative_text) > 100 else positive_text)
            
            axes[idx].imshow(wordcloud, interpolation='bilinear')
            axes[idx].axis('off')
            axes[idx].set_title(f'{bank} - Common Keywords', fontsize=12, fontweight='bold')
        
        plt.suptitle('Word Cloud Analysis of Reviews', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig('visualizations/word_clouds.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Saved: word_clouds.png")
    
    def plot_monthly_trends(self):
        """Plot 5: Monthly sentiment trends"""
        # Convert date and extract month-year
        self.df['review_date'] = pd.to_datetime(self.df['date'])
        self.df['month_year'] = self.df['review_date'].dt.to_period('M')
        
        # Calculate monthly positive percentage
        monthly_stats = self.df.groupby(['bank', 'month_year']).agg(
            total_reviews=('review_id', 'count'),
            positive_percentage=('sentiment_label', lambda x: (x == 'POSITIVE').mean() * 100)
        ).reset_index()
        
        # Convert period to datetime for plotting
        monthly_stats['month_date'] = monthly_stats['month_year'].dt.to_timestamp()
        
        # Plot
        fig, ax = plt.subplots(figsize=(14, 7))
        
        for bank, color in self.bank_colors.items():
            bank_data = monthly_stats[monthly_stats['bank'] == bank]
            if len(bank_data) > 0:
                ax.plot(bank_data['month_date'], bank_data['positive_percentage'], 
                       label=bank, color=color, linewidth=2.5, marker='o', markersize=6)
        
        ax.set_title('Monthly Positive Sentiment Trends', fontsize=16, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Positive Reviews (%)', fontsize=12)
        ax.legend(title='Bank', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('visualizations/monthly_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✅ Saved: monthly_trends.png")
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("🚀 Generating Business Visualizations...")
        print("=" * 60)
        
        # Create visualizations directory
        os.makedirs('visualizations', exist_ok=True)
        
        # Generate plots
        self.plot_sentiment_comparison()
        self.plot_pain_points_analysis()
        self.plot_rating_distribution()
        self.create_word_clouds()
        self.plot_monthly_trends()
        
        print("\n" + "=" * 60)
        print("✅ All visualizations generated successfully!")
        print("📁 Check the 'visualizations/' folder for PNG files")
        print("=" * 60)

if __name__ == "__main__":
    # Generate all visualizations
    viz = BankVisualizations()
    viz.generate_all_visualizations()