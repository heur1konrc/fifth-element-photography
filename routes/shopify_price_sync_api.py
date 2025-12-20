"""
Shopify Price Sync API
Bulk update prices for all existing Shopify products based on current database pricing
"""

from flask import Blueprint, jsonify
import sqlite3
import os
import requests
import time
from datetime import datetime

shopify_price_sync_bp = Blueprint('shopify_price_sync', __name__)

SHOPIFY_STORE = os.environ.get('SHOPIFY_STORE', 'fifth-element-photography.myshopify.com')
SHOPIFY_ACCESS_TOKEN = os.environ.get('SHOPIFY_API_SECRET', '')
SHOPIFY_API_VERSION = '2024-01'

def get_db_connection():
    """Get database connection"""
    # Use Railway's persistent volume path if it exists
    if os.path.exists('/data'):
        db_path = '/data/print_ordering.db'
    else:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'print_ordering.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def map_shopify_to_db_product_type(shopify_product_type):
    """Reverse map Shopify product type names to database product type names"""
    # Most names are the same, but some have mappings
    reverse_mapping = {
        'Hot Press (recommended for photos)': 'Hot Press Fine Art Paper',
        'Cold Press': 'Cold Press Fine Art Paper',
        'Semi-glossy': 'Semi-Glossy Fine Art Paper',
        'Glossy': 'Glossy Fine Art Paper',
    }
    return reverse_mapping.get(shopify_product_type, shopify_product_type)

def get_markup_multiplier():
    """Get global markup multiplier from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT markup_value FROM markup_rules 
            WHERE rule_type = 'global' AND is_active = TRUE 
            LIMIT 1
        """)
        markup_row = cursor.fetchone()
        global_markup = markup_row[0] if markup_row else 100.0
        return 1 + (global_markup / 100)
    finally:
        conn.close()

def calculate_price_for_variant(product_category, size_name, frame_color=None, subcategory=None):
    """
    Calculate price for a specific variant based on database pricing rules
    Returns price in dollars (float)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        markup_multiplier = get_markup_multiplier()
        
        # For non-framed products, use the subcategory from option1
        if product_category != "Framed Canvas" and subcategory:
            # Convert Shopify name back to database name
            db_subcategory = map_shopify_to_db_product_type(subcategory)
            
            # Query using the specific subcategory (e.g., "0.75\" Stretched Canvas")
            cursor.execute("""
                SELECT bp.cost_price
                FROM base_pricing bp
                JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                JOIN print_sizes pz ON bp.size_id = pz.size_id
                WHERE ps.display_name = ?
                AND pz.size_name = ?
                AND bp.is_available = TRUE
            """, (db_subcategory, size_name))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            cost_price = float(row[0])
            final_price = cost_price * markup_multiplier
            return round(final_price, 2)
        
        # Determine the subcategory name based on product category
        if product_category == "Framed Canvas" and frame_color:
            # For framed canvas, we need to find the specific frame type
            # Map frame color to subcategory
            frame_type_map = {
                'Black': ['0.75" Framed Canvas', '1.25" Framed Canvas', '1.50" Framed Canvas'],
                'White': ['0.75" Framed Canvas', '1.25" Framed Canvas', '1.50" Framed Canvas'],
                'Silver': ['0.75" Framed Canvas'],
                'Gold': ['0.75" Framed Canvas'],
                'Oak': ['1.25" Framed Canvas', '1.50" Framed Canvas']
            }
            
            # Try each possible frame type for this color
            base_price = None
            frame_adjustment = 0.0
            
            for frame_type in frame_type_map.get(frame_color, []):
                # Get base price for this frame type and size
                cursor.execute("""
                    SELECT bp.cost_price
                    FROM base_pricing bp
                    JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                    JOIN print_sizes pz ON bp.size_id = pz.size_id
                    WHERE ps.display_name = ?
                    AND pz.size_name = ?
                    AND bp.is_available = TRUE
                """, (frame_type, size_name))
                
                row = cursor.fetchone()
                if row:
                    base_price = float(row[0])
                    
                    # Get frame color adjustment
                    frame_option_map = {
                        ('0.75" Framed Canvas', 'Black'): 'black_floating_075',
                        ('0.75" Framed Canvas', 'White'): 'white_floating_075',
                        ('0.75" Framed Canvas', 'Silver'): 'silver_floating_075',
                        ('0.75" Framed Canvas', 'Gold'): 'gold_plein_air',
                        ('1.25" Framed Canvas', 'Black'): 'black_floating_125',
                        ('1.25" Framed Canvas', 'White'): 'white_floating_125',
                        ('1.25" Framed Canvas', 'Oak'): 'oak_floating_125',
                        ('1.50" Framed Canvas', 'Black'): 'black_floating_150',
                        ('1.50" Framed Canvas', 'White'): 'white_floating_150',
                        ('1.50" Framed Canvas', 'Oak'): 'oak_floating_150',
                    }
                    
                    option_name = frame_option_map.get((frame_type, frame_color))
                    if option_name:
                        cursor.execute("""
                            SELECT op.cost_price
                            FROM option_pricing op
                            JOIN product_options po ON op.option_id = po.option_id
                            WHERE po.option_name = ?
                        """, (option_name,))
                        
                        frame_row = cursor.fetchone()
                        if frame_row and frame_row[0]:
                            frame_adjustment = float(frame_row[0])
                    
                    break  # Found a match, stop searching
            
            if base_price is None:
                return None
            
            cost_price = base_price + frame_adjustment
        else:
            # For non-framed products (Canvas, Fine Art Paper, Foam-mounted)
            cursor.execute("""
                SELECT bp.cost_price
                FROM base_pricing bp
                JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                JOIN product_categories pc ON ps.category_id = pc.category_id
                JOIN print_sizes pz ON bp.size_id = pz.size_id
                WHERE pc.display_name = ?
                AND pz.size_name = ?
                AND bp.is_available = TRUE
            """, (product_category, size_name))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            cost_price = float(row[0])
        
        # Apply markup
        final_price = cost_price * markup_multiplier
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
                        # Shopify variants use option1 (Printed Product) and option2 (Size)
                        # option1 = subcategory (e.g., "0.75\" Stretched Canvas" or "Black")
                        # option2 = size (e.g., "8×12")
                        subcategory = variant.get('option1', '').strip()
                        size_name = variant.get('option2', '').strip()
                        
                        # For framed canvas, option1 is the frame color
                        frame_color = None
                        if category == "Framed Canvas":
                            frame_color = subcategory
                        
                        # Calculate new price
                        new_price = calculate_price_for_variant(category, size_name, frame_color, subcategory)
                        
                        if new_price is None:
                            errors.append(f"Variant {variant['id']}: Could not calculate price for {category} | subcategory='{subcategory}' | size='{size_name}' | frame_color='{frame_color}'")
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
