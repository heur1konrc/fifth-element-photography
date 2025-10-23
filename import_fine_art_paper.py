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

# Fine Art Paper - Archival Matte
# Subcategory ID: 8

sizes_prices = [
    # From first screenshot
    ("4x6", 1.71),
    ("5x7", 2.01),
    ("6x6", 2.04),
    ("8.5x11", 3.54),
    ("8x10", 3.19),
    ("8x12", 3.61),
    ("8x16", 4.43),
    ("8x24", 6.09),
    ("8x36", 8.55),
    ("8x48", 11.03),
    ("8x8", 2.79),
    ("9x12", 3.90),
    ("10x10", 3.68),
    ("10x20", 6.16),
    ("10x30", 8.64),
    ("10x40", 11.11),
    ("10x60", 16.06),
    ("11x14", 5.01),
    ("11x17", 5.81),
    ("12x12", 4.76),
    ("12x16", 5.92),
    ("12x18", 6.49),
    ("12x20", 7.07),
    ("12x24", 8.22),
    ("12x36", 11.69),
    ("12x48", 15.15),
    ("12x60", 18.63),
    ("14x14", 5.99),
    ("14x18", 7.32),
    ("16x16", 7.40),
    ("16x20", 8.89),
    ("16x24", 10.37),
    ("16x32", 13.34),
    ("16x36", 14.82),
    ("16x48", 19.29),
    # From second screenshot
    ("16x60", 23.74),
    ("16x72", 28.20),
    ("18x18", 8.96),
    ("18x24", 11.44),
    ("18x36", 16.39),
    ("18x48", 21.34),
    ("18x60", 26.29),
    ("18x72", 31.24),
    ("20x20", 10.70),
    ("20x24", 12.52),
    ("20x30", 15.24),
    ("20x36", 17.96),
    ("20x40", 19.78),
    ("20x60", 28.86),
    ("20x72", 34.30),
    ("22x28", 15.56),
    ("24x24", 14.66),
    ("24x30", 17.88),
    ("24x36", 21.10),
    ("24x40", 23.24),
    ("24x48", 27.53),
    ("24x60", 33.97),
    ("24x72", 40.40),
    ("30x30", 21.84),
    ("30x40", 28.44),
    ("30x60", 41.64),
    ("30x72", 49.56),
    ("32x32", 24.56),
    ("32x48", 35.79),
    ("36x36", 30.50),
    ("36x48", 39.91),
    ("36x72", 58.72),
    ("40x40", 37.10),
    ("40x60", 54.43),
]

category = "Fine Art Paper"
subcategory_id = 8
product_type = "Archival Matte"

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

print(f"✅ Successfully imported {products_added} Fine Art Paper products")
