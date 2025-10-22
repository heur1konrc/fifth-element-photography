"""
Diagnostic endpoint to check database status for print order system
"""

from flask import jsonify
import sqlite3
import os

DB_PATH = '/data/lumaprints_pricing.db'

def register_print_diagnostic_routes(app):
    """Register diagnostic routes for print order system"""
    
    @app.route('/api/print-order/diagnostic')
    def print_order_diagnostic():
        """Diagnostic endpoint to check database status"""
        try:
            # Check if database file exists
            db_exists = os.path.exists(DB_PATH)
            db_size = os.path.getsize(DB_PATH) if db_exists else 0
            
            # Try to connect and query
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get product count
            cursor.execute("SELECT COUNT(*) FROM products")
            product_count = cursor.fetchone()[0]
            
            # Get active product count
            cursor.execute("SELECT COUNT(*) FROM products WHERE active = 1")
            active_count = cursor.fetchone()[0]
            
            # Get sample product
            cursor.execute("SELECT * FROM products LIMIT 1")
            columns = [description[0] for description in cursor.description]
            sample_row = cursor.fetchone()
            sample_product = dict(zip(columns, sample_row)) if sample_row else None
            
            # Get product type count
            cursor.execute("SELECT COUNT(*) FROM product_types")
            product_type_count = cursor.fetchone()[0]
            
            # Get category count
            cursor.execute("SELECT COUNT(*) FROM categories")
            category_count = cursor.fetchone()[0]
            
            conn.close()
            
            return jsonify({
                'success': True,
                'database': {
                    'path': DB_PATH,
                    'exists': db_exists,
                    'size_bytes': db_size,
                    'size_mb': round(db_size / 1024 / 1024, 2)
                },
                'tables': tables,
                'counts': {
                    'total_products': product_count,
                    'active_products': active_count,
                    'product_types': product_type_count,
                    'categories': category_count
                },
                'sample_product': sample_product,
                'schema_columns': columns
            })
            
        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'database': {
                    'path': DB_PATH,
                    'exists': os.path.exists(DB_PATH) if os.path.exists('/data') else 'data_dir_missing'
                }
            }), 500

