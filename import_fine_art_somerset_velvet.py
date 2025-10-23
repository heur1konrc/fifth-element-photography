import os
import sys
import sqlite3

# Database connection
DB_PATH = '/data/lumaprints_pricing.db'
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Fine Art Paper - Somerset Velvet
# Subcategory ID: 14

sizes_prices = [
    # From first screenshot
    ("4x6", 3.02),
    ("5x7", 3.45),
    ("6x6", 3.48),
    ("8.5x11", 5.55),
    ("8x10", 5.09),
    ("8x12", 5.66),
    ("8x16", 6.80),
    ("8x24", 9.10),
    ("8x36", 12.54),
    ("8x48", 15.98),
    ("8x8", 4.51),
    ("9x12", 6.07),
    ("10x10", 5.78),
    ("10x20", 9.22),
    ("10x30", 12.66),
    ("10x40", 16.08),
    ("10x60", 22.96),
    ("11x14", 7.61),
    ("11x17", 8.73),
    ("12x12", 7.26),
    ("12x16", 8.86),
    ("12x18", 9.68),
    ("12x20", 10.48),
    ("12x24", 12.08),
    ("12x36", 16.89),
    ("12x48", 21.70),
    ("12x60", 26.52),
    ("14x14", 8.98),
    ("14x18", 10.82),
    ("16x16", 10.94),
    ("16x20", 12.99),
    ("16x24", 15.06),
    ("16x32", 19.16),
    ("16x36", 21.24),
    ("16x48", 27.44),
    ("16x60", 33.62),
    ("16x72", 39.80),
    # From second screenshot
    ("18x18", 13.10),
    ("18x24", 16.54),
    ("18x36", 23.42),
    ("18x48", 30.30),
    ("18x60", 37.18),
    ("18x72", 44.04),
    ("20x20", 15.51),
    ("20x24", 18.04),
    ("20x30", 21.82),
    ("20x36", 25.60),
    ("20x40", 28.12),
    ("20x60", 40.72),
    ("20x72", 48.28),
    ("22x28", 22.28),
    ("24x24", 21.01),
    ("24x30", 25.49),
    ("24x36", 29.96),
    ("24x40", 32.94),
    ("24x48", 38.89),
    ("24x60", 47.83),
    ("24x72", 56.76),
    ("30x30", 30.99),
    ("30x40", 40.16),
    ("30x60", 58.49),
    ("30x72", 69.48),
    ("32x32", 34.76),
    ("32x48", 50.35),
    ("36x36", 43.02),
    ("36x48", 56.08),
    ("36x72", 82.20),
    ("40x40", 52.18),
    ("40x60", 76.24),
]

category = "Fine Art Paper"
subcategory_id = 14
product_type = "Somerset Velvet"

products_added = 0

for size, price in sizes_prices:
    product_name = f'{category} {size}" - {product_type}'
    
    cur.execute("""
        INSERT INTO products (name, category, size, price, lumaprints_subcategory_id)
        VALUES (?, ?, ?, ?, ?)
    """, (product_name, category, size, price, subcategory_id))
    
    products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} Fine Art Paper Somerset Velvet products")
