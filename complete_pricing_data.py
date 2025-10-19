#!/usr/bin/env python3
"""
Complete Lumaprints Pricing Data Loading
Adds remaining product categories and products to the database
"""

import sqlite3
import os

def complete_pricing_data():
    """Add remaining Lumaprints products to the database"""
    
    db_path = 'lumaprints_pricing.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Adding remaining Fine Art Paper products...")
    
    # Fine Art Paper - Hot Press (category 9)
    hot_press_data = [
        ('4×6"', 2.86), ('5×7"', 3.24), ('8×8"', 4.17), ('8×10"', 4.68), ('8.5×11"', 5.09),
        ('8×12"', 5.18), ('10×10"', 5.28), ('11×14"', 6.90), ('11×17"', 7.87), ('12×12"', 6.59),
        ('12×16"', 8.01), ('12×24"', 10.83), ('12×36"', 15.06), ('16×16"', 9.83), ('16×20"', 11.64),
        ('16×24"', 13.46), ('16×32"', 17.09), ('20×20"', 13.85), ('20×60"', 36.03), ('24×24"', 18.69),
        ('24×30"', 22.63), ('24×36"', 26.55), ('30×30"', 27.47), ('30×40"', 35.53), ('30×60"', 51.67),
        ('40×40"', 46.13), ('40×60"', 67.31)
    ]
    
    for size, cost in hot_press_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (9, ?, ?, ?)', 
                      (f'Fine Art Hot Press {size}', size, cost))
    
    # Fine Art Paper - Cold Press (category 10) - same prices as Hot Press
    for size, cost in hot_press_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (10, ?, ?, ?)', 
                      (f'Fine Art Cold Press {size}', size, cost))
    
    # Fine Art Paper - Semi-Gloss (category 11) - same prices as Archival Matte
    archival_matte_data = [
        ('4×6"', 1.71), ('5×7"', 2.01), ('8×8"', 2.79), ('8×10"', 3.19), ('8.5×11"', 3.54),
        ('8×12"', 3.61), ('10×10"', 3.68), ('11×14"', 5.01), ('11×17"', 5.81), ('12×12"', 4.76),
        ('12×16"', 5.92), ('12×24"', 8.22), ('12×36"', 11.69), ('16×16"', 7.40), ('16×20"', 8.89),
        ('16×24"', 10.37), ('16×32"', 13.34), ('20×20"', 10.70), ('20×60"', 28.86), ('24×24"', 14.66),
        ('24×30"', 17.88), ('24×36"', 21.10), ('30×30"', 21.84), ('30×40"', 28.44), ('30×60"', 41.64),
        ('40×40"', 37.70), ('40×60"', 54.43)
    ]
    
    for size, cost in archival_matte_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (11, ?, ?, ?)', 
                      (f'Fine Art Semi-Gloss {size}', size, cost))
    
    # Fine Art Paper - Metallic (category 12)
    metallic_data = [
        ('4×6"', 2.92), ('5×7"', 3.61), ('8×8"', 5.30), ('8×10"', 6.22), ('8.5×11"', 6.97),
        ('8×12"', 7.12), ('10×10"', 7.32), ('11×14"', 10.25), ('11×17"', 12.04), ('12×12"', 9.70),
        ('12×16"', 12.26), ('12×24"', 17.40), ('12×36"', 25.10), ('16×16"', 15.56), ('16×20"', 18.86),
        ('16×24"', 22.16), ('16×32"', 28.76), ('20×20"', 22.90), ('20×60"', 63.23), ('24×24"', 31.70),
        ('24×30"', 38.85), ('24×36"', 46.00), ('30×30"', 47.65), ('30×40"', 62.32), ('30×60"', 91.66),
        ('40×40"', 81.56), ('40×60"', 120.06)
    ]
    
    for size, cost in metallic_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (12, ?, ?, ?)', 
                      (f'Fine Art Metallic {size}', size, cost))
    
    # Fine Art Paper - Glossy (category 13)
    glossy_data = [
        ('4×6"', 3.02), ('5×7"', 3.45), ('8×8"', 4.51), ('8×10"', 5.09), ('8.5×11"', 5.55),
        ('8×12"', 5.66), ('10×10"', 5.78), ('11×14"', 7.61), ('11×17"', 8.73), ('12×12"', 7.26),
        ('12×16"', 8.86), ('12×24"', 12.08), ('12×36"', 16.89), ('16×16"', 10.94), ('16×20"', 12.99),
        ('16×24"', 15.06), ('16×32"', 19.18), ('20×20"', 15.51), ('20×60"', 40.72), ('24×24"', 21.01),
        ('24×30"', 25.49), ('24×36"', 29.96), ('30×30"', 30.99), ('30×40"', 40.16), ('30×60"', 58.49),
        ('40×40"', 52.18), ('40×60"', 76.24)
    ]
    
    for size, cost in glossy_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (13, ?, ?, ?)', 
                      (f'Fine Art Glossy {size}', size, cost))
    
    # Fine Art Paper - Somerset Velvet (category 14) - same prices as Glossy
    for size, cost in glossy_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (14, ?, ?, ?)', 
                      (f'Fine Art Somerset Velvet {size}', size, cost))
    
    print("Adding Framed Canvas products...")
    
    # Framed Canvas - 0.75" (category 5)
    framed_075_data = [
        ('8×10"', 29.69), ('8×12"', 33.31), ('10×20"', 52.65), ('10×30"', 62.35), ('11×14"', 37.80),
        ('12×12"', 43.40), ('12×16"', 47.86), ('12×18"', 49.74), ('16×20"', 56.37), ('16×24"', 61.61),
        ('18×24"', 63.73), ('20×20"', 61.76), ('20×40"', 84.79), ('20×60"', 132.24), ('24×30"', 79.05),
        ('24×32"', 81.16), ('24×36"', 85.39), ('28×58"', 149.98), ('30×30"', 88.37), ('30×40"', 99.47),
        ('30×60"', 158.70), ('30×46"', 133.87), ('32×48"', 142.01), ('34×46"', 142.82), ('36×48"', 151.21),
        ('38×38"', 113.86), ('38×58"', 175.87), ('40×40"', 120.84), ('40×60"', 185.18), ('43×58"', 188.81),
        ('45×60"', 198.41), ('48×48"', 178.78)
    ]
    
    for size, cost in framed_075_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (5, ?, ?, ?)', 
                      (f'Framed Canvas 0.75" {size}', size, cost))
    
    # Framed Canvas - 1.25" (category 6)
    framed_125_data = [
        ('8×10"', 29.17), ('8×12"', 31.62), ('10×20"', 49.86), ('10×30"', 58.64), ('11×14"', 35.68),
        ('12×12"', 41.29), ('12×16"', 45.37), ('12×18"', 47.08), ('16×20"', 53.18), ('16×24"', 58.07),
        ('18×24"', 60.01), ('20×20"', 58.23), ('20×40"', 79.48), ('20×60"', 102.06), ('24×30"', 74.27),
        ('24×32"', 76.20), ('24×36"', 80.07), ('28×58"', 133.06), ('30×30"', 83.06), ('30×40"', 93.27),
        ('30×60"', 138.54), ('30×46"', 136.08), ('32×48"', 141.98), ('34×46"', 142.32), ('36×48"', 148.31),
        ('38×38"', 141.3), ('38×58"', 191.25), ('40×40"', 147.19), ('40×60"', 198.08), ('43×58"', 200.38),
        ('45×60"', 207.36), ('48×48"', 192.56)
    ]
    
    for size, cost in framed_125_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (6, ?, ?, ?)', 
                      (f'Framed Canvas 1.25" {size}', size, cost))
    
    # Framed Canvas - 1.5" (category 7)
    framed_150_data = [
        ('8×10"', 35.00), ('8×12"', 39.22), ('10×20"', 62.38), ('10×30"', 75.34), ('11×14"', 45.17),
        ('12×12"', 50.85), ('12×16"', 56.53), ('12×18"', 59.04), ('16×20"', 67.52), ('16×24"', 74.01),
        ('18×24"', 76.75), ('20×20"', 74.16), ('20×40"', 103.38), ('20×60"', 133.94), ('24×30"', 95.78),
        ('24×32"', 98.52), ('24×36"', 101.98), ('28×58"', 173.86), ('30×30"', 106.97), ('30×40"', 121.16),
        ('30×60"', 181.23), ('30×46"', 176.47), ('32×48"', 184.49), ('34×46"', 184.83), ('36×48"', 192.94),
        ('38×38"', 181.68), ('38×58"', 245.90), ('40×40"', 189.70), ('40×60"', 255.01), ('43×58"', 257.88),
        ('45×60"', 267.14), ('48×48"', 247.21)
    ]
    
    for size, cost in framed_150_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (7, ?, ?, ?)', 
                      (f'Framed Canvas 1.5" {size}', size, cost))
    
    print("Adding Foam Mounted products...")
    
    # Foam Mounted - Hot Press (category 18) - same prices as Foam Mounted Archival Matte but with Hot Press pricing
    foam_hot_press_data = [
        ('4×6"', 12.15), ('5×7"', 12.57), ('8×8"', 13.66), ('8×10"', 14.27), ('8.5×11"', 14.78),
        ('8×12"', 14.89), ('10×10"', 15.03), ('11×14"', 17.10), ('11×17"', 18.37), ('12×12"', 16.71),
        ('12×16"', 18.57), ('12×24"', 23.11), ('12×36"', 30.20), ('16×16"', 21.55), ('16×20"', 24.66),
        ('16×24"', 27.82), ('16×32"', 34.23), ('20×20"', 28.61), ('20×60"', 71.36), ('24×24"', 37.50),
        ('24×30"', 44.99), ('24×36"', 52.67), ('30×30"', 54.63), ('30×40"', 71.36), ('30×60"', 107.36),
        ('40×40"', 94.98), ('39.5×59.5"', 143.31)
    ]
    
    for size, cost in foam_hot_press_data:
        cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (18, ?, ?, ?)', 
                      (f'Foam Mounted Hot Press {size}', size, cost))
    
    # Add remaining foam mounted categories with their respective pricing
    # Categories 19-23 use the same data structure but different category IDs
    foam_categories = [
        (19, 'Cold Press', foam_hot_press_data),  # Same as Hot Press
        (20, 'Semi-Gloss', [  # Use archival matte base prices + foam mounting cost
            ('4×6"', 12.06), ('5×7"', 12.42), ('8×8"', 13.37), ('8×10"', 13.92), ('8.5×11"', 14.36),
            ('8×12"', 14.45), ('10×10"', 14.59), ('11×14"', 16.42), ('11×17"', 17.54), ('12×12"', 16.07),
            ('12×16"', 17.71), ('12×24"', 21.80), ('12×36"', 28.23), ('16×16"', 20.41), ('16×20"', 23.21),
            ('16×24"', 26.06), ('16×32"', 31.87), ('20×20"', 26.79), ('20×60"', 65.43), ('24×24"', 34.82),
            ('24×30"', 41.59), ('24×36"', 48.53), ('30×30"', 50.30), ('30×40"', 65.43), ('30×60"', 97.96),
            ('40×40"', 86.79), ('39.5×59.5"', 130.47)
        ]),
        (21, 'Metallic', [  # Metallic pricing + foam mounting
            ('4×6"', 12.37), ('5×7"', 12.88), ('8×8"', 14.24), ('8×10"', 14.98), ('8.5×11"', 15.61),
            ('8×12"', 15.73), ('10×10"', 15.91), ('11×14"', 18.47), ('11×17"', 20.05), ('12×12"', 18.00),
            ('12×16"', 20.28), ('12×24"', 25.71), ('12×36"', 34.18), ('16×16"', 23.86), ('16×20"', 27.58),
            ('16×24"', 31.32), ('16×32"', 38.97), ('20×20"', 32.27), ('20×60"', 83.22), ('24×24"', 42.87),
            ('24×30"', 51.79), ('24×36"', 60.94), ('30×30"', 63.28), ('30×40"', 83.22), ('30×60"', 126.13),
            ('40×40"', 111.38), ('39.5×59.5"', 169.02)
        ]),
        (22, 'Glossy', foam_hot_press_data),  # Same as Hot Press
        (23, 'Somerset Velvet', foam_hot_press_data)  # Same as Hot Press
    ]
    
    for cat_id, cat_name, data in foam_categories:
        for size, cost in data:
            cursor.execute('INSERT OR IGNORE INTO products (category_id, name, size, cost_price) VALUES (?, ?, ?, ?)', 
                          (cat_id, f'Foam Mounted {cat_name} {size}', size, cost))
    
    # Commit all changes
    conn.commit()
    
    # Print final statistics
    cursor.execute('SELECT COUNT(*) FROM products WHERE active = 1')
    total_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM categories WHERE active = 1')
    total_categories = cursor.fetchone()[0]
    
    print(f"\nData loading complete!")
    print(f"Total Products: {total_products}")
    print(f"Total Categories: {total_categories}")
    
    # Show products per category
    cursor.execute("""
        SELECT c.name, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id AND p.active = 1
        WHERE c.active = 1
        GROUP BY c.id, c.name
        ORDER BY c.display_order, c.name
    """)
    
    print("\nProducts per category:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} products")
    
    conn.close()
    return True

if __name__ == '__main__':
    complete_pricing_data()
