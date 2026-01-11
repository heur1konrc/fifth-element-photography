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
import base64

shopify_api_creator_bp = Blueprint('shopify_api_creator', __name__)

# Shopify API credentials from environment
SHOPIFY_STORE = os.environ.get('SHOPIFY_STORE', 'fifth-element-photography.myshopify.com')
SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY', '')
SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET', '')
SHOPIFY_API_VERSION = '2024-01'

# Database path
if os.path.exists('/data'):
    DB_PATH = '/data/print_ordering.db'
    IMAGES_FOLDER = '/data/gallery-images'  # Use gallery-optimized images (1200px, ~1-2MB for fast Shopify upload)
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'print_ordering.db')
    IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')

def ensure_shopify_products_table():
    """Ensure shopify_products table exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopify_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            category TEXT,
            shopify_product_id TEXT NOT NULL,
            shopify_handle TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(image_filename, category)
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    ensure_shopify_products_table()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_image_titles():
    """Load image titles from JSON file"""
    try:
        titles_file = '/data/image_titles.json' if os.path.exists('/data') else os.path.join(os.path.dirname(__file__), '..', 'data', 'image_titles.json')
        if os.path.exists(titles_file):
            with open(titles_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading image titles: {e}")
    return {}

def load_image_descriptions():
    """Load image descriptions from JSON file"""
    try:
        descriptions_file = '/data/image_descriptions.json' if os.path.exists('/data') else os.path.join(os.path.dirname(__file__), '..', 'data', 'image_descriptions.json')
        if os.path.exists(descriptions_file):
            with open(descriptions_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading image descriptions: {e}")
    return {}

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
        # Fine Art Paper
        'Hot Press Fine Art Paper': 'Hot Press (recommended for photos)',
        'Cold Press Fine Art Paper': 'Cold Press',
        'Semi-Glossy Fine Art Paper': 'Semi-glossy',
        'Glossy Fine Art Paper': 'Glossy',
        # Canvas
        '0.75" Stretched Canvas': '0.75 Stretched Canvas',
        '1.25" Stretched Canvas': '1.25 Stretched Canvas',
        '1.50" Stretched Canvas': '1.50 Stretched Canvas',
        # Framed Canvas
        '0.75" Framed Canvas': '0.75 Framed Canvas',
        '1.25" Framed Canvas': '1.25 Framed Canvas',
        '1.50" Framed Canvas': '1.50 Framed Canvas',
        # Foam-mounted
        'Foam-mounted Hot Press': 'Foam-mounted Hot Press',
        'Foam-mounted Cold Press': 'Foam-mounted Cold Press',
        'Foam-mounted Semi-Glossy': 'Foam-mounted Semi-Glossy',
        'Foam-mounted Glossy': 'Foam-mounted Glossy',
        # Metal
        'Glossy White Metal': 'Glossy White Metal Print',
        'Glossy Silver Metal': 'Glossy Silver Metal Print'
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
        
        # Load image titles and descriptions
        image_titles = load_image_titles()
        image_descriptions = load_image_descriptions()
        
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
            # Use saved title from database, or generate from filename
            if filename in image_titles:
                title = image_titles[filename]
            else:
                # Generate clean title from filename as fallback
                title = filename.replace('-', ' ').replace('_', ' ')
                title = os.path.splitext(title)[0]
                title = ' '.join(word.capitalize() for word in title.split())
            handle = slugify(title)
            
            # Load description for this image
            description = image_descriptions.get(filename, '')
            
            aspect_ratio = detect_aspect_ratio(filename)
            
            # Query pricing for unframed products
            cursor.execute("""
                SELECT 
                    ps.display_name as product_type,
                    pz.size_name,
                    bp.cost_price,
                    NULL as frame_option
                FROM base_pricing bp
                JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                JOIN product_categories pc ON ps.category_id = pc.category_id
                JOIN print_sizes pz ON bp.size_id = pz.size_id
                JOIN aspect_ratios ar ON pz.aspect_ratio_id = ar.aspect_ratio_id
                WHERE bp.is_available = TRUE
                AND ar.display_name = ?
                AND pc.display_name IN ('Canvas', 'Fine Art Paper', 'Foam-mounted Fine Art Paper', 'Metal')
                ORDER BY 
                    CASE pc.display_name 
                        WHEN 'Fine Art Paper' THEN 1 
                        WHEN 'Canvas' THEN 2 
                        WHEN 'Foam-mounted Fine Art Paper' THEN 3
                        WHEN 'Metal' THEN 4
                    END,
                    ps.display_order, 
                    pz.width, 
                    pz.height
            """, (aspect_ratio,))
            
            pricing_data = list(cursor.fetchall())
            
            # Add framed canvas options with flattened frame colors
            framed_canvas_config = [
                ('0.75" Framed Canvas', [
                    ('Black', 'black_floating_075'),
                    ('White', 'white_floating_075'),
                    ('Silver', 'silver_floating_075'),
                    ('Gold', 'gold_plein_air'),
                ]),
                ('1.25" Framed Canvas', [
                    ('Black', 'black_floating_125'),
                    ('Natural Oak', 'oak_floating_125'),
                    ('Walnut', 'walnut_floating_125'),
                ]),
                ('1.50" Framed Canvas', [
                    ('Black', 'black_floating_150'),
                    ('White', 'white_floating_150'),
                    ('Oak', 'oak_floating_150'),
                ]),
            ]
            
            for canvas_type, frame_colors in framed_canvas_config:
                # Get base pricing for this framed canvas type
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
                
                # For each frame color, add variants with the frame color in the name
                for color_name, option_name in frame_colors:
                    # Get frame price adjustment (if any)
                    cursor.execute("""
                        SELECT op.cost_price
                        FROM option_pricing op
                        JOIN product_options po ON op.option_id = po.option_id
                        WHERE po.option_name = ?
                    """, (option_name,))
                    
                    frame_row = cursor.fetchone()
                    frame_adjustment = float(frame_row[0]) if frame_row and frame_row[0] else 0.0
                    
                    # Add pricing data with flattened frame color name
                    for row in base_framed_pricing:
                        pricing_data.append({
                            'product_type': f"{canvas_type} {color_name}",
                            'size_name': row['size_name'],
                            'cost_price': row['cost_price'] + frame_adjustment,
                            'frame_option': color_name
                        })
            
            if not pricing_data:
                errors.append(f"{filename}: No pricing data found")
                continue
            
            # Group pricing data by category
            categories = {
                'Canvas': [],
                'Framed Canvas': [],
                'Fine Art Paper': [],
                'Foam-mounted Print': [],
                'Metal': []
            }
            
            for row in pricing_data:
                db_prod_type = row['product_type']
                
                # Determine category
                if 'Framed Canvas' in db_prod_type:
                    category = 'Framed Canvas'
                elif 'Canvas' in db_prod_type:
                    category = 'Canvas'
                elif 'Fine Art Paper' in db_prod_type:
                    category = 'Fine Art Paper'
                elif 'Foam-mounted' in db_prod_type:
                    category = 'Foam-mounted Print'
                elif 'Metal' in db_prod_type:
                    category = 'Metal'
                else:
                    continue
                
                categories[category].append(row)
            
            # Prepare image for upload
            image_path = os.path.join(IMAGES_FOLDER, filename)
            image_attachment = None
            
            # Check if image exists and is under 20MB
            if os.path.exists(image_path):
                file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
                if file_size_mb <= 20:
                    # Read image and encode as base64
                    with open(image_path, 'rb') as img_file:
                        image_data = base64.b64encode(img_file.read()).decode('utf-8')
                        image_attachment = {
                            'attachment': image_data,
                            'filename': filename
                        }
                else:
                    errors.append(f"{filename}: Image size ({file_size_mb:.1f}MB) exceeds 20MB limit")
                    continue
            else:
                errors.append(f"{filename}: Image file not found")
                continue
            
            # Create separate products for each category
            for category_name, category_data in categories.items():
                if not category_data:
                    continue  # Skip empty categories
                
                # Build variants for this category
                variants = []
                product_types = set()
                sizes = set()
                
                for row in category_data:
                    db_prod_type = row['product_type']
                    shopify_prod_type = map_product_type_to_shopify(db_prod_type)
                    
                    if shopify_prod_type is None:
                        shopify_prod_type = db_prod_type  # Use as-is if no mapping
                    
                    size = row['size_name'].strip('"')
                    price = round(row['cost_price'] * markup_multiplier, 2)
                    
                    product_types.add(shopify_prod_type)
                    sizes.add(size)
                    
                    variants.append({
                        'option1': f'Printed Product - {shopify_prod_type}',
                        'option2': f'Size - {size}',
                        'price': str(price),
                        'inventory_quantity': 10,
                        'inventory_management': 'shopify'
                    })
                
                # Create product title and handle for this category
                category_title = f"{title} - {category_name}"
                category_handle = f"{handle}-{slugify(category_name)}"
                
                # Create product via Shopify API
                product_data = {
                    'product': {
                        'title': category_title,
                        'body_html': description,  # Use image description
                        'handle': category_handle,
                        'vendor': 'Lumaprints',
                        'product_type': 'Prints',  # Set category to Prints
                        'status': 'active',
                        'options': [
                            {'name': 'Printed Product', 'values': sorted([f'Printed Product - {pt}' for pt in product_types])},
                            {'name': 'Size', 'values': sorted([f'Size - {s}' for s in sizes])}
                        ],
                        'variants': variants,
                        'images': [image_attachment] if image_attachment else []
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
                    created_products.append(category_title)
                    
                    # Extract Shopify product ID and handle from response
                    response_data = response.json()
                    shopify_product_id = str(response_data['product']['id'])
                    actual_handle = response_data['product']['handle']  # Use actual handle from Shopify
                    
                    # Publish product to Storefront API sales channel
                    try:
                        # Get the publication ID for the Storefront API channel
                        publications_url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/publications.json'
                        pub_response = requests.get(publications_url, headers=headers)
                        
                        if pub_response.status_code == 200:
                            publications = pub_response.json().get('publications', [])
                            # Find the Storefront API publication (app_id: 580111)
                            storefront_pub = next((p for p in publications if p.get('app_id') == 580111), None)
                            
                            if storefront_pub:
                                # Publish product to Storefront API channel
                                publish_url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/publications/{storefront_pub["id"]}/resource_publications.json'
                                publish_data = {
                                    'resource_publication': {
                                        'resource_id': shopify_product_id,
                                        'resource_type': 'Product',
                                        'published': True
                                    }
                                }
                                publish_response = requests.post(publish_url, headers=headers, json=publish_data)
                                if publish_response.status_code in [200, 201]:
                                    print(f"✓ Published {category_title} to Storefront API")
                                else:
                                    print(f"⚠ Failed to publish {category_title} to Storefront API: {publish_response.text}")
                            else:
                                print(f"⚠ Storefront API publication not found")
                    except Exception as pub_error:
                        print(f"⚠ Error publishing to Storefront API: {pub_error}")
                        # Don't fail the whole operation if publishing fails
                    
                    # Save to database for tracking with category column
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO shopify_products (image_filename, category, shopify_product_id, shopify_handle)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(image_filename, category) DO UPDATE SET
                            shopify_product_id = excluded.shopify_product_id,
                            shopify_handle = excluded.shopify_handle,
                            updated_at = CURRENT_TIMESTAMP
                    """, (filename, category_name, shopify_product_id, actual_handle))
                    conn.commit()
                else:
                    error_msg = f"{category_title}: HTTP {response.status_code} - {response.text}"
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


@shopify_api_creator_bp.route('/sync-shopify-prices', methods=['POST'])
def sync_shopify_prices():
    """
    Sync prices from database to existing Shopify products
    Updates all variant prices to match current database pricing with markup
    """
    try:
        # Get markup from request
        data = request.get_json()
        markup_multiplier = float(data.get('markup', 2.5))
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all Shopify products from tracking table
        cursor.execute("""
            SELECT image_filename, shopify_product_id, shopify_handle
            FROM shopify_products
            ORDER BY image_filename
        """)
        
        shopify_products = cursor.fetchall()
        
        if not shopify_products:
            return jsonify({'success': False, 'error': 'No Shopify products found in database'})
        
        updated_count = 0
        skipped_count = 0
        errors = []
        
        # Process each Shopify product
        for product_row in shopify_products:
            shopify_product_id = product_row['shopify_product_id']
            image_filename = product_row['image_filename']
            shopify_handle = product_row['shopify_handle']
            
            try:
                # Extract actual filename and category from tracking filename
                # Format: "filename_Category" or just "filename"
                if '_Canvas' in image_filename or '_Framed Canvas' in image_filename or '_Fine Art Paper' in image_filename or '_Foam-mounted Print' in image_filename:
                    # Split on last underscore to get category
                    parts = image_filename.rsplit('_', 1)
                    actual_filename = parts[0]
                    category = parts[1] if len(parts) > 1 else None
                else:
                    actual_filename = image_filename
                    category = None
                
                # Get aspect ratio for this image
                cursor.execute("SELECT aspect_ratio FROM images WHERE filename = ?", (actual_filename,))
                image_row = cursor.fetchone()
                
                if not image_row:
                    errors.append(f"{image_filename}: Image not found in database")
                    skipped_count += 1
                    continue
                
                aspect_ratio = image_row['aspect_ratio']
                
                # Get current pricing from database for this aspect ratio and category
                # This replicates the pricing logic from create_products
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
                
                # Add framed canvas variants with colors
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
                
                # Get Shopify product variants
                url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products/{shopify_product_id}.json'
                headers = {
                    'X-Shopify-Access-Token': SHOPIFY_API_SECRET
                }
                
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    errors.append(f"{image_filename}: Failed to fetch from Shopify (HTTP {response.status_code})")
                    skipped_count += 1
                    continue
                
                shopify_product = response.json()['product']
                variants = shopify_product.get('variants', [])
                
                # Update each variant's price
                for variant in variants:
                    variant_id = variant['id']
                    option1 = variant.get('option1', '')  # Product type
                    option2 = variant.get('option2', '')  # Size
                    
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
                        continue  # Skip variants with no matching price
                    
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
                        updated_count += 1
                    else:
                        errors.append(f"{image_filename} variant {variant_id}: HTTP {update_response.status_code}")
                
            except Exception as e:
                errors.append(f"{image_filename}: {str(e)}")
                skipped_count += 1
        
        conn.close()
        
        return jsonify({
            'success': True,
            'updated': updated_count,
            'skipped': skipped_count,
            'errors': errors[:10]  # Limit to first 10 errors
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@shopify_api_creator_bp.route('/api/shopify/product-categories/<filename>', methods=['GET'])
def get_product_categories(filename):
    """
    Get all Shopify product handles for a given image filename, organized by category
    Returns: {
        'Canvas': 'handle-canvas',
        'Metal': 'handle-metal',
        'Fine Art Paper': 'handle-fine-art-paper',
        'Framed Canvas': 'handle-framed-canvas',
        'Foam-mounted Print': 'handle-foam-mounted-print'
    }
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, shopify_handle
            FROM shopify_products
            WHERE image_filename = ?
            ORDER BY category
        """, (filename,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify({'success': False, 'error': 'No products found for this image'}), 404
        
        # Build category -> handle mapping
        categories = {}
        for row in rows:
            categories[row['category']] = row['shopify_handle']
        
        return jsonify({
            'success': True,
            'filename': filename,
            'categories': categories
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@shopify_api_creator_bp.route('/api/shopify/sync-products', methods=['POST'])
def sync_shopify_products():
    """
    Sync all products from Shopify to update the shopify_products table
    This refreshes the LIVE status badges in the admin panel
    """
    try:
        # Fetch all products from Shopify
        url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products.json?limit=250'
        auth = (SHOPIFY_API_KEY, SHOPIFY_API_SECRET)
        
        all_products = []
        while url:
            response = requests.get(url, auth=auth)
            if response.status_code != 200:
                return jsonify({
                    'success': False,
                    'error': f'Shopify API error: {response.status_code}'
                }), 500
            
            data = response.json()
            all_products.extend(data.get('products', []))
            
            # Check for pagination
            link_header = response.headers.get('Link', '')
            url = None
            if 'rel="next"' in link_header:
                # Extract next URL from Link header
                for link in link_header.split(','):
                    if 'rel="next"' in link:
                        url = link.split(';')[0].strip('<> ')
                        break
        
        # Clear existing shopify_products table
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM shopify_products')
        
        # Repopulate with current products
        synced_count = 0
        for product in all_products:
            # Extract image filename from product title or tags
            title = product.get('title', '')
            
            # Try to extract filename from title (format: "Title - Category")
            # The filename should be in the database based on the title
            cursor.execute("""
                SELECT DISTINCT image_filename 
                FROM base_pricing bp
                WHERE EXISTS (
                    SELECT 1 FROM images 
                    WHERE filename = bp.image_filename 
                    AND title = ?
                )
            """, (title.split(' - ')[0] if ' - ' in title else title,))
            
            result = cursor.fetchone()
            if result:
                image_filename = result[0]
                
                # Insert into shopify_products
                cursor.execute("""
                    INSERT OR REPLACE INTO shopify_products 
                    (image_filename, shopify_product_id, shopify_handle)
                    VALUES (?, ?, ?)
                """, (image_filename, str(product['id']), product['handle']))
                
                synced_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'total_shopify_products': len(all_products),
            'synced': synced_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
