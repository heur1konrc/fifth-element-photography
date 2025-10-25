"""
Remove exact duplicate sizes from pictorem_sizes table
Keeps only the first occurrence of each product_id + width + height combination
"""

import sqlite3

DB_PATH = '/data/pictorem.db'

def cleanup_exact_duplicates():
    """Remove exact duplicate sizes, keeping only the first occurrence"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Find all duplicate size entries
    cursor.execute("""
        SELECT product_id, width, height, COUNT(*) as count
        FROM pictorem_sizes
        GROUP BY product_id, width, height
        HAVING COUNT(*) > 1
    """)
    
    duplicates = cursor.fetchall()
    
    print(f"Found {len(duplicates)} sets of duplicates")
    
    total_deleted = 0
    
    for dup in duplicates:
        product_id = dup['product_id']
        width = dup['width']
        height = dup['height']
        count = dup['count']
        
        print(f"  Product {product_id}, {width}×{height}: {count} duplicates")
        
        # Get all IDs for this combination
        cursor.execute("""
            SELECT id FROM pictorem_sizes
            WHERE product_id = ? AND width = ? AND height = ?
            ORDER BY id
        """, (product_id, width, height))
        
        ids = [row['id'] for row in cursor.fetchall()]
        
        # Keep the first ID, delete the rest
        ids_to_delete = ids[1:]
        
        if ids_to_delete:
            # Delete pricing data first
            placeholders = ','.join('?' * len(ids_to_delete))
            cursor.execute(f"""
                DELETE FROM pictorem_product_pricing
                WHERE size_id IN ({placeholders})
            """, ids_to_delete)
            
            # Delete the duplicate sizes
            cursor.execute(f"""
                DELETE FROM pictorem_sizes
                WHERE id IN ({placeholders})
            """, ids_to_delete)
            
            deleted = len(ids_to_delete)
            total_deleted += deleted
            print(f"    Deleted {deleted} duplicates, kept ID {ids[0]}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Total duplicates removed: {total_deleted}")
    
    return {
        'success': True,
        'duplicate_sets': len(duplicates),
        'total_deleted': total_deleted
    }

if __name__ == '__main__':
    result = cleanup_exact_duplicates()
    print(f"\nResult: {result}")

