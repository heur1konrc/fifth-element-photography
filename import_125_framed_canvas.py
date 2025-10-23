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

# 1.25" Framed Canvas - Subcategory ID 6
# Frame styles: Walnut, Oak, Black (all same pricing)

sizes_prices = [
    ("8x10", 28.17),
    ("8x12", 31.62),
    ("10x20", 49.86),
    ("10x30", 58.64),
    ("11x14", 35.68),
    ("12x12", 41.29),
    ("12x16", 45.37),
    ("12x18", 47.08),
    ("16x20", 53.18),
    ("16x24", 58.07),
    ("16x48", 94.80),
    ("18x24", 60.01),
    ("20x20", 58.23),
    ("20x40", 79.48),
    ("20x60", 102.06),
    ("22x70", 170.43),
    ("24x30", 74.27),
    ("24x32", 76.20),
    ("24x36", 80.07),
    ("28x58", 133.06),
    ("30x30", 83.06),
    ("30x40", 93.27),
    ("30x60", 138.54),
    ("30x46", 136.64),
    ("32x48", 141.98),
    ("34x46", 142.32),
    ("36x48", 148.31),
    ("38x38", 141.30),
    ("38x58", 191.25),
    ("40x40", 147.19),
    ("40x60", 198.08),
    ("43x58", 200.38),
    ("45x60", 207.36),
    ("48x48", 192.56),
]

frame_styles = [
    ("Walnut", 12),
    ("Oak", 13),
    ("Black", 14),
]

category = "Framed Canvas 1.25\""
subcategory_id = 6

products_added = 0

for frame_name, frame_option_id in frame_styles:
    for size, price in sizes_prices:
        product_name = f'{category} {size}" - {frame_name}'
        
        cur.execute("""
            INSERT INTO products (name, category, size, price, lumaprints_subcategory_id, lumaprints_frame_option_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (product_name, category, size, price, subcategory_id, frame_option_id))
        
        products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} products for 1.25\" Framed Canvas")
print(f"   - 3 frame styles × 35 sizes = 105 products")
