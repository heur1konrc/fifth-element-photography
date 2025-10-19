"""
Check category names in the database to find the correct framed canvas category
"""
import sqlite3

def check_categories():
    """Check all category names to find framed canvas categories"""
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    # Get all categories
    categories = cursor.execute('SELECT id, name, description FROM categories ORDER BY name').fetchall()
    
    print("All categories in database:")
    print("-" * 50)
    for cat_id, name, description in categories:
        print(f"{cat_id:2d}. {name}")
        if description:
            print(f"    Description: {description}")
        print()
    
    # Look specifically for framed canvas
    framed_categories = cursor.execute('''
        SELECT id, name, description FROM categories 
        WHERE name LIKE '%Framed Canvas%' OR name LIKE '%Frame%'
        ORDER BY name
    ''').fetchall()
    
    print("\nFramed Canvas categories:")
    print("-" * 30)
    for cat_id, name, description in framed_categories:
        print(f"{cat_id}. {name}")
        
        # Count products in this category
        product_count = cursor.execute(
            'SELECT COUNT(*) FROM products WHERE category_id = ?', 
            (cat_id,)
        ).fetchone()[0]
        print(f"   Products: {product_count}")
        
        # Show a few sample products
        if product_count > 0:
            sample_products = cursor.execute(
                'SELECT name, size FROM products WHERE category_id = ? LIMIT 3', 
                (cat_id,)
            ).fetchall()
            for name, size in sample_products:
                print(f"   - {name} {size}")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_categories()
