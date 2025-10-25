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
@pictorem_admin_bp.route('/admin/products')
def admin_dashboard():
    """Pictorem admin dashboard"""
    if not check_admin():
        return redirect('/admin/login')
    
    return render_template('pictorem_admin.html')

@pictorem_admin_bp.route('/admin/database')
def admin_database():
    """Pictorem database administration"""
    if not check_admin():
        return redirect('/admin/login')
    
    return render_template('pictorem_db_admin.html')

@pictorem_admin_bp.route('/admin/products/list')
def admin_products():
    """View and manage products"""
    if not check_admin():
        return redirect(url_for('admin_login'))
    
    products = get_all_products()
    return render_template('pictorem_products.html', products=products)

@pictorem_admin_bp.route('/admin/catalog')
def admin_catalog():
    """Complete product catalog with all sizes and options"""
    if not check_admin():
        return redirect(url_for('admin_login'))
    
    return render_template('product_catalog.html')

@pictorem_admin_bp.route('/admin/pricing_management')
def admin_pricing_management():
    """Complete pricing management with individual price control"""
    if not check_admin():
        return redirect(url_for('admin_login'))
    
    return render_template('pricing_management.html')

@pictorem_admin_bp.route('/order-test')
def order_test():
    """Test order form to demonstrate customer experience"""
    return render_template('order_test.html')

@pictorem_admin_bp.route('/admin/pricing')
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

@pictorem_admin_bp.route('/admin/settings')
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

@pictorem_admin_bp.route('/api/get_price', methods=['POST'])
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

@pictorem_admin_bp.route('/api/update_markup', methods=['POST'])
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

@pictorem_admin_bp.route('/api/clear_cache', methods=['POST'])
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

@pictorem_admin_bp.route('/api/debug/data_directory')
def api_debug_data_directory():
    """Debug: Check /data directory contents"""
    import os
    try:
        if os.path.exists('/data'):
            files = os.listdir('/data')
            file_info = []
            for f in files:
                path = os.path.join('/data', f)
                size = os.path.getsize(path) if os.path.isfile(path) else 0
                file_info.append({
                    'name': f,
                    'size': size,
                    'is_file': os.path.isfile(path),
                    'is_dir': os.path.isdir(path)
                })
            return jsonify({
                'exists': True,
                'files': file_info,
                'db_path': DB_PATH,
                'db_exists': os.path.exists(DB_PATH)
            })
        else:
            return jsonify({
                'exists': False,
                'message': '/data directory does not exist'
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        })

@pictorem_admin_bp.route('/api/products/catalog')
def api_products():
    """Get all products"""
    products = get_all_products()
    return jsonify(products)

@pictorem_admin_bp.route('/api/product/<slug>/sizes')
def api_product_sizes(slug):
    """Get sizes for a product"""
    try:
        sizes = get_product_sizes(slug)
        return jsonify(sizes)
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc(),
            'slug': slug
        }), 500

@pictorem_admin_bp.route('/api/product/<slug>/options')
def api_product_options(slug):
    """Get options for a product"""
    option_type = request.args.get('type')
    options = get_product_options(slug, option_type)
    return jsonify(options)

@pictorem_admin_bp.route('/api/test_api', methods=['POST'])
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

@pictorem_admin_bp.route('/api/database/test')
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

@pictorem_admin_bp.route('/api/database/init', methods=['POST'])
def api_force_init_database():
    """Force re-initialization of database"""
    from init_pictorem_db import init_pictorem_database, check_database_status
    
    try:
        print("Force initializing Pictorem database...")
        init_result = init_pictorem_database(force=True)
        
        status = check_database_status()
        status['force_init'] = True
        
        # Handle both boolean and dict return values
        if isinstance(init_result, dict):
            status['init_success'] = init_result.get('success', False)
            status['init_error'] = init_result.get('error')
            status['init_error_type'] = init_result.get('error_type')
            status['init_traceback'] = init_result.get('traceback')
        else:
            status['init_success'] = init_result
        
        return jsonify(status)
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': traceback.format_exc()
        }), 500

@pictorem_admin_bp.route('/api/sync_prices', methods=['POST'])
def api_sync_prices():
    """Sync all prices from Pictorem API"""
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from sync_all_prices import sync_all_prices
        result = sync_all_prices()
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pictorem_admin_bp.route('/api/sync_product/<product_slug>', methods=['POST'])
def api_sync_single_product(product_slug):
    """Sync prices for a single product"""
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from sync_single_product import sync_product_prices
        result = sync_product_prices(product_slug)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@pictorem_admin_bp.route('/api/update_price', methods=['POST'])
def api_update_individual_price():
    """Update individual product price"""
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    pricing_id = data.get('id')
    new_price = data.get('price')
    
    if not pricing_id or not new_price:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE pictorem_product_pricing
            SET price_override = ?, customer_price = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (new_price, new_price, pricing_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pictorem_admin_bp.route('/api/get_all_pricing')
def api_get_all_pricing():
    """Get all product pricing data"""
    if not check_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                pp.id,
                p.name as product_name,
                p.slug as product_slug,
                s.width || 'x' || s.height as size_name,
                pp.preorder_code,
                pp.base_price,
                pp.markup_percentage,
                pp.customer_price,
                pp.price_override,
                pp.active,
                pp.last_synced,
                pp.updated_at
            FROM pictorem_product_pricing pp
            JOIN pictorem_products p ON pp.product_id = p.id
            JOIN pictorem_sizes s ON pp.size_id = s.id
            WHERE pp.active = 1
            ORDER BY p.display_order, p.name, s.width, s.height
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        pricing = []
        for row in rows:
            pricing.append({
                'id': row[0],
                'product_name': row[1],
                'product_slug': row[2],
                'size_name': row[3],
                'preorder_code': row[4],
                'base_price': row[5],
                'markup_percentage': row[6],
                'customer_price': row[7],
                'price_override': row[8],
                'active': row[9],
                'last_synced': row[10],
                'updated_at': row[11]
            })
        
        return jsonify(pricing)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@pictorem_admin_bp.route('/api/debug_duplicates', methods=['GET'])
def api_debug_duplicates():
    """Debug endpoint to see what duplicates exist"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM pictorem_sizes")
        total_count = cursor.fetchone()[0]
        
        # Find duplicates
        cursor.execute("""
            SELECT product_id, width, height, COUNT(*) as count
            FROM pictorem_sizes
            GROUP BY product_id, width, height
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        duplicate_details = []
        
        for dup in duplicates:
            product_id = dup[0]
            width = dup[1]
            height = dup[2]
            count = dup[3]
            
            # Get product name
            cursor.execute("SELECT name FROM pictorem_products WHERE id = ?", (product_id,))
            product_name = cursor.fetchone()[0]
            
            # Get all IDs for this duplicate
            cursor.execute("""
                SELECT id FROM pictorem_sizes
                WHERE product_id = ? AND width = ? AND height = ?
                ORDER BY id
            """, (product_id, width, height))
            
            ids = [row[0] for row in cursor.fetchall()]
            
            duplicate_details.append({
                'product_name': product_name,
                'product_id': product_id,
                'width': width,
                'height': height,
                'duplicate_count': count,
                'ids': ids,
                'ids_to_delete': ids[1:]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total_sizes': total_count,
            'duplicate_groups': len(duplicates),
            'total_duplicates_to_delete': sum(d['duplicate_count'] - 1 for d in duplicate_details),
            'details': duplicate_details
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@pictorem_admin_bp.route('/api/cleanup_duplicate_orientations', methods=['POST'])
def api_cleanup_duplicate_orientations():
    """Remove orientation duplicates - keep only one size per width/height pair"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Count total before
        cursor.execute("SELECT COUNT(*) as count FROM pictorem_sizes")
        total_before = cursor.fetchone()[0]
        
        # Find orientation duplicates (e.g., 8x10 and 10x8)
        # For each product, find sizes where both orientations exist
        cursor.execute("""
            SELECT DISTINCT
                s1.id as id_to_delete,
                s1.product_id,
                s1.width,
                s1.height,
                s1.orientation
            FROM pictorem_sizes s1
            JOIN pictorem_sizes s2 ON 
                s1.product_id = s2.product_id AND
                s1.width = s2.height AND
                s1.height = s2.width AND
                s1.id > s2.id
            WHERE s1.width < s1.height
        """)
        
        sizes_to_delete = [row[0] for row in cursor.fetchall()]
        
        if sizes_to_delete:
            placeholders = ','.join('?' * len(sizes_to_delete))
            
            # Delete associated pricing first
            cursor.execute(f"DELETE FROM pictorem_product_pricing WHERE size_id IN ({placeholders})", sizes_to_delete)
            pricing_deleted = cursor.rowcount
            
            # Delete the sizes
            cursor.execute(f"DELETE FROM pictorem_sizes WHERE id IN ({placeholders})", sizes_to_delete)
            sizes_deleted = cursor.rowcount
            
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) as count FROM pictorem_sizes")
            total_after = cursor.fetchone()[0]
            conn.close()
            
            return jsonify({
                'success': True,
                'total_sizes': total_before,
                'sizes_deleted': sizes_deleted,
                'pricing_deleted': pricing_deleted,
                'sizes_remaining': total_after
            })
        else:
            conn.close()
            return jsonify({'success': True, 'message': 'No orientation duplicates found'})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


