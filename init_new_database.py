#!/usr/bin/env python3
"""
Initialize the new simplified database structure for Fifth Element Photography.
This schema is designed to work directly with Lumaprints API.
"""

import sqlite3
import os

DB_PATH = '/data/lumaprints_pricing.db'

def init_new_database():
    """Create the new database structure"""
    
    # Ensure /data directory exists
    os.makedirs('/data', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop old views and tables if they exist
    print("Dropping old views and tables...")
    cursor.execute('DROP VIEW IF EXISTS active_products')
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('DROP TABLE IF EXISTS product_types')
    cursor.execute('DROP TABLE IF EXISTS categories')
    cursor.execute('DROP TABLE IF EXISTS settings')
    
    # Create new products table with simplified structure
    print("Creating new products table...")
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            size TEXT NOT NULL,
            price REAL NOT NULL,
            lumaprints_subcategory_id INTEGER NOT NULL,
            lumaprints_frame_option_id INTEGER,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for faster lookups
    print("Creating indexes...")
    cursor.execute('CREATE INDEX idx_category ON products(category)')
    cursor.execute('CREATE INDEX idx_size ON products(size)')
    cursor.execute('CREATE INDEX idx_lumaprints ON products(lumaprints_subcategory_id, lumaprints_frame_option_id)')
    cursor.execute('CREATE INDEX idx_active ON products(active)')
    
    # Create a view for easy querying
    print("Creating views...")
    cursor.execute('''
        CREATE VIEW active_products AS
        SELECT * FROM products WHERE active = 1
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {DB_PATH}")
    print("Ready for product import!")

if __name__ == '__main__':
    init_new_database()

