"""
Database Migration: Add category column to shopify_products table
Fifth Element Photography - v2.3.3
"""

from flask import Blueprint, jsonify
import sqlite3
import os

migrate_category_bp = Blueprint('migrate_category', __name__)

DB_PATH = '/data/print_ordering.db' if os.path.exists('/data') else os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'print_ordering.db')

@migrate_category_bp.route('/admin/migrate/add-category-column')
def migrate_add_category_column():
    """
    Migration: Add category column to shopify_products table
    Safe to run multiple times (checks if column exists first)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if category column already exists
        cursor.execute("PRAGMA table_info(shopify_products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'category' in columns:
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Category column already exists - no migration needed',
                'already_exists': True
            })
        
        # Step 1: Create new table with category column
        cursor.execute("""
            CREATE TABLE shopify_products_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_filename TEXT NOT NULL,
                category TEXT NOT NULL,
                shopify_product_id TEXT NOT NULL,
                shopify_handle TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(image_filename, category)
            )
        """)
        
        # Step 2: Copy existing data (extract category from filename if it exists)
        cursor.execute("SELECT * FROM shopify_products")
        old_rows = cursor.fetchall()
        
        migrated_count = 0
        for row in old_rows:
            old_id, image_filename, shopify_product_id, shopify_handle, created_at, updated_at = row
            
            # Try to extract category from filename (format: "filename_Category")
            category = 'Canvas'  # Default
            if '_Canvas' in image_filename:
                category = 'Canvas'
                image_filename = image_filename.replace('_Canvas', '')
            elif '_Metal' in image_filename:
                category = 'Metal'
                image_filename = image_filename.replace('_Metal', '')
            elif '_Fine Art Paper' in image_filename:
                category = 'Fine Art Paper'
                image_filename = image_filename.replace('_Fine Art Paper', '')
            elif '_Framed Canvas' in image_filename:
                category = 'Framed Canvas'
                image_filename = image_filename.replace('_Framed Canvas', '')
            elif '_Foam-mounted Print' in image_filename:
                category = 'Foam-mounted Print'
                image_filename = image_filename.replace('_Foam-mounted Print', '')
            
            cursor.execute("""
                INSERT INTO shopify_products_new (image_filename, category, shopify_product_id, shopify_handle, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (image_filename, category, shopify_product_id, shopify_handle, created_at, updated_at))
            
            migrated_count += 1
        
        # Step 3: Drop old table and rename new table
        cursor.execute("DROP TABLE shopify_products")
        cursor.execute("ALTER TABLE shopify_products_new RENAME TO shopify_products")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Migration complete! Added category column and migrated {migrated_count} rows.',
            'migrated_rows': migrated_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
