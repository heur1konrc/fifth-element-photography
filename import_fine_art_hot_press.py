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

# Fine Art Paper - Hot Press
# Subcategory ID: 9

sizes_prices = [
    # From first screenshot
    ("4x6", 2.86),
    ("5x7", 3.24),
    ("6x6", 3.27),
    ("8.5x11", 5.09),
    ("8x10", 4.68),
    ("8x12", 5.18),
    ("8x16", 6.19),
    ("8x24", 8.20),
    ("8x36", 11.24),
    ("8x48", 14.26),
    ("8x8", 4.17),
    ("9x12", 5.53),
    ("10x10", 5.28),
    ("10x20", 8.31),
    ("10x30", 11.33),
    ("10x40", 14.35),
    ("10x60", 20.41),
    ("11x14", 6.90),
    ("11x17", 7.87),
    ("12x12", 6.59),
    ("12x16", 8.01),
    ("12x18", 8.71),
    ("12x20", 9.42),
    ("12x24", 10.83),
    ("12x36", 15.06),
    ("12x48", 19.30),
    ("12x60", 23.53),
    ("14x14", 8.11),
    ("14x18", 9.71),
    ("16x16", 9.83),
    ("16x20", 11.64),
    ("16x24", 13.46),
    ("16x32", 17.09),
    ("16x36", 18.90),
    ("16x48", 24.34),
    ("16x60", 29.79),
    ("16x72", 35.23),
    # From second screenshot
    ("20x20", 13.85),
    ("20x24", 16.07),
    ("20x30", 19.39),
    ("20x36", 22.73),
    ("20x40", 24.95),
    ("20x60", 36.03),
    ("20x72", 42.69),
    ("22x28", 19.80),
    ("24x24", 18.69),
    ("24x30", 22.63),
    ("24x36", 26.55),
    ("24x40", 29.19),
    ("24x48", 34.42),
    ("24x60", 42.28),
    ("24x72", 50.15),
    ("30x30", 27.47),
    ("30x40", 35.53),
    ("30x60", 51.67),
    ("30x72", 61.35),
    ("32x32", 30.79),
    ("32x48", 44.50),
    ("36x36", 38.05),
    ("36x48", 49.54),
    ("36x72", 72.54),
    ("40x40", 46.13),
    ("40x60", 67.31),
]

category = "Fine Art Paper"
subcategory_id = 9
product_type = "Hot Press"

products_added = 0

for size, price in sizes_prices:
    product_name = f'{category} {size}" - {product_type}'
    
    cur.execute("""
        INSERT INTO products (name, category, size, price, lumaprints_subcategory_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (product_name, category, size, price, subcategory_id))
    
    products_added += 1

conn.commit()
cur.close()
conn.close()

print(f"✅ Successfully imported {products_added} Fine Art Paper Hot Press products")
