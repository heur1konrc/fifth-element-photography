"""
Fifth Element Photography - Shopify API Product Creator
Creates products directly via Shopify API instead of CSV import
Version: 1.0.0
"""

from flask import Blueprint, request, jsonify
import sqlite3
import os
import requests
import json

shopify_api_creator_bp = Blueprint('shopify_api_creator', __name__)

# Shopify API credentials from environment
SHOPIFY_STORE = os.environ.get('SHOPIFY_STORE', 'fifth-element-photography.myshopify.com')
SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY', '')
SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET', '')
SHOPIFY_API_VERSION = '2024-01'

# Database path
if os.path.exists('/data'):
    DB_PATH = '/data/print_ordering.db'
    IMAGES_FOLDER = '/data'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'print_ordering.db')
    IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def slugify(text):
    """Convert text to URL-friendly slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def map_product_type_to_shopify(db_product_type):
    """Map database product type names to Shopify product type names"""
    mapping = {
        'Hot Press Fine Art Paper': 'Hot Press (recommended for photos)',
        'Cold Press Fine Art Paper': None,  # Exclude
        'Semi-Glossy Fine Art Paper': 'Semi-glossy',
        'Glossy Fine Art Paper': 'Glossy',
        '0.75" Stretched Canvas': 'Canvas',
        '1.25" Stretched Canvas': 'Canvas',
        '1.50" Stretched Canvas': 'Canvas',
        'Rolled Canvas': 'Canvas'
    }
    return mapping.get(db_product_type, db_product_type)

def detect_aspect_ratio(image_filename):
    """Detect aspect ratio from image file"""
    from PIL import Image
    try:
        image_path = os.path.join(IMAGES_FOLDER, image_filename)
        with Image.open(image_path) as img:
            width, height = img.size
            ratio = width / height
            
            if 0.95 <= ratio <= 1.05:
                return 'Square'
            elif 1.45 <= ratio <= 1.55:
                return 'Standard'
            elif 0.65 <= ratio <= 0.70:
                return 'Standard'
            else:
                return 'Standard'
    except Exception as e:
        print(f"Error detecting aspect ratio for {image_filename}: {e}")
        return 'Standard'

@shopify_api_creator_bp.route('/api/shopify/create-product', methods=['POST'])
def create_shopify_product():
    """Create Shopify product directly via API"""
    try:
        data = request.json
        images = data.get('images', [])
        
        if not images:
            return jsonify({'success': False, 'error': 'No images selected'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get global markup
        cursor.execute("""
            SELECT markup_value FROM markup_rules 
            WHERE rule_type = 'global' AND is_active = TRUE 
            LIMIT 1
        """)
        markup_row = cursor.fetchone()
        global_markup = markup_row[0] if markup_row else 100.0
        markup_multiplier = 1 + (global_markup / 100)
        
        created_products = []
        errors = []
        
        for image in images:
            filename = image.get('filename')
            title = image.get('title', filename)
            handle = slugify(title)
            aspect_ratio = detect_aspect_ratio(filename)
            
            # Query pricing
            cursor.execute("""
                SELECT 
                    ps.display_name as product_type,
                    pz.size_name,
                    bp.cost_price
                FROM base_pricing bp
                JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                JOIN product_categories pc ON ps.category_id = pc.category_id
                JOIN print_sizes pz ON bp.size_id = pz.size_id
                JOIN aspect_ratios ar ON pz.aspect_ratio_id = ar.aspect_ratio_id
                WHERE bp.is_available = TRUE
                AND ar.display_name = ?
                AND pc.display_name IN ('Canvas', 'Fine Art Paper')
                ORDER BY 
                    CASE pc.display_name 
                        WHEN 'Fine Art Paper' THEN 1 
                        WHEN 'Canvas' THEN 2 
                    END,
                    ps.display_order, 
                    pz.width, 
                    pz.height
            """, (aspect_ratio,))
            
            pricing_data = cursor.fetchall()
            
            if not pricing_data:
                errors.append(f"{filename}: No pricing data found")
                continue
            
            # Build variants
            variants = []
            for row in pricing_data:
                db_prod_type = row['product_type']
                shopify_prod_type = map_product_type_to_shopify(db_prod_type)
                
                if shopify_prod_type is None:
                    continue
                
                size = row['size_name'].strip('"')
                price = round(row['cost_price'] * markup_multiplier, 2)
                
                variants.append({
                    'option1': shopify_prod_type,
                    'option2': size,
                    'price': str(price),
                    'inventory_quantity': 10,
                    'inventory_management': 'shopify'
                })
            
            # Create product via Shopify API
            product_data = {
                'product': {
                    'title': title,
                    'handle': handle,
                    'vendor': 'Lumaprints',
                    'product_type': 'Art Print',
                    'status': 'active',
                    'options': [
                        {'name': 'Printed Product'},
                        {'name': 'Size'}
                    ],
                    'variants': variants
                }
            }
            
            # Make API request
            url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products.json'
            headers = {
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': SHOPIFY_API_SECRET
            }
            
            response = requests.post(url, headers=headers, json=product_data)
            
            print(f"Shopify API Response Status: {response.status_code}")
            print(f"Shopify API Response: {response.text}")
            
            if response.status_code == 201:
                created_products.append(title)
            else:
                error_msg = f"{title}: HTTP {response.status_code} - {response.text}"
                print(f"ERROR: {error_msg}")
                errors.append(error_msg)
        
        conn.close()
        
        return jsonify({
            'success': len(created_products) > 0,
            'created': created_products,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
