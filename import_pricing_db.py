"""
Import pricing database from JSON export
Can be used to sync data between Railway and sandbox, or restore backups
"""

import sqlite3
import json
import sys
from datetime import datetime

def create_tables(conn):
    """Create database tables if they don't exist"""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            display_order INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            product_type_id INTEGER NOT NULL,
            display_order INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            product_type_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            size TEXT NOT NULL,
            cost_price REAL NOT NULL,
            retail_price REAL NOT NULL,
            lumaprints_subcategory_id INTEGER,
            lumaprints_options TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    conn.commit()

def import_database(json_file, db_path='/data/lumaprints_pricing.db', clear_existing=False):
    """Import database from JSON file"""
    
    # Read JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"Importing data exported at: {data.get('exported_at', 'Unknown')}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    create_tables(conn)
    
    # Clear existing data if requested
    if clear_existing:
        print("Clearing existing data...")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM product_types")
        cursor.execute("DELETE FROM settings")
        conn.commit()
    
    # Import product types
    print(f"Importing {len(data['product_types'])} product types...")
    for pt in data['product_types']:
        cursor.execute("""
            INSERT OR REPLACE INTO product_types (id, name, display_order)
            VALUES (?, ?, ?)
        """, (pt['id'], pt['name'], pt['display_order']))
    
    # Import categories
    print(f"Importing {len(data['categories'])} categories...")
    for cat in data['categories']:
        cursor.execute("""
            INSERT OR REPLACE INTO categories (id, name, product_type_id, display_order)
            VALUES (?, ?, ?, ?)
        """, (cat['id'], cat['name'], cat['product_type_id'], cat['display_order']))
    
    # Import products
    print(f"Importing {len(data['products'])} products...")
    for prod in data['products']:
        cursor.execute("""
            INSERT OR REPLACE INTO products 
            (id, name, product_type_id, category_id, size, cost_price, retail_price, 
             lumaprints_subcategory_id, lumaprints_options, active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prod['id'], prod['name'], prod['product_type_id'], prod['category_id'],
            prod['size'], prod['cost_price'], prod['retail_price'],
            prod.get('lumaprints_subcategory_id'), prod.get('lumaprints_options'),
            prod.get('active', 1), prod.get('created_at'), prod.get('updated_at')
        ))
    
    # Import settings
    print(f"Importing {len(data['settings'])} settings...")
    for key, value in data['settings'].items():
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        """, (key, value))
    
    conn.commit()
    conn.close()
    
    print("\n✅ Import complete!")
    print(f"   Product types: {len(data['product_types'])}")
    print(f"   Categories: {len(data['categories'])}")
    print(f"   Products: {len(data['products'])}")
    print(f"   Database: {db_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_pricing_db.py <json_file> [db_path] [--clear]")
        print("\nExamples:")
        print("  python import_pricing_db.py /tmp/pricing_db_export.json")
        print("  python import_pricing_db.py export.json /data/lumaprints_pricing.db")
        print("  python import_pricing_db.py export.json /tmp/test.db --clear")
        sys.exit(1)
    
    json_file = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else '/data/lumaprints_pricing.db'
    clear_existing = '--clear' in sys.argv
    
    import_database(json_file, db_path, clear_existing)

