"""
Admin route to rebuild Lumaprints database from pricing JSON files
"""
import sqlite3
import json
import os
from flask import jsonify
import traceback

# Use absolute path for Railway persistent volume
DB_PATH = '/data/lumaprints_pricing.db'

# Lumaprints product codes
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

def rebuild_database_route():
    """Rebuild the entire Lumaprints database from JSON files"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Drop existing tables
        cursor.execute('DROP TABLE IF EXISTS products')
        cursor.execute('DROP TABLE IF EXISTS categories')
        cursor.execute('DROP TABLE IF EXISTS product_types')
        
        # Create categories table
        cursor.execute('''
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create products table
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                size TEXT NOT NULL,
                price REAL NOT NULL,
                cost_price REAL NOT NULL,
                lumaprints_subcategory_id INTEGER,
                lumaprints_frame_option INTEGER,
                lumaprints_options TEXT,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id),
                UNIQUE(category_id, name, size)
            )
        ''')
        
        # Create settings table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Set default markup if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value) 
            VALUES ('global_markup_percentage', '50.0')
        ''')
        
        conn.commit()
        
        # Import all product categories
        stats = {
            'categories': 0,
            'products': 0
        }
        
        # 1. Import Canvas products
        stats = import_canvas(conn, stats)
        
        # 2. Import Framed Canvas products
        stats = import_framed_canvas(conn, stats)
        
        # 3. Import Fine Art Paper products
        stats = import_fine_art_paper(conn, stats)
        
        # 4. Import Foam Mounted products
        stats = import_foam_mounted(conn, stats)
        
        # 5. Import Framed Fine Art products
        stats = import_framed_fine_art(conn, stats)
        
        # 6. Import Metal Prints
        stats = import_metal_prints(conn, stats)
        
        # 7. Import Peel & Stick
        stats = import_peel_stick(conn, stats)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Database rebuilt successfully',
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Database rebuild failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

def get_or_create_category(conn, name, description=''):
    """Get or create a category and return its ID"""
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM categories WHERE name = ?', (name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
        return cursor.lastrowid

def import_canvas(conn, stats):
    """Import Canvas products from JSON"""
    try:
        with open('pricing_data_canvas.json', 'r') as f:
            data = json.load(f)
        
        cursor = conn.cursor()
        
        # Canvas categories
        canvas_categories = {
            'rolled': ('Canvas - Rolled', 101000),
            '0.75': ('Canvas - 0.75" Stretched', 101001),
            '1.25': ('Canvas - 1.25" Stretched', 101002),
            '1.5': ('Canvas - 1.5" Stretched', 101003)
        }
        
        for depth_key, depth_data in data.items():
            if depth_key not in canvas_categories:
                continue
                
            cat_name, subcategory_id = canvas_categories[depth_key]
            category_id = get_or_create_category(conn, cat_name, f'Canvas prints - {depth_data["name"]}')
            stats['categories'] += 1
            
            for size, price in depth_data['prices'].items():
                if price is None:
                    continue
                    
                clean_size = size.replace('"', '').replace('×', '×')
                name = f"Canvas {depth_data['name']}"
                
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (category_id, name, size, price, cost_price, lumaprints_subcategory_id, lumaprints_options)
                    VALUES (?, ?, ?, ?, ?, ?, '{}')
                ''', (category_id, name, clean_size, price, price, subcategory_id))
                stats['products'] += 1
        
        conn.commit()
        return stats
        
    except Exception as e:
        print(f"Error importing canvas: {e}")
        return stats

def import_framed_canvas(conn, stats):
    """Import Framed Canvas products from JSON"""
    try:
        with open('pricing_data_framed_canvas.json', 'r') as f:
            data = json.load(f)
        
        cursor = conn.cursor()
        
        framed_categories = {
            '0.75': ('Framed Canvas - 0.75"', 102001),
            '1.25': ('Framed Canvas - 1.25"', 102002),
            '1.5': ('Framed Canvas - 1.5"', 102003)
        }
        
        for depth_key, depth_data in data.items():
            if depth_key not in framed_categories:
                continue
                
            cat_name, subcategory_id = framed_categories[depth_key]
            category_id = get_or_create_category(conn, cat_name, f'Framed canvas - {depth_data["name"]}')
            stats['categories'] += 1
            
            for size, price in depth_data['prices'].items():
                if price is None:
                    continue
                    
                clean_size = size.replace('"', '').replace('×', '×')
                
                # Create product for each frame color
                for color_name, color_id in FRAME_COLORS.items():
                    name = f"Framed Canvas {depth_data['name']} - {color_name}"
                    options = json.dumps({'frame_color': color_id})
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO products 
                        (category_id, name, size, price, cost_price, lumaprints_subcategory_id, 
                         lumaprints_frame_option, lumaprints_options)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (category_id, name, clean_size, price, price, subcategory_id, color_id, options))
                    stats['products'] += 1
        
        conn.commit()
        return stats
        
    except Exception as e:
        print(f"Error importing framed canvas: {e}")
        return stats

def import_fine_art_paper(conn, stats):
    """Import Fine Art Paper products from JSON"""
    try:
        with open('pricing_data_fine_art_paper.json', 'r') as f:
            data = json.load(f)
        
        cursor = conn.cursor()
        
        for paper_key, paper_data in data.items():
            cat_name = f"Fine Art Paper - {paper_data['name']}"
            category_id = get_or_create_category(conn, cat_name, f'Fine art paper - {paper_data["name"]}')
            stats['categories'] += 1
            
            paper_type_id = paper_data['option_id']
            
            for size, price in paper_data['prices'].items():
                if price is None:
                    continue
                    
                clean_size = size.replace('"', '').replace('×', '×')
                name = f"Fine Art Paper {clean_size} - {paper_data['name']}"
                options = json.dumps({'paper_type': paper_type_id})
                
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (category_id, name, size, price, cost_price, lumaprints_subcategory_id, lumaprints_options)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (category_id, name, clean_size, price, price, 103001, options))
                stats['products'] += 1
        
        conn.commit()
        return stats
        
    except Exception as e:
        print(f"Error importing fine art paper: {e}")
        return stats

def import_foam_mounted(conn, stats):
    """Import Foam Mounted products from JSON"""
    try:
        with open('pricing_data_foam_mounted.json', 'r') as f:
            data = json.load(f)
        
        cursor = conn.cursor()
        
        for paper_key, paper_data in data.items():
            cat_name = f"Foam Mounted - {paper_data['name']}"
            category_id = get_or_create_category(conn, cat_name, f'Foam mounted - {paper_data["name"]}')
            stats['categories'] += 1
            
            paper_type_id = paper_data['option_id']
            
            for size, price in paper_data['prices'].items():
                if price is None:
                    continue
                    
                clean_size = size.replace('"', '').replace('×', '×')
                name = f"Foam Mounted {clean_size} - {paper_data['name']}"
                options = json.dumps({'paper_type': paper_type_id})
                
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (category_id, name, size, price, cost_price, lumaprints_subcategory_id, lumaprints_options)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (category_id, name, clean_size, price, price, 104001, options))
                stats['products'] += 1
        
        conn.commit()
        return stats
        
    except Exception as e:
        print(f"Error importing foam mounted: {e}")
        return stats

def import_framed_fine_art(conn, stats):
    """Import Framed Fine Art products from JSON files"""
    try:
        cursor = conn.cursor()
        
        # Import 0.875" frame
        with open('pricing_data_framed_fine_art_0875.json', 'r') as f:
            data_0875 = json.load(f)
        
        cat_name = "Framed Fine Art - 0.875\" Frame"
        category_id = get_or_create_category(conn, cat_name, 'Framed fine art with 0.875" frame')
        stats['categories'] += 1
        
        for frame_key, frame_data in data_0875.items():
            frame_color = frame_data['name'].split()[-1]  # Extract color
            color_id = FRAME_COLORS.get(frame_color, 12)
            subcategory_id = frame_data['subcategory_id']
            
            for paper_key, paper_data in frame_data['papers'].items():
                paper_type_id = paper_data['option_id']
                
                for size, price in paper_data['prices'].items():
                    if price is None:
                        continue
                        
                    clean_size = size.replace('"', '').replace('×', '×')
                    name = f"Framed Fine Art 0.875\" {clean_size} - {frame_color} - {paper_data['name']}"
                    options = json.dumps({'frame_color': color_id, 'paper_type': paper_type_id})
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO products 
                        (category_id, name, size, price, cost_price, lumaprints_subcategory_id, 
                         lumaprints_frame_option, lumaprints_options)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (category_id, name, clean_size, price, price, subcategory_id, color_id, options))
                    stats['products'] += 1
        
        # Import 1.25" frame
        with open('pricing_data_framed_fine_art_125.json', 'r') as f:
            data_125 = json.load(f)
        
        cat_name = "Framed Fine Art - 1.25\" Frame"
        category_id = get_or_create_category(conn, cat_name, 'Framed fine art with 1.25" frame')
        stats['categories'] += 1
        
        for frame_key, frame_data in data_125.items():
            frame_color = frame_data['name'].split()[-1]
            color_id = FRAME_COLORS.get(frame_color, 12)
            subcategory_id = frame_data['subcategory_id']
            
            for paper_key, paper_data in frame_data['papers'].items():
                paper_type_id = paper_data['option_id']
                
                for size, price in paper_data['prices'].items():
                    if price is None:
                        continue
                        
                    clean_size = size.replace('"', '').replace('×', '×')
                    name = f"Framed Fine Art 1.25\" {clean_size} - {frame_color} - {paper_data['name']}"
                    options = json.dumps({'frame_color': color_id, 'paper_type': paper_type_id})
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO products 
                        (category_id, name, size, price, cost_price, lumaprints_subcategory_id, 
                         lumaprints_frame_option, lumaprints_options)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (category_id, name, clean_size, price, price, subcategory_id, color_id, options))
                    stats['products'] += 1
        
        conn.commit()
        return stats
        
    except Exception as e:
        print(f"Error importing framed fine art: {e}")
        return stats

def import_metal_prints(conn, stats):
    """Import Metal Prints from JSON"""
    try:
        with open('pricing_data_metal_prints.json', 'r') as f:
            data = json.load(f)
        
        cursor = conn.cursor()
        
        cat_name = "Metal Prints"
        category_id = get_or_create_category(conn, cat_name, 'Metal prints')
        stats['categories'] += 1
        
        for size, price in data['prices'].items():
            if price is None:
                continue
                
            clean_size = size.replace('"', '').replace('×', '×')
            name = f"Metal Print {clean_size}"
            
            cursor.execute('''
                INSERT OR REPLACE INTO products 
                (category_id, name, size, price, cost_price, lumaprints_subcategory_id, lumaprints_options)
                VALUES (?, ?, ?, ?, ?, ?, '{}')
            ''', (category_id, name, clean_size, price, price, 106001))
            stats['products'] += 1
        
        conn.commit()
        return stats
        
    except Exception as e:
        print(f"Error importing metal prints: {e}")
        return stats

def import_peel_stick(conn, stats):
    """Import Peel & Stick from JSON"""
    try:
        with open('pricing_data_peel_stick.json', 'r') as f:
            data = json.load(f)
        
        cursor = conn.cursor()
        
        cat_name = "Peel & Stick"
        category_id = get_or_create_category(conn, cat_name, 'Peel and stick wall decals')
        stats['categories'] += 1
        
        for size, price in data['prices'].items():
            if price is None:
                continue
                
            clean_size = size.replace('"', '').replace('×', '×')
            name = f"Peel & Stick {clean_size}"
            
            cursor.execute('''
                INSERT OR REPLACE INTO products 
                (category_id, name, size, price, cost_price, lumaprints_subcategory_id, lumaprints_options)
                VALUES (?, ?, ?, ?, ?, ?, '{}')
            ''', (category_id, name, clean_size, price, price, 107001))
            stats['products'] += 1
        
        conn.commit()
        return stats
        
    except Exception as e:
        print(f"Error importing peel & stick: {e}")
        return stats

