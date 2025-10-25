@pictorem_admin_bp.route('/api/cleanup_duplicate_orientations', methods=['POST'])
def api_cleanup_duplicate_orientations():
    """Remove orientation duplicates - keep only one size per width/height pair"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Count total before
        cursor.execute("SELECT COUNT(*) as count FROM pictorem_sizes")
        total_before = cursor.fetchone()[0]
        
        # Find orientation duplicates (e.g., 8x10 and 10x8)
        # For each product, find sizes where both orientations exist
        cursor.execute("""
            SELECT DISTINCT
                s1.id as id_to_delete,
                s1.product_id,
                s1.width,
                s1.height,
                s1.orientation
            FROM pictorem_sizes s1
            JOIN pictorem_sizes s2 ON 
                s1.product_id = s2.product_id AND
                s1.width = s2.height AND
                s1.height = s2.width AND
                s1.id > s2.id
            WHERE s1.width < s1.height
        """)
        
        sizes_to_delete = [row[0] for row in cursor.fetchall()]
        
        if sizes_to_delete:
            placeholders = ','.join('?' * len(sizes_to_delete))
            
            # Delete associated pricing first
            cursor.execute(f"DELETE FROM pictorem_product_pricing WHERE size_id IN ({placeholders})", sizes_to_delete)
            pricing_deleted = cursor.rowcount
            
            # Delete the sizes
            cursor.execute(f"DELETE FROM pictorem_sizes WHERE id IN ({placeholders})", sizes_to_delete)
            sizes_deleted = cursor.rowcount
            
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) as count FROM pictorem_sizes")
            total_after = cursor.fetchone()[0]
            conn.close()
            
            return jsonify({
                'success': True,
                'total_sizes': total_before,
                'sizes_deleted': sizes_deleted,
                'pricing_deleted': pricing_deleted,
                'sizes_remaining': total_after
            })
        else:
            conn.close()
            return jsonify({'success': True, 'message': 'No orientation duplicates found'})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

