"""
Pictorem Product API for Frontend
Replaces dynamic_product_api.py with Pictorem integration
"""

import sqlite3
from flask import jsonify
from pictorem_api import PictoremAPI, get_all_products, get_product_sizes, get_product_options

DB_PATH = '/data/pictorem.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_products_for_frontend():
    """
    Get all products with sizes and options for frontend order form
    Returns data in the same format as the old API for compatibility
    """
    try:
        api = PictoremAPI()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all active products with categories
        cursor.execute('''
            SELECT 
                p.id,
                p.name,
                p.slug,
                p.material,
                p.type,
                p.description,
                p.preorder_template,
                c.name as category_name,
                c.slug as category_slug,
                c.material as category_material
            FROM pictorem_products p
            JOIN pictorem_categories c ON p.category_id = c.id
            WHERE p.active = 1 AND c.active = 1
            ORDER BY c.display_order, p.display_order
        ''')
        
        products = cursor.fetchall()
        formatted_products = []
        
        for product in products:
            product_dict = dict(product)
            product_slug = product_dict['slug']
            
            # Get sizes for this product
            cursor.execute('''
                SELECT width, height, orientation, display_name
                FROM pictorem_sizes
                WHERE product_id = ? AND active = 1
                ORDER BY display_order
            ''', (product_dict['id'],))
            
            sizes = [dict(row) for row in cursor.fetchall()]
            
            # Get options for this product (if any)
            cursor.execute('''
                SELECT option_type, option_code, option_name, description
                FROM pictorem_product_options
                WHERE product_id = ? AND active = 1
                ORDER BY option_type, display_order
            ''', (product_dict['id'],))
            
            options_rows = cursor.fetchall()
            
            # Group options by type
            options_by_type = {}
            for opt in options_rows:
                opt_dict = dict(opt)
                opt_type = opt_dict['option_type']
                if opt_type not in options_by_type:
                    options_by_type[opt_type] = []
                options_by_type[opt_type].append({
                    'code': opt_dict['option_code'],
                    'name': opt_dict['option_name'],
                    'description': opt_dict['description']
                })
            
            # Determine product type for frontend compatibility
            if product_dict['material'] == 'canvas' and product_dict['type'] == 'stretched':
                product_type = 'stretched_canvas'
            elif product_dict['material'] == 'paper' and 'framed' in product_dict['slug']:
                product_type = 'framed_fine_art'
            elif product_dict['material'] == 'metal':
                product_type = 'metal_print'
            elif product_dict['material'] == 'acrylic':
                product_type = 'acrylic_print'
            elif product_dict['material'] == 'paper':
                product_type = 'fine_art_paper'
            else:
                product_type = 'other'
            
            formatted_product = {
                'id': f"pictorem_{product_dict['id']}",
                'database_id': product_dict['id'],
                'name': product_dict['name'],
                'slug': product_slug,
                'description': product_dict['description'],
                'category_name': product_dict['category_name'],
                'category_slug': product_dict['category_slug'],
                'product_type': product_type,
                'material': product_dict['material'],
                'type': product_dict['type'],
                'sizes': sizes,
                'options': options_by_type,
                'has_options': len(options_by_type) > 0,
                'preorder_template': product_dict['preorder_template']
            }
            
            formatted_products.append(formatted_product)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'products': formatted_products,
            'total_count': len(formatted_products),
            'api_version': 'pictorem_v1'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching products: {str(e)}',
            'products': []
        }), 500

def get_product_price_api(product_slug, width, height, options=None):
    """
    Get pricing for a specific product configuration
    API endpoint for frontend
    """
    try:
        if options is None:
            options = {}
        
        api = PictoremAPI()
        preorder_code = api.build_preorder_code(product_slug, width, height, options)
        
        if not preorder_code:
            return jsonify({
                'success': False,
                'message': 'Invalid product configuration'
            }), 400
        
        price_data = api.get_price(preorder_code)
        
        if not price_data:
            return jsonify({
                'success': False,
                'message': 'Unable to get pricing from Pictorem API'
            }), 500
        
        return jsonify({
            'success': True,
            'base_price': price_data['base_price'],
            'customer_price': price_data['customer_price'],
            'breakdown': price_data['breakdown'],
            'preorder_code': preorder_code,
            'size': f"{width}x{height}",
            'cached': price_data.get('cached', False)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error calculating price: {str(e)}'
        }), 500

def get_categories_for_frontend():
    """Get all product categories for frontend navigation"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id,
                name,
                slug,
                material,
                description,
                display_order
            FROM pictorem_categories
            WHERE active = 1
            ORDER BY display_order
        ''')
        
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'categories': categories,
            'total_count': len(categories)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching categories: {str(e)}',
            'categories': []
        }), 500

def get_product_details(product_slug):
    """Get detailed information for a single product"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                p.id,
                p.name,
                p.slug,
                p.material,
                p.type,
                p.description,
                p.preorder_template,
                c.name as category_name,
                c.slug as category_slug
            FROM pictorem_products p
            JOIN pictorem_categories c ON p.category_id = c.id
            WHERE p.slug = ? AND p.active = 1
        ''', (product_slug,))
        
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Product not found'
            }), 404
        
        product_dict = dict(product)
        
        # Get sizes
        cursor.execute('''
            SELECT width, height, orientation, display_name
            FROM pictorem_sizes
            WHERE product_id = ? AND active = 1
            ORDER BY display_order
        ''', (product_dict['id'],))
        
        sizes = [dict(row) for row in cursor.fetchall()]
        
        # Get options grouped by type
        cursor.execute('''
            SELECT option_type, option_code, option_name, description
            FROM pictorem_product_options
            WHERE product_id = ? AND active = 1
            ORDER BY option_type, display_order
        ''', (product_dict['id'],))
        
        options_rows = cursor.fetchall()
        options_by_type = {}
        for opt in options_rows:
            opt_dict = dict(opt)
            opt_type = opt_dict['option_type']
            if opt_type not in options_by_type:
                options_by_type[opt_type] = []
            options_by_type[opt_type].append({
                'code': opt_dict['option_code'],
                'name': opt_dict['option_name'],
                'description': opt_dict['description']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'product': {
                'id': product_dict['id'],
                'name': product_dict['name'],
                'slug': product_dict['slug'],
                'description': product_dict['description'],
                'material': product_dict['material'],
                'type': product_dict['type'],
                'category_name': product_dict['category_name'],
                'category_slug': product_dict['category_slug'],
                'sizes': sizes,
                'options': options_by_type,
                'preorder_template': product_dict['preorder_template']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching product details: {str(e)}'
        }), 500

