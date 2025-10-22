#!/usr/bin/env python3
"""
Import ALL Lumaprints products with pricing from extracted JSON files.
This script populates the database with complete product catalog.
"""

import sqlite3
import json
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lumaprints_pricing.db')

# Lumaprints product codes from API documentation
LUMAPRINTS_CODES = {
    'canvas': {
        'rolled': 101000,
        '0.75': 101001,
        '1.25': 101002,
        '1.5': 101003
    },
    'framed_canvas': {
        '0.75': 102001,
        '1.25': 102002,
        '1.5': 102003
    },
    'fine_art_paper': 103001,  # Single subcategory, paper type is option
    'framed_fine_art': {
        '0.875_black': 105001,
        '0.875_white': 105002,
        '0.875_oak': 105003,
        '1.25_black': 105005,
        '1.25_white': 105006,
        '1.25_oak': 105007,
        '2x1_black': 105009,
        '2x1_white': 105010,
        '2x1_oak': 105011
    },
    'metal_prints': 106001,
    'peel_stick': 107001,
    'foam_mounted': 104001  # Single subcategory, paper type is option
}

# Option IDs
PAPER_TYPES = {
    'Archival Matte': 27,
    'Hot Press': 28,
    'Cold Press': 29,
    'Semi-Gloss': 30,
    'Metallic': 31,
    'Glossy': 32,
    'Somerset Velvet': 33
}

FRAME_COLORS = {
    'Black': 12,
    'White': 13,
    'Oak': 91
}

MAT_SIZES = {
    'No Mat': 64,
    '1.5"': 66,
    '2.0"': 67,
    '2.5"': 68,
    '3.0"': 69
}

def init_database():
    """Initialize database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            product_type_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            size TEXT NOT NULL,
            cost_price REAL NOT NULL,
            lumaprints_subcategory_id INTEGER,
            lumaprints_options TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create product_types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            display_order INTEGER DEFAULT 0
        )
    ''')
    
    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            product_type_id INTEGER NOT NULL,
            display_order INTEGER DEFAULT 0
        )
    ''')
    
    # Create settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    # Insert default global markup if not exists
    cursor.execute('''
        INSERT OR IGNORE INTO settings (key, value) VALUES ('global_markup_percentage', '0')
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def clear_existing_data():
    """Clear existing products and categories."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM products')
    cursor.execute('DELETE FROM categories')
    cursor.execute('DELETE FROM product_types')
    
    conn.commit()
    conn.close()
    print("✅ Cleared existing data")

def insert_product_types():
    """Insert product types."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    product_types = [
        (1, 'Canvas', 1),
        (2, 'Framed Canvas', 2),
        (3, 'Fine Art Paper', 3),
        (4, 'Framed Fine Art Paper', 4),
        (5, 'Metal Prints', 5),
        (6, 'Peel & Stick', 6),
        (7, 'Foam-Mounted Fine Art', 7)
    ]
    
    for pt_id, name, order in product_types:
        cursor.execute('''
            INSERT INTO product_types (id, name, display_order)
            VALUES (?, ?, ?)
        ''', (pt_id, name, order))
    
    conn.commit()
    conn.close()
    print("✅ Inserted product types")

def import_canvas():
    """Import Canvas products."""
    print("\n📦 Importing Canvas products...")
    
    with open('pricing_data_canvas.json', 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create categories for each canvas depth
    depths = ['Rolled Canvas', '0.75" Stretched Canvas', '1.25" Stretched Canvas', '1.5" Stretched Canvas']
    depth_codes = ['rolled', '0.75', '1.25', '1.5']
    
    for idx, (depth_name, depth_code) in enumerate(zip(depths, depth_codes), start=1):
        cursor.execute('''
            INSERT INTO categories (id, name, product_type_id, display_order)
            VALUES (?, ?, 1, ?)
        ''', (idx, depth_name, idx))
    
    # Insert products
    product_count = 0
    for depth_key, depth_data in data.items():
        # Use subcategory_id from JSON data directly
        subcategory_id = depth_data['subcategory_id']
        
        # Map subcategory to category
        if subcategory_id == 101000:
            category_id = 1  # Rolled
        elif subcategory_id == 101001:
            category_id = 2  # 0.75"
        elif subcategory_id == 101002:
            category_id = 3  # 1.25"
        elif subcategory_id == 101003:
            category_id = 4  # 1.5"
        else:
            category_id = 1
        
        for size, price in depth_data['prices'].items():
            # Skip null prices
            if price is None:
                continue
                
            clean_size = size.replace('"', '').replace('×', 'x')
            name = f"Canvas {depth_data['name']} {clean_size}"
            
            cursor.execute('''
                INSERT INTO products (name, product_type_id, category_id, size, cost_price, 
                                    lumaprints_subcategory_id, lumaprints_options)
                VALUES (?, 1, ?, ?, ?, ?, '{}')
            ''', (name, category_id, clean_size, price, subcategory_id))
            product_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {product_count} Canvas products")

def import_framed_canvas():
    """Import Framed Canvas products."""
    print("\n📦 Importing Framed Canvas products...")
    
    with open('pricing_data_framed_canvas.json', 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create categories for each frame depth
    depths = ['0.75" Framed Canvas', '1.25" Framed Canvas', '1.5" Framed Canvas']
    depth_codes = ['0.75', '1.25', '1.5']
    
    for idx, depth_name in enumerate(depths, start=5):
        cursor.execute('''
            INSERT INTO categories (id, name, product_type_id, display_order)
            VALUES (?, ?, 2, ?)
        ''', (idx, depth_name, idx))
    
    # Insert products (frame colors don't affect price, but we create variations)
    product_count = 0
    for depth_key, depth_data in data.items():
        # Use subcategory_id from JSON data directly
        subcategory_id = depth_data['subcategory_id']
        
        # Map subcategory to category
        if subcategory_id == 102001:
            category_id = 5  # 0.75"
        elif subcategory_id == 102002:
            category_id = 6  # 1.25"
        elif subcategory_id == 102003:
            category_id = 7  # 1.5"
        else:
            category_id = 5
        
        for size, price in depth_data['prices'].items():
            # Skip null prices
            if price is None:
                continue
                
            clean_size = size.replace('"', '').replace('×', 'x')
            
            # Create product for each frame color
            for color_name, color_id in FRAME_COLORS.items():
                name = f"Framed Canvas {depth_data['name']} {clean_size} - {color_name}"
                options = json.dumps({'frame_color': color_id})
                
                cursor.execute('''
                    INSERT INTO products (name, product_type_id, category_id, size, cost_price, 
                                        lumaprints_subcategory_id, lumaprints_options)
                    VALUES (?, 2, ?, ?, ?, ?, ?)
                ''', (name, category_id, clean_size, price, subcategory_id, options))
                product_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {product_count} Framed Canvas products")

def import_fine_art_paper():
    """Import Fine Art Paper products."""
    print("\n📦 Importing Fine Art Paper products...")
    
    with open('pricing_data_fine_art_paper.json', 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create categories for each paper type
    category_id = 8
    for paper_key, paper_data in data.items():
        cursor.execute('''
            INSERT INTO categories (id, name, product_type_id, display_order)
            VALUES (?, ?, 3, ?)
        ''', (category_id, f"Fine Art Paper - {paper_data['name']}", category_id))
        category_id += 1
    
    # Insert products
    product_count = 0
    category_id = 8
    for paper_key, paper_data in data.items():
        paper_type_id = paper_data['option_id']
        
        for size, price in paper_data['prices'].items():
            # Skip null prices
            if price is None:
                continue
                
            clean_size = size.replace('"', '').replace('×', 'x')
            name = f"Fine Art Paper {paper_data['name']} {clean_size}"
            options = json.dumps({'paper_type': paper_type_id})
            
            cursor.execute('''
                INSERT INTO products (name, product_type_id, category_id, size, cost_price, 
                                    lumaprints_subcategory_id, lumaprints_options)
                VALUES (?, 3, ?, ?, ?, ?, ?)
            ''', (name, category_id, clean_size, price, LUMAPRINTS_CODES['fine_art_paper'], options))
            product_count += 1
        
        category_id += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {product_count} Fine Art Paper products")

def import_framed_fine_art():
    """Import Framed Fine Art Paper products."""
    print("\n📦 Importing Framed Fine Art Paper products...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create categories for each frame size
    frame_sizes = [
        ('0.875"x0.875"', '0875', '0.875'),
        ('1.25"x0.875"', '125', '1.25'),
        ('2"x1.0625"', '2x1', '2x1')
    ]
    
    category_id = 15
    for frame_display, file_code, api_code in frame_sizes:
        cursor.execute('''
            INSERT INTO categories (id, name, product_type_id, display_order)
            VALUES (?, ?, 4, ?)
        ''', (category_id, f"Framed Fine Art - {frame_display} Frame", category_id))
        category_id += 1
    
    # Import each frame size
    product_count = 0
    category_id = 15
    
    for frame_display, file_code, api_code in frame_sizes:
        filename = f'pricing_data_framed_fine_art_{file_code}.json'
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Get mat options from data
        mat_options = data.get('mat_options', {})
        
        # Process each mat size
        for mat_key, mat_data in mat_options.items():
            mat_display = mat_data['name']
            mat_id = mat_data['mat_id']
                
            # Process each size/price
            for size, price in mat_data['prices'].items():
                # Skip null prices
                if price is None:
                    continue
                    
                clean_size = size.replace('"', '').replace('×', 'x')
                
                # Create product for each frame color and paper type
                for color_name, color_id in FRAME_COLORS.items():
                    for paper_name, paper_type_id in PAPER_TYPES.items():
                        try:
                            # Determine subcategory ID based on frame size and color
                            frame_key = f"{api_code}_{color_name.lower()}"
                            subcategory_id = LUMAPRINTS_CODES['framed_fine_art'].get(frame_key)
                            
                            if not subcategory_id:
                                print(f"⚠️  Warning: No subcategory ID for {frame_key}, skipping")
                                continue
                            
                            name = f"Framed Fine Art {frame_display} {color_name} {paper_name} {mat_display} {clean_size}"
                            options = json.dumps({
                                'frame_color': color_id,
                                'paper_type': paper_type_id,
                                'mat_size': mat_id
                            })
                            
                            cursor.execute('''
                                INSERT INTO products (name, product_type_id, category_id, size, cost_price, 
                                                    lumaprints_subcategory_id, lumaprints_options)
                                VALUES (?, 4, ?, ?, ?, ?, ?)
                            ''', (name, category_id, clean_size, price, subcategory_id, options))
                            product_count += 1
                        except Exception as e:
                            print(f"⚠️  Error importing {frame_key} {paper_name}: {e}")
                            continue
        
        category_id += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {product_count} Framed Fine Art Paper products")

def import_foam_mounted():
    """Import Foam-Mounted Fine Art products."""
    print("\n📦 Importing Foam-Mounted Fine Art products...")
    
    with open('pricing_data_foam_mounted.json', 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create categories for each paper type
    category_id = 18
    for paper_key, paper_data in data.items():
        cursor.execute('''
            INSERT INTO categories (id, name, product_type_id, display_order)
            VALUES (?, ?, 7, ?)
        ''', (category_id, f"Foam-Mounted - {paper_data['name']}", category_id))
        category_id += 1
    
    # Insert products
    product_count = 0
    category_id = 18
    for paper_key, paper_data in data.items():
        paper_type_id = paper_data['option_id']
        
        for size, price in paper_data['prices'].items():
            # Skip null prices
            if price is None:
                continue
                
            clean_size = size.replace('"', '').replace('×', 'x')
            name = f"Foam-Mounted {paper_data['name']} {clean_size}"
            options = json.dumps({'paper_type': paper_type_id})
            
            cursor.execute('''
                INSERT INTO products (name, product_type_id, category_id, size, cost_price, 
                                    lumaprints_subcategory_id, lumaprints_options)
                VALUES (?, 7, ?, ?, ?, ?, ?)
            ''', (name, category_id, clean_size, price, LUMAPRINTS_CODES['foam_mounted'], options))
            product_count += 1
        
        category_id += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {product_count} Foam-Mounted products")

def import_metal_prints():
    """Import Metal Prints products."""
    print("\n📦 Importing Metal Prints products...")
    
    with open('pricing_data_metal_prints.json', 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create category
    cursor.execute('''
        INSERT INTO categories (id, name, product_type_id, display_order)
        VALUES (25, 'Metal Prints', 5, 25)
    ''')
    
    # Insert products
    product_count = 0
    for size_data in data['sizes']:
        size = size_data['size'].replace('×', 'x')
        price = size_data['price']
        name = f"Metal Print {size}"
        
        cursor.execute('''
            INSERT INTO products (name, product_type_id, category_id, size, cost_price, 
                                lumaprints_subcategory_id, lumaprints_options)
            VALUES (?, 5, 25, ?, ?, ?, '{}')
        ''', (name, size, price, LUMAPRINTS_CODES['metal_prints']))
        product_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {product_count} Metal Prints products")

def import_peel_stick():
    """Import Peel & Stick products."""
    print("\n📦 Importing Peel & Stick products...")
    
    with open('pricing_data_peel_stick.json', 'r') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create category
    cursor.execute('''
        INSERT INTO categories (id, name, product_type_id, display_order)
        VALUES (26, 'Peel & Stick', 6, 26)
    ''')
    
    # Insert products
    product_count = 0
    for size_data in data['sizes']:
        size = size_data['size'].replace('×', 'x')
        price = size_data['price']
        name = f"Peel & Stick {size}"
        
        cursor.execute('''
            INSERT INTO products (name, product_type_id, category_id, size, cost_price, 
                                lumaprints_subcategory_id, lumaprints_options)
            VALUES (?, 6, 26, ?, ?, ?, '{}')
        ''', (name, size, price, LUMAPRINTS_CODES['peel_stick']))
        product_count += 1
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {product_count} Peel & Stick products")

def print_summary():
    """Print import summary."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM products')
    total_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM categories')
    total_categories = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM product_types')
    total_types = cursor.fetchone()[0]
    
    print("\n" + "="*60)
    print("📊 IMPORT SUMMARY")
    print("="*60)
    print(f"Product Types: {total_types}")
    print(f"Categories: {total_categories}")
    print(f"Products: {total_products}")
    print("="*60)
    
    # Show breakdown by product type
    cursor.execute('''
        SELECT pt.name, COUNT(p.id)
        FROM product_types pt
        LEFT JOIN products p ON p.product_type_id = pt.id
        GROUP BY pt.id
        ORDER BY pt.display_order
    ''')
    
    print("\nBreakdown by Product Type:")
    for type_name, count in cursor.fetchall():
        print(f"  {type_name}: {count} products")
    
    conn.close()

def main():
    """Main import process."""
    print("="*60)
    print("🚀 LUMAPRINTS PRODUCT IMPORT")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize database
    init_database()
    
    # Clear existing data
    clear_existing_data()
    
    # Insert product types
    insert_product_types()
    
    # Import all products
    import_canvas()
    import_framed_canvas()
    import_fine_art_paper()
    import_framed_fine_art()
    import_foam_mounted()
    import_metal_prints()
    import_peel_stick()
    
    # Print summary
    print_summary()
    
    print(f"\n✅ Import completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == '__main__':
    main()

