#!/usr/bin/env python3
"""
Import Lumaprints Products with Real Pricing from API
This script queries the Lumaprints API to get exact pricing for all products
"""

import sqlite3
import json
from lumaprints_api import get_lumaprints_client

# Common print sizes (width x height in inches)
COMMON_SIZES = [
    (5, 7), (6, 6), (8, 8), (8, 10), (8, 12),
    (10, 10), (10, 20), (10, 30),
    (11, 14), (11, 17),
    (12, 12), (12, 16), (12, 18), (12, 24), (12, 36),
    (16, 16), (16, 20), (16, 24),
    (18, 24),
    (20, 20), (20, 30), (20, 40), (20, 60),
    (24, 24), (24, 30), (24, 32), (24, 36),
    (30, 30), (30, 40), (30, 60),
    (32, 48),
    (36, 48),
    (40, 40), (40, 60),
    (45, 60)
]

# Lumaprints subcategory IDs
SUBCATEGORIES = {
    # Canvas Prints
    'canvas_075': 101001,
    'canvas_125': 101002,
    'canvas_150': 101003,
    
    # Framed Canvas
    'framed_canvas_075': 102001,
    'framed_canvas_125': 102002,
    'framed_canvas_150': 102003,
    
    # Framed Fine Art
    'framed_fine_art_0875_black': 105001,
    'framed_fine_art_0875_white': 105002,
    'framed_fine_art_0875_oak': 105003,
    'framed_fine_art_125_black': 105005,
    'framed_fine_art_125_white': 105006,
    'framed_fine_art_125_oak': 105007,
}

# Lumaprints option IDs
OPTIONS = {
    # Mat sizes
    'mat_none': 64,
    'mat_15': 66,
    'mat_20': 67,
    'mat_25': 68,
    'mat_30': 69,
    
    # Paper types
    'paper_archival_matte': 27,
    'paper_hot_press': 28,
    'paper_cold_press': 29,
    'paper_semi_gloss': 30,
    'paper_metallic': 31,
    'paper_glossy': 32,
    'paper_somerset_velvet': 33,
    'paper_canvas': 34,
    
    # Frame colors
    'frame_black': 12,
    'frame_white': 13,
    'frame_oak': 91,
}

def init_database():
    """Initialize database with new schema (Lumaprints codes only)"""
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    # Create new products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products_new (
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
    
    conn.commit()
    conn.close()
    print("✅ Database schema initialized")

def format_size(width, height):
    """Format size as string (e.g., '8×10\"')"""
    return f'{width}×{height}"'

def import_canvas_products(api_client):
    """Import Canvas print products (3 depths)"""
    products = []
    
    for depth_name, subcategory_id in [
        ('0.75"', SUBCATEGORIES['canvas_075']),
        ('1.25"', SUBCATEGORIES['canvas_125']),
        ('1.5"', SUBCATEGORIES['canvas_150'])
    ]:
        print(f"\n📦 Importing Canvas {depth_name} products...")
        
        for width, height in COMMON_SIZES:
            try:
                # Get pricing from Lumaprints API
                pricing = api_client.get_pricing(
                    subcategory_id=subcategory_id,
                    width=width,
                    height=height,
                    quantity=1
                )
                
                if 'price' in pricing:
                    cost_price = float(pricing['price'])
                    size_str = format_size(width, height)
                    
                    product = {
                        'name': f'Canvas {depth_name} {size_str}',
                        'product_type_id': 1,
                        'category_id': get_canvas_category_id(depth_name),
                        'size': size_str,
                        'cost_price': cost_price,
                        'lumaprints_subcategory_id': subcategory_id,
                        'lumaprints_options': None
                    }
                    products.append(product)
                    print(f"  ✓ {size_str}: ${cost_price}")
                    
            except Exception as e:
                print(f"  ✗ {format_size(width, height)}: {e}")
    
    return products

def import_framed_canvas_products(api_client):
    """Import Framed Canvas products (3 depths × 3 colors)"""
    products = []
    
    for depth_name, subcategory_id in [
        ('0.75"', SUBCATEGORIES['framed_canvas_075']),
        ('1.25"', SUBCATEGORIES['framed_canvas_125']),
        ('1.5"', SUBCATEGORIES['framed_canvas_150'])
    ]:
        for color_name, color_option in [
            ('Black', OPTIONS['frame_black']),
            ('White', OPTIONS['frame_white']),
            ('Oak', OPTIONS['frame_oak'])
        ]:
            print(f"\n📦 Importing Framed Canvas {depth_name} {color_name}...")
            
            for width, height in COMMON_SIZES:
                try:
                    pricing = api_client.get_pricing(
                        subcategory_id=subcategory_id,
                        width=width,
                        height=height,
                        quantity=1,
                        options=[color_option]
                    )
                    
                    if 'price' in pricing:
                        cost_price = float(pricing['price'])
                        size_str = format_size(width, height)
                        
                        product = {
                            'name': f'Framed Canvas {depth_name} {color_name} {size_str}',
                            'product_type_id': 2,
                            'category_id': get_framed_canvas_category_id(depth_name),
                            'size': size_str,
                            'cost_price': cost_price,
                            'lumaprints_subcategory_id': subcategory_id,
                            'lumaprints_options': json.dumps({'frame_color': color_option})
                        }
                        products.append(product)
                        print(f"  ✓ {size_str}: ${cost_price}")
                        
                except Exception as e:
                    print(f"  ✗ {format_size(width, height)}: {e}")
    
    return products

def import_framed_fine_art_products(api_client):
    """Import Framed Fine Art products (frame sizes × mat sizes × paper types)"""
    products = []
    
    # Frame sizes
    frames = [
        ('0.875" Black', SUBCATEGORIES['framed_fine_art_0875_black']),
        ('0.875" White', SUBCATEGORIES['framed_fine_art_0875_white']),
        ('0.875" Oak', SUBCATEGORIES['framed_fine_art_0875_oak']),
        ('1.25" Black', SUBCATEGORIES['framed_fine_art_125_black']),
        ('1.25" White', SUBCATEGORIES['framed_fine_art_125_white']),
        ('1.25" Oak', SUBCATEGORIES['framed_fine_art_125_oak']),
    ]
    
    # Mat sizes
    mats = [
        ('No Mat', OPTIONS['mat_none']),
        ('1.5" Mat', OPTIONS['mat_15']),
        ('2.0" Mat', OPTIONS['mat_20']),
        ('2.5" Mat', OPTIONS['mat_25']),
        ('3.0" Mat', OPTIONS['mat_30']),
    ]
    
    # Paper types
    papers = [
        ('Archival Matte', OPTIONS['paper_archival_matte']),
        ('Hot Press', OPTIONS['paper_hot_press']),
        ('Cold Press', OPTIONS['paper_cold_press']),
        ('Semi-Gloss', OPTIONS['paper_semi_gloss']),
        ('Metallic', OPTIONS['paper_metallic']),
        ('Glossy', OPTIONS['paper_glossy']),
        ('Somerset Velvet', OPTIONS['paper_somerset_velvet']),
    ]
    
    for frame_name, frame_id in frames:
        for mat_name, mat_id in mats:
            for paper_name, paper_id in papers:
                print(f"\n📦 Importing Framed Fine Art {frame_name} / {mat_name} / {paper_name}...")
                
                for width, height in COMMON_SIZES:
                    try:
                        pricing = api_client.get_pricing(
                            subcategory_id=frame_id,
                            width=width,
                            height=height,
                            quantity=1,
                            options=[mat_id, paper_id]
                        )
                        
                        if 'price' in pricing:
                            cost_price = float(pricing['price'])
                            size_str = format_size(width, height)
                            
                            product = {
                                'name': f'Framed Fine Art {frame_name} {mat_name} {paper_name} {size_str}',
                                'product_type_id': 4,
                                'category_id': get_framed_fine_art_category_id(frame_name),
                                'size': size_str,
                                'cost_price': cost_price,
                                'lumaprints_subcategory_id': frame_id,
                                'lumaprints_options': json.dumps({
                                    'mat_size': mat_id,
                                    'paper_type': paper_id
                                })
                            }
                            products.append(product)
                            print(f"  ✓ {size_str}: ${cost_price}")
                            
                    except Exception as e:
                        # Skip sizes that aren't available
                        pass
    
    return products

def get_canvas_category_id(depth):
    """Get category ID for Canvas products"""
    mapping = {
        '0.75"': 1,
        '1.25"': 2,
        '1.5"': 3
    }
    return mapping.get(depth, 1)

def get_framed_canvas_category_id(depth):
    """Get category ID for Framed Canvas products"""
    mapping = {
        '0.75"': 5,
        '1.25"': 6,
        '1.5"': 7
    }
    return mapping.get(depth, 5)

def get_framed_fine_art_category_id(frame):
    """Get category ID for Framed Fine Art products"""
    if '0.875"' in frame:
        return 15
    elif '1.25"' in frame:
        return 16
    return 15

def save_products_to_database(products):
    """Save products to database"""
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    for product in products:
        cursor.execute('''
            INSERT INTO products_new 
            (name, product_type_id, category_id, size, cost_price, 
             lumaprints_subcategory_id, lumaprints_options, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            product['name'],
            product['product_type_id'],
            product['category_id'],
            product['size'],
            product['cost_price'],
            product['lumaprints_subcategory_id'],
            product['lumaprints_options']
        ))
    
    conn.commit()
    conn.close()
    print(f"\n✅ Saved {len(products)} products to database")

def main():
    """Main import process"""
    print("🚀 Starting Lumaprints Product Import with Real Pricing\n")
    
    # Initialize API client
    api_client = get_lumaprints_client(sandbox=False)
    print("✅ Connected to Lumaprints API\n")
    
    # Initialize database
    init_database()
    
    all_products = []
    
    # Import Canvas products
    print("\n" + "="*60)
    print("CANVAS PRINTS")
    print("="*60)
    canvas_products = import_canvas_products(api_client)
    all_products.extend(canvas_products)
    print(f"\n✅ Imported {len(canvas_products)} Canvas products")
    
    # Import Framed Canvas products
    print("\n" + "="*60)
    print("FRAMED CANVAS PRINTS")
    print("="*60)
    framed_canvas_products = import_framed_canvas_products(api_client)
    all_products.extend(framed_canvas_products)
    print(f"\n✅ Imported {len(framed_canvas_products)} Framed Canvas products")
    
    # Import Framed Fine Art products
    print("\n" + "="*60)
    print("FRAMED FINE ART PAPER")
    print("="*60)
    framed_fine_art_products = import_framed_fine_art_products(api_client)
    all_products.extend(framed_fine_art_products)
    print(f"\n✅ Imported {len(framed_fine_art_products)} Framed Fine Art products")
    
    # Save all products
    save_products_to_database(all_products)
    
    print("\n" + "="*60)
    print(f"✅ IMPORT COMPLETE: {len(all_products)} total products")
    print("="*60)

if __name__ == '__main__':
    main()

