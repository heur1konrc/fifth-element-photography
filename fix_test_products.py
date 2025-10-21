#!/usr/bin/env python3
"""
Fix test products with correct sub_option IDs
This script fixes the test products that were added with NULL sub_option_1_id and sub_option_2_id
"""

import sqlite3
import os

def fix_test_products():
    """Fix the test products with correct sub_option IDs"""
    db_path = os.path.join(os.path.dirname(__file__), 'lumaprints_pricing.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Fixing test products with correct sub_option IDs...")
        
        # Update the test products with correct sub_option_1_id and sub_option_2_id
        # Product IDs 682, 683, 684 are 0.75" Frame + White (sub_option_1_id=4, sub_option_2_id=11)
        cursor.execute('UPDATE products SET sub_option_1_id = 4, sub_option_2_id = 11 WHERE id IN (682, 683, 684)')
        
        # Product ID 681 is 1.25" Frame + White (sub_option_1_id=5, sub_option_2_id=11)
        cursor.execute('UPDATE products SET sub_option_1_id = 5, sub_option_2_id = 11 WHERE id = 681')
        
        conn.commit()
        
        print("Updated products. Checking results:")
        cursor.execute('SELECT id, name, size, product_type_id, sub_option_1_id, sub_option_2_id FROM products WHERE id IN (681, 682, 683, 684)')
        for row in cursor.fetchall():
            print(f'ID: {row[0]}, Name: {row[1]}, Size: {row[2]}, Type: {row[3]}, Sub1: {row[4]}, Sub2: {row[5]}')
        
        conn.close()
        print("Test products fixed successfully!")
        return True
        
    except Exception as e:
        print(f"Error fixing test products: {e}")
        return False

if __name__ == "__main__":
    fix_test_products()
