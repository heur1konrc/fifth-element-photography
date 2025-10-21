#!/usr/bin/env python3
"""
Fix Sub-Option Assignments for Hierarchical Wizard
This script properly assigns sub_option_1_id and sub_option_2_id to all products
based on their product types and Lumaprints structure.
"""

import sqlite3
import json

def fix_sub_option_assignments():
    """
    Assign sub_option_1_id and sub_option_2_id to products based on their product types.
    
    Product Type Structure (based on Lumaprints API):
    - 0 Options: Metal Prints, Rolled Canvas - Direct to size selection
    - 1 Option: Canvas (mounting depth), Fine Art Paper (paper type)  
    - 2 Options: Framed Canvas (frame size + color), Framed Fine Art Paper (frame + mat)
    """
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("Starting sub-option assignment fix...")
    
    # First, clear all existing sub-option assignments
    print("Clearing existing sub-option assignments...")
    cursor.execute("UPDATE products SET sub_option_1_id = NULL, sub_option_2_id = NULL")
    
    # Get product type mappings
    cursor.execute("SELECT id, name FROM product_types ORDER BY name")
    product_types = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Get sub-option mappings
    cursor.execute("SELECT id, name, level FROM sub_options ORDER BY level, name")
    sub_options = {}
    for row in cursor.fetchall():
        option_id, name, level = row
        if level not in sub_options:
            sub_options[level] = {}
        sub_options[level][name] = option_id
    
    print(f"Found product types: {list(product_types.keys())}")
    print(f"Found sub-options: {sub_options}")
    
    # Assignment rules based on Lumaprints structure
    assignments = []
    
    # 0 Options - No sub-options needed (direct to sizes)
    zero_option_types = ['Metal Prints', 'Rolled Canvas Prints']
    for product_type in zero_option_types:
        if product_type in product_types:
            print(f"Processing {product_type} (0 options)...")
            # These products need no sub-option assignments - they go directly to sizes
            # The wizard will skip option steps for these
            pass
    
    # 1 Option Products
    # Canvas Prints - Need mounting depth selection
    if 'Canvas Prints' in product_types:
        print("Processing Canvas Prints (1 option - mounting depth)...")
        product_type_id = product_types['Canvas Prints']
        
        # Assign all Canvas products to each mounting depth
        mounting_options = [1, 2, 3]  # 0.75", 1.25", 1.5" mounting depths
        
        for mounting_id in mounting_options:
            if mounting_id in [opt_id for opt_id in sub_options.get(1, {}).values()]:
                assignments.append((product_type_id, mounting_id, None, 'Canvas Prints'))
    
    # Fine Art Paper Prints - Need paper type selection  
    if 'Fine Art Paper Prints' in product_types:
        print("Processing Fine Art Paper Prints (1 option - paper type)...")
        product_type_id = product_types['Fine Art Paper Prints']
        
        # Get paper type options (level 1)
        paper_types = [opt_id for name, opt_id in sub_options.get(1, {}).items() if 'Paper Type' in name]
        
        for paper_id in paper_types:
            assignments.append((product_type_id, paper_id, None, 'Fine Art Paper Prints'))
    
    # 2 Option Products
    # Framed Canvas Prints - Need frame size + frame color
    if 'Framed Canvas Prints' in product_types:
        print("Processing Framed Canvas Prints (2 options - frame size + color)...")
        product_type_id = product_types['Framed Canvas Prints']
        
        # Get frame size options (level 1) and frame color options (level 2)
        frame_sizes = [opt_id for name, opt_id in sub_options.get(1, {}).items() if 'Frame Size' in name]
        frame_colors = [opt_id for name, opt_id in sub_options.get(2, {}).items() if 'Frame Color' in name]
        
        for frame_size_id in frame_sizes:
            for frame_color_id in frame_colors:
                assignments.append((product_type_id, frame_size_id, frame_color_id, 'Framed Canvas Prints'))
    
    # Framed Fine Art Paper Prints - Need frame size + mat size
    if 'Framed Fine Art Paper Prints' in product_types:
        print("Processing Framed Fine Art Paper Prints (2 options - frame + mat)...")
        product_type_id = product_types['Framed Fine Art Paper Prints']
        
        # Get frame size options (level 1) and mat size options (level 2)
        frame_sizes = [opt_id for name, opt_id in sub_options.get(1, {}).items() if 'Frame Size' in name]
        mat_sizes = [opt_id for name, opt_id in sub_options.get(2, {}).items() if 'Mat Size' in name]
        
        for frame_size_id in frame_sizes:
            for mat_size_id in mat_sizes:
                assignments.append((product_type_id, frame_size_id, mat_size_id, 'Framed Fine Art Paper Prints'))
    
    # Single option products that don't need combinations
    single_option_types = [
        'Foam-Mounted Fine Art Paper Prints',
        'Peel and Stick Prints'
    ]
    
    for product_type in single_option_types:
        if product_type in product_types:
            print(f"Processing {product_type} (1 option)...")
            product_type_id = product_types[product_type]
            
            # These get a default sub-option assignment
            if 'Paper Type' in sub_options.get(1, {}):
                paper_type_id = list(sub_options[1].values())[0]  # Use first available paper type
                assignments.append((product_type_id, paper_type_id, None, product_type))
    
    print(f"\nCreated {len(assignments)} sub-option assignments")
    
    # Now create product variants for each assignment
    print("Creating product variants with sub-option assignments...")
    
    # Get all base products (current products without sub-option assignments)
    cursor.execute("""
        SELECT id, category_id, name, size, cost_price, description, product_type_id,
               lumaprints_subcategory_id, lumaprints_options, lumaprints_frame_option
        FROM products 
        WHERE active = 1
    """)
    
    base_products = cursor.fetchall()
    print(f"Found {len(base_products)} base products")
    
    # Clear products table and recreate with proper sub-option assignments
    cursor.execute("DELETE FROM products")
    
    product_id = 1
    created_count = 0
    
    for assignment in assignments:
        product_type_id, sub_option_1_id, sub_option_2_id, type_name = assignment
        
        # Find base products for this product type
        matching_products = [p for p in base_products if p[6] == product_type_id]  # product_type_id is index 6
        
        for base_product in matching_products:
            # Create new product with sub-option assignments
            cursor.execute("""
                INSERT INTO products (
                    id, category_id, name, size, cost_price, description, active,
                    product_type_id, sub_option_1_id, sub_option_2_id,
                    lumaprints_subcategory_id, lumaprints_options, lumaprints_frame_option
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                base_product[1],  # category_id
                base_product[2],  # name
                base_product[3],  # size
                base_product[4],  # cost_price
                base_product[5],  # description
                product_type_id,
                sub_option_1_id,
                sub_option_2_id,
                base_product[7],  # lumaprints_subcategory_id
                base_product[8],  # lumaprints_options
                base_product[9]   # lumaprints_frame_option
            ))
            
            product_id += 1
            created_count += 1
    
    # Handle 0-option products (Metal Prints, Rolled Canvas) - they keep original structure
    zero_option_product_types = [product_types[name] for name in zero_option_types if name in product_types]
    
    for product_type_id in zero_option_product_types:
        matching_products = [p for p in base_products if p[6] == product_type_id]
        
        for base_product in matching_products:
            cursor.execute("""
                INSERT INTO products (
                    id, category_id, name, size, cost_price, description, active,
                    product_type_id, sub_option_1_id, sub_option_2_id,
                    lumaprints_subcategory_id, lumaprints_options, lumaprints_frame_option
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, NULL, NULL, ?, ?, ?)
            """, (
                product_id,
                base_product[1],  # category_id
                base_product[2],  # name
                base_product[3],  # size
                base_product[4],  # cost_price
                base_product[5],  # description
                product_type_id,
                base_product[7],  # lumaprints_subcategory_id
                base_product[8],  # lumaprints_options
                base_product[9]   # lumaprints_frame_option
            ))
            
            product_id += 1
            created_count += 1
    
    conn.commit()
    
    # Verify results
    cursor.execute("""
        SELECT 
            pt.name as product_type,
            COUNT(*) as total_products,
            COUNT(p.sub_option_1_id) as has_sub_option_1,
            COUNT(p.sub_option_2_id) as has_sub_option_2
        FROM products p
        JOIN product_types pt ON p.product_type_id = pt.id
        WHERE p.active = 1
        GROUP BY pt.name
        ORDER BY pt.name
    """)
    
    results = cursor.fetchall()
    
    print(f"\nCreated {created_count} total products with proper sub-option assignments:")
    print("Product Type | Total | Sub-Option 1 | Sub-Option 2")
    print("-" * 60)
    for row in results:
        print(f"{row[0]:<30} | {row[1]:>5} | {row[2]:>12} | {row[3]:>12}")
    
    conn.close()
    print("\nSub-option assignment fix completed successfully!")

if __name__ == "__main__":
    fix_sub_option_assignments()
