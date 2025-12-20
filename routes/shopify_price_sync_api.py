from flask import Blueprint, jsonify, request
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
    
    cursor.execute("SELECT markup_percentage FROM markup_rules WHERE rule_name = 'global_markup'")
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0]:
        return 1 + (float(row[0]) / 100)
    return 1.5  # Default 50% markup

def calculate_price_for_variant(product_category, size_name, frame_color, subcategory):
    """
    Calculate price for a variant using the exact same logic as shopify_api_creator.
    
    Args:
        product_category: Category from product title (Canvas, Fine Art Paper, etc.)
        size_name: Size like "8×12"
        frame_color: Frame color for framed canvas (or None)
        subcategory: Subcategory from option1 (e.g., "0.75\\" Stretched Canvas")
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        markup_multiplier = get_markup_multiplier()
        
        # Convert Shopify name back to database name
        db_subcategory = map_shopify_to_db_product_type(subcategory)
        
        # For Framed Canvas, extract the base canvas type and frame color
        if product_category == "Framed Canvas" and frame_color:
            # Parse frame color like "0.75\\" Framed Canvas Black" -> canvas_type="0.75\\" Framed Canvas", color="Black"
            # The subcategory already has the full name with color
            parts = db_subcategory.rsplit(' ', 1)  # Split from right to get color
            if len(parts) == 2:
                canvas_type = parts[0]  # e.g., "0.75\\" Framed Canvas"
                color_name = parts[1]   # e.g., "Black"
                
                # Map color names to option names (from shopify_api_creator)
                frame_color_mapping = {
                    'Black': {'0.75" Framed Canvas': 'black_floating_075', '1.25" Framed Canvas': 'black_floating_125', '1.50" Framed Canvas': 'black_floating_150'},
                    'White': {'0.75" Framed Canvas': 'white_floating_075', '1.25" Framed Canvas': 'white_floating_125', '1.50" Framed Canvas': 'white_floating_150'},
                    'Silver': {'0.75" Framed Canvas': 'silver_floating_075'},
                    'Gold': {'0.75" Framed Canvas': 'gold_plein_air'},
                    'Oak': {'1.25" Framed Canvas': 'oak_floating_125', '1.50" Framed Canvas': 'oak_floating_150'},
                }
                
                # Get base price for the framed canvas type and size
                cursor.execute("""
                    SELECT bp.cost_price
                    FROM base_pricing bp
                    JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                    JOIN print_sizes pz ON bp.size_id = pz.size_id
                    WHERE ps.display_name = ?
                    AND pz.size_name = ?
                    AND bp.is_available = TRUE
                """, (canvas_type, size_name))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                base_price = float(row[0])
                
                # Get frame color adjustment
                if color_name in frame_color_mapping and canvas_type in frame_color_mapping[color_name]:
                    option_name = frame_color_mapping[color_name][canvas_type]
                    
                    cursor.execute("""
                        SELECT op.cost_price
                        FROM option_pricing op
                        JOIN product_options po ON op.option_id = po.option_id
                        WHERE po.option_name = ?
                    """, (option_name,))
                    
                    frame_row = cursor.fetchone()
                    frame_adjustment = float(frame_row[0]) if frame_row and frame_row[0] else 0.0
                else:
                    frame_adjustment = 0.0
                
                final_price = (base_price + frame_adjustment) * markup_multiplier
                return round(final_price, 2)
        
        # For non-framed products, query directly by subcategory and size
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
        
        base_price = float(row[0])
        final_price = base_price * markup_multiplier
        return round(final_price, 2)
        
    except Exception as e:
        print(f"Error calculating price: {e}")
        return None
    finally:
        conn.close()

@shopify_price_sync_bp.route('/api/shopify/sync-prices', methods=['POST'])
def sync_shopify_prices():
    """
    Sync prices for all existing Shopify products based on current database pricing.
    This updates prices for products that were already created in Shopify.
    """
    try:
        start_time = time.time()
        
        # Shopify API headers
        headers = {
            'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
            'Content-Type': 'application/json'
        }
        
        # Fetch all products from Shopify
        products_url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products.json?limit=250'
        products_response = requests.get(products_url, headers=headers)
        
        if products_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Failed to fetch products from Shopify: HTTP {products_response.status_code}'
            }), 500
        
        products = products_response.json().get('products', [])
        
        products_updated = 0
        variants_updated = 0
        errors = []
        
        # Process each product
        for product in products:
            product_title = product.get('title', '')
            variants = product.get('variants', [])
            
            # Extract category from product title (e.g., "Image Name - Canvas")
            if ' - ' in product_title:
                category = product_title.split(' - ')[-1].strip()
            else:
                category = product.get('product_type', 'Unknown')
            
            product_had_updates = False
            
            # Process each variant
            for variant in variants:
                try:
                    variant_id = variant['id']
                    
                    # Get variant options
                    subcategory = variant.get('option1', '')  # e.g., "0.75\" Stretched Canvas" or "Black" for framed
                    size_name = variant.get('option2', '')     # e.g., "8×12"
                    
                    if not subcategory or not size_name:
                        errors.append(f"Variant {variant_id}: Missing option1 or option2")
                        continue
                    
                    # For framed canvas, the frame color is in the subcategory
                    frame_color = None
                    if category == "Framed Canvas":
                        frame_color = subcategory
                    
                    # Calculate new price
                    new_price = calculate_price_for_variant(category, size_name, frame_color, subcategory)
                    
                    if new_price is None:
                        errors.append(f"Variant {variant_id}: Could not calculate price for {category} | subcategory='{subcategory}' | size='{size_name}' | frame_color='{frame_color}'")
                        continue
                    
                    # Check if price needs updating
                    current_price = float(variant.get('price', 0))
                    
                    # Only update if price changed (with small tolerance for rounding)
                    if abs(current_price - new_price) > 0.01:
                        # Update variant price via API
                        update_url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/variants/{variant_id}.json'
                        update_data = {
                            'variant': {
                                'id': variant_id,
                                'price': str(new_price)
                            }
                        }
                        
                        update_response = requests.put(update_url, headers=headers, json=update_data)
                        
                        if update_response.status_code == 200:
                            variants_updated += 1
                            product_had_updates = True
                        else:
                            errors.append(f"Variant {variant_id}: HTTP {update_response.status_code} - {update_response.text}")
                        
                        # Rate limiting: 2 requests per second
                        time.sleep(0.5)
                
                except Exception as e:
                    errors.append(f"Variant {variant.get('id', 'unknown')}: {str(e)}")
            
            if product_had_updates:
                products_updated += 1
        
        end_time = time.time()
        duration_seconds = end_time - start_time
        
        return jsonify({
            'success': True,
            'products_updated': products_updated,
            'variants_updated': variants_updated,
            'total_products': len(products),
            'duration_seconds': duration_seconds,
            'errors': errors
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@shopify_price_sync_bp.route('/api/shopify/debug-pricing', methods=['GET'])
def debug_pricing():
    """Debug endpoint to inspect database pricing structure"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get a sample of subcategories
        cursor.execute("""
            SELECT ps.display_name, pc.display_name as category
            FROM product_subcategories ps
            JOIN product_categories pc ON ps.category_id = pc.category_id
            LIMIT 10
        """)
        subcategories = [dict(row) for row in cursor.fetchall()]
        
        # Get a sample of sizes
        cursor.execute("""
            SELECT size_name, ar.display_name as aspect_ratio
            FROM print_sizes pz
            JOIN aspect_ratios ar ON pz.aspect_ratio_id = ar.aspect_ratio_id
            LIMIT 10
        """)
        sizes = [dict(row) for row in cursor.fetchall()]
        
        # Try a simple pricing query for "0.75\" Stretched Canvas" and "8×12"
        cursor.execute("""
            SELECT 
                ps.display_name as subcategory,
                pz.size_name,
                bp.cost_price
            FROM base_pricing bp
            JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
            JOIN print_sizes pz ON bp.size_id = pz.size_id
            WHERE ps.display_name = '0.75" Stretched Canvas'
            AND pz.size_name = '8×12'
            AND bp.is_available = TRUE
        """)
        test_price = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'subcategories': subcategories,
            'sizes': sizes,
            'test_query_result': dict(test_price) if test_price else None
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
