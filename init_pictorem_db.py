"""
Initialize Pictorem Database
Creates database and populates with products if it doesn't exist
"""

import sqlite3
import os

DB_PATH = '/data/pictorem.db'

def init_pictorem_database(force=False):
    """Initialize Pictorem database with schema and data"""
    
    # If force=True, delete existing database
    if force and os.path.exists(DB_PATH):
        print(f"Force re-initialize: Deleting existing database at {DB_PATH}")
        os.remove(DB_PATH)
    
    # Check if database already exists and is populated
    if os.path.exists(DB_PATH) and not force:
        # Check if it has tables
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            if len(tables) > 0:
                print(f"Pictorem database already exists and is populated at {DB_PATH}")
                return True
            else:
                print(f"Database exists but is empty, will populate...")
        except:
            print(f"Database exists but has errors, will recreate...")
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
    
    print(f"Creating Pictorem database at {DB_PATH}...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Read and execute schema
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_path = os.path.join(script_dir, 'create_pictorem_db.sql')
        
        if not os.path.exists(sql_path):
            raise FileNotFoundError(f"SQL schema file not found at {sql_path}")
        
        with open(sql_path, 'r') as f:
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
        
        # Verify it worked
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pictorem_products")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Verified: {count} products in database")
        
        return True
        
    except Exception as e:
        error_msg = f"❌ Error initializing Pictorem database: {e}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        
        # Return detailed error info
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        }

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

