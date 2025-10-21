@app.route('/admin/fix-test-products')
def fix_test_products_route():
    """Fix test products with correct sub_option IDs"""
    try:
        import sqlite3
        conn = sqlite3.connect('lumaprints_pricing.db')
        cursor = conn.cursor()
        
        # Update the test products with correct sub_option_1_id and sub_option_2_id
        # Product IDs 682, 683, 684 are 0.75" Frame + White (sub_option_1_id=4, sub_option_2_id=11)
        cursor.execute('UPDATE products SET sub_option_1_id = 4, sub_option_2_id = 11 WHERE id IN (682, 683, 684)')
        
        # Product ID 681 is 1.25" Frame + White (sub_option_1_id=5, sub_option_2_id=11)
        cursor.execute('UPDATE products SET sub_option_1_id = 5, sub_option_2_id = 11 WHERE id = 681')
        
        conn.commit()
        
        # Verify the fix
        cursor.execute('SELECT id, name, size, product_type_id, sub_option_1_id, sub_option_2_id FROM products WHERE id IN (681, 682, 683, 684)')
        results = cursor.fetchall()
        
        conn.close()
        
        html = "<h2>Test Products Fixed!</h2><table border='1'><tr><th>ID</th><th>Name</th><th>Size</th><th>Type</th><th>Sub1</th><th>Sub2</th></tr>"
        for row in results:
            html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
        html += "</table>"
        
        return html
        
    except Exception as e:
        return f"Error fixing test products: {str(e)}", 500
