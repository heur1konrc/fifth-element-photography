from flask import Blueprint, jsonify
import sqlite3
import os

fix_metal_category_name_bp = Blueprint('fix_metal_category_name', __name__)

@fix_metal_category_name_bp.route('/api/admin/fix-metal-category-name', methods=['POST'])
def fix_metal_category_name():
    """Fix Metal category_name to lowercase 'metal'"""
    
    # Get database path
    if os.path.exists('/data'):
        db_path = '/data/print_ordering.db'
    else:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'print_ordering.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update category_name to lowercase
        cursor.execute("""
            UPDATE product_categories 
            SET category_name = 'metal'
            WHERE category_name = 'Metal'
        """)
        
        rows_updated = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Updated {rows_updated} category',
            'old_category_name': 'Metal',
            'new_category_name': 'metal'
        })
    
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
