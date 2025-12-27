import sqlite3
import os

# Define database path
if os.path.exists('/data'):
    DB_PATH = '/data/lumaprints_pricing.db'
else:
    # Fallback for local dev
    DB_PATH = '/home/ubuntu/fifth-element-photography/data/lumaprints_pricing.db'

print(f"Fixing database at: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop the broken table
    print("Dropping 'shopify_products' table...")
    cursor.execute("DROP TABLE IF EXISTS shopify_products")
    
    # Recreate it with correct schema
    print("Recreating 'shopify_products' table...")
    cursor.execute("""
        CREATE TABLE shopify_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            category TEXT,
            shopify_product_id TEXT NOT NULL,
            shopify_handle TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(image_filename, category)
        )
    """)
    
    conn.commit()
    print("✓ Success! Table recreated with correct schema.")
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
