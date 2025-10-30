"""
Fifth Element Photography - Pricing Management Admin Routes
Handles pricing, markup, and product management for print ordering
Version: Beta 0.1.0
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from functools import wraps
import sqlite3
import os

pricing_admin_bp = Blueprint('pricing_admin', __name__)

# Database path - use /data on Railway, fallback to local for development
if os.path.exists('/data'):
    DB_PATH = '/data/print_ordering.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'print_ordering.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        if not session.get('logged_in'):
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# MAIN PRICING DASHBOARD
# ============================================================================

@pricing_admin_bp.route('/admin/pricing')
# @admin_required  # Temporarily disabled for testing
def pricing_dashboard():
    """Main pricing management dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get summary statistics
    cursor.execute('SELECT COUNT(*) FROM base_pricing WHERE is_available = TRUE')
    total_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM markup_rules WHERE is_active = TRUE')
    active_markups = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT category_id) FROM product_categories WHERE is_enabled = TRUE')
    enabled_categories = cursor.fetchone()[0]
    
    # Get active markup rules
    cursor.execute('''
        SELECT 
            markup_id,
            rule_name,
            rule_type,
            markup_type,
            markup_value,
            priority,
            CASE 
                WHEN rule_type = 'global' THEN 'All Products'
                WHEN rule_type = 'category' THEN (SELECT display_name FROM product_categories WHERE category_id = markup_rules.category_id)
                WHEN rule_type = 'subcategory' THEN (SELECT display_name FROM product_subcategories WHERE subcategory_id = markup_rules.subcategory_id)
                WHEN rule_type = 'specific' THEN 'Specific Product/Size'
            END as applies_to
        FROM markup_rules
        WHERE is_active = TRUE
        ORDER BY priority DESC, markup_id DESC
        LIMIT 10
    ''')
    recent_markups = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_pricing.html',
                         total_products=total_products,
                         active_markups=active_markups,
                         enabled_categories=enabled_categories,
                         recent_markups=recent_markups)

# ============================================================================
# PRICING BROWSER
# ============================================================================

@pricing_admin_bp.route('/admin/pricing/browse')
# @admin_required  # Temporarily disabled for testing
def browse_pricing():
    """Browse and search all product pricing"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get filter parameters
    category_id = request.args.get('category_id', type=int)
    subcategory_id = request.args.get('subcategory_id', type=int)
    aspect_ratio_id = request.args.get('aspect_ratio_id', type=int)
    
    # Build query
    query = '''
        SELECT 
            bp.pricing_id,
            pc.display_name as category_name,
            ps.display_name as product_name,
            pz.size_name,
            pz.width,
            pz.height,
            ar.ratio_name,
            bp.cost_price,
            bp.is_available,
            COALESCE(
                (SELECT markup_value FROM markup_rules 
                 WHERE rule_type = 'specific' AND subcategory_id = bp.subcategory_id AND size_id = bp.size_id AND is_active = TRUE 
                 ORDER BY priority DESC LIMIT 1),
                (SELECT markup_value FROM markup_rules 
                 WHERE rule_type = 'subcategory' AND subcategory_id = bp.subcategory_id AND is_active = TRUE 
                 ORDER BY priority DESC LIMIT 1),
                (SELECT markup_value FROM markup_rules 
                 WHERE rule_type = 'category' AND category_id = ps.category_id AND is_active = TRUE 
                 ORDER BY priority DESC LIMIT 1),
                (SELECT markup_value FROM markup_rules 
                 WHERE rule_type = 'global' AND is_active = TRUE 
                 ORDER BY priority DESC LIMIT 1),
                0
            ) as markup_percentage,
            ROUND(bp.cost_price * (1 + COALESCE(
                (SELECT markup_value / 100.0 FROM markup_rules WHERE rule_type = 'specific' AND subcategory_id = bp.subcategory_id AND size_id = bp.size_id AND is_active = TRUE ORDER BY priority DESC LIMIT 1),
                (SELECT markup_value / 100.0 FROM markup_rules WHERE rule_type = 'subcategory' AND subcategory_id = bp.subcategory_id AND is_active = TRUE ORDER BY priority DESC LIMIT 1),
                (SELECT markup_value / 100.0 FROM markup_rules WHERE rule_type = 'category' AND category_id = ps.category_id AND is_active = TRUE ORDER BY priority DESC LIMIT 1),
                (SELECT markup_value / 100.0 FROM markup_rules WHERE rule_type = 'global' AND is_active = TRUE ORDER BY priority DESC LIMIT 1),
                0
            )), 2) as retail_price
        FROM base_pricing bp
        JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
        JOIN product_categories pc ON ps.category_id = pc.category_id
        JOIN print_sizes pz ON bp.size_id = pz.size_id
        JOIN aspect_ratios ar ON pz.aspect_ratio_id = ar.aspect_ratio_id
        WHERE 1=1
    '''
    
    params = []
    
    if category_id:
        query += ' AND pc.category_id = ?'
        params.append(category_id)
    
    if subcategory_id:
        query += ' AND ps.subcategory_id = ?'
        params.append(subcategory_id)
    
    if aspect_ratio_id:
        query += ' AND ar.aspect_ratio_id = ?'
        params.append(aspect_ratio_id)
    
    query += ' ORDER BY pc.display_order, ps.display_order, pz.width, pz.height'
    
    cursor.execute(query, params)
    pricing_data = cursor.fetchall()
    
    # Get filter options
    cursor.execute('SELECT category_id, display_name FROM product_categories WHERE is_enabled = TRUE ORDER BY display_order')
    categories = cursor.fetchall()
    
    cursor.execute('SELECT subcategory_id, display_name, category_id FROM product_subcategories WHERE is_enabled = TRUE ORDER BY display_order')
    subcategories = cursor.fetchall()
    
    cursor.execute('SELECT aspect_ratio_id, display_name FROM aspect_ratios WHERE is_enabled = TRUE ORDER BY ratio_decimal')
    aspect_ratios = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_pricing_browse.html',
                         pricing_data=pricing_data,
                         categories=categories,
                         subcategories=subcategories,
                         aspect_ratios=aspect_ratios,
                         selected_category=category_id,
                         selected_subcategory=subcategory_id,
                         selected_aspect_ratio=aspect_ratio_id)

# ============================================================================
# MARKUP MANAGEMENT
# ============================================================================

@pricing_admin_bp.route('/admin/pricing/markups')
# @admin_required  # Temporarily disabled for testing
def manage_markups():
    """Manage markup rules"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all markup rules
    cursor.execute('''
        SELECT 
            m.markup_id,
            m.rule_name,
            m.rule_type,
            m.markup_type,
            m.markup_value,
            m.priority,
            m.is_active,
            CASE 
                WHEN m.rule_type = 'global' THEN 'All Products'
                WHEN m.rule_type = 'category' THEN pc.display_name
                WHEN m.rule_type = 'subcategory' THEN ps.display_name
                WHEN m.rule_type = 'specific' THEN ps.display_name || ' - ' || pz.size_name
            END as applies_to,
            m.created_at
        FROM markup_rules m
        LEFT JOIN product_categories pc ON m.category_id = pc.category_id
        LEFT JOIN product_subcategories ps ON m.subcategory_id = ps.subcategory_id
        LEFT JOIN print_sizes pz ON m.size_id = pz.size_id
        ORDER BY m.priority DESC, m.is_active DESC, m.created_at DESC
    ''')
    markups = cursor.fetchall()
    
    # Get categories for dropdown
    cursor.execute('SELECT category_id, display_name FROM product_categories WHERE is_enabled = TRUE ORDER BY display_order')
    categories = cursor.fetchall()
    
    # Get subcategories for dropdown
    cursor.execute('SELECT subcategory_id, display_name, category_id FROM product_subcategories WHERE is_enabled = TRUE ORDER BY display_order')
    subcategories = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_pricing_markups.html',
                         markups=markups,
                         categories=categories,
                         subcategories=subcategories)

@pricing_admin_bp.route('/admin/pricing/markups/add', methods=['POST'])
# @admin_required  # Temporarily disabled for testing
def add_markup():
    """Add new markup rule"""
    conn = get_db()
    cursor = conn.cursor()
    
    rule_name = request.form.get('rule_name')
    rule_type = request.form.get('rule_type')
    markup_type = request.form.get('markup_type')
    markup_value = float(request.form.get('markup_value'))
    priority = int(request.form.get('priority', 0))
    category_id = request.form.get('category_id', type=int)
    subcategory_id = request.form.get('subcategory_id', type=int)
    
    cursor.execute('''
        INSERT INTO markup_rules 
        (rule_name, rule_type, markup_type, markup_value, priority, category_id, subcategory_id, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, TRUE)
    ''', (rule_name, rule_type, markup_type, markup_value, priority, category_id, subcategory_id))
    
    conn.commit()
    conn.close()
    
    flash(f'Markup rule "{rule_name}" added successfully', 'success')
    return redirect(url_for('pricing_admin.manage_markups'))

@pricing_admin_bp.route('/admin/pricing/markups/<int:markup_id>/toggle', methods=['POST'])
# @admin_required  # Temporarily disabled for testing
def toggle_markup(markup_id):
    """Toggle markup rule active/inactive"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE markup_rules SET is_active = NOT is_active WHERE markup_id = ?', (markup_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@pricing_admin_bp.route('/admin/pricing/markups/<int:markup_id>/delete', methods=['POST'])
# @admin_required  # Temporarily disabled for testing
def delete_markup(markup_id):
    """Delete markup rule"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM markup_rules WHERE markup_id = ?', (markup_id,))
    conn.commit()
    conn.close()
    
    flash('Markup rule deleted successfully', 'success')
    return redirect(url_for('pricing_admin.manage_markups'))

# ============================================================================
# INDIVIDUAL PRICE EDITING
# ============================================================================

@pricing_admin_bp.route('/admin/pricing/edit/<int:pricing_id>', methods=['POST'])
# @admin_required  # Temporarily disabled for testing
def edit_price(pricing_id):
    """Edit individual product price"""
    conn = get_db()
    cursor = conn.cursor()
    
    new_cost = float(request.form.get('cost_price'))
    is_available = request.form.get('is_available') == 'true'
    
    cursor.execute('''
        UPDATE base_pricing 
        SET cost_price = ?, is_available = ?, updated_at = CURRENT_TIMESTAMP
        WHERE pricing_id = ?
    ''', (new_cost, is_available, pricing_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ============================================================================
# PRODUCT ENABLE/DISABLE
# ============================================================================

@pricing_admin_bp.route('/admin/pricing/products')
# @admin_required  # Temporarily disabled for testing
def manage_products():
    """Manage product availability"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all categories with subcategories
    cursor.execute('''
        SELECT 
            pc.category_id,
            pc.display_name as category_name,
            pc.is_enabled as category_enabled,
            COUNT(DISTINCT ps.subcategory_id) as subcategory_count,
            COUNT(DISTINCT CASE WHEN ps.is_enabled THEN ps.subcategory_id END) as enabled_count
        FROM product_categories pc
        LEFT JOIN product_subcategories ps ON pc.category_id = ps.category_id
        GROUP BY pc.category_id
        ORDER BY pc.display_order
    ''')
    categories = cursor.fetchall()
    
    # Get all subcategories
    cursor.execute('''
        SELECT 
            ps.subcategory_id,
            ps.category_id,
            ps.display_name,
            ps.is_enabled,
            COUNT(bp.pricing_id) as price_count
        FROM product_subcategories ps
        LEFT JOIN base_pricing bp ON ps.subcategory_id = bp.subcategory_id AND bp.is_available = TRUE
        GROUP BY ps.subcategory_id
        ORDER BY ps.display_order
    ''')
    subcategories = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_pricing_products.html',
                         categories=categories,
                         subcategories=subcategories)

@pricing_admin_bp.route('/admin/pricing/products/category/<int:category_id>/toggle', methods=['POST'])
# @admin_required  # Temporarily disabled for testing
def toggle_category(category_id):
    """Toggle category enabled/disabled"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE product_categories SET is_enabled = NOT is_enabled WHERE category_id = ?', (category_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@pricing_admin_bp.route('/admin/pricing/products/subcategory/<int:subcategory_id>/toggle', methods=['POST'])
# @admin_required  # Temporarily disabled for testing
def toggle_subcategory(subcategory_id):
    """Toggle subcategory enabled/disabled"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE product_subcategories SET is_enabled = NOT is_enabled WHERE subcategory_id = ?', (subcategory_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ============================================================================
# API ENDPOINTS FOR AJAX
# ============================================================================

@pricing_admin_bp.route('/api/pricing/calculate', methods=['POST'])
# @admin_required  # Temporarily disabled for testing
def calculate_pricing():
    """Calculate retail price for given cost and markup"""
    data = request.json
    cost = float(data.get('cost', 0))
    markup_percentage = float(data.get('markup', 0))
    
    retail = round(cost * (1 + markup_percentage / 100), 2)
    profit = round(retail - cost, 2)
    
    return jsonify({
        'retail_price': retail,
        'profit': profit,
        'margin_percentage': round((profit / retail * 100) if retail > 0 else 0, 2)
    })

