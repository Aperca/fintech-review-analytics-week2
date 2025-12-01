import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_CONFIG

class DatabaseManager:
    def __init__(self, config=None):
        """Initialize database connection"""
        self.config = config or DATABASE_CONFIG
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("✅ Connected to PostgreSQL database!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")
    
    def create_database(self):
        """Create database if it doesn't exist"""
        # Connect to default postgres database to create our db
        temp_config = self.config.copy()
        temp_config['dbname'] = 'postgres'
        
        try:
            conn = psycopg2.connect(**temp_config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.config['dbname'],))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(self.config['dbname'])
                ))
                print(f"✅ Database '{self.config['dbname']}' created successfully!")
            else:
                print(f"✅ Database '{self.config['dbname']}' already exists.")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            return False
    
    def create_tables(self):
        """Create Banks and Reviews tables"""
        if not self.connect():
            return False
        
        try:
            # Create Banks table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS banks (
                    bank_id SERIAL PRIMARY KEY,
                    bank_name VARCHAR(50) NOT NULL UNIQUE,
                    app_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Reviews table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id VARCHAR(100) PRIMARY KEY,
                    bank_id INTEGER REFERENCES banks(bank_id),
                    review_text TEXT NOT NULL,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    review_date DATE,
                    sentiment_label VARCHAR(10),
                    sentiment_score DECIMAL(5,4),
                    themes TEXT,
                    source VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    -- Indexes for faster queries
                    CONSTRAINT fk_bank FOREIGN KEY(bank_id) REFERENCES banks(bank_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for performance
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_bank_id ON reviews(bank_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_sentiment ON reviews(sentiment_label)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(review_date)")
            
            self.conn.commit()
            print("✅ Tables created successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()
    
    def get_schema_info(self):
        """Get information about the database schema"""
        if not self.connect():
            return
        
        try:
            # Get table information
            self.cursor.execute("""
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)
            
            tables = {}
            for table, column, data_type, nullable in self.cursor.fetchall():
                if table not in tables:
                    tables[table] = []
                tables[table].append({
                    'column': column,
                    'type': data_type,
                    'nullable': nullable
                })
            
            print("\n📊 DATABASE SCHEMA:")
            for table, columns in tables.items():
                print(f"\n{table.upper()} TABLE:")
                for col in columns:
                    print(f"  - {col['column']}: {col['type']} ({'NULL' if col['nullable'] == 'YES' else 'NOT NULL'})")
            
            return tables
            
        except Exception as e:
            print(f"Error getting schema: {e}")
            return None
        finally:
            self.close()

def main():
    """Main function to setup database"""
    print("🚀 Setting up PostgreSQL Database...")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # Step 1: Create database
    print("\n1. Creating database...")
    db.create_database()
    
    # Step 2: Create tables
    print("\n2. Creating tables...")
    db.create_tables()
    
    # Step 3: Show schema
    print("\n3. Database schema:")
    db.get_schema_info()
    
    print("\n✅ Database setup completed!")

if __name__ == "__main__":
    main()