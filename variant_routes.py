"""
Variant management routes for handling product variants in the frontend
"""
import sqlite3
from flask import request, jsonify

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_product_variants_route():
    """Get variants for a specific product"""
    try:
        product_id = request.args.get('product_id')
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required'})
        
        conn = get_db_connection()
        
        # Get product info
        product = conn.execute('''
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        ''', (product_id,)).fetchone()
        
        if not product:
            conn.close()
            return jsonify({'success': False, 'message': 'Product not found'})
        
        # Get variants for this product
        variants = conn.execute('''
            SELECT id, variant_name, variant_description, price_modifier, is_default
            FROM product_variants
            WHERE product_id = ?
            ORDER BY is_default DESC, variant_name
        ''', (product_id,)).fetchall()
        
        conn.close()
        
        # Convert to dict format
        variants_list = []
        for variant in variants:
            variants_list.append({
                'id': variant['id'],
                'name': variant['variant_name'],
                'description': variant['variant_description'],
                'price_modifier': float(variant['price_modifier']),
                'is_default': bool(variant['is_default'])
            })
        
        return jsonify({
            'success': True,
            'product': {
                'id': product['id'],
                'name': product['name'],
                'size': product['size'],
                'cost_price': float(product['cost_price']),
                'category_name': product['category_name']
            },
            'variants': variants_list,
            'has_variants': len(variants_list) > 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching variants: {str(e)}'})

def get_variant_price_route():
    """Get price for a specific variant"""
    try:
        variant_id = request.args.get('variant_id')
        
        if not variant_id:
            return jsonify({'success': False, 'message': 'Variant ID is required'})
        
        conn = get_db_connection()
        
        # Get variant and product info with pricing
        result = conn.execute('''
            SELECT 
                pv.id as variant_id,
                pv.variant_name,
                pv.price_modifier,
                p.id as product_id,
                p.name as product_name,
                p.size,
                p.cost_price,
                gs.markup_percentage
            FROM product_variants pv
            JOIN products p ON pv.product_id = p.id
            CROSS JOIN global_settings gs
            WHERE pv.id = ?
        ''', (variant_id,)).fetchone()
        
        conn.close()
        
        if not result:
            return jsonify({'success': False, 'message': 'Variant not found'})
        
        # Calculate pricing
        base_cost = float(result['cost_price'])
        variant_modifier = float(result['price_modifier'])
        markup_percentage = float(result['markup_percentage'])
        
        # Final cost = base cost + variant modifier (for framed canvas, modifier is 0)
        final_cost = base_cost + variant_modifier
        
        # Customer price = final cost * (1 + markup percentage / 100)
        customer_price = final_cost * (1 + markup_percentage / 100)
        
        return jsonify({
            'success': True,
            'variant_id': result['variant_id'],
            'variant_name': result['variant_name'],
            'product_name': result['product_name'],
            'size': result['size'],
            'cost_price': final_cost,
            'customer_price': round(customer_price, 2),
            'markup_percentage': markup_percentage
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error calculating variant price: {str(e)}'})

def get_products_with_variants_route():
    """Get all products and indicate which ones have variants"""
    try:
        conn = get_db_connection()
        
        # Get all products with variant count
        products = conn.execute('''
            SELECT 
                p.id,
                p.name,
                p.size,
                p.cost_price,
                c.name as category_name,
                c.id as category_id,
                COUNT(pv.id) as variant_count,
                gs.markup_percentage
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_variants pv ON p.id = pv.product_id
            CROSS JOIN global_settings gs
            GROUP BY p.id, p.name, p.size, p.cost_price, c.name, c.id, gs.markup_percentage
            ORDER BY c.name, p.name, p.size
        ''').fetchall()
        
        conn.close()
        
        # Format products with pricing and variant info
        products_list = []
        for product in products:
            cost_price = float(product['cost_price'])
            markup_percentage = float(product['markup_percentage'])
            customer_price = cost_price * (1 + markup_percentage / 100)
            
            products_list.append({
                'id': product['id'],
                'name': product['name'],
                'size': product['size'],
                'cost_price': cost_price,
                'customer_price': round(customer_price, 2),
                'category_name': product['category_name'],
                'category_id': product['category_id'],
                'has_variants': product['variant_count'] > 0,
                'variant_count': product['variant_count']
            })
        
        return jsonify({
            'success': True,
            'products': products_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching products: {str(e)}'})
