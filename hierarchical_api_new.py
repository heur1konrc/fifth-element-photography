"""
New Hierarchical API endpoints for simplified Lumaprints database structure.
These endpoints replace the old sub_options system with direct product queries.
"""

import sqlite3
import json
from flask import jsonify, request

DB_PATH = '/data/lumaprints_pricing.db'

def get_hierarchical_product_types_new():
    """Get all product types for hierarchical ordering system"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, display_order
            FROM product_types 
            ORDER BY display_order
        """)
        
        product_types = []
        for row in cursor.fetchall():
            product_types.append({
                'id': row['id'],
                'name': row['name'],
                'display_order': row['display_order']
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'product_types': product_types
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def get_hierarchical_categories_new():
    """Get categories for a specific product type"""
    try:
        product_type_id = request.args.get('product_type_id', type=int)
        
        if not product_type_id:
            return jsonify({
                'success': False,
                'error': 'product_type_id is required'
            }), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT c.id, c.name, c.display_order
            FROM categories c
            INNER JOIN products p ON p.category_id = c.id
            WHERE c.product_type_id = ?
            AND p.active = 1
            ORDER BY c.display_order
        """, (product_type_id,))
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row['id'],
                'name': row['name'],
                'display_order': row['display_order']
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def get_hierarchical_sizes_new():
    """Get available sizes for a specific category"""
    try:
        category_id = request.args.get('category_id', type=int)
        
        if not category_id:
            return jsonify({
                'success': False,
                'error': 'category_id is required'
            }), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get global markup
        cursor.execute("SELECT value FROM settings WHERE key = 'global_markup_percentage'")
        markup_row = cursor.fetchone()
        global_markup = float(markup_row['value']) if markup_row else 0.0
        
        # Get distinct sizes with pricing
        cursor.execute("""
            SELECT DISTINCT 
                p.id,
                p.name,
                p.size,
                p.cost_price,
                p.lumaprints_subcategory_id,
                p.lumaprints_options
            FROM products p
            WHERE p.category_id = ?
            AND p.active = 1
            ORDER BY 
                CAST(SUBSTR(p.size, 1, INSTR(p.size, 'x')-1) AS INTEGER),
                CAST(SUBSTR(p.size, INSTR(p.size, 'x')+1) AS INTEGER)
        """, (category_id,))
        
        sizes = []
        seen_sizes = set()
        
        for row in cursor.fetchall():
            size = row['size']
            if size not in seen_sizes:
                seen_sizes.add(size)
                
                # Calculate retail price with markup
                cost_price = row['cost_price']
                retail_price = cost_price * (1 + global_markup / 100)
                
                sizes.append({
                    'id': row['id'],
                    'size': size,
                    'cost_price': round(cost_price, 2),
                    'retail_price': round(retail_price, 2),
                    'lumaprints_subcategory_id': row['lumaprints_subcategory_id'],
                    'lumaprints_options': row['lumaprints_options']
                })
        
        conn.close()
        return jsonify({
            'success': True,
            'sizes': sizes,
            'global_markup': global_markup
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def get_product_by_selection_new():
    """Get specific product by category and size"""
    try:
        category_id = request.args.get('category_id', type=int)
        size = request.args.get('size')
        
        if not category_id or not size:
            return jsonify({
                'success': False,
                'error': 'category_id and size are required'
            }), 400
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get global markup
        cursor.execute("SELECT value FROM settings WHERE key = 'global_markup_percentage'")
        markup_row = cursor.fetchone()
        global_markup = float(markup_row['value']) if markup_row else 0.0
        
        # Get product
        cursor.execute("""
            SELECT 
                p.id,
                p.name,
                p.size,
                p.cost_price,
                p.lumaprints_subcategory_id,
                p.lumaprints_options,
                pt.name as product_type_name,
                c.name as category_name
            FROM products p
            INNER JOIN product_types pt ON p.product_type_id = pt.id
            INNER JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = ?
            AND p.size = ?
            AND p.active = 1
            LIMIT 1
        """, (category_id, size))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Calculate retail price
        cost_price = row['cost_price']
        retail_price = cost_price * (1 + global_markup / 100)
        
        # Parse Lumaprints options
        lumaprints_options = {}
        if row['lumaprints_options']:
            try:
                lumaprints_options = json.loads(row['lumaprints_options'])
            except:
                pass
        
        product = {
            'id': row['id'],
            'name': row['name'],
            'size': row['size'],
            'cost_price': round(cost_price, 2),
            'retail_price': round(retail_price, 2),
            'product_type': row['product_type_name'],
            'category': row['category_name'],
            'lumaprints_subcategory_id': row['lumaprints_subcategory_id'],
            'lumaprints_options': lumaprints_options
        }
        
        conn.close()
        return jsonify({
            'success': True,
            'product': product,
            'global_markup': global_markup
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def register_hierarchical_routes_new(app):
    """Register new hierarchical API routes"""
    
    @app.route('/api/hierarchical/v2/product-types', methods=['GET'])
    def get_product_types_v2():
        return get_hierarchical_product_types_new()
    
    @app.route('/api/hierarchical/v2/categories', methods=['GET'])
    def get_categories_v2():
        return get_hierarchical_categories_new()
    
    @app.route('/api/hierarchical/v2/sizes', methods=['GET'])
    def get_sizes_v2():
        return get_hierarchical_sizes_new()
    
    @app.route('/api/hierarchical/v2/product', methods=['GET'])
    def get_product_v2():
        return get_product_by_selection_new()

