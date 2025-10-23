import os
import sys
import sqlite3

# Database connection
DB_PATH = '/data/lumaprints_pricing.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1.50" Framed Canvas - Subcategory ID 7
# 8 frame styles - all same pricing

sizes_prices = [
    ("8x10", 35.00),
    ("8x12", 39.22),
    ("10x20", 62.38),
    ("10x30", 75.34),
    ("11x14", 45.17),
    ("12x12", 50.85),
    ("12x16", 56.53),
    ("12x18", 59.04),
    ("16x20", 67.52),
    ("16x24", 74.01),
    ("16x48", 121.90),
    ("18x24", 76.75),
    ("20x20", 74.16),
    ("20x40", 103.38),
    ("20x60", 133.94),
    ("22x70", 220.72),
    ("24x30", 95.78),
    ("24x32", 98.52),
    ("24x36", 103.98),
    ("28x58", 173.86),
    ("30x30", 106.97),
    ("30x40", 121.16),
    ("30x60", 181.23),
    ("30x46", 176.47),
    ("32x48", 184.49),
    ("34x46", 184.83),
    ("36x48", 192.94),
    ("38x38", 181.68),
    ("38x58", 245.90),
    ("40x40", 189.70),
    ("40x60", 255.01),
    ("43x58", 257.88),
    ("45x60", 267.14),
    ("48x48", 247.21),
]

frame_styles = [
    ("Maple Wood", 15),
    ("Espresso", 16),
    ("Natural Wood", 17),
    ("Oak", 18),
    ("Gold", 19),
    ("Silver", 20),
    ("White", 21),
    ("Black", 22),
]

category = "Framed Canvas 1.50\""
subcategory_id = 7

products_added = 0

for frame_name, frame_option_id in frame_styles:
    for size, price in sizes_prices:
        product_name = f'{category} {size}" - {frame_name}'
        
        cur.execute("""
            INSERT INTO products (name, category, size, price, lumaprints_subcategory_id, lumaprints_frame_option_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_name, category, size, price, subcategory_id, frame_option_id))
        
        products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} products for 1.50\" Framed Canvas")
print(f"   - 8 frame styles × 35 sizes = 280 products")
