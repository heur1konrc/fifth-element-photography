#!/usr/bin/env python3
"""
Comprehensive product mapping script to map all 684 products to correct sub_options
"""

import sqlite3

def map_all_products():
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    results = []
    
    # Product Type 1: Canvas Prints (71 products)
    # Sub-options: 1=0.75", 2=1.25", 3=1.5"
    cursor.execute("UPDATE products SET sub_option_1_id=1 WHERE product_type_id=1 AND name LIKE '%0.75\"%'")
    results.append(f"Canvas 0.75\": {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=2 WHERE product_type_id=1 AND name LIKE '%1.25\"%'")
    results.append(f"Canvas 1.25\": {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=3 WHERE product_type_id=1 AND name LIKE '%1.5\"%'")
    results.append(f"Canvas 1.5\": {cursor.rowcount} products")
    
    # Product Type 2: Framed Canvas (102 products)
    # Sub-option 1: Frame size (4=0.75", 5=1.25", 6=1.5")
    # Sub-option 2: Frame color (7-14)
    # Map by lumaprints codes
    cursor.execute("""
        UPDATE products SET sub_option_1_id=4, sub_option_2_id=8 
        WHERE product_type_id=2 AND lumaprints_subcategory_id=102001 
        AND (lumaprints_frame_option=12 OR lumaprints_frame_option IS NULL)
    """)
    results.append(f"Framed Canvas 0.75\" Black: {cursor.rowcount} products")
    
    cursor.execute("""
        UPDATE products SET sub_option_1_id=4, sub_option_2_id=14 
        WHERE product_type_id=2 AND lumaprints_subcategory_id=102001 AND lumaprints_frame_option=13
    """)
    results.append(f"Framed Canvas 0.75\" White: {cursor.rowcount} products")
    
    cursor.execute("""
        UPDATE products SET sub_option_1_id=5, sub_option_2_id=8 
        WHERE product_type_id=2 AND lumaprints_subcategory_id=102002 AND lumaprints_frame_option=27
    """)
    results.append(f"Framed Canvas 1.25\" Black: {cursor.rowcount} products")
    
    cursor.execute("""
        UPDATE products SET sub_option_1_id=5, sub_option_2_id=12 
        WHERE product_type_id=2 AND lumaprints_subcategory_id=102002 AND lumaprints_frame_option=91
    """)
    results.append(f"Framed Canvas 1.25\" Oak: {cursor.rowcount} products")
    
    cursor.execute("""
        UPDATE products SET sub_option_1_id=6, sub_option_2_id=8 
        WHERE product_type_id=2 AND lumaprints_subcategory_id=102003 AND lumaprints_frame_option=23
    """)
    results.append(f"Framed Canvas 1.5\" Black: {cursor.rowcount} products")
    
    # Product Type 3: Fine Art Paper (189 products)
    # Sub-options: 15-21 (paper types)
    cursor.execute("UPDATE products SET sub_option_1_id=15 WHERE product_type_id=3 AND name LIKE '%Archival Matte%'")
    results.append(f"Fine Art Archival Matte: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=16 WHERE product_type_id=3 AND name LIKE '%Hot Press%'")
    results.append(f"Fine Art Hot Press: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=17 WHERE product_type_id=3 AND name LIKE '%Cold Press%'")
    results.append(f"Fine Art Cold Press: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=18 WHERE product_type_id=3 AND name LIKE '%Semi-Gloss%'")
    results.append(f"Fine Art Semi-Gloss: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=19 WHERE product_type_id=3 AND name LIKE '%Metallic%'")
    results.append(f"Fine Art Metallic: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=20 WHERE product_type_id=3 AND name LIKE '%Glossy%'")
    results.append(f"Fine Art Glossy: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=21 WHERE product_type_id=3 AND name LIKE '%Somerset Velvet%'")
    results.append(f"Fine Art Somerset Velvet: {cursor.rowcount} products")
    
    # Product Type 4: Framed Fine Art Paper (54 products)
    # Sub-option 1: Frame size (22-32)
    # Sub-option 2: Mat size (33-42)
    cursor.execute("UPDATE products SET sub_option_1_id=22, sub_option_2_id=33 WHERE product_type_id=4 AND name LIKE '%0.875\" No Mat%'")
    results.append(f"Framed Fine Art 0.875\" No Mat: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=23, sub_option_2_id=33 WHERE product_type_id=4 AND name LIKE '%1.25\" No Mat%'")
    results.append(f"Framed Fine Art 1.25\" No Mat: {cursor.rowcount} products")
    
    # Product Type 5: Foam-Mounted (189 products)
    # Sub-options: 43-49 (paper types)
    cursor.execute("UPDATE products SET sub_option_1_id=43 WHERE product_type_id=5 AND name LIKE '%Archival Matte%'")
    results.append(f"Foam-Mounted Archival Matte: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=44 WHERE product_type_id=5 AND name LIKE '%Hot Press%'")
    results.append(f"Foam-Mounted Hot Press: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=45 WHERE product_type_id=5 AND name LIKE '%Cold Press%'")
    results.append(f"Foam-Mounted Cold Press: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=46 WHERE product_type_id=5 AND name LIKE '%Semi-Gloss%'")
    results.append(f"Foam-Mounted Semi-Gloss: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=47 WHERE product_type_id=5 AND name LIKE '%Metallic%'")
    results.append(f"Foam-Mounted Metallic: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=48 WHERE product_type_id=5 AND name LIKE '%Glossy%'")
    results.append(f"Foam-Mounted Glossy: {cursor.rowcount} products")
    
    cursor.execute("UPDATE products SET sub_option_1_id=49 WHERE product_type_id=5 AND name LIKE '%Somerset Velvet%'")
    results.append(f"Foam-Mounted Somerset Velvet: {cursor.rowcount} products")
    
    # Product Types 6-8 have no sub-options (Metal, Peel and Stick, Rolled Canvas)
    # No mapping needed
    
    conn.commit()
    conn.close()
    
    print("✅ ALL PRODUCTS MAPPED!")
    print("\nResults:")
    for result in results:
        print(f"  - {result}")
    
    return results

if __name__ == "__main__":
    map_all_products()

