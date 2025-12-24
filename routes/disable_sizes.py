"""
Utility endpoint to disable specific sizes in the database
"""

from flask import Blueprint, jsonify
import sqlite3
import os

disable_sizes_bp = Blueprint('disable_sizes', __name__)

# Database path
if os.path.exists('/data'):
    DB_PATH = '/data/print_ordering.db'
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'print_ordering.db')

@disable_sizes_bp.route('/api/admin/disable-large-sizes', methods=['POST'])
def disable_large_sizes():
    """Disable 32×48 and 40×60 sizes in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Find 32x48 and 40x60 sizes
        cursor.execute("""
            SELECT size_id, size_name, width, height 
            FROM print_sizes 
            WHERE (width = 32 AND height = 48) OR (width = 40 AND height = 60)
        """)
        sizes = cursor.fetchall()
        
        if not sizes:
            return jsonify({
                'success': True,
                'message': 'No 32×48 or 40×60 sizes found in database'
            })
        
        disabled_count = 0
        size_info = []
        
        # Mark all base_pricing entries for these sizes as unavailable
        for size in sizes:
            size_id = size[0]
            size_name = size[1]
            dimensions = f"{size[2]}×{size[3]}"
            
            cursor.execute("""
                UPDATE base_pricing 
                SET is_available = 0 
                WHERE size_id = ?
            """, (size_id,))
            
            affected = cursor.rowcount
            disabled_count += affected
            
            size_info.append({
                'size_id': size_id,
                'name': size_name,
                'dimensions': dimensions,
                'pricing_entries_disabled': affected
            })
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully disabled {disabled_count} pricing entries',
            'sizes_disabled': size_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
