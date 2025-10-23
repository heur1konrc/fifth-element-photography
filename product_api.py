"""
Product API endpoints for the pricing form
"""
from flask import Blueprint, jsonify, request
import sqlite3
import os

product_api = Blueprint('product_api', __name__)

DB_PATH = '/data/lumaprints_pricing.db'

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

@product_api.route('/api/products/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT category FROM products ORDER BY category')
    categories = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(categories)

@product_api.route('/api/products/subcategories/<category>', methods=['GET'])
def get_subcategories(category):
    """Get all unique products for a category"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT 
            name,
            lumaprints_subcategory_id,
            lumaprints_frame_option_id
        FROM products 
        WHERE category = ?
        ORDER BY name
    ''', (category,))
    
    products = []
    for row in cursor.fetchall():
        products.append({
            'name': row[0],
            'subcategory_id': row[1],
            'option_id': row[2]
        })
    
    conn.close()
    return jsonify(products)

@product_api.route('/api/products/sizes', methods=['GET'])
def get_sizes():
    """Get available sizes for a subcategory and optional frame option"""
    subcategory_id = request.args.get('subcategory_id')
    option_id = request.args.get('option_id')
    
    if not subcategory_id:
        return jsonify({'error': 'subcategory_id required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    if option_id:
        cursor.execute('''
            SELECT DISTINCT size, price
            FROM products
            WHERE lumaprints_subcategory_id = ? AND lumaprints_frame_option_id = ?
            ORDER BY 
                CAST(SUBSTR(size, 1, INSTR(size, 'x')-1) AS INTEGER),
                CAST(SUBSTR(size, INSTR(size, 'x')+1) AS INTEGER)
        ''', (subcategory_id, option_id))
    else:
        cursor.execute('''
            SELECT DISTINCT size, price
            FROM products
            WHERE lumaprints_subcategory_id = ?
            ORDER BY 
                CAST(SUBSTR(size, 1, INSTR(size, 'x')-1) AS INTEGER),
                CAST(SUBSTR(size, INSTR(size, 'x')+1) AS INTEGER)
        ''', (subcategory_id,))
    
    sizes = [{'size': row[0], 'price': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(sizes)

@product_api.route('/api/products/price', methods=['GET'])
def get_price():
    """Get price for a specific product configuration"""
    subcategory_id = request.args.get('subcategory_id')
    size = request.args.get('size')
    option_id = request.args.get('option_id')
    
    if not subcategory_id or not size:
        return jsonify({'error': 'subcategory_id and size required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    if option_id:
        cursor.execute('''
            SELECT price, name
            FROM products
            WHERE lumaprints_subcategory_id = ? 
            AND size = ?
            AND lumaprints_frame_option_id = ?
            LIMIT 1
        ''', (subcategory_id, size, option_id))
    else:
        cursor.execute('''
            SELECT price, name
            FROM products
            WHERE lumaprints_subcategory_id = ? 
            AND size = ?
            LIMIT 1
        ''', (subcategory_id, size))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'price': result[0],
            'product_name': result[1]
        })
    else:
        return jsonify({'error': 'Product not found'}), 404

