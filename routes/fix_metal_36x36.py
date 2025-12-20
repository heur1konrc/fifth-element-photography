from flask import Blueprint, jsonify
import sqlite3
import os

fix_metal_36x36_bp = Blueprint('fix_metal_36x36', __name__)

@fix_metal_36x36_bp.route('/api/admin/fix-metal-36x36', methods=['POST'])
def fix_metal_36x36():
    """Add 36x36 size and update Metal pricing"""
    
    # Get database path
    if os.path.exists('/data'):
        db_path = '/data/print_ordering.db'
    else:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'print_ordering.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get Square aspect ratio ID
        cursor.execute("SELECT aspect_ratio_id FROM aspect_ratios WHERE display_name = 'Square'")
        square_aspect_id = cursor.fetchone()[0]
        
        # Add 36×36" size
        cursor.execute("""
            INSERT INTO print_sizes (size_name, width, height, aspect_ratio_id)
            VALUES ('36×36"', 36, 36, ?)
        """, (square_aspect_id,))
        size_36x36_id = cursor.lastrowid
        
        # Get Metal subcategory IDs
        cursor.execute("""
            SELECT ps.subcategory_id, ps.display_name
            FROM product_subcategories ps
            JOIN product_categories pc ON ps.category_id = pc.category_id
            WHERE pc.category_name = 'Metal'
        """)
        metal_subcategories = cursor.fetchall()
        
        # Add 36×36" pricing for both Metal subcategories
        for subcategory_id, display_name in metal_subcategories:
            cursor.execute("""
                INSERT INTO base_pricing (subcategory_id, size_id, cost_price, is_available)
                VALUES (?, ?, 270.62, TRUE)
            """, (subcategory_id, size_36x36_id))
        
        conn.commit()
        
        # Verify
        cursor.execute("""
            SELECT ps.display_name, COUNT(bp.pricing_id) as price_count
            FROM product_subcategories ps
            JOIN product_categories pc ON ps.category_id = pc.category_id
            LEFT JOIN base_pricing bp ON ps.subcategory_id = bp.subcategory_id
            WHERE pc.category_name = 'Metal'
            GROUP BY ps.subcategory_id
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '36×36" size added and Metal pricing updated',
            'size_36x36_id': size_36x36_id,
            'subcategories': [{'name': row[0], 'price_count': row[1]} for row in results]
        })
    
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
