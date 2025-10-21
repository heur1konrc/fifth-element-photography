@app.route('/fix-canvas-now')
def fix_canvas_now():
    """FINAL Canvas fix - distribute products across all mounting options"""
    import sqlite3
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        # Get Canvas product IDs
        cursor.execute("SELECT id FROM products WHERE product_type_id = 1 ORDER BY id")
        canvas_ids = [row[0] for row in cursor.fetchall()]
        
        # Distribute evenly across 3 mounting options
        total = len(canvas_ids)
        per_option = total // 3
        
        # Assign to mounting option 1 (0.75")
        cursor.execute(f"""
            UPDATE products 
            SET sub_option_1_id = 1 
            WHERE product_type_id = 1 
            AND id IN ({','.join(map(str, canvas_ids[:per_option]))})
        """)
        
        # Assign to mounting option 2 (1.25")  
        cursor.execute(f"""
            UPDATE products 
            SET sub_option_1_id = 2 
            WHERE product_type_id = 1 
            AND id IN ({','.join(map(str, canvas_ids[per_option:per_option*2]))})
        """)
        
        # Assign remaining to mounting option 3 (1.5")
        cursor.execute(f"""
            UPDATE products 
            SET sub_option_1_id = 3 
            WHERE product_type_id = 1 
            AND id IN ({','.join(map(str, canvas_ids[per_option*2:]))})
        """)
        
        conn.commit()
        
        # Check results
        cursor.execute("""
            SELECT sub_option_1_id, COUNT(*) 
            FROM products 
            WHERE product_type_id = 1 
            GROUP BY sub_option_1_id
        """)
        results = cursor.fetchall()
        
        return f"""
        <h1>CANVAS FIX COMPLETE!</h1>
        <h3>Distribution:</h3>
        <ul>
        {''.join([f'<li>Mounting {["0.75", "1.25", "1.5"][sub_id-1]}": {count} products</li>' for sub_id, count in results])}
        </ul>
        
        <h2>TEST LINKS:</h2>
        <ul>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=1">Test 0.75" Canvas</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=2">Test 1.25" Canvas</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=3">Test 1.5" Canvas</a></li>
        </ul>
        
        <h1>🎉 CANVAS SHOULD WORK NOW! 🎉</h1>
        """
        
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()
