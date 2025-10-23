"""
Order Form API - Dynamic Product Selection
Reads from lumaprints_orders.db to provide product data for dynamic form
"""

from flask import Blueprint, jsonify, request
import sqlite3
import os

order_form_api = Blueprint('order_form_api', __name__)

DB_PATH = 'data/lumaprints_orders.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@order_form_api.route('/api/order-form/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.name, COUNT(s.id) as subcategory_count
            FROM categories c
            LEFT JOIN subcategories s ON c.id = s.category_id
            GROUP BY c.id, c.name
            ORDER BY c.name
        ''')
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row['id'],
                'name': row['name'],
                'subcategory_count': row['subcategory_count']
            })
        
        conn.close()
        return jsonify({'success': True, 'categories': categories})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@order_form_api.route('/api/order-form/subcategories/<int:category_id>', methods=['GET'])
def get_subcategories(category_id):
    """Get all subcategories for a category"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, minimum_width, maximum_width, 
                   minimum_height, maximum_height, required_dpi
            FROM subcategories
            WHERE category_id = ?
            ORDER BY name
        ''', (category_id,))
        
        subcategories = []
        for row in cursor.fetchall():
            subcategories.append({
                'id': row['id'],
                'name': row['name'],
                'minimumWidth': row['minimum_width'],
                'maximumWidth': row['maximum_width'],
                'minimumHeight': row['minimum_height'],
                'maximumHeight': row['maximum_height'],
                'requiredDPI': row['required_dpi']
            })
        
        conn.close()
        return jsonify({'success': True, 'subcategories': subcategories})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@order_form_api.route('/api/order-form/option-groups/<int:subcategory_id>', methods=['GET'])
def get_option_groups(subcategory_id):
    """Get all option groups for a subcategory"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get option groups
        cursor.execute('''
            SELECT id, name, display_order
            FROM option_groups
            WHERE subcategory_id = ?
            ORDER BY display_order
        ''', (subcategory_id,))
        
        option_groups = []
        for row in cursor.fetchall():
            group_id = row['id']
            
            # Get options for this group
            cursor.execute('''
                SELECT id, name, display_order
                FROM options
                WHERE option_group_id = ?
                ORDER BY display_order
            ''', (group_id,))
            
            options = []
            for opt_row in cursor.fetchall():
                options.append({
                    'id': opt_row['id'],
                    'name': opt_row['name']
                })
            
            option_groups.append({
                'id': row['id'],
                'name': row['name'],
                'options': options
            })
        
        conn.close()
        return jsonify({'success': True, 'option_groups': option_groups})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@order_form_api.route('/api/order-form/product-structure/<int:category_id>', methods=['GET'])
def get_product_structure(category_id):
    """Get complete product structure for a category (for dynamic form building)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get category info
        cursor.execute('SELECT id, name FROM categories WHERE id = ?', (category_id,))
        category_row = cursor.fetchone()
        
        if not category_row:
            return jsonify({'success': False, 'error': 'Category not found'}), 404
        
        category = {
            'id': category_row['id'],
            'name': category_row['name'],
            'subcategories': []
        }
        
        # Get subcategories
        cursor.execute('''
            SELECT id, name, minimum_width, maximum_width,
                   minimum_height, maximum_height, required_dpi
            FROM subcategories
            WHERE category_id = ?
            ORDER BY name
        ''', (category_id,))
        
        for subcat_row in cursor.fetchall():
            subcat_id = subcat_row['id']
            
            # Get option groups for this subcategory
            cursor.execute('''
                SELECT id, name, display_order
                FROM option_groups
                WHERE subcategory_id = ?
                ORDER BY display_order
            ''', (subcat_id,))
            
            option_groups = []
            for og_row in cursor.fetchall():
                og_id = og_row['id']
                
                # Get options
                cursor.execute('''
                    SELECT id, name, display_order
                    FROM options
                    WHERE option_group_id = ?
                    ORDER BY display_order
                ''', (og_id,))
                
                options = [{'id': opt['id'], 'name': opt['name']} for opt in cursor.fetchall()]
                
                option_groups.append({
                    'id': og_row['id'],
                    'name': og_row['name'],
                    'options': options
                })
            
            category['subcategories'].append({
                'id': subcat_id,
                'name': subcat_row['name'],
                'minimumWidth': subcat_row['minimum_width'],
                'maximumWidth': subcat_row['maximum_width'],
                'minimumHeight': subcat_row['minimum_height'],
                'maximumHeight': subcat_row['maximum_height'],
                'requiredDPI': subcat_row['required_dpi'],
                'option_groups': option_groups
            })
        
        conn.close()
        return jsonify({'success': True, 'structure': category})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@order_form_api.route('/api/order-form/pricing', methods=['POST'])
def get_pricing():
    """Get pricing for a product configuration (placeholder - needs Lumaprints API integration)"""
    try:
        data = request.json
        subcategory_id = data.get('subcategory_id')
        width = data.get('width')
        height = data.get('height')
        options = data.get('options', [])
        quantity = data.get('quantity', 1)
        
        # TODO: Call Lumaprints pricing API
        # For now, return placeholder
        
        return jsonify({
            'success': True,
            'pricing': {
                'wholesale_price': 0.00,
                'retail_price': 0.00,
                'quantity': quantity,
                'message': 'Pricing integration pending'
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

