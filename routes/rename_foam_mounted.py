from flask import Blueprint, jsonify
import sqlite3
import os

rename_foam_mounted_bp = Blueprint('rename_foam_mounted', __name__)

@rename_foam_mounted_bp.route('/api/admin/rename-foam-mounted', methods=['POST'])
def rename_foam_mounted():
    """Rename Foam-mounted Print to Foam-mounted Fine Art Paper"""
    
    # Get database path
    if os.path.exists('/data'):
        db_path = '/data/print_ordering.db'
    else:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'print_ordering.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update the display_name in product_categories table
        cursor.execute("""
            UPDATE product_categories 
            SET display_name = 'Foam-mounted Fine Art Paper'
            WHERE category_name = 'foam_mounted'
        """)
        
        rows_updated = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Updated {rows_updated} category',
            'old_name': 'Foam-mounted Print',
            'new_name': 'Foam-mounted Fine Art Paper'
        })
    
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
