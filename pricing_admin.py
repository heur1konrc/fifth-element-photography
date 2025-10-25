"""
Lumaprints Pricing Admin Backend - Updated for New Database Structure
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
    """Get the current global markup percentage - stored in a simple key-value table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create settings table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("SELECT value FROM settings WHERE key = 'global_markup_percentage'")
    result = cursor.fetchone()
    
    if not result:
        # Set default markup
        cursor.execute("INSERT INTO settings (key, value) VALUES ('global_markup_percentage', '50.0')")
        conn.commit()
        markup = 50.0
    else:
        markup = float(result['value'])
    
    conn.close()
    return markup

def set_global_markup(markup_percentage):
    """Set the global markup percentage"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        INSERT OR REPLACE INTO settings (key, value, updated_at) 
        VALUES ('global_markup_percentage', ?, CURRENT_TIMESTAMP)
    """, (str(markup_percentage),))
    
    conn.commit()
    conn.close()

def get_pricing_data():
    """Get all pricing data for the admin interface using NEW database structure"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get global markup
    global_markup = get_global_markup()
    multiplier = (global_markup / 100) + 1
    
    # Get all categories from categories table
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    category_rows = cursor.fetchall()
    
    categories = []
    for cat_row in category_rows:
        cat_id = cat_row['id']
        cat_name = cat_row['name']
        
        # Get all products in this category
        cursor.execute("""
            SELECT 
                p.id,
                p.name,
                p.size,
                p.cost_price as price,
                p.lumaprints_subcategory_id,
                p.lumaprints_frame_option as lumaprints_frame_option_id
            FROM products p
            WHERE p.category_id = ?
            ORDER BY p.name, p.size
        """, (cat_id,))
        
        products = []
        for prod_row in cursor.fetchall():
            product = dict(prod_row)
            # Calculate customer price with markup
            product['cost_price'] = product['price']
            product['customer_price'] = product['price'] * multiplier
            products.append(product)
        
        categories.append({
            'name': cat_name,
            'products': products,
            'product_count': len(products)
        })
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as total FROM products")
    total_products = cursor.fetchone()['total']
    
    total_categories = len(categories)
    
    cursor.execute("SELECT AVG(price) as avg FROM products")
    avg_cost = cursor.fetchone()['avg'] or 0
    
    conn.close()
    
    # Calculate avg customer price
    multiplier = (global_markup / 100) + 1
    avg_customer_price = avg_cost * multiplier
    
    return {
        'categories': categories,
        'global_markup': global_markup,
        'total_products': total_products,
        'total_categories': total_categories,
        'avg_cost': avg_cost,
        'avg_customer_price': avg_customer_price,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def admin_pricing_route():
    """Main admin pricing page"""
    try:
        data = get_pricing_data()
        return render_template('admin_pricing.html', **data)
    except Exception as e:
        return f"Pricing Admin Error: {str(e)}", 500

def update_global_markup_route():
    """Update global markup percentage"""
    try:
        data = request.get_json()
        markup = float(data.get('markup', 50.0))
        set_global_markup(markup)
        return jsonify({'success': True, 'markup': markup})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def update_product_cost_route():
    """Update individual product cost"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        new_cost = float(data.get('cost'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE products 
            SET price = ?
            WHERE id = ?
        """, (new_cost, product_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def add_product_route():
    """Add new product"""
    return jsonify({'success': False, 'error': 'Use import interface to add products'}), 400

def delete_product_route():
    """Delete product"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def add_category_route():
    """Add new category"""
    return jsonify({'success': False, 'error': 'Categories are auto-created from imports'}), 400

def delete_category_route():
    """Delete category"""
    return jsonify({'success': False, 'error': 'Cannot delete categories - remove all products instead'}), 400

def get_categories_route():
    """Get all categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
        categories = [{'name': row['category']} for row in cursor.fetchall()]
        
        conn.close()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

