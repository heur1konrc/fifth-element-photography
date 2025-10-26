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
            'product_types': [],
            'categories': [],
            'products': [],
            'settings': {},
            'statistics': {}
        }
        
        # Export product types
        cursor.execute("SELECT * FROM product_types ORDER BY display_order")
        export_data['product_types'] = [dict(row) for row in cursor.fetchall()]
        
        # Export categories
        cursor.execute("SELECT * FROM categories ORDER BY product_type_id, display_order")
        export_data['categories'] = [dict(row) for row in cursor.fetchall()]
        
        # Export all products
        cursor.execute("SELECT * FROM products ORDER BY category_id, size")
        export_data['products'] = [dict(row) for row in cursor.fetchall()]
        
        # Export settings
        cursor.execute("SELECT * FROM settings")
        for row in cursor.fetchall():
            export_data['settings'][row['key']] = row['value']
        
        # Calculate statistics
        cursor.execute("""
            SELECT 
                pt.name as product_type,
                c.name as category,
                COUNT(p.id) as product_count,
                MIN(p.cost_price) as min_cost,
                MAX(p.cost_price) as max_cost,
                AVG(p.cost_price) as avg_cost
            FROM product_types pt
            LEFT JOIN categories c ON pt.id = c.product_type_id
            LEFT JOIN products p ON c.id = p.category_id
            GROUP BY pt.id, c.id
            ORDER BY pt.display_order, c.display_order
        """)
        export_data['statistics']['by_category'] = [dict(row) for row in cursor.fetchall()]
        
        # Total counts
        cursor.execute("SELECT COUNT(*) as total FROM products")
        export_data['statistics']['total_products'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM categories")
        export_data['statistics']['total_categories'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM product_types")
        export_data['statistics']['total_product_types'] = cursor.fetchone()['total']
        
        conn.close()
        
        return export_data
        
    except Exception as e:
        raise Exception(f"Database export failed: {str(e)}")

