"""
Initialize Pictorem Database
Creates database and populates with products if it doesn't exist
"""

import sqlite3
import os

DB_PATH = '/data/pictorem.db'

def init_pictorem_database():
    """Initialize Pictorem database with schema and data"""
    
    # Check if database already exists
    if os.path.exists(DB_PATH):
        print(f"Pictorem database already exists at {DB_PATH}")
        return True
    
    print(f"Creating Pictorem database at {DB_PATH}...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Read and execute schema
        with open('create_pictorem_db.sql', 'r') as f:
            schema = f.read()
            cursor.executescript(schema)
        
        print("✅ Database schema created")
        
        # Import products
        from import_pictorem_products import populate_database
        populate_database(DB_PATH)
        
        print("✅ Products imported")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Pictorem database initialized successfully at {DB_PATH}")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Pictorem database: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_status():
    """Check if database exists and is populated"""
    if not os.path.exists(DB_PATH):
        return {
            'exists': False,
            'path': DB_PATH,
            'message': 'Database does not exist'
        }
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Count records
        stats = {}
        for table in ['pictorem_categories', 'pictorem_products', 'pictorem_sizes', 'pictorem_product_options']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'exists': True,
            'path': DB_PATH,
            'tables': tables,
            'stats': stats,
            'message': 'Database is initialized and populated'
        }
        
    except Exception as e:
        return {
            'exists': True,
            'path': DB_PATH,
            'error': str(e),
            'message': 'Database exists but has errors'
        }

if __name__ == '__main__':
    init_pictorem_database()

