"""
Lumaprints Pricing Admin Backend
Handles all pricing management operations
"""

import sqlite3
import json
from datetime import datetime
from flask import request, jsonify, render_template

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_global_markup():
    """Get the current global markup percentage"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
    result = cursor.fetchone()
    conn.close()
    
    return float(result['value']) if result else 123.0

def set_global_markup(markup_percentage):
    """Set the global markup percentage"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE settings 
        SET value = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE key_name = 'global_markup_percentage'
    """, (str(markup_percentage),))
    
    conn.commit()
    conn.close()

def get_pricing_data():
    """Get all pricing data for the admin interface"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get global markup
    global_markup = get_global_markup()
    multiplier = (global_markup / 100) + 1
    
    # Get categories with product counts
    cursor.execute("""
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id AND p.active = 1
        WHERE c.active = 1
        GROUP BY c.id
        ORDER BY c.display_order, c.name
    """)
    categories = []
    
    for cat_row in cursor.fetchall():
        category = dict(cat_row)
        
        # Get products for this category
        cursor.execute("""
            SELECT * FROM products 
            WHERE category_id = ? AND active = 1 
            ORDER BY name, size
        """, (category['id'],))
        
        products = []
        for prod_row in cursor.fetchall():
            product = dict(prod_row)
            product['customer_price'] = product['cost_price'] * multiplier
            products.append(product)
        
        category['products'] = products
        categories.append(category)
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as total FROM products WHERE active = 1")
    total_products = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM categories WHERE active = 1")
    total_categories = cursor.fetchone()['total']
    
    cursor.execute("SELECT AVG(cost_price) as avg FROM products WHERE active = 1")
    avg_cost = cursor.fetchone()['avg'] or 0
    
    cursor.execute("SELECT value FROM settings WHERE key_name = 'last_updated'")
    last_updated = cursor.fetchone()['value']
    
    conn.close()
    
    return {
        'categories': categories,
        'global_markup': global_markup,
        'total_products': total_products,
        'total_categories': total_categories,
        'avg_cost': avg_cost,
        'avg_customer_price': avg_cost * multiplier,
        'last_updated': last_updated
    }

def admin_pricing_route():
    """Main admin pricing page route"""
    try:
        pricing_data = get_pricing_data()
        return render_template('admin_pricing.html', **pricing_data)
    except Exception as e:
        return f"Pricing Admin Error: {str(e)}", 500

def update_global_markup_route():
    """Update global markup percentage"""
    try:
        data = request.get_json()
        markup = float(data.get('markup', 123.0))
        
        if markup < 0 or markup > 1000:
            return jsonify({'success': False, 'error': 'Markup must be between 0 and 1000%'})
        
        set_global_markup(markup)
        
        # Update last_updated timestamp
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE settings 
            SET value = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE key_name = 'last_updated'
        """, (datetime.now().strftime('%Y-%m-%d'),))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'markup': markup})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def update_product_cost_route():
    """Update individual product cost"""
    try:
        data = request.get_json()
        product_id = int(data.get('product_id'))
        cost_price = float(data.get('cost_price'))
        
        if cost_price < 0:
            return jsonify({'success': False, 'error': 'Cost must be positive'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE products 
            SET cost_price = ? 
            WHERE id = ? AND active = 1
        """, (cost_price, product_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Product not found'})
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'product_id': product_id, 'cost_price': cost_price})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def add_product_route():
    """Add new product"""
    try:
        data = request.get_json()
        category_id = int(data.get('category_id'))
        name = data.get('name', '').strip()
        size = data.get('size', '').strip()
        cost_price = float(data.get('cost_price'))
        
        if not name or not size:
            return jsonify({'success': False, 'error': 'Name and size are required'})
        
        if cost_price < 0:
            return jsonify({'success': False, 'error': 'Cost must be positive'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if category exists
        cursor.execute("SELECT id FROM categories WHERE id = ? AND active = 1", (category_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Invalid category'})
        
        # Check for duplicate product
        cursor.execute("""
            SELECT id FROM products 
            WHERE category_id = ? AND name = ? AND size = ? AND active = 1
        """, (category_id, name, size))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Product with this name and size already exists'})
        
        # Insert new product
        cursor.execute("""
            INSERT INTO products (category_id, name, size, cost_price) 
            VALUES (?, ?, ?, ?)
        """, (category_id, name, size, cost_price))
        
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'product_id': product_id,
            'category_id': category_id,
            'name': name,
            'size': size,
            'cost_price': cost_price
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def delete_product_route():
    """Delete product (soft delete)"""
    try:
        data = request.get_json()
        product_id = int(data.get('product_id'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE products 
            SET active = 0 
            WHERE id = ? AND active = 1
        """, (product_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Product not found'})
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'product_id': product_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_product_pricing(product_id):
    """Get pricing for a specific product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = ? AND p.active = 1
    """, (product_id,))
    
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        return None
    
    global_markup = get_global_markup()
    multiplier = (global_markup / 100) + 1
    
    product_dict = dict(product)
    product_dict['customer_price'] = product_dict['cost_price'] * multiplier
    product_dict['markup_percentage'] = global_markup
    product_dict['multiplier'] = multiplier
    
    return product_dict

def get_category_products(category_id):
    """Get all products in a category with pricing"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM products 
        WHERE category_id = ? AND active = 1 
        ORDER BY name, size
    """, (category_id,))
    
    products = cursor.fetchall()
    conn.close()
    
    global_markup = get_global_markup()
    multiplier = (global_markup / 100) + 1
    
    result = []
    for product in products:
        product_dict = dict(product)
        product_dict['customer_price'] = product_dict['cost_price'] * multiplier
        result.append(product_dict)
    
    return result

def search_products(query):
    """Search products by name or size"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_term = f"%{query}%"
    cursor.execute("""
        SELECT p.*, c.name as category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.active = 1 AND (
            p.name LIKE ? OR 
            p.size LIKE ? OR 
            c.name LIKE ?
        )
        ORDER BY p.name, p.size
    """, (search_term, search_term, search_term))
    
    products = cursor.fetchall()
    conn.close()
    
    global_markup = get_global_markup()
    multiplier = (global_markup / 100) + 1
    
    result = []
    for product in products:
        product_dict = dict(product)
        product_dict['customer_price'] = product_dict['cost_price'] * multiplier
        result.append(product_dict)
    
    return result
