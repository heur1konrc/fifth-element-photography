#!/usr/bin/env python3
"""
Import Core Pictorem Products
Populates the database with canvas, framed, metal, and acrylic products
"""

import sqlite3
from datetime import datetime

DB_PATH = 'pictorem.db'

def get_db(db_path=None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def import_categories():
    """Import product categories"""
    conn = get_db()
    cursor = conn.cursor()
    
    categories = [
        {
            'name': 'Canvas - 0.75" Stretched',
            'slug': 'canvas-075-stretched',
            'material': 'canvas',
            'description': 'Gallery-wrapped stretched canvas with 0.75" depth',
            'display_order': 1
        },
        {
            'name': 'Canvas - 1.5" Stretched',
            'slug': 'canvas-15-stretched',
            'material': 'canvas',
            'description': 'Gallery-wrapped stretched canvas with 1.5" depth',
            'display_order': 2
        },
        {
            'name': 'Framed Fine Art Print',
            'slug': 'framed-fine-art',
            'material': 'paper',
            'description': 'Fine art paper print with professional framing',
            'display_order': 3
        },
        {
            'name': 'Metal Print - HD Chromaluxe',
            'slug': 'metal-hd',
            'material': 'metal',
            'description': 'Premium HD Chromaluxe metal print',
            'display_order': 4
        },
        {
            'name': 'Metal Print - Brushed Aluminum',
            'slug': 'metal-brushed',
            'material': 'metal',
            'description': 'Brushed aluminum metal print',
            'display_order': 5
        },
        {
            'name': 'Acrylic Print - 1/8"',
            'slug': 'acrylic-18',
            'material': 'acrylic',
            'description': 'Direct acrylic print with 1/8" thickness',
            'display_order': 6
        },
        {
            'name': 'Fine Art Paper Print',
            'slug': 'fine-art-paper',
            'material': 'paper',
            'description': 'Unframed fine art paper print',
            'display_order': 7
        }
    ]
    
    for cat in categories:
        cursor.execute('''
            INSERT INTO pictorem_categories (name, slug, material, description, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (cat['name'], cat['slug'], cat['material'], cat['description'], cat['display_order']))
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {len(categories)} categories")

def import_products():
    """Import base products"""
    conn = get_db()
    cursor = conn.cursor()
    
    products = [
        # Canvas 0.75"
        {
            'category_slug': 'canvas-075-stretched',
            'name': 'Stretched Canvas 0.75"',
            'slug': 'stretched-canvas-075',
            'material': 'canvas',
            'type': 'stretched',
            'description': 'Gallery-wrapped canvas with 0.75" depth, mirror wrap edges',
            'preorder_template': '1|canvas|stretched|{orientation}|{width}|{height}|mirrorimage|c075|regular',
            'display_order': 1
        },
        # Canvas 1.5"
        {
            'category_slug': 'canvas-15-stretched',
            'name': 'Stretched Canvas 1.5"',
            'slug': 'stretched-canvas-15',
            'material': 'canvas',
            'type': 'stretched',
            'description': 'Gallery-wrapped canvas with 1.5" depth, mirror wrap edges',
            'preorder_template': '1|canvas|stretched|{orientation}|{width}|{height}|mirrorimage|c15|regular',
            'display_order': 1
        },
        # Framed Fine Art
        {
            'category_slug': 'framed-fine-art',
            'name': 'Framed Fine Art Print',
            'slug': 'framed-fine-art-print',
            'material': 'paper',
            'type': 'art',
            'description': 'Fine art paper print with professional frame, mat, and glazing',
            'preorder_template': '1|paper|art|{orientation}|{width}|{height}|none|none|none|none|frame|{moulding}|{glazing}|{hanging}',
            'display_order': 1
        },
        # Metal HD
        {
            'category_slug': 'metal-hd',
            'name': 'HD Chromaluxe Metal Print',
            'slug': 'metal-hd-chromaluxe',
            'material': 'metal',
            'type': 'hd',
            'description': 'Premium HD Chromaluxe metal print with vibrant colors',
            'preorder_template': '1|metal|hd|{orientation}|{width}|{height}',
            'display_order': 1
        },
        # Metal Brushed
        {
            'category_slug': 'metal-brushed',
            'name': 'Brushed Aluminum Metal Print',
            'slug': 'metal-brushed-aluminum',
            'material': 'metal',
            'type': 'al',
            'description': 'Brushed aluminum metal print with modern finish',
            'preorder_template': '1|metal|al|{orientation}|{width}|{height}',
            'display_order': 1
        },
        # Acrylic
        {
            'category_slug': 'acrylic-18',
            'name': 'Acrylic Print 1/8"',
            'slug': 'acrylic-print-18',
            'material': 'acrylic',
            'type': 'da8',
            'description': 'Direct acrylic print with 1/8" thickness, stunning depth',
            'preorder_template': '1|acrylic|da8|{orientation}|{width}|{height}',
            'display_order': 1
        },
        # Fine Art Paper
        {
            'category_slug': 'fine-art-paper',
            'name': 'Fine Art Paper Print',
            'slug': 'fine-art-paper-print',
            'material': 'paper',
            'type': 'art',
            'description': 'Unframed fine art paper print',
            'preorder_template': '1|paper|art|{orientation}|{width}|{height}',
            'display_order': 1
        }
    ]
    
    for prod in products:
        # Get category ID
        cursor.execute('SELECT id FROM pictorem_categories WHERE slug = ?', (prod['category_slug'],))
        category = cursor.fetchone()
        
        if category:
            cursor.execute('''
                INSERT INTO pictorem_products 
                (category_id, name, slug, material, type, description, preorder_template, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                category['id'],
                prod['name'],
                prod['slug'],
                prod['material'],
                prod['type'],
                prod['description'],
                prod['preorder_template'],
                prod['display_order']
            ))
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {len(products)} products")

def import_standard_sizes():
    """Import standard sizes for all products"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Standard photography sizes
    standard_sizes = [
        (8, 10), (10, 8),
        (11, 14), (14, 11),
        (12, 16), (16, 12),
        (16, 20), (20, 16),
        (18, 24), (24, 18),
        (20, 24), (24, 20),
        (20, 30), (30, 20),
        (24, 30), (30, 24),
        (24, 36), (36, 24),
        (30, 40), (40, 30),
        (36, 48), (48, 36)
    ]
    
    # Get all products
    cursor.execute('SELECT id, slug FROM pictorem_products WHERE active = 1')
    products = cursor.fetchall()
    
    size_count = 0
    for product in products:
        for width, height in standard_sizes:
            orientation = 'horizontal' if width > height else 'vertical' if height > width else 'square'
            display_name = f'{width}x{height}"'
            
            try:
                cursor.execute('''
                    INSERT INTO pictorem_sizes 
                    (product_id, width, height, orientation, display_name, display_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (product['id'], width, height, orientation, display_name, size_count))
                size_count += 1
            except sqlite3.IntegrityError:
                # Size already exists for this product
                pass
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {size_count} sizes")

def import_framing_options():
    """Import framing options for framed fine art"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get framed fine art product
    cursor.execute('SELECT id FROM pictorem_products WHERE slug = ?', ('framed-fine-art-print',))
    product = cursor.fetchone()
    
    if not product:
        print("⚠️  Framed fine art product not found")
        return
    
    product_id = product['id']
    
    # Popular frame mouldings (starting with a curated selection)
    mouldings = [
        ('301-21', '301-21 Espresso Floating Frame', 1),
        ('301-22', '301-22 White Floating Frame', 2),
        ('301-29', '301-29 Black Floating Frame', 3),
        ('303-11', '303-11 Espresso Floating Frame', 4),
        ('303-12', '303-12 Natural Wood Floating Frame', 5),
        ('303-19', '303-19 Black Floating Frame', 6),
        ('317-21', '317-21 Espresso Floating Frame', 7),
        ('317-22', '317-22 White Floating Frame', 8),
        ('317-29', '317-29 Black Floating Frame', 9),
        ('317-30', '317-30 Gold Floating Frame', 10),
        ('432-12', '432 Natural Wood Thin Picture Frame', 11),
        ('432-21', '432-21 Espresso Picture Frame', 12),
        ('432-22', '432 White Thin Picture Frame', 13),
        ('432-29', '432 Black Thin Picture Frame', 14),
        ('241-21', '241-21 Espresso Picture Frame', 15),
        ('241-22', '241-22 White Picture Frame', 16),
        ('241-29', '241-29 Black Picture Frame', 17)
    ]
    
    # Mat board options
    mats = [
        ('none', 'No Mat', 1),
        ('mb01', 'Mat Board 01', 2),
        ('mb02', 'Mat Board 02', 3),
        ('mb03', 'Mat Board 03', 4),
        ('mb04', 'Mat Board 04', 5),
        ('mb05', 'Mat Board 05', 6)
    ]
    
    # Glazing options
    glazing = [
        ('plexiglass', 'Standard Plexiglass', 1),
        ('plexinonglare', 'Non-Glare Plexiglass', 2)
    ]
    
    # Hanging options
    hanging = [
        ('wire', 'Hanging Wire', 1),
        ('cleat', 'French Cleat', 2)
    ]
    
    # Insert mouldings
    for code, name, order in mouldings:
        cursor.execute('''
            INSERT INTO pictorem_product_options 
            (product_id, option_type, option_code, option_name, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, 'moulding', code, name, order))
    
    # Insert mats
    for code, name, order in mats:
        cursor.execute('''
            INSERT INTO pictorem_product_options 
            (product_id, option_type, option_code, option_name, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, 'mat', code, name, order))
    
    # Insert glazing
    for code, name, order in glazing:
        cursor.execute('''
            INSERT INTO pictorem_product_options 
            (product_id, option_type, option_code, option_name, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, 'glazing', code, name, order))
    
    # Insert hanging
    for code, name, order in hanging:
        cursor.execute('''
            INSERT INTO pictorem_product_options 
            (product_id, option_type, option_code, option_name, display_order)
            VALUES (?, ?, ?, ?, ?)
        ''', (product_id, 'hanging', code, name, order))
    
    conn.commit()
    conn.close()
    
    total_options = len(mouldings) + len(mats) + len(glazing) + len(hanging)
    print(f"✅ Imported {total_options} framing options")
    print(f"   - {len(mouldings)} mouldings")
    print(f"   - {len(mats)} mat boards")
    print(f"   - {len(glazing)} glazing options")
    print(f"   - {len(hanging)} hanging options")

def verify_import():
    """Verify the import was successful"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM pictorem_categories WHERE active = 1')
    cat_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM pictorem_products WHERE active = 1')
    prod_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM pictorem_sizes WHERE active = 1')
    size_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM pictorem_product_options WHERE active = 1')
    option_count = cursor.fetchone()['count']
    
    conn.close()
    
    print("\n" + "="*60)
    print("DATABASE IMPORT SUMMARY")
    print("="*60)
    print(f"Categories:       {cat_count}")
    print(f"Products:         {prod_count}")
    print(f"Sizes:            {size_count}")
    print(f"Product Options:  {option_count}")
    print("="*60)

def populate_database(db_path=None):
    """Main function to populate database with all products"""
    global DB_PATH
    if db_path:
        DB_PATH = db_path
    
    print("Starting Pictorem product import...")
    print(f"Database: {DB_PATH}")
    print()
    
    import_categories()
    import_products()
    import_standard_sizes()
    import_framing_options()
    
    print()
    verify_import()
    print()
    print("✅ Import complete!")

if __name__ == '__main__':
    populate_database()

