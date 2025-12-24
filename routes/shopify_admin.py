"""
Shopify Product Mapping Admin - Multi-Product Support
Fifth Element Photography - v3.0.0
Supports mapping 5 product types per image
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import sqlite3
import os
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
    # Get all images from gallery
    gallery_db = get_db_path('gallery_images.db')
    
    try:
        conn = sqlite3.connect(gallery_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT id, filename, title FROM images ORDER BY created_at DESC')
        images = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Error loading images: {e}")
        images = []
    
    # Get existing mappings from shopify_products table
    print_db = get_db_path('print_ordering.db')
    conn = sqlite3.connect(print_db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Ensure table exists with correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shopify_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_title TEXT NOT NULL,
            category TEXT NOT NULL,
            shopify_product_id TEXT,
            shopify_handle TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(image_title, category)
        )
    ''')
    
    try:
        cursor.execute('SELECT image_title, category, shopify_handle FROM shopify_products')
        mappings_rows = cursor.fetchall()
    except sqlite3.OperationalError:
        mappings_rows = []
    conn.close()
    
    # Build mappings dict: {image_title: {category: handle}}
    mappings = {}
    for row in mappings_rows:
        title = row['image_title']
        if title not in mappings:
            mappings[title] = {}
        mappings[title][row['category']] = row['shopify_handle']
    
    # Build images data with mappings
    images_data = []
    for img in images:
        img_title = img['title'] or img['filename']
        img_mappings = mappings.get(img_title, {})
        images_data.append({
            'id': img['id'],
            'filename': img['filename'],
            'title': img_title,
            'mappings': {cat: img_mappings.get(cat, '') for cat in PRODUCT_CATEGORIES}
        })
    
    return render_template('admin/shopify_mapping.html', 
                         images=images_data,
                         categories=PRODUCT_CATEGORIES)

@shopify_admin_bp.route('/api/shopify-mapping/save', methods=['POST'])
def save_shopify_mapping():
    """Save multiple product mappings for an image"""
    data = request.json
    image_title = data.get('image_title')
    mappings = data.get('mappings', {})  # {category: handle}
    
    if not image_title:
        return jsonify({'success': False, 'error': 'Image title required'}), 400
    
    print_db = get_db_path('print_ordering.db')
    conn = sqlite3.connect(print_db)
    cursor = conn.cursor()
    
    try:
        # Delete existing mappings for this image
        cursor.execute('DELETE FROM shopify_products WHERE image_title = ?', (image_title,))
        
        # Insert new mappings
        for category, handle in mappings.items():
            if handle and handle.strip():  # Only save non-empty handles
                cursor.execute('''
                    INSERT INTO shopify_products (image_title, category, shopify_handle)
                    VALUES (?, ?, ?)
                ''', (image_title, category, handle.strip()))
        
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
        
        # Get shopify products with image titles
        cursor.execute('SELECT image_title, category, shopify_handle FROM shopify_products ORDER BY image_title, category')
        rows = cursor.fetchall()
        conn.close()
        
        # Get gallery images to map title -> filename
        gallery_db = get_db_path('gallery_images.db')
        
        if not os.path.exists(gallery_db):
            return jsonify({'success': True, 'mappings': {}})
        
        gallery_conn = sqlite3.connect(gallery_db)
        gallery_conn.row_factory = sqlite3.Row
        gallery_cursor = gallery_conn.cursor()
        gallery_cursor.execute('SELECT filename, title FROM images')
        gallery_rows = gallery_cursor.fetchall()
        gallery_conn.close()
        
        # Build title -> filename mapping
        title_to_filename = {row['title']: row['filename'] for row in gallery_rows if row['title']}
        
        # Build nested structure: { filename: { category: handle, ... }, ... }
        mappings = {}
        for row in rows:
            title = row['image_title']
            category = row['category']
            handle = row['shopify_handle']
            
            # Get filename from title
            filename = title_to_filename.get(title)
            if not filename:
                continue  # Skip if we can't find the image file
            
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
