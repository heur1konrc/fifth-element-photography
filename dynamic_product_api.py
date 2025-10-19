"""
Dynamic Product API - Serves products from database instead of hardcoded data
"""
import sqlite3
from flask import jsonify

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_products_for_frontend():
    """Get all products with variants for frontend order form"""
    try:
        conn = get_db_connection()
        
        # Check what tables exist and adapt accordingly
        cursor = conn.cursor()
        
        # Check if we have the new pricing tables or old structure
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [table[0] for table in tables]
        
        # If we don't have the new tables, return sample products for now
        if 'global_settings' not in table_names or 'products' not in table_names or 'categories' not in table_names:
            conn.close()
            return get_fallback_products()
        
        # Get all products with category info, pricing, and variant counts
        products_query = '''
            SELECT 
                p.id,
                p.name,
                p.size,
                p.cost_price,
                c.name as category_name,
                c.id as category_id,
                COUNT(pv.id) as variant_count,
                COALESCE(gs.markup_percentage, 123.0) as markup_percentage
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_variants pv ON p.id = pv.product_id
            LEFT JOIN global_settings gs ON 1=1
            WHERE c.name IN (
                'Canvas - 0.75" Stretched',
                'Canvas - 1.25" Stretched', 
                'Canvas - 1.5" Stretched',
                'Framed Canvas - 0.75"',
                'Framed Canvas - 1.25"',
                'Framed Canvas - 1.5"'
            )
            GROUP BY p.id, p.name, p.size, p.cost_price, c.name, c.id, gs.markup_percentage
            ORDER BY c.name, p.name, p.size
        '''
        
        products = conn.execute(products_query).fetchall()
        
        # Format products for frontend
        formatted_products = []
        for product in products:
            cost_price = float(product['cost_price'])
            markup_percentage = float(product['markup_percentage'])
            customer_price = cost_price * (1 + markup_percentage / 100)
            
            # Determine product type and thickness from category
            category_name = product['category_name']
            if 'Stretched' in category_name:
                product_type = 'stretched_canvas'
                thickness = category_name.split(' - ')[1].replace(' Stretched', '')
            elif 'Framed Canvas' in category_name:
                product_type = 'framed_canvas'
                thickness = category_name.split(' - ')[1].replace('"', '')
            else:
                product_type = 'other'
                thickness = 'Unknown'
            
            formatted_product = {
                'id': f"product_{product['id']}",
                'database_id': product['id'],
                'name': product['name'],
                'size': product['size'],
                'cost_price': cost_price,
                'customer_price': round(customer_price, 2),
                'category_name': category_name,
                'category_id': product['category_id'],
                'product_type': product_type,
                'thickness': thickness,
                'has_variants': product['variant_count'] > 0,
                'variant_count': product['variant_count']
            }
            
            # If product has variants, get them
            if product['variant_count'] > 0:
                variants_query = '''
                    SELECT id, variant_name, variant_description, price_modifier, is_default
                    FROM product_variants
                    WHERE product_id = ?
                    ORDER BY is_default DESC, variant_name
                '''
                variants = conn.execute(variants_query, (product['id'],)).fetchall()
                
                formatted_product['variants'] = []
                for variant in variants:
                    formatted_product['variants'].append({
                        'id': variant['id'],
                        'name': variant['variant_name'],
                        'description': variant['variant_description'],
                        'price_modifier': float(variant['price_modifier']),
                        'is_default': bool(variant['is_default'])
                    })
            
            formatted_products.append(formatted_product)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'products': formatted_products,
            'total_count': len(formatted_products)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching products: {str(e)}',
            'products': []
        })

def get_product_details_api():
    """Get detailed product information including variants"""
    from flask import request
    
    try:
        product_id = request.args.get('id')
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required'})
        
        # Extract database ID from frontend ID
        if product_id.startswith('product_'):
            db_id = product_id.replace('product_', '')
        else:
            db_id = product_id
        
        conn = get_db_connection()
        
        # Get product with category and pricing info
        product_query = '''
            SELECT 
                p.id,
                p.name,
                p.size,
                p.cost_price,
                c.name as category_name,
                c.id as category_id,
                gs.markup_percentage
            FROM products p
            JOIN categories c ON p.category_id = c.id
            CROSS JOIN global_settings gs
            WHERE p.id = ?
        '''
        
        product = conn.execute(product_query, (db_id,)).fetchone()
        
        if not product:
            conn.close()
            return jsonify({'success': False, 'message': 'Product not found'})
        
        # Get variants if any
        variants_query = '''
            SELECT id, variant_name, variant_description, price_modifier, is_default
            FROM product_variants
            WHERE product_id = ?
            ORDER BY is_default DESC, variant_name
        '''
        variants = conn.execute(variants_query, (db_id,)).fetchall()
        
        conn.close()
        
        # Calculate pricing
        cost_price = float(product['cost_price'])
        markup_percentage = float(product['markup_percentage'])
        customer_price = cost_price * (1 + markup_percentage / 100)
        
        # Format response
        response_data = {
            'success': True,
            'product': {
                'id': f"product_{product['id']}",
                'database_id': product['id'],
                'name': product['name'],
                'size': product['size'],
                'cost_price': cost_price,
                'customer_price': round(customer_price, 2),
                'category_name': product['category_name'],
                'category_id': product['category_id'],
                'markup_percentage': markup_percentage
            }
        }
        
        # Add variants if any
        if variants:
            response_data['product']['variants'] = []
            for variant in variants:
                response_data['product']['variants'].append({
                    'id': variant['id'],
                    'name': variant['variant_name'],
                    'description': variant['variant_description'],
                    'price_modifier': float(variant['price_modifier']),
                    'is_default': bool(variant['is_default'])
                })
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching product details: {str(e)}'
        })


def get_fallback_products():
    """Return sample products when database tables don't exist"""
    sample_products = [
        {
            'id': 'sample_canvas_075_8x10',
            'database_id': 1,
            'name': 'Canvas 0.75"',
            'size': '8×10"',
            'cost_price': 15.39,
            'customer_price': 34.32,
            'category_name': 'Canvas - 0.75" Stretched',
            'category_id': 1,
            'product_type': 'stretched_canvas',
            'thickness': '0.75"',
            'has_variants': False,
            'variant_count': 0
        },
        {
            'id': 'sample_canvas_075_11x14',
            'database_id': 2,
            'name': 'Canvas 0.75"',
            'size': '11×14"',
            'cost_price': 18.76,
            'customer_price': 41.85,
            'category_name': 'Canvas - 0.75" Stretched',
            'category_id': 1,
            'product_type': 'stretched_canvas',
            'thickness': '0.75"',
            'has_variants': False,
            'variant_count': 0
        },
        {
            'id': 'sample_framed_15_8x10',
            'database_id': 3,
            'name': 'Framed Canvas 1.5"',
            'size': '8×10"',
            'cost_price': 31.25,
            'customer_price': 69.69,
            'category_name': 'Framed Canvas - 1.5"',
            'category_id': 6,
            'product_type': 'framed_canvas',
            'thickness': '1.5"',
            'has_variants': True,
            'variant_count': 8,
            'variants': [
                {'id': 1, 'name': 'Maple Wood', 'description': 'Maple Wood Floating Frame', 'price_modifier': 0.0, 'is_default': True},
                {'id': 2, 'name': 'Espresso', 'description': 'Espresso Floating Frame', 'price_modifier': 0.0, 'is_default': False},
                {'id': 3, 'name': 'Natural Wood', 'description': 'Natural Wood Floating Frame', 'price_modifier': 0.0, 'is_default': False},
                {'id': 4, 'name': 'Oak', 'description': 'Oak Floating Frame', 'price_modifier': 0.0, 'is_default': False},
                {'id': 5, 'name': 'Gold', 'description': 'Gold Floating Frame', 'price_modifier': 0.0, 'is_default': False},
                {'id': 6, 'name': 'Silver', 'description': 'Silver Floating Frame', 'price_modifier': 0.0, 'is_default': False},
                {'id': 7, 'name': 'White', 'description': 'White Floating Frame', 'price_modifier': 0.0, 'is_default': False},
                {'id': 8, 'name': 'Black', 'description': 'Black Floating Frame', 'price_modifier': 0.0, 'is_default': False}
            ]
        }
    ]
    
    return jsonify({
        'success': True,
        'products': sample_products,
        'total_count': len(sample_products),
        'note': 'Using sample products - database tables not fully initialized'
    })
