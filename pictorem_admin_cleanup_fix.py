"""
Replacement cleanup function for pictorem_admin.py
"""

def api_cleanup_duplicate_orientations_NEW():
    """Remove exact duplicate sizes using SQL GROUP BY"""
    from flask import jsonify
    import sqlite3
    import traceback
    
    DB_PATH = '/data/pictorem.db'
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Count total sizes before
        cursor.execute("SELECT COUNT(*) as count FROM pictorem_sizes")
        total_before = cursor.fetchone()['count']
        
        # Find all duplicate size entries
        cursor.execute("""
            SELECT product_id, width, height, COUNT(*) as count
            FROM pictorem_sizes
            GROUP BY product_id, width, height
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        total_deleted = 0
        sizes_to_delete = []
        
        for dup in duplicates:
            product_id = dup['product_id']
            width = dup['width']
            height = dup['height']
            
            # Get all IDs for this combination
            cursor.execute("""
                SELECT id FROM pictorem_sizes
                WHERE product_id = ? AND width = ? AND height = ?
                ORDER BY id
            """, (product_id, width, height))
            
            ids = [row['id'] for row in cursor.fetchall()]
            
            # Keep the first ID, delete the rest
            if len(ids) > 1:
                sizes_to_delete.extend(ids[1:])
        
        if sizes_to_delete:
            # Delete pricing data first
            placeholders = ','.join('?' * len(sizes_to_delete))
            cursor.execute(f"""
                DELETE FROM pictorem_product_pricing
                WHERE size_id IN ({placeholders})
            """, sizes_to_delete)
            pricing_deleted = cursor.rowcount
            
            # Delete the duplicate sizes
            cursor.execute(f"""
                DELETE FROM pictorem_sizes
                WHERE id IN ({placeholders})
            """, sizes_to_delete)
            sizes_deleted = cursor.rowcount
            
            conn.commit()
            
            # Count total sizes after
            cursor.execute("SELECT COUNT(*) as count FROM pictorem_sizes")
            total_after = cursor.fetchone()['count']
            
            conn.close()
            
            return jsonify({
                'success': True,
                'duplicate_sets': len(duplicates),
                'total_sizes': total_before,
                'sizes_deleted': sizes_deleted,
                'pricing_deleted': pricing_deleted,
                'sizes_remaining': total_after
            })
        else:
            conn.close()
            return jsonify({
                'success': True,
                'message': 'No duplicates found',
                'total_sizes': total_before
            })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

