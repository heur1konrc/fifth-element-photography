"""
Pictorem Admin Interface
Manage products, pricing, and settings
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from pictorem_api import PictoremAPI, get_all_products, get_product_sizes, get_product_options

pictorem_admin_bp = Blueprint('pictorem_admin', __name__)

DB_PATH = '/data/pictorem.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Admin authentication check
def check_admin():
    """Check if user is authenticated as admin"""
    # TEMPORARILY DISABLED FOR TESTING
    return True
    # return session.get('admin_logged_in', False)
@pictorem_admin_bp.route('/admin/pictorem')
def admin_dashboard():
    """Pictorem admin dashboard"""
    if not check_admin():
        return redirect('/admin/login')
    
    return render_template('pictorem_admin.html')

@pictorem_admin_bp.route('/admin/pictorem/database')
def admin_database():
    """Pictorem database administration"""
    if not check_admin():
        return redirect('/admin/login')
    
    return render_template('pictorem_db_admin.html')

@pictorem_admin_bp.route('/admin/pictorem/products')
def admin_products():
    """View and manage products"""
    if not check_admin():
        return redirect(url_for('admin_login'))
    
    products = get_all_products()
    return render_template('pictorem_products.html', products=products)

@pictorem_admin_bp.route('/admin/pictorem/pricing')
def admin_pricing():
    """Pricing management interface"""
    if not check_admin():
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all products with sample pricing
    cursor.execute('''
        SELECT 
            p.id,
            p.name,
            p.slug,
            c.name as category_name
        FROM pictorem_products p
        JOIN pictorem_categories c ON p.category_id = c.id
        WHERE p.active = 1 AND c.active = 1
        ORDER BY c.display_order, p.display_order
    ''')
    
    products = [dict(row) for row in cursor.fetchall()]
    
    # Get current markup
    cursor.execute('SELECT value FROM pictorem_settings WHERE key_name = "global_markup_percentage"')
    markup = float(cursor.fetchone()['value'])
    
    conn.close()
    
    # Get sample pricing for each product
    api = PictoremAPI()
    for product in products:
        # Get first available size
        sizes = get_product_sizes(product['slug'])
        if sizes:
            size = sizes[0]
            
            # Get pricing
            if product['slug'] == 'framed-fine-art-print':
                # Use default frame options
                options = {
                    'moulding': '301-21',
                    'glazing': 'plexiglass',
                    'hanging': 'wire'
                }
            else:
                options = {}
            
            preorder_code = api.build_preorder_code(
                product['slug'],
                size['width'],
                size['height'],
                options
            )
            
            if preorder_code:
                price = api.get_price(preorder_code)
                if price:
                    product['sample_size'] = size['display_name']
                    product['sample_base_price'] = price['base_price']
                    product['sample_customer_price'] = price['customer_price']
    
    return render_template('pictorem_pricing.html', products=products, markup=markup)

@pictorem_admin_bp.route('/admin/pictorem/settings')
def admin_settings():
    """Settings management"""
    if not check_admin():
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT key_name, value, description FROM pictorem_settings ORDER BY key_name')
    settings = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('pictorem_settings.html', settings=settings)

# API Endpoints

@pictorem_admin_bp.route('/api/pictorem/get_price', methods=['POST'])
def api_get_price():
    """Get price for a product configuration"""
    data = request.json
    
    product_slug = data.get('product_slug')
    width = data.get('width')
    height = data.get('height')
    options = data.get('options', {})
    
    if not all([product_slug, width, height]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    api = PictoremAPI()
    preorder_code = api.build_preorder_code(product_slug, width, height, options)
    
    if not preorder_code:
        return jsonify({'error': 'Invalid product configuration'}), 400
    
    price = api.get_price(preorder_code)
    
    if not price:
        return jsonify({'error': 'Unable to get pricing'}), 500
    
    return jsonify(price)

@pictorem_admin_bp.route('/api/pictorem/update_markup', methods=['POST'])
def api_update_markup():
    """Update global markup percentage"""
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    new_markup = data.get('markup')
    
    if new_markup is None:
        return jsonify({'error': 'Missing markup parameter'}), 400
    
    try:
        new_markup = float(new_markup)
        if new_markup < 0 or new_markup > 500:
            return jsonify({'error': 'Markup must be between 0 and 500'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid markup value'}), 400
    
    api = PictoremAPI()
    api.update_markup(new_markup)
    
    return jsonify({'success': True, 'markup': new_markup})

@pictorem_admin_bp.route('/api/pictorem/clear_cache', methods=['POST'])
def api_clear_cache():
    """Clear pricing cache"""
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    api = PictoremAPI()
    deleted = api.clear_expired_cache()
    
    # Also clear all cache
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pictorem_pricing_cache')
    total_deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'deleted': total_deleted})

@pictorem_admin_bp.route('/api/pictorem/products')
def api_products():
    """Get all products"""
    products = get_all_products()
    return jsonify(products)

@pictorem_admin_bp.route('/api/pictorem/product/<slug>/sizes')
def api_product_sizes(slug):
    """Get sizes for a product"""
    sizes = get_product_sizes(slug)
    return jsonify(sizes)

@pictorem_admin_bp.route('/api/pictorem/product/<slug>/options')
def api_product_options(slug):
    """Get options for a product"""
    option_type = request.args.get('type')
    options = get_product_options(slug, option_type)
    return jsonify(options)

@pictorem_admin_bp.route('/api/pictorem/test_api', methods=['POST'])
def api_test_api():
    """Test Pictorem API connection"""
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    api = PictoremAPI()
    
    # Test with a simple canvas print
    test_code = '1|canvas|stretched|horizontal|24|30|mirrorimage|c15|regular'
    price = api.get_price(test_code, use_cache=False)
    
    if price:
        return jsonify({
            'success': True,
            'message': 'API connection successful',
            'test_price': price
        })
    else:
        return jsonify({
            'success': False,
            'message': 'API connection failed'
        }), 500

@pictorem_admin_bp.route('/api/pictorem/test')
def api_test_database():
    """Test database status and initialization"""
    from init_pictorem_db import check_database_status, init_pictorem_database
    import os
    
    status = check_database_status()
    
    # If database doesn't exist or is empty, try to initialize it
    if not status['exists'] or (status.get('stats') and len(status['stats']) == 0):
        print("Database not found or empty, attempting initialization...")
        init_success = init_pictorem_database(force=False)
        status['initialization_attempted'] = True
        status['initialization_success'] = init_success
        
        if init_success:
            status = check_database_status()
    
    return jsonify(status)

@pictorem_admin_bp.route('/api/pictorem/init', methods=['POST'])
def api_force_init_database():
    """Force re-initialization of database"""
    from init_pictorem_db import init_pictorem_database, check_database_status
    
    print("Force initializing Pictorem database...")
    init_success = init_pictorem_database(force=True)
    
    status = check_database_status()
    status['force_init'] = True
    status['init_success'] = init_success
    
    return jsonify(status)

