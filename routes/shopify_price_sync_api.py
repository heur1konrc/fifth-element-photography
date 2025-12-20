"""
Shopify Price Sync API
Bulk update prices for all existing Shopify products based on current database pricing
"""

from flask import Blueprint, jsonify
import sqlite3
import os
import requests
import time
import base64
from datetime import datetime

shopify_price_sync_bp = Blueprint('shopify_price_sync', __name__)

SHOPIFY_STORE = os.environ.get('SHOPIFY_STORE')
SHOPIFY_ACCESS_TOKEN = os.environ.get('SHOPIFY_ACCESS_TOKEN')
SHOPIFY_API_VERSION = '2024-01'

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'print_ordering.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_price_for_variant(product_category, size_name, frame_color=None):
    """
    Calculate price for a specific variant based on database pricing rules
    Returns price in dollars (float)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get the product option ID for this category
        cursor.execute("""
            SELECT id FROM product_options 
            WHERE name = ?
        """, (product_category,))
        option_row = cursor.fetchone()
        
        if not option_row:
            return None
            
        option_id = option_row['id']
        
        # Get base price for this size
        cursor.execute("""
            SELECT base_price FROM product_option_sizes
            WHERE product_option_id = ? AND size_name = ?
        """, (option_id, size_name))
        size_row = cursor.fetchone()
        
        if not size_row:
            return None
            
        base_price = size_row['base_price']
        
        # Add frame color markup if applicable
        frame_markup = 0
        if frame_color and product_category == "Framed Canvas":
            cursor.execute("""
                SELECT price_markup FROM product_option_subcategories
                WHERE product_option_id = ? AND size_name = ? AND subcategory_value = ?
            """, (option_id, size_name, frame_color))
            frame_row = cursor.fetchone()
            
            if frame_row:
                frame_markup = frame_row['price_markup']
        
        # Get global markup percentage
        cursor.execute("SELECT markup_percentage FROM pricing_settings WHERE id = 1")
        markup_row = cursor.fetchone()
        markup_percentage = markup_row['markup_percentage'] if markup_row else 0
        
        # Calculate final price
        subtotal = base_price + frame_markup
        final_price = subtotal * (1 + markup_percentage / 100)
        
        return round(final_price, 2)
        
    finally:
        conn.close()

def get_all_shopify_products():
    """Fetch all products from Shopify"""
    url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products.json"
    headers = {
        'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }
    
    all_products = []
    params = {'limit': 250}
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to fetch products: {response.text}")
        
        data = response.json()
        all_products.extend(data.get('products', []))
        
        # Check for pagination
        link_header = response.headers.get('Link', '')
        if 'rel="next"' not in link_header:
            break
            
        # Extract next page URL from Link header
        for link in link_header.split(','):
            if 'rel="next"' in link:
                next_url = link[link.find('<')+1:link.find('>')]
                url = next_url
                params = {}
                break
        
        time.sleep(0.5)  # Rate limiting
    
    return all_products

def update_product_variant_price(variant_id, new_price):
    """Update a single variant's price in Shopify"""
    url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/variants/{variant_id}.json"
    headers = {
        'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'variant': {
            'id': variant_id,
            'price': str(new_price)
        }
    }
    
    response = requests.put(url, headers=headers, json=payload)
    time.sleep(0.5)  # Rate limiting: 2 requests/second
    
    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to update variant {variant_id}: {response.text}")
    
    return response.json()

@shopify_price_sync_bp.route('/api/shopify/sync-prices', methods=['POST'])
def sync_shopify_prices():
    """
    Sync all Shopify product prices with current database pricing
    This can take 30-60 minutes due to rate limits
    """
    start_time = time.time()
    
    try:
        # Fetch all products from Shopify
        products = get_all_shopify_products()
        
        products_updated = 0
        variants_updated = 0
        errors = []
        
        for product in products:
            try:
                # Extract category from product title
                # Expected format: "Image Title - Canvas" or "Image Title - Framed Canvas"
                title = product.get('title', '')
                
                if ' - ' not in title:
                    errors.append(f"Product {product['id']}: Invalid title format '{title}'")
                    continue
                
                category = title.split(' - ')[-1].strip()
                
                # Update each variant
                product_had_updates = False
                for variant in product.get('variants', []):
                    try:
                        # Parse variant title to get size and frame color
                        variant_title = variant.get('title', '')
                        
                        # Handle different variant title formats
                        size_name = variant_title
                        frame_color = None
                        
                        if ' - ' in variant_title:
                            parts = variant_title.split(' - ')
                            size_name = parts[0].strip()
                            if len(parts) > 1:
                                frame_color = parts[1].strip()
                        
                        # Calculate new price
                        new_price = calculate_price_for_variant(category, size_name, frame_color)
                        
                        if new_price is None:
                            errors.append(f"Variant {variant['id']}: Could not calculate price for {category} - {size_name}")
                            continue
                        
                        # Check if price needs updating
                        current_price = float(variant.get('price', 0))
                        
                        if abs(current_price - new_price) > 0.01:  # Only update if different
                            update_product_variant_price(variant['id'], new_price)
                            variants_updated += 1
                            product_had_updates = True
                    
                    except Exception as e:
                        errors.append(f"Variant {variant.get('id', 'unknown')}: {str(e)}")
                
                if product_had_updates:
                    products_updated += 1
                    
            except Exception as e:
                errors.append(f"Product {product.get('id', 'unknown')}: {str(e)}")
        
        duration = time.time() - start_time
        
        return jsonify({
            'success': True,
            'products_updated': products_updated,
            'variants_updated': variants_updated,
            'total_products': len(products),
            'duration_seconds': round(duration, 2),
            'errors': errors
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
