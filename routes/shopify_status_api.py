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
