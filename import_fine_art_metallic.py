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

# Fine Art Paper - Metallic
# Subcategory ID: 12

sizes_prices = [
    # From first screenshot
    ("4x6", 2.92),
    ("5x7", 3.61),
    ("6x6", 3.65),
    ("8.5x11", 6.97),
    ("8x10", 6.22),
    ("8x12", 7.12),
    ("8x16", 8.96),
    ("8x24", 12.63),
    ("8x36", 18.13),
    ("8x48", 23.63),
    ("8x8", 5.30),
    ("9x12", 7.78),
    ("10x10", 7.32),
    ("10x20", 12.82),
    ("10x30", 18.32),
    ("10x40", 23.82),
    ("10x60", 34.82),
    ("11x14", 10.25),
    ("11x17", 12.04),
    ("12x12", 9.70),
    ("12x16", 12.26),
    ("12x18", 13.55),
    ("12x20", 14.83),
    ("12x24", 17.40),
    ("12x36", 25.10),
    ("12x48", 32.80),
    ("12x60", 40.50),
    ("14x14", 12.45),
    ("14x18", 15.38),
    ("16x16", 15.56),
    ("16x20", 18.86),
    ("16x24", 22.16),
    ("16x32", 28.76),
    ("16x36", 32.06),
    ("16x48", 41.96),
    ("16x60", 51.86),
    ("16x72", 61.76),
    # From second screenshot
    ("18x18", 19.05),
    ("18x24", 24.55),
    ("18x36", 35.55),
    ("18x48", 46.55),
    ("18x60", 57.55),
    ("18x72", 68.55),
    ("20x20", 22.90),
    ("20x24", 26.93),
    ("20x30", 32.98),
    ("20x36", 39.04),
    ("20x40", 43.06),
    ("20x60", 63.23),
    ("20x72", 75.34),
    ("22x28", 33.72),
    ("24x24", 31.70),
    ("24x30", 38.85),
    ("24x36", 46.00),
    ("24x40", 50.76),
    ("24x48", 60.30),
    ("24x60", 74.60),
    ("24x72", 88.90),
    ("30x30", 47.65),
    ("30x40", 62.32),
    ("30x60", 91.66),
    ("30x72", 109.26),
    ("32x32", 53.70),
    ("32x48", 78.64),
    ("36x36", 66.90),
    ("36x48", 87.80),
    ("36x72", 129.60),
    ("40x40", 81.56),
    ("40x60", 120.06),
]

category = "Fine Art Paper"
subcategory_id = 12
product_type = "Metallic"

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

print(f"✅ Successfully imported {products_added} Fine Art Paper Metallic products")
