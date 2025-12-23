from flask import Blueprint, jsonify
import sqlite3
import os

remove_foam_invalid_bp = Blueprint('remove_foam_invalid', __name__)

def get_db_path():
    """Get the correct database path (same as shopify_api_creator.py)"""
    if os.path.exists('/data'):
        return '/data/print_ordering.db'
    else:
        return os.path.join(os.path.dirname(__file__), '..', 'database', 'print_ordering.db')

@remove_foam_invalid_bp.route('/admin/remove-foam-invalid-sizes')
def remove_foam_invalid_sizes():
    """Remove Foam-mounted products with 4×6 and 40×60 sizes (outside Lumaprints limits)"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, check what we're about to delete
        cursor.execute("""
            SELECT COUNT(*) FROM base_pricing bp
            JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
            JOIN product_categories pc ON ps.category_id = pc.category_id
            JOIN print_sizes pz ON bp.size_id = pz.size_id
            WHERE pc.display_name = 'Foam-mounted Fine Art Paper'
            AND (pz.size_name IN ('4×6', '40×60', '4x6', '40x60') OR pz.size_name LIKE '4_6' OR pz.size_name LIKE '40_60')
        """)
        
        count_to_delete = cursor.fetchone()[0]
        
        if count_to_delete == 0:
            return jsonify({
                'success': True,
                'message': 'No Foam-mounted 4×6 or 40×60 products found',
                'deleted': 0
            })
        
        # Delete the entries
        cursor.execute("""
            DELETE FROM base_pricing 
            WHERE pricing_id IN (
                SELECT bp.pricing_id FROM base_pricing bp
                JOIN product_subcategories ps ON bp.subcategory_id = ps.subcategory_id
                JOIN product_categories pc ON ps.category_id = pc.category_id
                JOIN print_sizes pz ON bp.size_id = pz.size_id
                WHERE pc.display_name = 'Foam-mounted Fine Art Paper'
                AND (pz.size_name IN ('4×6', '40×60', '4x6', '40x60') OR pz.size_name LIKE '4_6' OR pz.size_name LIKE '40_60')
            )
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully removed {deleted_count} Foam-mounted products with invalid sizes (4×6, 40×60)',
            'deleted': deleted_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
