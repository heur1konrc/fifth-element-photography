
"""
Fifth Element Photography - Shopify CSV Generator
Automatically generates Shopify product CSVs with pricing from database
Version: 1.1.0
"""

from flask import Blueprint, request, jsonify, send_file
import sqlite3
import csv
import io
import os
from datetime import datetime

shopify_csv_bp = Blueprint('shopify_csv', __name__)

# Database path - use /data on Railway, fallback to local for development
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
    """Map database product type names to Shopify product type names for mapping compatibility"""
    mapping = {
        'Hot Press Fine Art Paper': 'Hot Press (recommended for photos)',
        'Cold Press Fine Art Paper': None,  # Exclude Cold Press - not used in Shopify
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
            
            # Determine aspect ratio category
            if 0.95 <= ratio <= 1.05:  # Square (1:1)
                return 'Square'
            elif 1.45 <= ratio <= 1.55:  # Standard (3:2)
                return 'Standard'
            elif 0.65 <= ratio <= 0.70:  # Portrait (2:3)
                return 'Standard'  # Use same sizes as 3:2
            else:
                return 'Standard'  # Default to standard
    except Exception as e:
        print(f"Error detecting aspect ratio for {image_filename}: {e}")
        return 'Standard'  # Default

@shopify_csv_bp.route('/api/shopify/generate-csv', methods=['POST'])
def generate_shopify_csv():
    """Generate Shopify product CSV for selected images"""
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
        
        # Prepare CSV data
        csv_rows = []
        
        for image in images:
            filename = image.get('filename')
            title = image.get('title', filename)
            description = image.get('description', '')
            # Leave image_url blank - user will add images manually in Shopify
            image_url = ''
            
            # Detect aspect ratio
            aspect_ratio = detect_aspect_ratio(filename)
            
            # Generate product handle
            handle = slugify(title)

            # Get available frame options for 1.25" Framed Canvas
            cursor.execute("""
                SELECT DISTINCT fo.frame_name 
                FROM frame_options fo
                JOIN product_subcategories ps ON fo.subcategory_id = ps.subcategory_id
                WHERE ps.display_name = '1.25" Framed Canvas' AND fo.is_available = TRUE
            """)
            frame_options_125 = [row['frame_name'] for row in cursor.fetchall()]

            # Query pricing for all product types
            cursor.execute("""
                SELECT 
                    ps.display_name as product_type,
                    pz.size_name,
                    bp.cost_price,
                    pc.display_name as category_name
                FROM base_pricing bp
                JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                JOIN product_categories pc ON ps.category_id = pc.category_id
                JOIN print_sizes pz ON bp.size_id = pz.size_id
                JOIN aspect_ratios ar ON pz.aspect_ratio_id = ar.aspect_ratio_id
                WHERE bp.is_available = TRUE
                AND ar.display_name = ?
                ORDER BY 
                    pc.display_name, 
                    ps.display_order, 
                    pz.width, 
                    pz.height
            """, (aspect_ratio,))
            
            pricing_data = cursor.fetchall()
            
            if not pricing_data:
                continue

            # Generate CSV rows
            first_row = True
            for row in pricing_data:
                db_prod_type = row['product_type']
                size = row['size_name'].strip('\'')
                cost = row['cost_price']
                price = round(cost * markup_multiplier, 2)
                category = row['category_name']

                # Special handling for Framed Canvas
                if "Framed Canvas" in db_prod_type:
                    if db_prod_type == '1.25" Framed Canvas':
                        for frame in frame_options_125:
                            if first_row:
                                csv_rows.append(get_product_row(handle, title, description, image_url, 'Framed Canvas', size, price, frame, True))
                                first_row = False
                            else:
                                csv_rows.append(get_variant_row(handle, 'Framed Canvas', size, price, frame))
                else:
                    if first_row:
                        csv_rows.append(get_product_row(handle, title, description, image_url, category, size, price, None, True))
                        first_row = False
                    else:
                        csv_rows.append(get_variant_row(handle, category, size, price, None))

        conn.close()
        
        if not csv_rows:
            return jsonify({'success': False, 'error': 'No pricing data found for selected images'}), 400
        
        # Generate CSV file
        output = io.StringIO()
        fieldnames = list(csv_rows[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(csv_rows)
        
        # Convert to bytes for download with UTF-8 BOM for proper Excel compatibility
        csv_content = output.getvalue()
        csv_bytes = io.BytesIO()
        csv_bytes.write('\ufeff'.encode('utf-8'))  # UTF-8 BOM
        csv_bytes.write(csv_content.encode('utf-8'))
        csv_bytes.seek(0)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'shopify_products_{timestamp}.csv'
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_product_row(handle, title, description, image_url, prod_type, size, price, frame, is_first):
    row = {
        'Handle': handle,
        'Title': title,
        'Body (HTML)': description,
        'Vendor': 'Lumaprints',
        'Product Category': 'Home & Garden > Decor > Artwork > Posters, Prints, & Visual Artwork',
        'Type': prod_type,
        'Tags': '',
        'Published': 'true',
        'Option1 Name': 'Size',
        'Option1 Value': size,
        'Option2 Name': 'Frame' if frame else '',
        'Option2 Value': frame if frame else '',
        'Option3 Name': '',
        'Option3 Value': '',
        'Variant SKU': '',
        'Variant Grams': '0.0',
        'Variant Inventory Tracker': 'shopify',
        'Variant Inventory Qty': '10',
        'Variant Inventory Policy': 'deny',
        'Variant Fulfillment Service': 'manual',
        'Variant Price': str(price),
        'Variant Compare At Price': '',
        'Variant Requires Shipping': 'true',
        'Variant Taxable': 'true',
        'Variant Barcode': '',
        'Image Src': image_url,
        'Image Position': '1' if is_first else '',
        'Image Alt Text': title if is_first else '',
        'Gift Card': 'false',
        'Status': 'active'
    }
    return row

def get_variant_row(handle, prod_type, size, price, frame):
    row = {
        'Handle': handle,
        'Title': '',
        'Body (HTML)': '',
        'Vendor': '',
        'Product Category': '',
        'Type': '',
        'Tags': '',
        'Published': '',
        'Option1 Name': '',
        'Option1 Value': size,
        'Option2 Name': '',
        'Option2 Value': frame if frame else '',
        'Option3 Name': '',
        'Option3 Value': '',
        'Variant SKU': '',
        'Variant Grams': '0.0',
        'Variant Inventory Tracker': 'shopify',
        'Variant Inventory Qty': '10',
        'Variant Inventory Policy': 'deny',
        'Variant Fulfillment Service': 'manual',
        'Variant Price': str(price),
        'Variant Compare At Price': '',
        'Variant Requires Shipping': 'true',
        'Variant Taxable': 'true',
        'Variant Barcode': '',
        'Image Src': '',
        'Image Position': '',
        'Image Alt Text': '',
        'Gift Card': 'false',
        'Status': 'active'
    }
    return row
