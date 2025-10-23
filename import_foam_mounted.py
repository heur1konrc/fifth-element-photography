import os
import sys
import sqlite3
import json

# Database connection
DB_PATH = '/data/lumaprints_pricing.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Load pricing data
with open('pricing_data_foam_mounted.json', 'r') as f:
    foam_data = json.load(f)

category = "Foam-Mounted"
subcategory_id = 15  # Foam-Mounted Fine Art Paper

# Map JSON keys to product types and option IDs
foam_types = [
    ("archival_matte", "Archival Matte", 27),
    ("hot_press", "Hot Press", 28),
    ("cold_press", "Cold Press", 29),
    ("semi_gloss", "Semi-Glossy", 30),
    ("metallic", "Metallic", 31),
    ("glossy", "Glossy", 32),
    ("somerset_velvet", "Somerset Velvet", 33),
]

products_added = 0

for json_key, product_type, option_id in foam_types:
    prices = foam_data[json_key]['prices']
    
    for size_with_quotes, price in prices.items():
        # Remove quotes and × symbol for database storage
        size = size_with_quotes.replace('"', '').replace('×', 'x')
        
        product_name = f'{category} {size}" - {product_type}'
        
        cur.execute("""
            INSERT INTO products (name, category, size, price, lumaprints_subcategory_id, lumaprints_frame_option_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_name, category, size, price, subcategory_id, option_id))
        
        products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} Foam-Mounted products")
print(f"   - 7 paper types × ~29 sizes each")
