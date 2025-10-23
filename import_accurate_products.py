#!/usr/bin/env python3
"""
Import Accurate Product Data from Lumaprints
This script imports verified size and pricing data for each product
"""

import sqlite3
import json
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lumaprints_pricing.db')

# Accurate product data from Lumaprints
PRODUCTS = {
    "canvas_075": {
        "name": "0.75\" Stretched Canvas",
        "subcategory_id": 101001,
        "product_type_id": 1,
        "category_id": 2,  # 0.75" category
        "sizes": {
            "8x10": 9.89,
            "8x12": 15.39,
            "10x20": 22.73,
            "10x30": 26.40,
            "11x14": 12.09,
            "12x12": 18.31,
            "12x16": 20.44,
            "12x18": 21.18,
            "16x20": 24.35,
            "16x24": 27.30,
            "18x24": 28.26,
            "20x20": 27.46,
            "20x40": 38.96,
            "24x30": 36.68,
            "24x32": 37.64,
            "24x36": 39.56,
            "30x30": 42.54
        }
    },
    "canvas_125": {
        "name": "1.25\" Stretched Canvas",
        "subcategory_id": 101002,
        "product_type_id": 1,
        "category_id": 3,  # 1.25" category
        "sizes": {
            "8x10": 10.99,
            "8x12": 16.23,
            "10x20": 24.13,
            "10x30": 28.26,
            "11x14": 13.19,
            "12x12": 19.36,
            "12x16": 21.68,
            "12x18": 22.50,
            "16x20": 25.95,
            "16x24": 29.07,
            "16x48": 50.61,
            "18x24": 30.12,
            "19x42": 42.89,
            "20x20": 29.23,
            "20x30": 33.68,
            "20x40": 41.63,
            "20x60": 55.34,
            "22x30": 37.54,
            "24x30": 39.07,
            "24x32": 40.11,
            "24x36": 42.21,
            "24x72": 95.72,
            "27x60": 74.58,
            "30x30": 45.20,
            "30x40": 50.99,
            "30x60": 80.03,
            "32x48": 79.69,
            "36x48": 86.33,
            "40x40": 81.37,
            "40x60": 112.07,
            "45x60": 118.17
        }
    },
    "canvas_150": {
        "name": "1.50\" Stretched Canvas",
        "subcategory_id": 101003,
        "product_type_id": 1,
        "category_id": 4,
        "sizes": {
            "8x10": 12.09,
            "8x12": 18.76,
            "10x20": 28.29,
            "10x30": 33.82,
            "11x14": 14.29,
            "12x12": 22.56,
            "12x16": 25.40,
            "12x18": 26.49,
            "16x20": 30.73,
            "16x24": 34.39,
            "16x48": 59.63,
            "18x24": 35.69,
            "20x20": 34.54,
            "20x40": 49.59,
            "20x60": 65.97,
            "24x30": 46.23,
            "24x32": 47.55,
            "24x36": 50.19,
            "24x72": 112.46,
            "30x30": 53.16,
            "30x40": 60.29,
            "30x60": 94.26,
            "32x48": 93.87,
            "36x48": 101.20,
            "40x40": 95.54,
            "40x60": 131.03,
            "45x60": 138.10
        }
    },
    "canvas_rolled": {
        "name": "Rolled Canvas",
        "subcategory_id": 101005,
        "product_type_id": 1,
        "category_id": 5,
        "sizes": {
            "8x10": 9.13,
            "8x12": 10.28,
            "10x20": 13.05,
            "10x30": 14.87,
            "11x14": 12.20,
            "12x12": 12.02,
            "12x16": 12.85,
            "12x18": 13.25,
            "16x20": 14.92,
            "16x24": 15.96,
            "18x24": 18.67,
            "20x20": 17.74,
            "20x40": 23.96,
            "20x60": 30.18,
            "24x30": 22.62,
            "24x32": 23.35,
            "24x36": 24.80,
            "30x30": 25.26,
            "30x40": 32.83,
            "30x60": 41.64,
            "32x48": 37.70,
            "36x48": 40.39,
            "40x40": 40.10,
            "40x60": 51.51,
            "45x60": 55.66
        }
    },
    "framed_canvas_075_black": {
        "name": "0.75\" Framed Canvas - 1.625x1.375 Black Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    },
    "framed_canvas_075_white": {
        "name": "0.75\" Framed Canvas - 1.25x0.875 White Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    },
    "framed_canvas_075_oak": {
        "name": "0.75\" Framed Canvas - 1.25x0.875 Oak Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    },
    "framed_canvas_075_maple": {
        "name": "0.75\" Framed Canvas - 1.25x0.875 Maple Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    },
    "framed_canvas_075_black_125": {
        "name": "0.75\" Framed Canvas - 1.25x0.875 Black Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    },
    "framed_canvas_075_natural_wood": {
        "name": "0.75\" Framed Canvas - 0.875x1.125 Natural Wood Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    },
    "framed_canvas_075_maple_0875": {
        "name": "0.75\" Framed Canvas - 0.875x1.125 Maple Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    },
    "framed_canvas_075_espresso": {
        "name": "0.75\" Framed Canvas - 0.875x1.125 Espresso Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    },
    "framed_canvas_075_gold_plein_air": {
        "name": "0.75\" Framed Canvas - 0.75in Gold Plein Air Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    },
    "framed_canvas_075_vintage_copper": {
        "name": "0.75\" Framed Canvas - Vintage Collection Copper Frame",
        "subcategory_id": 102001,
        "product_type_id": 2,
        "category_id": 6,
        "sizes": {
            "8x10": 29.69,
            "8x12": 33.31,
            "10x20": 52.65,
            "10x30": 62.35,
            "11x14": 37.80,
            "12x12": 43.40,
            "12x16": 47.86,
            "12x18": 49.74,
            "16x20": 56.37,
            "16x24": 61.61,
            "18x24": 63.73,
            "20x20": 61.76,
            "20x40": 84.79,
            "24x30": 79.05,
            "24x32": 81.16,
            "24x36": 85.39,
            "30x30": 88.37,
            "30x40": 99.47
        }
    }
}

def clear_products():
    """Clear existing products from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🗑️  Clearing existing products...")
    cursor.execute('DELETE FROM products')
    
    conn.commit()
    conn.close()
    print("✅ Products cleared")

def import_product(product_key, product_data):
    """Import a single product with all its sizes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    name = product_data['name']
    subcategory_id = product_data['subcategory_id']
    product_type_id = product_data['product_type_id']
    category_id = product_data['category_id']
    
    print(f"\n📦 Importing {name} (Subcategory {subcategory_id})...")
    
    count = 0
    for size, cost_price in product_data['sizes'].items():
        # Product name includes size
        full_name = f"{name} {size}\""
        
        # Insert product
        cursor.execute('''
            INSERT INTO products (
                name, 
                product_type_id, 
                category_id, 
                size, 
                cost_price, 
                retail_price,
                lumaprints_subcategory_id, 
                lumaprints_options,
                active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            full_name,
            product_type_id,
            category_id,
            size,
            cost_price,
            cost_price,  # retail_price same as cost for now, markup applied at order time
            subcategory_id,
            json.dumps([])  # Empty options array, options selected at order time
        ))
        count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Imported {count} sizes for {name}")
    return count

def main():
    """Main import function"""
    print("=" * 60)
    print("ACCURATE PRODUCT DATA IMPORT")
    print("=" * 60)
    
    # Clear existing products
    clear_products()
    
    # Import each product
    total_count = 0
    for product_key, product_data in PRODUCTS.items():
        count = import_product(product_key, product_data)
        total_count += count
    
    print("\n" + "=" * 60)
    print(f"✅ IMPORT COMPLETE: {total_count} products imported")
    print("=" * 60)

if __name__ == "__main__":
    main()

