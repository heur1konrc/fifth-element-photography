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

category = "Metal"

# Metal Glossy White - Subcategory 16, Option 34
white_sizes_prices = [
    ("8x10", 30.57),
    ("8x12", 33.95),
    ("10x30", 79.79),
    ("11x14", 46.12),
    ("11x17", 53.37),
    ("12x12", 43.94),
    ("12x18", 59.77),
    ("12x16", 54.38),
    ("12x24", 76.59),
    ("15x45", 153.63),
    ("16x16", 68.66),
    ("16x20", 82.46),
    ("16x24", 95.21),
    ("18x24", 104.53),
    ("20x20", 98.15),
    ("20x24", 113.84),
    ("20x30", 137.37),
    ("20x40", 176.58),
    ("20x60", 255.01),
    ("24x30", 160.39),
    ("24x36", 188.32),
    ("24x24", 132.45),
    ("24x48", 244.19),
    ("30x30", 194.93),
    ("30x40", 252.50),
    ("30x60", 367.64),
    ("32x48", 367.64),
    ("36x36", 270.62),
    ("36x48", 352.92),
    ("40x60", 480.27),
]

# Metal Glossy Silver - Subcategory 16, Option 35
silver_sizes_prices = [
    ("8x10", 30.57),
    ("8x12", 33.95),
    ("10x30", 79.79),
    ("11x14", 46.12),
    ("11x17", 53.37),
    ("12x12", 43.94),
    ("12x18", 59.77),
    ("16x16", 68.66),
    ("16x20", 82.46),
    ("16x24", 95.21),
    ("20x20", 98.15),
    ("20x24", 113.84),
    ("20x30", 137.37),
    ("24x30", 160.39),
    ("24x36", 188.32),
]

subcategory_id = 16
products_added = 0

# Import White Metal
for size, price in white_sizes_prices:
    product_name = f'{category} {size}" - Glossy White'
    cur.execute("""
        INSERT INTO products (name, category, size, price, lumaprints_subcategory_id, lumaprints_frame_option_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (product_name, category, size, price, subcategory_id, 34))
    products_added += 1

# Import Silver Metal
for size, price in silver_sizes_prices:
    product_name = f'{category} {size}" - Glossy Silver'
    cur.execute("""
        INSERT INTO products (name, category, size, price, lumaprints_subcategory_id, lumaprints_frame_option_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (product_name, category, size, price, subcategory_id, 35))
    products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} Metal products")
print(f"   - Glossy White: {len(white_sizes_prices)} sizes")
print(f"   - Glossy Silver: {len(silver_sizes_prices)} sizes")
