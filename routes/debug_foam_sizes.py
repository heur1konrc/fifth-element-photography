from flask import Blueprint, jsonify
import sqlite3
import os

debug_foam_bp = Blueprint('debug_foam', __name__)

def get_db_path():
    """Get the correct database path"""
    if os.path.exists('/data'):
        return '/data/print_ordering.db'
    else:
        return os.path.join(os.path.dirname(__file__), '..', 'database', 'print_ordering.db')

@debug_foam_bp.route('/admin/debug-foam-sizes')
def debug_foam_sizes():
    """Debug: Show all Foam-mounted products and their sizes"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all categories with "foam" in the name
        cursor.execute("""
            SELECT category_id, category_name, display_name 
            FROM product_categories 
            WHERE LOWER(display_name) LIKE '%foam%' 
            OR LOWER(category_name) LIKE '%foam%'
        """)
        categories = cursor.fetchall()
        
        # Get all subcategories with "foam" in the name
        cursor.execute("""
            SELECT ps.subcategory_id, ps.subcategory_name, ps.display_name, pc.display_name as category_name
            FROM product_subcategories ps
            JOIN product_categories pc ON ps.category_id = pc.category_id
            WHERE LOWER(ps.display_name) LIKE '%foam%' 
            OR LOWER(ps.subcategory_name) LIKE '%foam%'
            OR LOWER(pc.display_name) LIKE '%foam%'
        """)
        subcategories = cursor.fetchall()
        
        # Get all pricing entries for foam products
        cursor.execute("""
            SELECT 
                pc.display_name as category,
                ps.display_name as subcategory,
                pz.size_name,
                bp.cost_price,
                bp.is_available,
                bp.pricing_id
            FROM base_pricing bp
            JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
            JOIN product_categories pc ON ps.category_id = pc.category_id
            JOIN print_sizes pz ON bp.size_id = pz.size_id
            WHERE LOWER(pc.display_name) LIKE '%foam%'
            OR LOWER(ps.display_name) LIKE '%foam%'
            ORDER BY ps.display_name, pz.size_name
        """)
        pricing_entries = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'categories': [{'id': c[0], 'name': c[1], 'display_name': c[2]} for c in categories],
            'subcategories': [{'id': s[0], 'name': s[1], 'display_name': s[2], 'category': s[3]} for s in subcategories],
            'pricing_entries': [
                {
                    'category': p[0],
                    'subcategory': p[1],
                    'size': p[2],
                    'cost': p[3],
                    'available': bool(p[4]),
                    'pricing_id': p[5]
                } for p in pricing_entries
            ],
            'total_foam_products': len(pricing_entries)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
