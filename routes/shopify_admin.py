"""
Shopify Product Mapping Admin - Multi-Product Support
Fifth Element Photography - v3.0.2
Supports mapping 5 product types per image
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import sqlite3
import os
import json
from functools import wraps

shopify_admin_bp = Blueprint('shopify_admin', __name__, url_prefix='/admin')

PRODUCT_CATEGORIES = [
    'Metal',
    'Canvas',
    'Fine Art Paper',
    'Framed Canvas',
    'Foam-mounted Print'
]

def get_db_path(db_name='print_ordering.db'):
    """Get database path for production or local"""
    if os.path.exists('/data'):
        return f'/data/{db_name}'
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', db_name)

def load_image_titles():
    """Load image titles from JSON file"""
    titles_path = '/data/image_titles.json' if os.path.exists('/data') else 'image_titles.json'
    try:
        if os.path.exists(titles_path):
            with open(titles_path, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def login_required(f):
    """Decorator to require login for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@shopify_admin_bp.route('/shopify-mapping')
def shopify_mapping():
    """Shopify product mapping management page - supports multiple products per image"""
    # Get all image files from /data directory
    images_dir = '/data' if os.path.exists('/data') else os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
    
    image_files = []
    error_msg = None
    
    try:
        if not os.path.exists(images_dir):
            error_msg = f"Images directory not found at {images_dir}"
        else:
            for filename in os.listdir(images_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    image_files.append(filename)
    except Exception as e:
        error_msg = f"Error loading images: {e}"
        print(error_msg)
    
    # Load image titles
    image_titles_map = load_image_titles()
    
    # Get existing mappings from shopify_products table
    print_db = get_db_path('print_ordering.db')
    conn = sqlite3.connect(print_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Ensure table exists with correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shopify_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_filename TEXT NOT NULL,
            category TEXT NOT NULL,
            shopify_product_id TEXT,
            shopify_handle TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(image_filename, category)
        )
    ''')
    
    try:
        cursor.execute('SELECT image_filename, category, shopify_handle FROM shopify_products')
        mappings_rows = cursor.fetchall()
    except sqlite3.OperationalError:
        mappings_rows = []
    conn.close()
    
    # Build mappings dict: {image_filename: {category: handle}}
    mappings = {}
    for row in mappings_rows:
        filename = row['image_filename']
        if filename not in mappings:
            mappings[filename] = {}
        mappings[filename][row['category']] = row['shopify_handle']
    
    # Build images data with mappings
    images_data = []
    for filename in sorted(image_files):
        # Get title from image_titles.json or use filename
        img_title = image_titles_map.get(filename, filename.replace('-', ' ').replace('_', ' ').rsplit('.', 1)[0])
        img_mappings = mappings.get(filename, {})
        images_data.append({
            'filename': filename,
            'title': img_title,
            'mappings': {cat: img_mappings.get(cat, '') for cat in PRODUCT_CATEGORIES}
        })
    
    return render_template('admin/shopify_mapping.html', 
                         images=images_data,
                         categories=PRODUCT_CATEGORIES,
                         error=error_msg)

@shopify_admin_bp.route('/api/shopify-mapping/save', methods=['POST'])
def save_shopify_mapping():
    """Save multiple product mappings for an image"""
    data = request.json
    image_filename = data.get('image_filename')
    mappings = data.get('mappings', {})  # {category: handle}
    
    if not image_filename:
        return jsonify({'success': False, 'error': 'Image filename required'}), 400
    
    print_db = get_db_path('print_ordering.db')
    conn = sqlite3.connect(print_db)
    conn.row_factory = sqlite3.Row  # Enable row access by name
    cursor = conn.cursor()
    
    try:
        # Get existing mappings to preserve shopify_product_id
        cursor.execute('SELECT category, shopify_product_id FROM shopify_products WHERE image_filename = ?', (image_filename,))
        existing_rows = cursor.fetchall()
        existing_ids = {row['category']: row['shopify_product_id'] for row in existing_rows}
        
        # Delete existing mappings for this image
        cursor.execute('DELETE FROM shopify_products WHERE image_filename = ?', (image_filename,))
        
        # Insert new mappings
        for category, handle in mappings.items():
            if handle and handle.strip():  # Only save non-empty handles
                # Use existing shopify_product_id if available, otherwise use a placeholder or None
                # Note: If the table has NOT NULL constraint on shopify_product_id, we must provide a value.
                # Since these are manually mapped or updated, we might not have the ID if it wasn't created via API.
                # However, the error suggests it IS required.
                
                shopify_id = existing_ids.get(category)
                
                # If we don't have an ID (e.g. manual entry), we might need to fetch it from Shopify or use a placeholder.
                # For now, if it's missing, we'll use a placeholder to satisfy the constraint if it's a manual mapping.
                if not shopify_id:
                    shopify_id = f"manual_{handle.strip()}"
                
                cursor.execute('''
                    INSERT INTO shopify_products (image_filename, category, shopify_handle, shopify_product_id)
                    VALUES (?, ?, ?, ?)
                ''', (image_filename, category, handle.strip(), shopify_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@shopify_admin_bp.route('/api/shopify-mapping/all')
def get_all_mappings():
    """Get all Shopify mappings (public endpoint for frontend)"""
    try:
        print_db = get_db_path('print_ordering.db')
        conn = sqlite3.connect(print_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get shopify products with image filenames
        cursor.execute('SELECT image_filename, category, shopify_handle FROM shopify_products ORDER BY image_filename, category')
        rows = cursor.fetchall()
        conn.close()
        
        # Build nested structure: { filename: { category: handle, ... }, ... }
        mappings = {}
        for row in rows:
            filename = row['image_filename']
            category = row['category']
            handle = row['shopify_handle']
            
            if not filename:
                continue
            
            if filename not in mappings:
                mappings[filename] = {}
            
            mappings[filename][category] = handle
        
        return jsonify({'success': True, 'mappings': mappings})
    except Exception as e:
        import traceback
        print(f"Error in get_all_mappings: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e), 'mappings': {}}), 500

@shopify_admin_bp.route('/image/<filename>')
def serve_image(filename):
    """Serve image from /data directory"""
    from flask import send_from_directory
    if os.path.exists('/data'):
        return send_from_directory('/data', filename)
    else:
        images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
        return send_from_directory(images_dir, filename)
