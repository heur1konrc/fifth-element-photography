"""
Fifth Element Photography - Shopify Status API
Returns image list with Shopify product status for filtering
Version: 1.0.0
"""

from flask import Blueprint, jsonify
import sqlite3
import os

shopify_status_api_bp = Blueprint('shopify_status_api', __name__)

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

@shopify_status_api_bp.route('/api/shopify/sync-products', methods=['POST'])
def sync_shopify_products():
    """Sync existing Shopify products into database"""
    import requests
    
    SHOPIFY_STORE = os.environ.get('SHOPIFY_STORE', 'fifth-element-photography.myshopify.com')
    SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET', '')
    SHOPIFY_API_VERSION = '2024-01'
    
    try:
        # Fetch all products from Shopify
        url = f'https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products.json?limit=250'
        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': SHOPIFY_API_SECRET
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': f'Shopify API error: {response.status_code}'}), 500
        
        products = response.json().get('products', [])
        
        # Save to database
        conn = get_db()
        cursor = conn.cursor()
        synced_count = 0
        
        for product in products:
            product_id = str(product['id'])
            handle = product['handle']
            title = product['title']
            
            # Try to match title to filename (title should be the image name without extension)
            # Look for matching image file
            image_filename = None
            if os.path.exists(IMAGES_FOLDER):
                for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    potential_file = title + ext
                    if os.path.exists(os.path.join(IMAGES_FOLDER, potential_file)):
                        image_filename = potential_file
                        break
            
            if image_filename:
                cursor.execute("""
                    INSERT OR REPLACE INTO shopify_products (image_filename, shopify_product_id, shopify_handle)
                    VALUES (?, ?, ?)
                """, (image_filename, product_id, handle))
                synced_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'synced': synced_count,
            'total_shopify_products': len(products)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@shopify_status_api_bp.route('/api/images/shopify-status', methods=['GET'])
def get_images_shopify_status():
    """Get all images with their Shopify product status"""
    try:
        # Get all image files
        image_files = []
        if os.path.exists(IMAGES_FOLDER):
            for filename in os.listdir(IMAGES_FOLDER):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    image_files.append(filename)
        
        # Get Shopify product status from database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT image_filename, shopify_product_id, shopify_handle FROM shopify_products")
        shopify_products = {row['image_filename']: {
            'product_id': row['shopify_product_id'],
            'handle': row['shopify_handle']
        } for row in cursor.fetchall()}
        conn.close()
        
        # Build response
        images_with_status = []
        for filename in image_files:
            images_with_status.append({
                'filename': filename,
                'in_shopify': filename in shopify_products,
                'shopify_product_id': shopify_products.get(filename, {}).get('product_id'),
                'shopify_handle': shopify_products.get(filename, {}).get('handle')
            })
        
        return jsonify({
            'success': True,
            'images': images_with_status
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
