# scripts/database_queries.py
import psycopg2
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_CONFIG

class DatabaseQueries:
    def __init__(self):
        self.config = DATABASE_CONFIG
    
    def execute_query(self, query, params=None, return_df=True):
        """Execute SQL query and return results"""
        try:
            conn = psycopg2.connect(**self.config)
            if return_df:
                df = pd.read_sql_query(query, conn, params=params)
                conn.close()
                return df
            else:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                conn.close()
                return results, columns
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return None
    
    def get_business_insights(self):
        """Execute business-relevant queries"""
        print("📊 BUSINESS INSIGHTS FROM DATABASE")
        print("=" * 50)
        
        queries = {
            "1. Top Pain Points by Bank": """
                SELECT 
                    b.bank_name,
                    UNNEST(STRING_TO_ARRAY(r.themes, ', ')) as theme,
                    COUNT(*) as complaint_count
                FROM reviews r
                JOIN banks b ON r.bank_id = b.bank_id
                WHERE r.sentiment_label = 'NEGATIVE'
                    AND r.themes != 'Other'
                    AND r.themes != ''
                GROUP BY b.bank_name, theme
                ORDER BY b.bank_name, complaint_count DESC
            """,
            
            "2. Monthly Sentiment Trends": """
                SELECT 
                    b.bank_name,
                    DATE_TRUNC('month', r.review_date) as month,
                    AVG(CASE WHEN r.sentiment_label = 'POSITIVE' THEN 1 ELSE 0 END) * 100 as positive_percentage,
                    COUNT(*) as review_count
                FROM reviews r
                JOIN banks b ON r.bank_id = b.bank_id
                GROUP BY b.bank_name, DATE_TRUNC('month', r.review_date)
                ORDER BY b.bank_name, month DESC
            """,
            
            "3. Rating vs Sentiment Analysis": """
                SELECT 
                    r.rating,
                    r.sentiment_label,
                    COUNT(*) as count,
                    ROUND(AVG(r.sentiment_score), 3) as avg_confidence
                FROM reviews r
                GROUP BY r.rating, r.sentiment_label
                ORDER BY r.rating, r.sentiment_label
            """,
            
            "4. Most Common Themes in 1-Star Reviews": """
                SELECT 
                    b.bank_name,
                    UNNEST(STRING_TO_ARRAY(r.themes, ', ')) as theme,
                    COUNT(*) as count
                FROM reviews r
                JOIN banks b ON r.bank_id = b.bank_id
                WHERE r.rating = 1
                    AND r.themes != 'Other'
                    AND r.themes != ''
                GROUP BY b.bank_name, theme
                ORDER BY count DESC
                LIMIT 10
            """,
            
            "5. Bank Performance Comparison": """
                SELECT 
                    b.bank_name,
                    COUNT(r.review_id) as total_reviews,
                    ROUND(AVG(r.rating), 2) as avg_rating,
                    ROUND(AVG(CASE WHEN r.sentiment_label = 'POSITIVE' THEN 1 ELSE 0 END) * 100, 1) as positive_percentage,
                    ROUND(AVG(r.sentiment_score), 3) as avg_sentiment_confidence
                FROM banks b
                LEFT JOIN reviews r ON b.bank_id = r.bank_id
                GROUP BY b.bank_name
                ORDER BY avg_rating DESC
            """
        }
        
        for name, query in queries.items():
            print(f"\n{name}:")
            df = self.execute_query(query)
            if df is not None and not df.empty:
                print(df.to_string(index=False))
            print("-" * 50)

def main():
    """Run business insights queries"""
    print("🚀 Running Business Intelligence Queries...")
    
    db_queries = DatabaseQueries()
    
    # Test connection
    test_df = db_queries.execute_query("SELECT COUNT(*) as total_reviews FROM reviews")
    if test_df is not None:
        print(f"✅ Database connection successful")
        print(f"📊 Total reviews in database: {test_df.iloc[0]['total_reviews']}")
        
        # Run business insights
        db_queries.get_business_insights()
    else:
        print("❌ Failed to connect to database")

if __name__ == "__main__":
    main()