import os
import sys
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

category = "Framed Fine Art Paper"
subcategory_id = 19

sizes_prices = [
    ("5x7", 17.34),
    ("6x6", 17.38),
    ("8x10", 20.80),
    ("8x12", 22.00),
    ("8x16", 24.38),
    ("8x24", 29.55),
    ("8x36", 37.92),
    ("8x8", 19.61),
    ("9x12", 22.75),
    ("10x10", 22.15),
    ("10x20", 29.22),
    ("10x30", 37.08),
    ("10x40", 44.93),
    ("11x14", 25.66),
    ("11x17", 27.95),
    ("12x12", 24.99),
    ("12x16", 28.17),
    ("12x18", 29.93),
    ("12x20", 31.68),
    ("12x24", 35.17),
    ("12x36", 45.66),
    ("14x14", 28.36),
    ("14x18", 32.20),
    ("16x16", 32.37),
    ("16x20", 36.58),
    ("16x24", 40.78),
    ("16x32", 49.18),
    ("16x36", 53.39),
    ("18x18", 36.76),
    ("18x24", 43.59),
    ("18x36", 57.24),
    ("20x20", 41.48),
    ("20x24", 46.39),
    ("20x30", 53.75),
    ("20x36", 61.12),
    ("20x40", 66.02),
    ("22x28", 54.46),
    ("24x24", 52.01),
    ("24x30", 60.43),
    ("24x36", 68.84),
    ("24x40", 74.46),
    ("30x30", 70.43),
    ("30x40", 87.12),
    ("30x60", 120.47),
    ("30x46", 94.29),
    ("32x32", 77.28),
    ("32x48", 105.37),
    ("36x48", 115.23),
    ("40x60", 150.37),
]

frames = [
    ("Black", 39),
    ("White", 40),
    ("Oak", 41),
]

products_added = 0

for frame_name, option_id in frames:
    for size, price in sizes_prices:
        product_name = f'{category} {size}" - 1.25x0.875" {frame_name} Frame'
        
        cur.execute("""
            INSERT INTO products (name, category, size, price, lumaprints_subcategory_id, lumaprints_frame_option_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (product_name, category, size, price, subcategory_id, option_id))
        
        products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} Framed Fine Art Paper 1.25x0.875\" products")
