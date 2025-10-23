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
subcategory_id = 22
option_id = 47

sizes_prices = [
    ("5x7", 27.12),
    ("6x6", 27.15),
    ("8x10", 35.46),
    ("8x12", 38.28),
    ("8x16", 43.92),
    ("8x24", 55.60),
    ("8x36", 73.75),
    ("8x8", 32.64),
    ("9x12", 39.84),
    ("10x10", 38.43),
    ("10x20", 53.63),
    ("10x30", 69.63),
    ("10x40", 85.63),
    ("11x14", 46.02),
    ("11x17", 50.75),
    ("12x12", 44.54),
    ("12x16", 50.97),
    ("12x18", 54.34),
    ("12x20", 57.73),
    ("12x24", 64.48),
    ("12x36", 84.72),
    ("14x14", 51.15),
    ("14x18", 58.25),
    ("16x16", 58.43),
    ("16x20", 65.88),
    ("16x24", 73.34),
    ("16x32", 88.26),
    ("16x36", 95.71),
    ("18x18", 66.06),
    ("18x24", 77.77),
    ("18x36", 101.20),
    ("20x20", 74.04),
    ("20x24", 82.21),
    ("20x30", 94.45),
    ("20x36", 106.70),
    ("20x40", 114.86),
    ("22x28", 95.16),
    ("24x24", 91.08),
    ("24x30", 104.39),
    ("24x36", 117.68),
    ("24x40", 126.56),
    ("30x30", 119.27),
    ("30x40", 144.09),
    ("30x60", 193.74),
    ("32x32", 129.38),
    ("32x48", 170.50),
    ("36x48", 183.60),
    ("40x60", 231.78),
]

products_added = 0

for size, price in sizes_prices:
    product_name = f'{category} {size}" - 2x10.62" Framer\'s Choice Black with Gold Frame'
    
    cur.execute("""
        INSERT INTO products (name, category, size, price, lumaprints_subcategory_id, lumaprints_frame_option_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (product_name, category, size, price, subcategory_id, option_id))
    
    products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} Framed Fine Art Paper 2x10.62\" products")
