#!/usr/bin/env python3
"""
Fix aspect ratios in print_ordering database
Consolidates duplicate aspect ratio entries into standard ratios: 1:1, 3:2, 4:3, 16:9
"""

import sqlite3
import os
from fractions import Fraction

# Database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'database_templates', 'print_ordering_initial.db')

def normalize_aspect_ratio(width, height):
    """Convert width and height to normalized aspect ratio string"""
    # Calculate GCD to get simplified ratio
    fraction = Fraction(width, height)
    w = fraction.numerator
    h = fraction.denominator
    
    # Return standard format
    return f"{w}:{h}"

def get_standard_ratio_info(ratio_name):
    """Get display name and description for standard ratios"""
    ratios = {
        "1:1": ("Square", "Square format (1:1 aspect ratio)"),
        "3:2": ("Standard", "Standard digital/35mm format (3:2 aspect ratio)"),
        "2:3": ("Standard Portrait", "Standard portrait format (2:3 aspect ratio)"),
        "4:3": ("Classic", "Classic photo format (4:3 aspect ratio)"),
        "3:4": ("Classic Portrait", "Classic portrait format (3:4 aspect ratio)"),
        "16:9": ("Widescreen", "Widescreen format (16:9 aspect ratio)"),
        "9:16": ("Widescreen Portrait", "Widescreen portrait format (9:16 aspect ratio)")
    }
    return ratios.get(ratio_name, (ratio_name, f"{ratio_name} aspect ratio"))

def main():
    print("Fixing aspect ratios in database...")
    print(f"Database: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Step 1: Get all print sizes with their dimensions
    cursor.execute("""
        SELECT size_id, width, height, size_name, aspect_ratio_id
        FROM print_sizes
        ORDER BY size_id
    """)
    sizes = cursor.fetchall()
    
    print(f"Found {len(sizes)} print sizes")
    
    # Step 2: Calculate correct aspect ratios for each size
    size_updates = []
    aspect_ratios_needed = {}
    
    for size_id, width, height, size_name, old_aspect_id in sizes:
        # Calculate normalized aspect ratio
        normalized_ratio = normalize_aspect_ratio(width, height)
        ratio_decimal = width / height
        
        # Store for later
        if normalized_ratio not in aspect_ratios_needed:
            display_name, description = get_standard_ratio_info(normalized_ratio)
            aspect_ratios_needed[normalized_ratio] = {
                'decimal': ratio_decimal,
                'display_name': display_name,
                'description': description
            }
        
        size_updates.append((size_id, normalized_ratio, old_aspect_id))
    
    print(f"\nAspect ratios needed: {list(aspect_ratios_needed.keys())}")
    
    # Step 3: Clear existing aspect_ratios table and insert only needed ones
    cursor.execute("DELETE FROM aspect_ratios")
    
    aspect_ratio_map = {}
    for ratio_name, info in sorted(aspect_ratios_needed.items()):
        cursor.execute("""
            INSERT INTO aspect_ratios 
            (ratio_name, ratio_decimal, display_name, description, is_enabled)
            VALUES (?, ?, ?, ?, TRUE)
        """, (ratio_name, info['decimal'], info['display_name'], info['description']))
        
        new_id = cursor.lastrowid
        aspect_ratio_map[ratio_name] = new_id
        print(f"  Created aspect ratio: {ratio_name} (ID: {new_id})")
    
    # Step 4: Update all print_sizes with correct aspect_ratio_id
    print("\nUpdating print sizes...")
    for size_id, normalized_ratio, old_aspect_id in size_updates:
        new_aspect_id = aspect_ratio_map[normalized_ratio]
        cursor.execute("""
            UPDATE print_sizes
            SET aspect_ratio_id = ?
            WHERE size_id = ?
        """, (new_aspect_id, size_id))
    
    conn.commit()
    
    # Step 5: Verify results
    cursor.execute("SELECT COUNT(*) FROM aspect_ratios")
    aspect_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT ar.ratio_name, COUNT(ps.size_id) as size_count
        FROM aspect_ratios ar
        LEFT JOIN print_sizes ps ON ar.aspect_ratio_id = ps.aspect_ratio_id
        GROUP BY ar.ratio_name
        ORDER BY ar.ratio_name
    """)
    results = cursor.fetchall()
    
    print(f"\n✓ Database updated successfully!")
    print(f"\nFinal aspect ratios ({aspect_count} total):")
    for ratio_name, size_count in results:
        print(f"  {ratio_name}: {size_count} sizes")
    
    conn.close()

if __name__ == '__main__':
    main()

