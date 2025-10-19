#!/usr/bin/env python3
"""
Add remaining Framed Fine Art and Foam Mounted products
"""

import sqlite3

def add_remaining_products():
    """Add the final missing products"""
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("Adding Framed Fine Art Paper products...")
    
    # Framed Fine Art - 0.875" Frame (category 15)
    # No Mat pricing from the data
    framed_0875_no_mat = [
        ('5×7"', 16.85), ('6×6"', 16.90), ('8×8"', 18.97), ('8×10"', 20.08), ('8×12"', 21.19),
        ('10×10"', 21.34), ('11×14"', 24.65), ('11×17"', 26.82), ('12×12"', 24.01), ('12×16"', 27.04),
        ('12×24"', 33.71), ('12×36"', 43.70), ('16×16"', 31.08), ('16×20"', 35.12), ('16×24"', 39.15),
        ('16×32"', 47.24), ('18×36"', 55.06), ('20×20"', 39.86), ('20×36"', 58.84), ('24×24"', 50.06),
        ('24×30"', 58.23), ('24×36"', 66.40)
    ]
    
    for size, cost in framed_0875_no_mat:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (15, ?, ?, ?)', 
                      (f'Framed Fine Art 0.875" No Mat {size}', size, cost))
    
    # Framed Fine Art - 1.25" Frame (category 16)
    # No Mat pricing from the data
    framed_125_no_mat = [
        ('5×7"', 17.34), ('6×6"', 17.38), ('8×8"', 19.61), ('8×10"', 20.80), ('8×12"', 22.00),
        ('10×10"', 22.15), ('11×14"', 25.66), ('11×17"', 27.95), ('12×12"', 24.99), ('12×16"', 28.17),
        ('12×24"', 35.17), ('12×36"', 45.66), ('16×16"', 32.37), ('16×20"', 36.58), ('16×24"', 40.78),
        ('16×32"', 49.18), ('18×36"', 57.24), ('20×20"', 41.48), ('20×36"', 61.12), ('20×40"', 66.02),
        ('24×24"', 52.01), ('24×30"', 60.43), ('24×36"', 68.84), ('30×30"', 70.43), ('24×40"', 74.46),
        ('30×40"', 87.12), ('30×32"', 77.28), ('32×48"', 105.37), ('36×36"', 92.03), ('36×48"', 115.23),
        ('40×40"', 108.20), ('40×60"', 150.37)
    ]
    
    for size, cost in framed_125_no_mat:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (16, ?, ?, ?)', 
                      (f'Framed Fine Art 1.25" No Mat {size}', size, cost))
    
    # Foam Mounted - Archival Matte (category 17)
    foam_archival_data = [
        ('4×6"', 11.88), ('5×7"', 12.16), ('8×8"', 12.92), ('8×10"', 13.34), ('8.5×11"', 13.70),
        ('8×12"', 13.78), ('10×10"', 13.87), ('11×14"', 15.32), ('11×17"', 16.19), ('12×12"', 15.05),
        ('12×16"', 16.33), ('12×24"', 19.73), ('12×36"', 25.04), ('16×16"', 18.56), ('16×20"', 20.89),
        ('16×24"', 23.25), ('16×32"', 28.08), ('20×20"', 23.85), ('20×60"', 55.94), ('24×24"', 30.52),
        ('24×30"', 36.15), ('24×36"', 41.92), ('30×30"', 43.38), ('30×40"', 55.94), ('30×60"', 82.93),
        ('40×40"', 73.65), ('39.5×59.5"', 109.91)
    ]
    
    for size, cost in foam_archival_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (17, ?, ?, ?)', 
                      (f'Foam Mounted Archival Matte {size}', size, cost))
    
    conn.commit()
    
    # Final statistics
    cursor.execute('SELECT COUNT(*) FROM products WHERE active = 1')
    total_products = cursor.fetchone()[0]
    
    print(f"\nFinal product count: {total_products}")
    
    # Show updated category counts
    cursor.execute("""
        SELECT c.name, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id AND p.active = 1
        WHERE c.active = 1 AND c.id IN (15, 16, 17)
        GROUP BY c.id, c.name
        ORDER BY c.display_order
    """)
    
    print("\nUpdated categories:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} products")
    
    conn.close()

if __name__ == '__main__':
    add_remaining_products()
