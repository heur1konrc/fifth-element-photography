"""
Inline database export functions for app.py
Avoids import issues
"""

import sqlite3
import json
from datetime import datetime

def export_pricing_database():
    """Export pricing database to JSON - inline version"""
    try:
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'categories': [],
            'products': [],
            'product_variants': [],
            'sub_options': [],
            'settings': {},
            'statistics': {}
        }
        
        # Export categories
        cursor.execute("SELECT * FROM categories ORDER BY id")
        export_data['categories'] = [dict(row) for row in cursor.fetchall()]
        
        # Export all products
        cursor.execute("SELECT * FROM products ORDER BY category_id, size")
        export_data['products'] = [dict(row) for row in cursor.fetchall()]
        
        # Export product variants
        cursor.execute("SELECT * FROM product_variants ORDER BY product_id")
        export_data['product_variants'] = [dict(row) for row in cursor.fetchall()]
        
        # Export sub_options
        cursor.execute("SELECT * FROM sub_options ORDER BY product_type_id, level, display_order")
        export_data['sub_options'] = [dict(row) for row in cursor.fetchall()]
        
        # Export settings
        cursor.execute("SELECT * FROM settings")
        for row in cursor.fetchall():
            export_data['settings'][row['key']] = row['value']
        
        # Calculate statistics
        cursor.execute("""
            SELECT 
                c.name as category,
                COUNT(p.id) as product_count,
                MIN(p.cost_price) as min_cost,
                MAX(p.cost_price) as max_cost,
                AVG(p.cost_price) as avg_cost,
                MIN(p.price) as min_price,
                MAX(p.price) as max_price,
                AVG(p.price) as avg_price
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            GROUP BY c.id
            ORDER BY c.id
        """)
        export_data['statistics']['by_category'] = [dict(row) for row in cursor.fetchall()]
        
        # Total counts
        cursor.execute("SELECT COUNT(*) as total FROM products WHERE active = 1")
        export_data['statistics']['total_active_products'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM products")
        export_data['statistics']['total_products'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM categories")
        export_data['statistics']['total_categories'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM product_variants")
        export_data['statistics']['total_variants'] = cursor.fetchone()['total']
        
        conn.close()
        
        return export_data
        
    except Exception as e:
        raise Exception(f"Database export failed: {str(e)}")

