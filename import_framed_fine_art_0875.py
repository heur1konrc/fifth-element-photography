import os
import sys
import psycopg2

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

category = "Framed Fine Art Paper"
subcategory_id = 18  # 0.875x0.875 frame

# All 3 frames have same sizes/prices
sizes_prices = [
    ("5x7", 16.85),
    ("6x6", 16.90),
    ("8x10", 20.08),
    ("8x12", 21.19),
    ("8x16", 23.40),
    ("8x24", 28.25),
    ("8x36", 36.13),
    ("8x8", 18.97),
    ("9x12", 21.89),
    ("10x10", 21.34),
    ("10x20", 27.99),
    ("10x30", 35.45),
    ("11x14", 24.65),
    ("11x17", 26.82),
    ("12x12", 24.01),
    ("12x16", 27.04),
    ("12x18", 28.71),
    ("12x20", 30.37),
    ("12x24", 33.71),
    ("12x36", 43.70),
    ("14x14", 27.21),
    ("14x18", 30.90),
    ("16x16", 31.08),
    ("16x20", 35.12),
    ("16x24", 39.15),
    ("16x32", 47.24),
    ("16x36", 51.27),
    ("18x18", 35.29),
    ("18x24", 41.88),
    ("18x36", 55.06),
    ("20x20", 39.86),
    ("20x24", 44.60),
    ("20x30", 51.72),
    ("20x36", 58.84),
    ("22x28", 52.43),
    ("24x24", 50.06),
    ("24x30", 58.23),
    ("24x36", 66.40),
]

# Frame types with their option IDs
frames = [
    ("Black", 36),
    ("White", 37),
    ("Oak", 38),
]

products_added = 0

for frame_name, option_id in frames:
    for size, price in sizes_prices:
        product_name = f'{category} {size}" - 0.875" {frame_name} Frame'
        
        cur.execute("""
            INSERT INTO products (name, category, size, price, lumaprints_subcategory_id, lumaprints_frame_option_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (product_name, category, size, price, subcategory_id, option_id))
        
        products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} Framed Fine Art Paper 0.875\" products")
print(f"   - 3 frame types × {len(sizes_prices)} sizes")
