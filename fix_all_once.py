#!/usr/bin/env python3
"""
COMPREHENSIVE FIX FOR ALL PRODUCT TYPES
This script assigns sub-options to ALL product types in ONE operation
"""

import sqlite3

def fix_all_product_types():
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        # 1. Canvas Prints (product_type_id = 1) - 1 option level
        # Sub-option 1: Mounting sizes (1, 2, 3)
        cursor.execute("SELECT id FROM products WHERE product_type_id = 1 ORDER BY id")
        canvas_ids = [row[0] for row in cursor.fetchall()]
        mounting_options = [1, 2, 3]  # 0.75", 1.25", 1.5"
        
        for i, product_id in enumerate(canvas_ids):
            mounting = mounting_options[i % 3]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = NULL WHERE id = ?", (mounting, product_id))
        
        # 2. Framed Canvas Prints (product_type_id = 2) - 2 option levels  
        # Sub-option 1: Frame sizes (4, 5, 6)
        # Sub-option 2: Frame colors (7, 8, 9, 10, 11, 12, 13, 14)
        cursor.execute("SELECT id FROM products WHERE product_type_id = 2 ORDER BY id")
        framed_canvas_ids = [row[0] for row in cursor.fetchall()]
        frame_sizes = [4, 5, 6]
        frame_colors = [7, 8, 9, 10, 11, 12, 13, 14]
        
        for i, product_id in enumerate(framed_canvas_ids):
            frame_size = frame_sizes[i % 3]
            frame_color = frame_colors[i % 8]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = ? WHERE id = ?", (frame_size, frame_color, product_id))
        
        # 3. Fine Art Paper Prints (product_type_id = 3) - 1 option level
        # Sub-option 1: Paper types (15, 16, 17, 18, 19, 20, 21)
        cursor.execute("SELECT id FROM products WHERE product_type_id = 3 ORDER BY id")
        fine_art_ids = [row[0] for row in cursor.fetchall()]
        paper_types = [15, 16, 17, 18, 19, 20, 21]
        
        for i, product_id in enumerate(fine_art_ids):
            paper_type = paper_types[i % 7]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = NULL WHERE id = ?", (paper_type, product_id))
        
        # 4. Framed Fine Art Paper Prints (product_type_id = 4) - 2 option levels
        # Sub-option 1: Frame sizes (22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32)
        # Sub-option 2: Mat sizes (33, 34, 35, 36, 37, 38, 39, 40, 41, 42)
        cursor.execute("SELECT id FROM products WHERE product_type_id = 4 ORDER BY id")
        framed_fine_art_ids = [row[0] for row in cursor.fetchall()]
        fine_art_frame_sizes = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        mat_sizes = [33, 34, 35, 36, 37, 38, 39, 40, 41, 42]
        
        for i, product_id in enumerate(framed_fine_art_ids):
            frame_size = fine_art_frame_sizes[i % 11]
            mat_size = mat_sizes[i % 10]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = ? WHERE id = ?", (frame_size, mat_size, product_id))
        
        # 5. Foam-Mounted Fine Art Paper Prints (product_type_id = 5) - 1 option level
        # Sub-option 1: Paper types (15, 16, 17, 18, 19, 20, 21) - same as Fine Art Paper
        cursor.execute("SELECT id FROM products WHERE product_type_id = 5 ORDER BY id")
        foam_mounted_ids = [row[0] for row in cursor.fetchall()]
        
        for i, product_id in enumerate(foam_mounted_ids):
            paper_type = paper_types[i % 7]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = NULL WHERE id = ?", (paper_type, product_id))
        
        # 6. 0-option products (Rolled Canvas, Metal, Peel & Stick) - keep NULL
        for product_type_id in [8, 6, 7]:  # Rolled Canvas, Metal, Peel & Stick
            cursor.execute("UPDATE products SET sub_option_1_id = NULL, sub_option_2_id = NULL WHERE product_type_id = ?", (product_type_id,))
        
        conn.commit()
        
        # Verify results
        cursor.execute("""
            SELECT pt.name, COUNT(*) as count,
                   COUNT(CASE WHEN sub_option_1_id IS NOT NULL THEN 1 END) as has_sub1,
                   COUNT(CASE WHEN sub_option_2_id IS NOT NULL THEN 1 END) as has_sub2
            FROM products p
            JOIN product_types pt ON p.product_type_id = pt.id
            GROUP BY pt.name
            ORDER BY pt.id
        """)
        
        results = cursor.fetchall()
        return results
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    results = fix_all_product_types()
    print("COMPREHENSIVE FIX COMPLETE!")
    print("\nResults:")
    for name, count, has_sub1, has_sub2 in results:
        print(f"- {name}: {count} products, {has_sub1} have sub_option_1, {has_sub2} have sub_option_2")
