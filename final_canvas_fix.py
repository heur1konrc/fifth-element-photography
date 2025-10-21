#!/usr/bin/env python3
"""
Final Canvas Fix: Distribute Canvas products across all mounting options
"""

import sqlite3

def fix_canvas_distribution():
    """Distribute Canvas products across all three mounting options (1, 2, 3)"""
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        # Get all Canvas products
        cursor.execute("""
            SELECT id, name, size 
            FROM products 
            WHERE product_type_id = 1 
            ORDER BY id
        """)
        canvas_products = cursor.fetchall()
        
        print(f"Found {len(canvas_products)} Canvas products")
        
        # Distribute products across the three mounting options
        # Split evenly: 1/3 to each mounting option
        total_products = len(canvas_products)
        products_per_option = total_products // 3
        remainder = total_products % 3
        
        updates = []
        
        for i, (product_id, name, size) in enumerate(canvas_products):
            if i < products_per_option:
                sub_option_1_id = 1  # 0.75"
            elif i < products_per_option * 2:
                sub_option_1_id = 2  # 1.25"
            else:
                sub_option_1_id = 3  # 1.5"
            
            updates.append((sub_option_1_id, product_id))
        
        # If there's a remainder, distribute the extra products
        if remainder > 0:
            # Give extra products to the first mounting options
            for i in range(remainder):
                idx = products_per_option * 3 + i
                if idx < len(canvas_products):
                    product_id = canvas_products[idx][0]
                    sub_option_1_id = (i % 3) + 1
                    # Update the existing entry
                    for j, (existing_sub_option, existing_id) in enumerate(updates):
                        if existing_id == product_id:
                            updates[j] = (sub_option_1_id, product_id)
                            break
        
        # Apply all updates
        cursor.executemany("""
            UPDATE products 
            SET sub_option_1_id = ? 
            WHERE id = ?
        """, updates)
        
        conn.commit()
        
        # Verify the distribution
        cursor.execute("""
            SELECT sub_option_1_id, COUNT(*) 
            FROM products 
            WHERE product_type_id = 1 
            GROUP BY sub_option_1_id
        """)
        distribution = cursor.fetchall()
        
        print("Canvas product distribution:")
        for sub_option_id, count in distribution:
            mounting_size = {1: "0.75\"", 2: "1.25\"", 3: "1.5\""}
            print(f"  {mounting_size.get(sub_option_id, f'ID {sub_option_id}')}: {count} products")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_canvas_distribution()
