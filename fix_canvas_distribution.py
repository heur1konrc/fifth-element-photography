import sqlite3

def fix_canvas_distribution():
    """Distribute Canvas products across all three mounting options (0.75", 1.25", 1.5")"""
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        # Get all Canvas products
        cursor.execute("""
            SELECT id, name FROM products 
            WHERE product_type_id = 1 
            ORDER BY id
        """)
        canvas_products = cursor.fetchall()
        
        print(f"Found {len(canvas_products)} Canvas products")
        
        # Distribute products across the three mounting options
        # 0.75" = sub_option_1_id = 1
        # 1.25" = sub_option_1_id = 2  
        # 1.5" = sub_option_1_id = 3
        
        updates = []
        for i, (product_id, name) in enumerate(canvas_products):
            # Cycle through mounting options: 1, 2, 3, 1, 2, 3, ...
            sub_option_id = (i % 3) + 1
            
            cursor.execute("""
                UPDATE products 
                SET sub_option_1_id = ? 
                WHERE id = ?
            """, (sub_option_id, product_id))
            
            updates.append((product_id, name, sub_option_id))
        
        conn.commit()
        
        print("Canvas products distributed:")
        for product_id, name, sub_option_id in updates[:10]:  # Show first 10
            mounting = ["0.75\"", "1.25\"", "1.5\""][sub_option_id - 1]
            print(f"  {product_id}: {name} -> {mounting} (sub_option_1_id={sub_option_id})")
        
        if len(updates) > 10:
            print(f"  ... and {len(updates) - 10} more")
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_canvas_distribution()
