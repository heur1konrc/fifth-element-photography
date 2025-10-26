"""
Pricing API for Fifth Element Photography
Returns pricing for products based on Lumaprints subcategory ID and size
"""

import sqlite3
from flask import jsonify

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_product_price(lumaprints_subcategory_id, size, variant_id=None):
    """
    Get pricing for a specific product
    
    Args:
        lumaprints_subcategory_id: Lumaprints subcategory ID
        size: Size string (e.g., "10×20" or "10x20")
        variant_id: Optional variant ID for frame options
    
    Returns:
        dict with pricing information or error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Normalize size format (replace x with ×)
        size_normalized = size.replace('x', '×').replace('X', '×')
        
        # Query for the product
        cursor.execute("""
            SELECT 
                p.id,
                p.name,
                p.size,
                p.cost_price,
                p.price as retail_price,
                p.lumaprints_subcategory_id,
                p.lumaprints_frame_option,
                p.lumaprints_options,
                c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.lumaprints_subcategory_id = ? 
            AND p.size = ?
            AND p.active = 1
        """, (lumaprints_subcategory_id, size_normalized))
        
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            return {
                'success': False,
                'error': f'Product not found for subcategory {lumaprints_subcategory_id} and size {size}'
            }
        
        # Base pricing
        result = {
            'success': True,
            'product_id': product['id'],
            'product_name': product['name'],
            'category': product['category_name'],
            'size': product['size'],
            'cost_price': product['cost_price'],
            'retail_price': product['retail_price'],
            'lumaprints_subcategory_id': product['lumaprints_subcategory_id'],
            'variant': None,
            'total_price': product['retail_price']
        }
        
        # Add variant pricing if applicable
        if variant_id:
            cursor.execute("""
                SELECT 
                    id,
                    variant_name,
                    variant_description,
                    price_modifier,
                    is_default
                FROM product_variants
                WHERE id = ? AND product_id = ?
            """, (variant_id, product['id']))
            
            variant = cursor.fetchone()
            
            if variant:
                result['variant'] = {
                    'id': variant['id'],
                    'name': variant['variant_name'],
                    'description': variant['variant_description'],
                    'price_modifier': variant['price_modifier']
                }
                result['total_price'] = product['retail_price'] + variant['price_modifier']
        
        # Get global markup setting
        cursor.execute("SELECT value FROM settings WHERE key = 'global_markup_percentage'")
        markup_row = cursor.fetchone()
        markup_percentage = float(markup_row['value']) if markup_row else 0.0
        
        result['markup_percentage'] = markup_percentage
        
        conn.close()
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }

def get_category_products(category_id):
    """
    Get all products for a Lumaprints subcategory with pricing
    
    Args:
        category_id: Lumaprints subcategory ID (e.g., 102003)
    
    Returns:
        dict with products list or error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                p.id,
                p.name,
                p.size,
                p.cost_price,
                p.price as retail_price,
                p.lumaprints_subcategory_id,
                c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.lumaprints_subcategory_id = ?
            AND p.active = 1
            ORDER BY p.size
        """, (category_id,))
        
        products = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'success': True,
            'subcategory_id': category_id,
            'products': products
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }

def get_product_variants(product_id):
    """
    Get all variants for a product (e.g., frame options)
    
    Args:
        product_id: Product ID
    
    Returns:
        dict with variants list or error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                variant_name,
                variant_description,
                price_modifier,
                is_default
            FROM product_variants
            WHERE product_id = ?
            ORDER BY is_default DESC, variant_name
        """, (product_id,))
        
        variants = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'success': True,
            'product_id': product_id,
            'variants': variants
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }

