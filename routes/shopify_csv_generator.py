"""
Fifth Element Photography - Shopify CSV Generator
Automatically generates Shopify product CSVs with pricing from database
Version: 1.0.0
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
            image_url = image.get('url', '')
            
            # Detect aspect ratio
            aspect_ratio = detect_aspect_ratio(filename)
            
            # Generate product handle
            handle = slugify(title)
            
            # Query pricing for Fine Art Paper and Canvas
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
                ORDER BY pc.display_order, ps.display_order, pz.width, pz.height
            """, (aspect_ratio,))
            
            pricing_data = cursor.fetchall()
            
            if not pricing_data:
                continue
            
            # Group by product type
            product_types = {}
            for row in pricing_data:
                prod_type = row['product_type']
                if prod_type not in product_types:
                    product_types[prod_type] = []
                product_types[prod_type].append({
                    'size': row['size_name'],
                    'cost': row['cost_price'],
                    'price': round(row['cost_price'] * markup_multiplier, 2)
                })
            
            # Generate CSV rows
            first_row = True
            for prod_type, variants in product_types.items():
                for variant in variants:
                    if first_row:
                        # First row has full product details
                        csv_rows.append({
                            'Handle': handle,
                            'Title': title,
                            'Body (HTML)': description,
                            'Vendor': 'Lumaprints',
                            'Product Category': 'Home & Garden > Decor > Artwork > Posters, Prints, & Visual Artwork',
                            'Type': 'Canvas Print' if 'Canvas' in prod_type else 'Art Print',
                            'Tags': '',
                            'Published': 'true',
                            'Option1 Name': 'Printed Product',
                            'Option1 Value': prod_type,
                            'Option1 Linked To': '',
                            'Option2 Name': 'Size',
                            'Option2 Value': variant['size'],
                            'Option2 Linked To': '',
                            'Option3 Name': '',
                            'Option3 Value': '',
                            'Option3 Linked To': '',
                            'Variant SKU': '',
                            'Variant Grams': '0.0',
                            'Variant Inventory Tracker': 'shopify',
                            'Variant Inventory Qty': '10',
                            'Variant Inventory Policy': 'deny',
                            'Variant Fulfillment Service': 'manual',
                            'Variant Price': str(variant['price']),
                            'Variant Compare At Price': '',
                            'Variant Requires Shipping': 'true',
                            'Variant Taxable': 'true',
                            'Unit Price Total Measure': '',
                            'Unit Price Total Measure Unit': '',
                            'Unit Price Base Measure': '',
                            'Unit Price Base Measure Unit': '',
                            'Variant Barcode': '',
                            'Image Src': image_url,
                            'Image Position': '1',
                            'Image Alt Text': '',
                            'Gift Card': 'false',
                            'SEO Title': '',
                            'SEO Description': '',
                            'Color (product.metafields.shopify.color-pattern)': '',
                            'Frame style (product.metafields.shopify.frame-style)': '',
                            'Material (product.metafields.shopify.material)': 'canvas' if 'Canvas' in prod_type else '',
                            'Plant characteristics (product.metafields.shopify.plant-characteristics)': '',
                            'Plant class (product.metafields.shopify.plant-class)': '',
                            'Plant name (product.metafields.shopify.plant-name)': '',
                            'Suitable space (product.metafields.shopify.suitable-space)': '',
                            'Sunlight (product.metafields.shopify.sunlight)': '',
                            'Theme (product.metafields.shopify.theme)': '',
                            'Variant Image': '',
                            'Variant Weight Unit': 'lb',
                            'Variant Tax Code': '',
                            'Cost per item': '',
                            'Status': 'active'
                        })
                        first_row = False
                    else:
                        # Subsequent rows only have variant details
                        csv_rows.append({
                            'Handle': handle,
                            'Title': '',
                            'Body (HTML)': '',
                            'Vendor': '',
                            'Product Category': '',
                            'Type': '',
                            'Tags': '',
                            'Published': '',
                            'Option1 Name': '',
                            'Option1 Value': prod_type,
                            'Option1 Linked To': '',
                            'Option2 Name': '',
                            'Option2 Value': variant['size'],
                            'Option2 Linked To': '',
                            'Option3 Name': '',
                            'Option3 Value': '',
                            'Option3 Linked To': '',
                            'Variant SKU': '',
                            'Variant Grams': '0.0',
                            'Variant Inventory Tracker': 'shopify',
                            'Variant Inventory Qty': '10',
                            'Variant Inventory Policy': 'deny',
                            'Variant Fulfillment Service': 'manual',
                            'Variant Price': str(variant['price']),
                            'Variant Compare At Price': '',
                            'Variant Requires Shipping': 'true',
                            'Variant Taxable': 'true',
                            'Unit Price Total Measure': '',
                            'Unit Price Total Measure Unit': '',
                            'Unit Price Base Measure': '',
                            'Unit Price Base Measure Unit': '',
                            'Variant Barcode': '',
                            'Image Src': '',
                            'Image Position': '',
                            'Image Alt Text': '',
                            'Gift Card': '',
                            'SEO Title': '',
                            'SEO Description': '',
                            'Color (product.metafields.shopify.color-pattern)': '',
                            'Frame style (product.metafields.shopify.frame-style)': '',
                            'Material (product.metafields.shopify.material)': '',
                            'Plant characteristics (product.metafields.shopify.plant-characteristics)': '',
                            'Plant class (product.metafields.shopify.plant-class)': '',
                            'Plant name (product.metafields.shopify.plant-name)': '',
                            'Suitable space (product.metafields.shopify.suitable-space)': '',
                            'Sunlight (product.metafields.shopify.sunlight)': '',
                            'Theme (product.metafields.shopify.theme)': '',
                            'Variant Image': '',
                            'Variant Weight Unit': 'lb',
                            'Variant Tax Code': '',
                            'Cost per item': '',
                            'Status': ''
                        })
        
        conn.close()
        
        if not csv_rows:
            return jsonify({'success': False, 'error': 'No pricing data found for selected images'}), 400
        
        # Generate CSV file
        output = io.StringIO()
        fieldnames = list(csv_rows[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)
        
        # Convert to bytes for download
        csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
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
