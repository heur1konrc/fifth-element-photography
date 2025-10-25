"""
Check for duplicate sizes in the database
"""
import sqlite3

DB_PATH = '/data/pictorem.db'

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find duplicates
cursor.execute("""
    SELECT product_id, width, height, COUNT(*) as count
    FROM pictorem_sizes
    GROUP BY product_id, width, height
    HAVING COUNT(*) > 1
    ORDER BY product_id, width, height
""")

duplicates = cursor.fetchall()

print(f"Found {len(duplicates)} sets of duplicates:\n")

for dup in duplicates:
    product_id = dup['product_id']
    width = dup['width']
    height = dup['height']
    count = dup['count']
    
    print(f"Product {product_id}: {width}×{height} appears {count} times")
    
    # Show the IDs
    cursor.execute("""
        SELECT id FROM pictorem_sizes
        WHERE product_id = ? AND width = ? AND height = ?
        ORDER BY id
    """, (product_id, width, height))
    
    ids = [row['id'] for row in cursor.fetchall()]
    print(f"  IDs: {ids} (will keep {ids[0]}, delete {ids[1:]})")
    print()

conn.close()

print(f"\nTotal duplicate sets: {len(duplicates)}")

