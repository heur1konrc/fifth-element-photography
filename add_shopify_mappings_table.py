#!/usr/bin/env python3
"""
Database Migration Script: Add shopify_mappings table
Run this script on Railway to add the shopify_mappings table to the database.

Usage: python3 add_shopify_mappings_table.py
"""

import sqlite3
import os

def add_shopify_mappings_table():
    """Add shopify_mappings table to the database"""
    
    # Database path on Railway
    db_path = '/data/lumaprints_pricing.db'
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='shopify_mappings'")
        if cursor.fetchone():
            print("✓ Table 'shopify_mappings' already exists")
            conn.close()
            return True
        
        # Create the table
        cursor.execute('''
            CREATE TABLE shopify_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_filename TEXT UNIQUE NOT NULL,
                shopify_product_handle TEXT,
                order_prints_enabled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✓ Successfully created 'shopify_mappings' table")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create table: {e}")
        return False

if __name__ == '__main__':
    print("Running database migration...")
    success = add_shopify_mappings_table()
    if success:
        print("\n✓ Migration completed successfully!")
    else:
        print("\n✗ Migration failed!")
        exit(1)

