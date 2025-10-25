"""
Remove duplicate orientation sizes from Pictorem database
Keep only smaller-first dimensions (e.g., 8x10, not 10x8)
"""

import sqlite3

DB_PATH = 'pictorem.db'

def remove_duplicate_orientations():
    """Remove duplicate orientation sizes, keeping only width < height entries"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all sizes
    cursor.execute("""
        SELECT id, product_id, width, height, orientation
        FROM pictorem_sizes
        ORDER BY product_id, width, height
    """)
    
    all_sizes = cursor.fetchall()
    
    # Track which sizes to keep (smaller dimension first)
    sizes_to_delete = []
    seen_combinations = set()
    
    for size_id, product_id, width, height, orientation in all_sizes:
        # Create a normalized key (smaller dimension first)
        min_dim = min(width, height)
        max_dim = max(width, height)
        key = (product_id, min_dim, max_dim)
        
        if key in seen_combinations:
            # This is a duplicate (opposite orientation)
            sizes_to_delete.append(size_id)
            print(f"Marking for deletion: Product {product_id}, Size {width}x{height} (ID: {size_id})")
        else:
            # First time seeing this combination
            seen_combinations.add(key)
            print(f"Keeping: Product {product_id}, Size {width}x{height} (ID: {size_id})")
    
    print(f"\n{'='*60}")
    print(f"Total sizes: {len(all_sizes)}")
    print(f"Sizes to keep: {len(all_sizes) - len(sizes_to_delete)}")
    print(f"Sizes to delete: {len(sizes_to_delete)}")
    print(f"{'='*60}\n")
    
    if sizes_to_delete:
        # Delete pricing data for these sizes first
        cursor.execute(f"""
            DELETE FROM pictorem_product_pricing
            WHERE size_id IN ({','.join('?' * len(sizes_to_delete))})
        """, sizes_to_delete)
        print(f"Deleted pricing data for {cursor.rowcount} size entries")
        
        # Delete the duplicate sizes
        cursor.execute(f"""
            DELETE FROM pictorem_sizes
            WHERE id IN ({','.join('?' * len(sizes_to_delete))})
        """)
        print(f"Deleted {cursor.rowcount} duplicate size entries")
        
        conn.commit()
        print("\n✓ Database cleaned successfully!")
    else:
        print("\nNo duplicates found.")
    
    conn.close()

if __name__ == '__main__':
    remove_duplicate_orientations()
