#!/usr/bin/env python3
"""
Import all Framed Fine Art products with proper Lumaprints mappings
6 frame styles × 10 mat sizes × 8 paper types × multiple print sizes
"""

import sqlite3
import sys

# Lumaprints frame subcategories
FRAME_STYLES = {
    105001: {"name": "0.875\" Black Frame", "wizard_id": 22, "color": "Black"},
    105002: {"name": "0.875\" White Frame", "wizard_id": 22, "color": "White"},
    105003: {"name": "0.875\" Oak Frame", "wizard_id": 22, "color": "Oak"},
    105005: {"name": "1.25\" Black Frame", "wizard_id": 23, "color": "Black"},
    105006: {"name": "1.25\" White Frame", "wizard_id": 23, "color": "White"},
    105007: {"name": "1.25\" Oak Frame", "wizard_id": 23, "color": "Oak"},
}

# Lumaprints mat sizes
MAT_SIZES = {
    64: {"name": "No Mat", "wizard_id": 33},
    65: {"name": "1.0\" Mat", "wizard_id": 34},
    66: {"name": "1.5\" Mat", "wizard_id": 35},
    67: {"name": "2.0\" Mat", "wizard_id": 36},
    68: {"name": "2.5\" Mat", "wizard_id": 37},
    69: {"name": "3.0\" Mat", "wizard_id": 38},
    70: {"name": "3.5\" Mat", "wizard_id": 39},
    71: {"name": "4.0\" Mat", "wizard_id": 40},
    72: {"name": "4.5\" Mat", "wizard_id": 41},
    73: {"name": "5.0\" Mat", "wizard_id": 42},
}

# Lumaprints paper types
PAPER_TYPES = {
    74: "Archival Matte",
    75: "Hot Press",
    76: "Cold Press",
    77: "Metallic",
    78: "Semi-Glossy",
    79: "Glossy",
    80: "Semi-Matte",
    82: "Somerset Velvet",
}

# Standard print sizes for Framed Fine Art
PRINT_SIZES = [
    "5×7", "6×6", "8×8", "8×10", "8×12",
    "10×10", "11×14", "11×17",
    "12×12", "12×16", "12×24", "12×36",
    "16×16", "16×20", "16×24", "16×32",
    "18×36", "20×20", "20×36", "20×40",
    "24×24", "24×30", "24×36", "24×40",
    "30×30", "30×32", "30×40", "32×48",
    "36×36", "36×48", "40×40", "40×60"
]

def get_base_price(size):
    """Calculate base price based on size (simplified for now)"""
    # Parse dimensions
    parts = size.split('×')
    w, h = int(parts[0]), int(parts[1])
    area = w * h
    
    # Base pricing (can be adjusted)
    if area <= 50:  # 5x7, 6x6, 8x8
        return 20.0
    elif area <= 100:  # 8x10, 8x12, 10x10
        return 25.0
    elif area <= 200:  # 11x14, 11x17, 12x12, 12x16
        return 35.0
    elif area <= 400:  # 16x20, 16x24, 20x20
        return 50.0
    elif area <= 800:  # 24x30, 24x36, 30x30
        return 75.0
    else:
        return 100.0

def import_products(conn, limit_to_no_mat=False):
    """Import all Framed Fine Art products"""
    cursor = conn.cursor()
    
    product_count = 0
    
    for frame_id, frame_info in FRAME_STYLES.items():
        for mat_id, mat_info in MAT_SIZES.items():
            # Skip if limiting to No Mat only
            if limit_to_no_mat and mat_id != 64:
                continue
                
            for paper_id, paper_name in PAPER_TYPES.items():
                for size in PRINT_SIZES:
                    # Create product name
                    product_name = f"Framed Fine Art {frame_info['color']} {mat_info['name']} {paper_name} {size}\""
                    
                    # Calculate pricing
                    base_price = get_base_price(size)
                    
                    # Check if product already exists
                    cursor.execute("""
                        SELECT id FROM products 
                        WHERE name = ? AND product_type_id = 4
                    """, (product_name,))
                    
                    if cursor.fetchone():
                        continue  # Skip if exists
                    
                    # Insert product
                    # Store Lumaprints options as JSON
                    lumaprints_opts = f'{{"mat_size": {mat_id}, "paper_type": {paper_id}}}'
                    
                    cursor.execute("""
                        INSERT INTO products (
                            name, product_type_id, category_id, size, cost_price,
                            sub_option_1_id, sub_option_2_id,
                            lumaprints_subcategory_id, lumaprints_options,
                            active
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        product_name,
                        4,  # Framed Fine Art Paper
                        4,  # Category ID for Framed Fine Art
                        size,
                        base_price,
                        frame_info['wizard_id'],  # Frame size wizard ID
                        mat_info['wizard_id'],    # Mat size wizard ID
                        frame_id,                 # Lumaprints frame subcategory
                        lumaprints_opts,          # Lumaprints options JSON
                        1                         # active
                    ))
                    
                    product_count += 1
    
    conn.commit()
    return product_count

def main():
    # Ask user if they want all products or just No Mat
    print("Framed Fine Art Product Import")
    print("=" * 50)
    print("\nOptions:")
    print("1. Import only 'No Mat' products (6 frames × 8 papers × 32 sizes = ~1,536 products)")
    print("2. Import ALL products (6 frames × 10 mats × 8 papers × 32 sizes = ~15,360 products)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    limit_to_no_mat = (choice == "1")
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    
    print(f"\n{'Importing No Mat products only...' if limit_to_no_mat else 'Importing ALL products...'}")
    
    count = import_products(conn, limit_to_no_mat)
    
    conn.close()
    
    print(f"\n✅ Successfully imported {count} Framed Fine Art products!")
    
if __name__ == "__main__":
    main()

