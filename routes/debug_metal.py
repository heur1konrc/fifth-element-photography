from flask import Blueprint, jsonify
import sqlite3
import os

debug_metal_bp = Blueprint('debug_metal', __name__)

@debug_metal_bp.route('/api/admin/debug-metal', methods=['GET'])
def debug_metal():
    """Debug endpoint to check database structure for Metal prints"""
    
    # Get database path
    if os.path.exists('/data'):
        db_path = '/data/print_ordering.db'
    else:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'print_ordering.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check aspect ratios
        cursor.execute("SELECT * FROM aspect_ratios")
        aspect_ratios = [{'aspect_ratio_id': row[0], 'display_name': row[1], 'ratio': row[2]} 
                        for row in cursor.fetchall()]
        
        # Check print sizes
        cursor.execute("SELECT size_id, size_name, aspect_ratio_id FROM print_sizes ORDER BY size_name")
        print_sizes = [{'size_id': row[0], 'size_name': row[1], 'aspect_ratio_id': row[2]} 
                      for row in cursor.fetchall()]
        
        # Check categories
        cursor.execute("SELECT category_id, category_name FROM product_categories ORDER BY display_order")
        categories = [{'category_id': row[0], 'category_name': row[1]} 
                     for row in cursor.fetchall()]
        
        # Check if Metal category exists
        cursor.execute("SELECT * FROM product_categories WHERE category_name = 'Metal'")
        metal_category = cursor.fetchone()
        
        # Check Metal subcategories
        cursor.execute("""
            SELECT ps.subcategory_id, ps.subcategory_name, ps.display_name
            FROM product_subcategories ps
            JOIN product_categories pc ON ps.category_id = pc.category_id
            WHERE pc.category_name = 'Metal'
        """)
        metal_subcategories = [{'subcategory_id': row[0], 'subcategory_name': row[1], 'display_name': row[2]} 
                              for row in cursor.fetchall()]
        
        # Check Metal pricing
        cursor.execute("""
            SELECT bp.pricing_id, ps.display_name, pz.size_name, bp.cost_price
            FROM base_pricing bp
            JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
            JOIN product_categories pc ON ps.category_id = pc.category_id
            JOIN print_sizes pz ON bp.size_id = pz.size_id
            WHERE pc.category_name = 'Metal'
            ORDER BY ps.display_name, pz.size_name
        """)
        metal_pricing = [{'pricing_id': row[0], 'subcategory': row[1], 'size': row[2], 'cost': row[3]} 
                        for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'aspect_ratios': aspect_ratios,
            'print_sizes': print_sizes,
            'categories': categories,
            'metal_category': metal_category,
            'metal_subcategories': metal_subcategories,
            'metal_pricing': metal_pricing
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
