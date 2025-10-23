# Add this to your app.py routes

@app.route('/admin/backup-products')
def backup_products():
    """Export all current products to JSON"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, name, category, size, price, 
                   lumaprints_subcategory_id, lumaprints_frame_option_id,
                   created_at
            FROM products
            ORDER BY id
        """)
        
        products = []
        for row in cur.fetchall():
            products.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'size': row[3],
                'price': float(row[4]) if row[4] else None,
                'lumaprints_subcategory_id': row[5],
                'lumaprints_frame_option_id': row[6],
                'created_at': row[7].isoformat() if row[7] else None
            })
        
        cur.close()
        conn.close()
        
        # Return as downloadable JSON
        from flask import Response
        import json
        
        response = Response(
            json.dumps(products, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment;filename=products_backup.json'}
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

