"""
Shopify Product Mapping Admin
Fifth Element Photography - v2.1.0
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import sqlite3
import os
from functools import wraps

shopify_admin_bp = Blueprint('shopify_admin', __name__, url_prefix='/admin')

def get_db_path():
    """Get the database path"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'lumaprints_pricing.db')

def login_required(f):
    """Decorator to require login for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@shopify_admin_bp.route('/shopify-mapping')
@login_required
def shopify_mapping():
    """Shopify product mapping management page"""
    # Get all images from static/images directory
    images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
    image_files = []
    
    if os.path.exists(images_dir):
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                image_files.append(filename)
    
    # Get existing mappings from database
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM shopify_mappings')
    mappings_rows = cursor.fetchall()
    conn.close()
    
    # Convert to dict for easier lookup
    mappings = {row['image_filename']: dict(row) for row in mappings_rows}
    
    # Build image list with mapping data
    images_data = []
    for filename in sorted(image_files):
        mapping = mappings.get(filename, {})
        images_data.append({
            'filename': filename,
            'shopify_product_handle': mapping.get('shopify_product_handle', ''),
            'order_prints_enabled': bool(mapping.get('order_prints_enabled', 0))
        })
    
    return render_template('admin/shopify_mapping.html', images=images_data)

@shopify_admin_bp.route('/api/shopify-mapping/update', methods=['POST'])
@login_required
def update_shopify_mapping():
    """Update Shopify mapping for an image"""
    data = request.json
    filename = data.get('filename')
    product_handle = data.get('product_handle', '').strip()
    enabled = data.get('enabled', False)
    
    if not filename:
        return jsonify({'success': False, 'error': 'Filename is required'}), 400
    
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    try:
        # Insert or update mapping
        cursor.execute('''
            INSERT INTO shopify_mappings (image_filename, shopify_product_handle, order_prints_enabled, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(image_filename) DO UPDATE SET
                shopify_product_handle = excluded.shopify_product_handle,
                order_prints_enabled = excluded.order_prints_enabled,
                updated_at = CURRENT_TIMESTAMP
        ''', (filename, product_handle if product_handle else None, 1 if enabled else 0))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@shopify_admin_bp.route('/api/shopify-mapping/get/<filename>')
@login_required
def get_shopify_mapping(filename):
    """Get Shopify mapping for a specific image"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM shopify_mappings WHERE image_filename = ?', (filename,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'success': True,
            'mapping': {
                'filename': row['image_filename'],
                'product_handle': row['shopify_product_handle'],
                'enabled': bool(row['order_prints_enabled'])
            }
        })
    else:
        return jsonify({
            'success': True,
            'mapping': {
                'filename': filename,
                'product_handle': '',
                'enabled': False
            }
        })

@shopify_admin_bp.route('/api/shopify-mapping/all')
def get_all_mappings():
    """Get all Shopify mappings (public endpoint for frontend)"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM shopify_mappings WHERE order_prints_enabled = 1')
    rows = cursor.fetchall()
    conn.close()
    
    mappings = {}
    for row in rows:
        if row['shopify_product_handle']:
            mappings[row['image_filename']] = row['shopify_product_handle']
    
    return jsonify({'success': True, 'mappings': mappings})

