from flask import Blueprint, jsonify
import os
import sqlite3
import requests
import time

shopify_price_sync_bp = Blueprint('shopify_price_sync_api', __name__)

# Shopify configuration
SHOPIFY_STORE = os.environ.get('SHOPIFY_STORE', 'fifth-element-photography.myshopify.com')
SHOPIFY_ACCESS_TOKEN = os.environ.get('SHOPIFY_API_SECRET', '')
SHOPIFY_API_VERSION = '2024-01'

def get_db_connection():
    """Get database connection with proper path handling for Railway"""
    # Check if running on Railway (has /data volume)
    if os.path.exists('/data'):
        db_path = '/data/print_ordering.db'
    else:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'print_ordering.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def map_product_type_to_shopify(db_product_type):
    """Map database product type names to Shopify-friendly names (copied from shopify_api_creator)"""
    mapping = {
        'Hot Press Fine Art Paper': 'Hot Press (recommended for photos)',
        'Cold Press Fine Art Paper': 'Cold Press',
        'Semi-Glossy Fine Art Paper': 'Semi-glossy',
        'Glossy Fine Art Paper': 'Glossy',
        'Foam-mounted Hot Press': 'Foam-mounted Hot Press',
        'Foam-mounted Cold Press': 'Foam-mounted Cold Press',
        'Foam-mounted Semi-Glossy': 'Foam-mounted Semi-Glossy',
        'Foam-mounted Glossy': 'Foam-mounted Glossy',
    }
    return mapping.get(db_product_type, db_product_type)

@shopify_price_sync_bp.route('/api/shopify/sync-prices', methods=['POST'])
def sync_shopify_prices():
    """
    Sync prices for all existing Shopify products based on current database pricing.
    Uses the EXACT same logic as shopify_api_creator.py
    """
    start_time = time.time()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get global markup multiplier
        cursor.execute("""
            SELECT markup_value FROM markup_rules 
            WHERE rule_type = 'global' AND is_active = TRUE 
            LIMIT 1
        """)
        markup_row = cursor.fetchone()
        global_markup = markup_row[0] if markup_row else 100.0
        markup_multiplier = 1 + (global_markup / 100)
        
        # Fetch all Shopify products (paginated)
        all_products = []
        url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products.json?limit=250'
        headers = {'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN}
        
        while url:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return jsonify({
                    'success': False,
                    'error': f'Failed to fetch products from Shopify: HTTP {response.status_code}'
                }), 500
            
            data = response.json()
            all_products.extend(data.get('products', []))
            
            # Check for next page
            link_header = response.headers.get('Link', '')
            if 'rel="next"' in link_header:
                # Extract next URL from Link header
                next_link = [l.split(';')[0].strip('<> ') for l in link_header.split(',') if 'rel="next"' in l]
                url = next_link[0] if next_link else None
            else:
                url = None
            
            time.sleep(0.5)  # Rate limiting
        
        products_updated = 0
        variants_updated = 0
        errors = []
        
        # Process each product
        for product in all_products:
            product_title = product.get('title', '')
            
            # Extract image filename from product title (format: "ImageName - Category")
            if ' - ' not in product_title:
                continue
            
            image_filename = product_title.split(' - ')[0].strip()
            
            # Get aspect ratio for this image from database
            cursor.execute("SELECT aspect_ratio FROM images WHERE filename = ?", (image_filename,))
            image_row = cursor.fetchone()
            
            if not image_row:
                errors.append(f"{product_title}: Image not found in database")
                continue
            
            aspect_ratio = image_row['aspect_ratio']
            
            # Get pricing data for this aspect ratio (EXACT copy from shopify_api_creator)
            pricing_data = []
            
            # Get base pricing for all categories
            cursor.execute("""
                SELECT 
                    ps.display_name as product_type,
                    pz.size_name,
                    bp.cost_price
                FROM base_pricing bp
                JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                JOIN print_sizes pz ON bp.size_id = pz.size_id
                JOIN aspect_ratios ar ON pz.aspect_ratio_id = ar.aspect_ratio_id
                WHERE bp.is_available = TRUE
                AND ar.display_name = ?
                ORDER BY pz.width, pz.height
            """, (aspect_ratio,))
            
            base_pricing = cursor.fetchall()
            
            for row in base_pricing:
                pricing_data.append({
                    'product_type': row['product_type'],
                    'size_name': row['size_name'],
                    'cost_price': row['cost_price']
                })
            
            # Add framed canvas variants with colors (EXACT copy from shopify_api_creator)
            framed_canvas_config = [
                ('0.75" Framed Canvas', [
                    ('Black', 'black_floating_075'),
                    ('White', 'white_floating_075'),
                    ('Silver', 'silver_floating_075'),
                    ('Gold', 'gold_floating_075'),
                ]),
                ('1.25" Framed Canvas', [
                    ('Black', 'black_floating_125'),
                    ('White', 'white_floating_125'),
                    ('Oak', 'oak_floating_125'),
                ]),
                ('1.50" Framed Canvas', [
                    ('Black', 'black_floating_150'),
                    ('White', 'white_floating_150'),
                    ('Oak', 'oak_floating_150'),
                ]),
            ]
            
            for canvas_type, frame_colors in framed_canvas_config:
                cursor.execute("""
                    SELECT 
                        ps.display_name as product_type,
                        pz.size_name,
                        bp.cost_price
                    FROM base_pricing bp
                    JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                    JOIN print_sizes pz ON bp.size_id = pz.size_id
                    JOIN aspect_ratios ar ON pz.aspect_ratio_id = ar.aspect_ratio_id
                    WHERE bp.is_available = TRUE
                    AND ar.display_name = ?
                    AND ps.display_name = ?
                    ORDER BY pz.width, pz.height
                """, (aspect_ratio, canvas_type))
                
                base_framed_pricing = cursor.fetchall()
                
                for color_name, option_name in frame_colors:
                    cursor.execute("""
                        SELECT op.cost_price
                        FROM option_pricing op
                        JOIN product_options po ON op.option_id = po.option_id
                        WHERE po.option_name = ?
                    """, (option_name,))
                    
                    frame_row = cursor.fetchone()
                    frame_adjustment = float(frame_row[0]) if frame_row and frame_row[0] else 0.0
                    
                    for row in base_framed_pricing:
                        pricing_data.append({
                            'product_type': f"{canvas_type} {color_name}",
                            'size_name': row['size_name'],
                            'cost_price': row['cost_price'] + frame_adjustment
                        })
            
            # Now update variants (EXACT copy from shopify_api_creator)
            product_updated = False
            for variant in product.get('variants', []):
                variant_id = variant.get('id')
                option1 = variant.get('option1')  # Product type
                option2 = variant.get('option2')  # Size
                
                if not option1 or not option2:
                    continue
                
                # Find matching price in database
                matching_price = None
                for price_row in pricing_data:
                    db_prod_type = price_row['product_type']
                    shopify_prod_type = map_product_type_to_shopify(db_prod_type)
                    if shopify_prod_type is None:
                        shopify_prod_type = db_prod_type
                    
                    db_size = price_row['size_name'].strip('"')
                    
                    if shopify_prod_type == option1 and db_size == option2:
                        matching_price = round(price_row['cost_price'] * markup_multiplier, 2)
                        break
                
                if matching_price is None:
                    errors.append(f"{product_title} - {option1} / {option2}: No matching price found")
                    continue
                
                # Update variant price via API
                update_url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/variants/{variant_id}.json'
                update_data = {
                    'variant': {
                        'id': variant_id,
                        'price': str(matching_price)
                    }
                }
                
                update_response = requests.put(update_url, headers=headers, json=update_data)
                
                if update_response.status_code == 200:
                    variants_updated += 1
                    product_updated = True
                else:
                    errors.append(f"{product_title} - {option1} / {option2}: Failed to update (HTTP {update_response.status_code})")
                
                time.sleep(0.5)  # Rate limiting
            
            if product_updated:
                products_updated += 1
        
        conn.close()
        
        duration = round((time.time() - start_time) / 60, 2)
        
        return jsonify({
            'success': True,
            'products_updated': products_updated,
            'variants_updated': variants_updated,
            'duration_minutes': duration,
            'errors': errors[:100]  # Limit to first 100 errors
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
