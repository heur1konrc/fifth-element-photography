"""
Sync Prices for a Single Product
Fetches prices for all sizes of one product from Pictorem API
"""

import sqlite3
from pictorem_api import PictoremAPI
from datetime import datetime
import time

DB_PATH = '/data/pictorem.db'

def sync_product_prices(product_slug):
    """
    Fetch prices for all sizes of a single product
    
    Args:
        product_slug: Product slug (e.g., 'canvas-075', 'metal-hd')
    
    Returns:
        dict with sync results
    """
    
    api = PictoremAPI()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get global markup
    cursor.execute("SELECT value FROM pictorem_settings WHERE key_name = 'global_markup_percentage'")
    markup_row = cursor.fetchone()
    if not markup_row:
        conn.close()
        return {
            'success': False,
            'error': 'Global markup not found in settings'
        }
    
    markup = float(markup_row[0])
    
    # Get product
    cursor.execute("SELECT id, slug, name, preorder_template FROM pictorem_products WHERE slug = ? AND active = 1", (product_slug,))
    product = cursor.fetchone()
    
    if not product:
        conn.close()
        return {
            'success': False,
            'error': f'Product not found: {product_slug}'
        }
    
    product_id, slug, name, preorder_template = product
    
    # Get all sizes for this product
    cursor.execute("""
        SELECT id, width, height, orientation 
        FROM pictorem_sizes 
        WHERE product_id = ? AND active = 1
        ORDER BY width, height
    """, (product_id,))
    sizes = cursor.fetchall()
    
    if not sizes:
        conn.close()
        return {
            'success': False,
            'error': f'No sizes found for product: {product_slug}'
        }
    
    total_synced = 0
    total_errors = 0
    errors = []
    
    print(f"\n{'='*60}")
    print(f"Syncing prices for: {name}")
    print(f"Product slug: {slug}")
    print(f"Markup: {markup}%")
    print(f"Sizes to sync: {len(sizes)}")
    print(f"{'='*60}\n")
    
    for size_id, width, height, orientation in sizes:
        try:
            # Build preorder code
            preorder_code = preorder_template.format(
                orientation=orientation,
                width=width,
                height=height
            )
            
            print(f"Fetching price for {width}x{height}...")
            print(f"  Preorder code: {preorder_code}")
            
            # Get price from API
            price_data = api.get_price(preorder_code, use_cache=False)
            
            if price_data and price_data.get('base_price'):
                base_price = float(price_data['base_price'])
                customer_price = float(price_data['customer_price'])
                
                # Insert or update pricing
                cursor.execute("""
                    INSERT INTO pictorem_product_pricing 
                    (product_id, size_id, option_id, preorder_code, base_price, markup_percentage, customer_price, last_synced, updated_at)
                    VALUES (?, ?, NULL, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    ON CONFLICT(product_id, size_id, option_id) DO UPDATE SET
                        preorder_code = excluded.preorder_code,
                        base_price = excluded.base_price,
                        markup_percentage = excluded.markup_percentage,
                        customer_price = excluded.customer_price,
                        last_synced = datetime('now'),
                        updated_at = datetime('now')
                """, (product_id, size_id, preorder_code, base_price, markup, customer_price))
                
                total_synced += 1
                print(f"  ✓ Success: Base ${base_price:.2f} → Customer ${customer_price:.2f}")
            else:
                total_errors += 1
                error_msg = f"{width}x{height}: API returned no price data"
                errors.append(error_msg)
                print(f"  ✗ Error: {error_msg}")
            
            # Rate limiting - be nice to the API
            time.sleep(0.2)
            
        except Exception as e:
            total_errors += 1
            error_msg = f"{width}x{height}: {str(e)}"
            errors.append(error_msg)
            print(f"  ✗ Exception: {error_msg}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Sync complete for {name}")
    print(f"Successfully synced: {total_synced}/{len(sizes)}")
    print(f"Errors: {total_errors}")
    print(f"{'='*60}\n")
    
    return {
        'success': True,
        'product_name': name,
        'product_slug': slug,
        'synced': total_synced,
        'errors': total_errors,
        'total_sizes': len(sizes),
        'error_details': errors if errors else None
    }

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        product_slug = sys.argv[1]
        result = sync_product_prices(product_slug)
        print(f"\nResult: {result}")
    else:
        print("Usage: python sync_single_product.py <product_slug>")
        print("Example: python sync_single_product.py canvas-075")
