# scripts/database_insert.py
import pandas as pd
import psycopg2
from psycopg2 import sql
import sys
import os
from tqdm import tqdm  # For progress bar

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_CONFIG

class DataInserter:
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def insert_banks(self, banks_data):
        """Insert bank information into banks table"""
        try:
            inserted_banks = {}
            
            for bank_name, app_name in banks_data.items():
                # Check if bank already exists
                self.cursor.execute(
                    "SELECT bank_id FROM banks WHERE bank_name = %s",
                    (bank_name,)
                )
                existing = self.cursor.fetchone()
                
                if existing:
                    inserted_banks[bank_name] = existing[0]
                    print(f"  Bank '{bank_name}' already exists (ID: {existing[0]})")
                else:
                    # Insert new bank
                    self.cursor.execute(
                        """
                        INSERT INTO banks (bank_name, app_name)
                        VALUES (%s, %s)
                        RETURNING bank_id
                        """,
                        (bank_name, app_name)
                    )
                    bank_id = self.cursor.fetchone()[0]
                    inserted_banks[bank_name] = bank_id
                    print(f"  ✅ Inserted bank '{bank_name}' (ID: {bank_id})")
            
            self.conn.commit()
            return inserted_banks
            
        except Exception as e:
            print(f"❌ Failed to insert banks: {e}")
            self.conn.rollback()
            return {}
    
    def insert_reviews(self, reviews_df, bank_mapping):
        """Insert reviews data into reviews table in batches"""
        try:
            # Prepare data for insertion
            records = []
            for _, row in reviews_df.iterrows():
                bank_id = bank_mapping.get(row['bank'])
                if bank_id:
                    records.append((
                        row['review_id'],
                        bank_id,
                        row['review_text'],
                        int(row['rating']),
                        row['date'],
                        row.get('sentiment_label', 'NEUTRAL'),
                        float(row.get('sentiment_score', 0.5)),
                        row.get('themes', ''),
                        row.get('source', 'Google Play')
                    ))
            
            print(f"\n📊 Preparing to insert {len(records)} reviews...")
            
            # Insert in batches for performance
            batch_size = 100
            inserted_count = 0
            skipped_count = 0
            
            with tqdm(total=len(records), desc="Inserting reviews") as pbar:
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    # Use executemany for batch insertion
                    self.cursor.executemany("""
                        INSERT INTO reviews 
                        (review_id, bank_id, review_text, rating, review_date, 
                         sentiment_label, sentiment_score, themes, source)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (review_id) DO NOTHING
                    """, batch)
                    
                    inserted_count += self.cursor.rowcount
                    pbar.update(len(batch))
            
            self.conn.commit()
            
            print(f"\n✅ Inserted {inserted_count} new reviews")
            print(f"⚠️  Skipped {len(records) - inserted_count} duplicate reviews")
            
            return inserted_count
            
        except Exception as e:
            print(f"❌ Failed to insert reviews: {e}")
            self.conn.rollback()
            return 0
    
    def verify_data(self):
        """Verify data integrity with SQL queries"""
        try:
            print("\n" + "=" * 50)
            print("🔍 VERIFYING DATA INTEGRITY")
            print("=" * 50)
            
            queries = {
                "Total Reviews": "SELECT COUNT(*) FROM reviews",
                "Reviews per Bank": """
                    SELECT b.bank_name, COUNT(r.review_id) as review_count
                    FROM banks b
                    LEFT JOIN reviews r ON b.bank_id = r.bank_id
                    GROUP BY b.bank_name
                    ORDER BY review_count DESC
                """,
                "Average Rating per Bank": """
                    SELECT b.bank_name, 
                           ROUND(AVG(r.rating), 2) as avg_rating,
                           COUNT(r.review_id) as review_count
                    FROM banks b
                    JOIN reviews r ON b.bank_id = r.bank_id
                    GROUP BY b.bank_name
                    ORDER BY avg_rating DESC
                """,
                "Sentiment Distribution": """
                    SELECT sentiment_label, COUNT(*) as count,
                           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
                    FROM reviews
                    GROUP BY sentiment_label
                    ORDER BY count DESC
                """,
                "Rating Distribution": """
                    SELECT rating, COUNT(*) as count,
                           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
                    FROM reviews
                    GROUP BY rating
                    ORDER BY rating
                """,
                "Date Range": """
                    SELECT MIN(review_date) as earliest, 
                           MAX(review_date) as latest,
                           COUNT(DISTINCT review_date) as days_with_reviews
                    FROM reviews
                """
            }
            
            for query_name, query in queries.items():
                print(f"\n📊 {query_name}:")
                self.cursor.execute(query)
                results = self.cursor.fetchall()
                
                if len(results[0]) == 1:
                    # Single value result
                    print(f"  Result: {results[0][0]}")
                else:
                    # Multiple columns
                    for row in results:
                        print(f"  {row}")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def export_schema(self, filename="database_schema.sql"):
        """Export database schema to SQL file"""
        try:
            self.cursor.execute("""
                SELECT table_name, column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)
            
            schema = []
            current_table = None
            
            for table, column, data_type, nullable, default in self.cursor.fetchall():
                if table != current_table:
                    if current_table:
                        schema.append(");\n")
                    schema.append(f"CREATE TABLE {table} (\n")
                    current_table = table
                
                line = f"  {column} {data_type}"
                if nullable == 'NO':
                    line += " NOT NULL"
                if default:
                    line += f" DEFAULT {default}"
                line += ","
                schema.append(line + "\n")
            
            if current_table:
                schema.append(");\n")
            
            # Write to file
            with open(filename, 'w') as f:
                f.writelines(schema)
            
            print(f"✅ Schema exported to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to export schema: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def main():
    """Main function to insert data into database"""
    print("🚀 Inserting Data into PostgreSQL...")
    print("=" * 50)
    
    # Load the analyzed data
    data_file = 'data/processed/reviews_with_sentiment_themes.csv'
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("Please run sentiment and thematic analysis first.")
        return
    
    print("1. Loading analyzed data...")
    df = pd.read_csv(data_file)
    print(f"   Loaded {len(df)} reviews from CSV")
    
    # Create bank mapping from config
    from config import BANK_APPS
    banks_data = {bank: app_id for bank, app_id in BANK_APPS.items()}
    
    # Initialize inserter
    inserter = DataInserter()
    
    if not inserter.connect():
        return
    
    try:
        # Step 1: Insert banks
        print("\n2. Inserting banks...")
        bank_mapping = inserter.insert_banks(banks_data)
        
        if not bank_mapping:
            print("❌ Failed to insert banks")
            return
        
        # Step 2: Insert reviews
        print("\n3. Inserting reviews...")
        inserted_count = inserter.insert_reviews(df, bank_mapping)
        
        if inserted_count == 0:
            print("❌ No reviews inserted")
            return
        
        # Step 3: Verify data
        print("\n4. Verifying data integrity...")
        inserter.verify_data()
        
        # Step 4: Export schema
        print("\n5. Exporting schema...")
        inserter.export_schema("database/schema.sql")
        
        print("\n" + "=" * 50)
        print("✅ DATABASE POPULATION COMPLETED!")
        print(f"   Total reviews in database: {inserted_count}")
        print("=" * 50)
        
        # KPI Check
        print("\n🎯 KPI VERIFICATION:")
        print(f"  Working database connection: ✅ YES")
        print(f"  Tables populated: ✅ YES")
        print(f"  Reviews inserted: {inserted_count}/1000 - {'✅ MET' if inserted_count >= 1000 else '❌ NOT MET'}")
        
    finally:
        inserter.close()

if __name__ == "__main__":
    # Install tqdm for progress bar if not installed
    try:
        from tqdm import tqdm
    except ImportError:
        print("Installing tqdm for progress bar...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
        from tqdm import tqdm
    
    main()