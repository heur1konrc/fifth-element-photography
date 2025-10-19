#!/usr/bin/env python3
"""
Lumaprints Pricing Database Initialization
Creates SQLite database with complete Lumaprints pricing data
"""

import sqlite3
import json
import os

def init_pricing_database():
    """Initialize the pricing database with schema and data"""
    
    # Database file path
    db_path = 'lumaprints_pricing.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create new database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    print("Creating database schema...")
    
    # Categories table
    cursor.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            display_order INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            size TEXT NOT NULL,
            cost_price DECIMAL(10,2) NOT NULL,
            description TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            UNIQUE(category_id, name, size)
        )
    ''')
    
    # Global settings table
    cursor.execute('''
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_name TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("Schema created successfully!")
    
    # Insert categories
    print("Inserting categories...")
    categories = [
        ('Canvas - 1.25" Stretched', 'Canvas prints with 1.25 inch stretching', 1),
        ('Canvas - 1.5" Stretched', 'Canvas prints with 1.5 inch stretching', 2),
        ('Canvas - 0.75" Stretched', 'Canvas prints with 0.75 inch stretching', 3),
        ('Canvas - Rolled', 'Rolled canvas prints (no stretching)', 4),
        ('Framed Canvas - 0.75"', 'Framed canvas with 0.75 inch frame', 5),
        ('Framed Canvas - 1.25"', 'Framed canvas with 1.25 inch frame', 6),
        ('Framed Canvas - 1.5"', 'Framed canvas with 1.5 inch frame', 7),
        ('Fine Art Paper - Archival Matte', 'Archival matte fine art paper', 8),
        ('Fine Art Paper - Hot Press', 'Hot press fine art paper', 9),
        ('Fine Art Paper - Cold Press', 'Cold press fine art paper', 10),
        ('Fine Art Paper - Semi-Gloss', 'Semi-gloss fine art paper', 11),
        ('Fine Art Paper - Metallic', 'Metallic fine art paper', 12),
        ('Fine Art Paper - Glossy', 'Glossy fine art paper', 13),
        ('Fine Art Paper - Somerset Velvet', 'Somerset velvet fine art paper', 14),
        ('Framed Fine Art - 0.875" Frame', 'Fine art paper with 0.875" frame', 15),
        ('Framed Fine Art - 1.25" Frame', 'Fine art paper with 1.25" frame', 16),
        ('Foam Mounted - Archival Matte', 'Foam mounted archival matte', 17),
        ('Foam Mounted - Hot Press', 'Foam mounted hot press', 18),
        ('Foam Mounted - Cold Press', 'Foam mounted cold press', 19),
        ('Foam Mounted - Semi-Gloss', 'Foam mounted semi-gloss', 20),
        ('Foam Mounted - Metallic', 'Foam mounted metallic', 21),
        ('Foam Mounted - Glossy', 'Foam mounted glossy', 22),
        ('Foam Mounted - Somerset Velvet', 'Foam mounted Somerset velvet', 23),
        ('Metal Prints', 'Metal print products', 24),
        ('Peel & Stick', 'Peel and stick products', 25),
    ]
    
    cursor.executemany('INSERT INTO categories (name, description, display_order) VALUES (?, ?, ?)', categories)
    
    # Insert default settings
    print("Inserting default settings...")
    settings = [
        ('global_markup_percentage', '123.0', 'Global markup percentage (123% = 2.23x multiplier)'),
        ('currency_symbol', '$', 'Currency symbol for display'),
        ('tax_rate', '0.0', 'Tax rate percentage'),
        ('last_updated', '2025-10-18', 'Last time pricing was updated'),
    ]
    
    cursor.executemany('INSERT INTO settings (key_name, value, description) VALUES (?, ?, ?)', settings)
    
    # Insert Canvas products
    print("Inserting Canvas products...")
    canvas_data = [
        # 1.25" Stretched Canvas
        ('8×10"', 10.99), ('8×12"', 16.23), ('10×20"', 24.13), ('10×30"', 28.26), ('11×14"', 13.19),
        ('12×12"', 19.36), ('12×16"', 21.68), ('12×18"', 22.50), ('16×20"', 25.95), ('16×24"', 29.07),
        ('18×24"', 30.12), ('20×20"', 29.23), ('20×40"', 41.63), ('20×60"', 55.34), ('24×30"', 39.07),
        ('24×32"', 40.11), ('24×36"', 42.21), ('30×30"', 45.20), ('30×40"', 50.99), ('30×60"', 80.03),
        ('32×48"', 79.69), ('36×48"', 86.33), ('40×40"', 81.37), ('40×60"', 112.07), ('45×60"', 118.17)
    ]
    
    for size, cost in canvas_data:
        cursor.execute('INSERT INTO products (category_id, name, size, cost_price) VALUES (1, ?, ?, ?)', 
                      (f'Canvas 1.25" Stretched {size}', size, cost))
    
    # 1.5" Stretched Canvas
    canvas_15_data = [
        ('8×10"', 12.09), ('8×12"', 18.76), ('10×20"', 28.29), ('10×30"', 33.82), ('11×14"', 14.29),
        ('12×12"', 22.56), ('12×16"', 25.40), ('12×18"', 26.49), ('16×20"', 30.73), ('16×24"', 34.39),
        ('18×24"', 35.69), ('20×20"', 34.54), ('20×40"', 49.59), ('20×60"', 65.97), ('24×30"', 46.23),
        ('24×32"', 47.56), ('24×36"', 50.19), ('30×30"', 53.17), ('30×40"', 60.29), ('30×60"', 94.26),
        ('32×48"', 93.87), ('36×48"', 101.20), ('40×40"', 95.54), ('40×60"', 131.03), ('45×60"', 138.10)
    ]
    
    for size, cost in canvas_15_data:
        cursor.execute('INSERT INTO products (category_id, name, size, cost_price) VALUES (2, ?, ?, ?)', 
                      (f'Canvas 1.5" Stretched {size}', size, cost))
    
    # 0.75" Stretched Canvas (some sizes not available)
    canvas_075_data = [
        ('8×10"', 9.89), ('8×12"', 15.39), ('10×20"', 22.73), ('10×30"', 26.4), ('11×14"', 12.09),
        ('12×12"', 18.31), ('12×16"', 20.44), ('12×18"', 21.18), ('16×20"', 24.35), ('16×24"', 27.30),
        ('18×24"', 28.26), ('20×20"', 27.46), ('20×40"', 38.96), ('20×60"', 66.85), ('24×30"', 36.68),
        ('24×32"', 37.64), ('24×36"', 39.56), ('30×30"', 42.54), ('30×40"', 66.85), ('32×48"', 81.77),
        ('36×48"', 90.29)
    ]
    
    for size, cost in canvas_075_data:
        cursor.execute('INSERT INTO products (category_id, name, size, cost_price) VALUES (3, ?, ?, ?)', 
                      (f'Canvas 0.75" Stretched {size}', size, cost))
    
    # Rolled Canvas
    rolled_canvas_data = [
        ('8×10"', 9.13), ('8×12"', 10.28), ('10×20"', 13.05), ('10×30"', 14.87), ('11×14"', 12.20),
        ('12×12"', 12.02), ('12×16"', 12.85), ('12×18"', 13.25), ('16×20"', 14.92), ('16×24"', 15.96),
        ('18×24"', 16.67), ('20×20"', 17.74), ('20×40"', 23.96), ('20×60"', 30.18), ('24×30"', 22.62),
        ('24×32"', 23.35), ('24×36"', 24.8), ('30×30"', 25.26), ('30×40"', 32.83), ('30×60"', 41.64),
        ('32×48"', 37.70), ('36×48"', 40.39), ('40×40"', 40.10), ('40×60"', 51.51), ('45×60"', 55.66)
    ]
    
    for size, cost in rolled_canvas_data:
        cursor.execute('INSERT INTO products (category_id, name, size, cost_price) VALUES (4, ?, ?, ?)', 
                      (f'Rolled Canvas {size}', size, cost))
    
    # Metal Prints
    print("Inserting Metal Print products...")
    metal_data = [
        ('8×10"', 30.57), ('8×12"', 33.95), ('10×30"', 79.79), ('11×14"', 46.12), ('11×17"', 53.37),
        ('12×12"', 43.94), ('12×16"', 54.38), ('12×18"', 59.77), ('12×24"', 76.59), ('15×45"', 153.63),
        ('16×20"', 82.46), ('16×24"', 95.21), ('18×24"', 104.53), ('20×20"', 98.15), ('20×30"', 137.37),
        ('20×40"', 176.58), ('20×60"', 255.01), ('24×24"', 132.45), ('24×30"', 160.39), ('24×36"', 188.32),
        ('24×48"', 244.19), ('30×30"', 194.93), ('30×40"', 252.50), ('30×60"', 367.64), ('32×48"', 316.67),
        ('36×36"', 270.62), ('36×48"', 352.92), ('40×60"', 480.27)
    ]
    
    for size, cost in metal_data:
        cursor.execute('INSERT INTO products (category_id, name, size, cost_price) VALUES (24, ?, ?, ?)', 
                      (f'Metal Print {size}', size, cost))
    
    # Peel & Stick
    print("Inserting Peel & Stick products...")
    peel_stick_data = [
        ('4×6"', 3.79), ('8×10"', 4.30), ('8×12"', 4.43), ('10×20"', 7.08), ('10×30"', 8.48),
        ('11×14"', 6.44), ('12×12"', 6.30), ('12×16"', 6.96), ('12×18"', 7.31), ('16×20"', 8.76),
        ('16×24"', 9.64), ('16×48"', 17.91), ('18×24"', 10.32), ('20×20"', 9.87), ('20×40"', 18.48),
        ('20×60"', 25.58), ('24×30"', 17.07), ('24×36"', 19.61), ('30×30"', 20.25), ('30×40"', 25.58),
        ('30×60"', 34.59), ('32×48"', 33.17), ('36×48"', 33.86), ('36×72"', 34.82), ('40×40"', 32.06),
        ('40×60"', 40.26)
    ]
    
    for size, cost in peel_stick_data:
        cursor.execute('INSERT INTO products (category_id, name, size, cost_price) VALUES (25, ?, ?, ?)', 
                      (f'Peel & Stick {size}', size, cost))
    
    # Fine Art Paper - Archival Matte (category 8)
    print("Inserting Fine Art Paper products...")
    archival_matte_data = [
        ('4×6"', 1.71), ('5×7"', 2.01), ('8×8"', 2.79), ('8×10"', 3.19), ('8.5×11"', 3.54),
        ('8×12"', 3.61), ('10×10"', 3.68), ('11×14"', 5.01), ('11×17"', 5.81), ('12×12"', 4.76),
        ('12×16"', 5.92), ('12×24"', 8.22), ('12×36"', 11.69), ('16×16"', 7.40), ('16×20"', 8.89),
        ('16×24"', 10.37), ('16×32"', 13.34), ('20×20"', 10.70), ('20×60"', 28.86), ('24×24"', 14.66),
        ('24×30"', 17.88), ('24×36"', 21.10), ('30×30"', 21.84), ('30×40"', 28.44), ('30×60"', 41.64),
        ('40×40"', 37.70), ('40×60"', 54.43)
    ]
    
    for size, cost in archival_matte_data:
        cursor.execute('INSERT INTO products (category_id, name, size, cost_price) VALUES (8, ?, ?, ?)', 
                      (f'Fine Art Archival Matte {size}', size, cost))
    
    # Commit all changes
    conn.commit()
    
    # Print summary
    cursor.execute('SELECT COUNT(*) FROM categories')
    cat_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products')
    prod_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM settings')
    set_count = cursor.fetchone()[0]
    
    print(f"\nDatabase initialization complete!")
    print(f"Categories: {cat_count}")
    print(f"Products: {prod_count}")
    print(f"Settings: {set_count}")
    print(f"Database saved as: {db_path}")
    
    conn.close()
    return db_path

if __name__ == '__main__':
    init_pricing_database()
