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

category = "Peel and Stick"
subcategory_id = 17

sizes_prices = [
    ("4x6", 3.79),
    ("8x10", 4.30),
    ("8x12", 4.43),
    ("10x20", 7.08),
    ("10x30", 8.48),
    ("11x14", 6.44),
    ("12x12", 6.30),
    ("12x16", 6.96),
    ("12x18", 7.31),
    ("16x20", 8.76),
    ("16x24", 9.64),
    ("16x48", 17.51),
    ("18x24", 10.32),
    ("20x20", 9.87),
    ("20x40", 18.48),
    ("20x60", 25.58),
    ("24x30", 17.07),
    ("24x36", 19.61),
    ("30x30", 20.25),
    ("30x40", 25.58),
    ("30x60", 34.59),
    ("32x48", 31.17),
    ("36x48", 33.86),
    ("36x72", 34.82),
    ("40x40", 32.06),
    ("40x60", 40.26),
]

products_added = 0

for size, price in sizes_prices:
    product_name = f'{category} {size}"'
    
    cur.execute("""
        INSERT INTO products (name, category, size, price, lumaprints_subcategory_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (product_name, category, size, price, subcategory_id))
    
    products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} Peel and Stick products")
