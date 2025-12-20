from flask import Blueprint, jsonify
import sqlite3
import os

add_metal_36x36_pricing_bp = Blueprint('add_metal_36x36_pricing', __name__)

@add_metal_36x36_pricing_bp.route('/api/admin/add-metal-36x36-pricing', methods=['POST'])
def add_metal_36x36_pricing():
    """Add 36x36 pricing for Metal prints"""
    
    # Get database path
    if os.path.exists('/data'):
        db_path = '/data/print_ordering.db'
    else:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'print_ordering.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get 36×36" size ID
        cursor.execute("""
            SELECT size_id FROM print_sizes 
            WHERE size_name = '36×36"'
        """)
        size_result = cursor.fetchone()
        if not size_result:
            return jsonify({
                'success': False,
                'error': '36×36" size not found in database'
            }), 404
        
        size_36x36_id = size_result[0]
        
        # Get Metal subcategory IDs
        cursor.execute("""
            SELECT ps.subcategory_id, ps.display_name
            FROM product_subcategories ps
            JOIN product_categories pc ON ps.category_id = pc.category_id
            WHERE pc.category_name = 'Metal'
        """)
        metal_subcategories = cursor.fetchall()
        
        if not metal_subcategories:
            return jsonify({
                'success': False,
                'error': 'Metal subcategories not found'
            }), 404
        
        # Add 36×36" pricing for both Metal subcategories
        added_count = 0
        for subcategory_id, display_name in metal_subcategories:
            cursor.execute("""
                INSERT OR IGNORE INTO base_pricing (subcategory_id, size_id, cost_price, is_available)
                VALUES (?, ?, 270.62, TRUE)
            """, (subcategory_id, size_36x36_id))
            if cursor.rowcount > 0:
                added_count += 1
        
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
            'message': f'Added 36×36" pricing for {added_count} Metal subcategories',
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
