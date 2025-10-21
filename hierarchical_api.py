from flask import Blueprint, jsonify, request
import sqlite3
import json

hierarchical_bp = Blueprint('hierarchical', __name__)

def get_db_connection():
    conn = sqlite3.connect('lumaprints_pricing.db')
    conn.row_factory = sqlite3.Row
    return conn

@hierarchical_bp.route('/api/product-types', methods=['GET'])
def get_product_types():
    """Get all product types"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, display_order, has_sub_options, max_sub_option_levels, active
            FROM product_types 
            WHERE active = 1 
            ORDER BY display_order
        """)
        
        product_types = []
        for row in cursor.fetchall():
            product_types.append({
                'id': row['id'],
                'name': row['name'],
                'display_order': row['display_order'],
                'has_sub_options': bool(row['has_sub_options']),
                'max_sub_option_levels': row['max_sub_option_levels'],
                'active': bool(row['active'])
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

@hierarchical_bp.route('/api/sub-options/<int:product_type_id>/<int:level>', methods=['GET'])
def get_sub_options(product_type_id, level):
    """Get sub-options for a product type at a specific level"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, option_type, name, value, image_path, display_order
            FROM sub_options 
            WHERE product_type_id = ? AND level = ? AND active = 1
            ORDER BY display_order
        """, (product_type_id, level))
        
        sub_options = []
        for row in cursor.fetchall():
            sub_options.append({
                'id': row['id'],
                'option_type': row['option_type'],
                'name': row['name'],
                'value': row['value'],
                'image_path': row['image_path'],
                'display_order': row['display_order']
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'sub_options': sub_options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@hierarchical_bp.route('/api/available-sizes', methods=['GET'])
def get_available_sizes():
    """Get available sizes based on product type and sub-options"""
    try:
        product_type_id = request.args.get('product_type_id', type=int)
        sub_option_1_id = request.args.get('sub_option_1_id', type=int)
        sub_option_2_id = request.args.get('sub_option_2_id', type=int)
        
        if not product_type_id:
            return jsonify({
                'success': False,
                'error': 'product_type_id is required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get global markup percentage
        cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
        markup_row = cursor.fetchone()
        markup_percentage = float(markup_row['value']) if markup_row else 150.0
        
        # Build query based on available parameters
        query = """
            SELECT p.id, p.name, p.size, p.cost_price, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.active = 1 AND p.product_type_id = ?
        """
        params = [product_type_id]
        
        if sub_option_1_id:
            query += " AND p.sub_option_1_id = ?"
            params.append(sub_option_1_id)
            
        if sub_option_2_id:
            query += " AND p.sub_option_2_id = ?"
            params.append(sub_option_2_id)
            
        query += " ORDER BY p.name, p.size"
        
        cursor.execute(query, params)
        
        products = []
        for row in cursor.fetchall():
            # Calculate customer price using global markup
            customer_price = row['cost_price'] * (markup_percentage / 100)
            
            products.append({
                'id': row['id'],
                'name': row['name'],
                'size': row['size'],
                'category_name': row['category_name'],
                'cost_price': float(row['cost_price']),
                'customer_price': round(customer_price, 2)
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'products': products,
            'markup_percentage': markup_percentage
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@hierarchical_bp.route('/api/product-details/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    """Get detailed information about a specific product"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get global markup percentage
        cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
        markup_row = cursor.fetchone()
        markup_percentage = float(markup_row['value']) if markup_row else 150.0
        
        cursor.execute("""
            SELECT p.*, c.name as category_name, pt.name as product_type_name,
                   so1.value as sub_option_1_value, so2.value as sub_option_2_value
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_types pt ON p.product_type_id = pt.id
            LEFT JOIN sub_options so1 ON p.sub_option_1_id = so1.id
            LEFT JOIN sub_options so2 ON p.sub_option_2_id = so2.id
            WHERE p.id = ? AND p.active = 1
        """, (product_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Calculate customer price using global markup
        customer_price = row['cost_price'] * (markup_percentage / 100)
        
        product = {
            'id': row['id'],
            'name': row['name'],
            'size': row['size'],
            'cost_price': float(row['cost_price']),
            'customer_price': round(customer_price, 2),
            'category_name': row['category_name'],
            'product_type_name': row['product_type_name'],
            'sub_option_1_value': row['sub_option_1_value'],
            'sub_option_2_value': row['sub_option_2_value'],
            'description': row['description']
        }
        
        conn.close()
        return jsonify({
            'success': True,
            'product': product,
            'markup_percentage': markup_percentage
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
