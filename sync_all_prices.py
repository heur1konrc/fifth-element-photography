"""
Sync All Product Prices from Pictorem API
Fetches prices for all product/size combinations and stores in database
"""

import sqlite3
from pictorem_api import PictoremAPI
from datetime import datetime
import time

DB_PATH = '/data/pictorem.db'

def sync_all_prices():
    """Fetch all prices from Pictorem API and store in database"""
    
    api = PictoremAPI()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create pricing table if it doesn't exist
    import os
    sql_path = os.path.join(os.path.dirname(__file__), 'add_pricing_table.sql')
    with open(sql_path, 'r') as f:
        cursor.executescript(f.read())
    
    # Get global markup
    cursor.execute("SELECT value FROM pictorem_settings WHERE key_name = 'global_markup_percentage'")
    markup = float(cursor.fetchone()[0])
    
    # Get all products
    cursor.execute("SELECT id, slug, preorder_template FROM pictorem_products WHERE active = 1")
    products = cursor.fetchall()
    
    total_synced = 0
    total_errors = 0
    
    print(f"Starting price sync with {markup}% markup...")
    print(f"Found {len(products)} products")
    print()
    
    for product_id, slug, preorder_template in products:
        print(f"Syncing prices for {slug}...")
        
        # Skip framed products for now (they need options)
        if 'framed' in slug.lower():
            print(f"  Skipping {slug} (framed products need options - coming soon)")
            print()
            continue
        
        # Get all sizes for this product
        cursor.execute("""
            SELECT id, width, height, orientation 
            FROM pictorem_sizes 
            WHERE product_id = ? AND active = 1
        """, (product_id,))
        sizes = cursor.fetchall()
        
        for size_id, width, height, orientation in sizes:
            # Build preorder code
            preorder_code = preorder_template.format(
                orientation=orientation,
                width=width,
                height=height
            )
            
            # Get price from API
            try:
                price_data = api.get_price(preorder_code, use_cache=False)
                
                if price_data:
                    base_price = price_data['base_price']
                    customer_price = price_data['customer_price']
                    
                    # Insert or update pricing
                    cursor.execute("""
                        INSERT INTO pictorem_product_pricing 
                        (product_id, size_id, option_id, preorder_code, base_price, markup_percentage, customer_price, last_synced, updated_at)
                        VALUES (?, ?, NULL, ?, ?, ?, ?, datetime('now'), datetime('now'))
                        ON CONFLICT(product_id, size_id, option_id) DO UPDATE SET
                            base_price = excluded.base_price,
                            markup_percentage = excluded.markup_percentage,
                            customer_price = excluded.customer_price,
                            last_synced = datetime('now'),
                            updated_at = datetime('now')
                    """, (product_id, size_id, preorder_code, base_price, markup, customer_price))
                    
                    total_synced += 1
                    print(f"  ✓ {width}x{height}: ${base_price} → ${customer_price}")
                else:
                    total_errors += 1
                    print(f"  ✗ {width}x{height}: Failed to get price")
                
                # Rate limiting - don't hammer the API
                time.sleep(0.1)
                
            except Exception as e:
                total_errors += 1
                print(f"  ✗ {width}x{height}: Error - {e}")
        
        print()
    
    conn.commit()
    conn.close()
    
    print("="*60)
    print(f"Price sync complete!")
    print(f"Successfully synced: {total_synced}")
    print(f"Errors: {total_errors}")
    print("="*60)
    
    return {
        'success': True,
        'synced': total_synced,
        'errors': total_errors
    }

if __name__ == '__main__':
    sync_all_prices()

