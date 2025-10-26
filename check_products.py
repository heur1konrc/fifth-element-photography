#!/usr/bin/env python3
"""Check what products exist in the database"""
import sqlite3
import json

def check_products():
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    result = {}
    
    # Get distinct subcategory IDs
    cursor.execute("SELECT DISTINCT lumaprints_subcategory_id FROM products ORDER BY lumaprints_subcategory_id")
    result['subcategory_ids'] = [row[0] for row in cursor.fetchall()]
    
    # Check for subcategory 105003
    cursor.execute("SELECT COUNT(*) FROM products WHERE lumaprints_subcategory_id = 105003")
    result['count_105003'] = cursor.fetchone()[0]
    
    # Get sample products for 105003
    cursor.execute("SELECT id, name, size, price, cost_price FROM products WHERE lumaprints_subcategory_id = 105003 LIMIT 10")
    result['sample_105003'] = [
        {'id': row[0], 'name': row[1], 'size': row[2], 'price': row[3], 'cost': row[4]}
        for row in cursor.fetchall()
    ]
    
    # Get distinct size formats
    cursor.execute("SELECT DISTINCT size FROM products ORDER BY size LIMIT 30")
    result['size_formats'] = [row[0] for row in cursor.fetchall()]
    
    # Get sample products (any subcategory)
    cursor.execute("SELECT id, name, size, price, lumaprints_subcategory_id FROM products LIMIT 10")
    result['sample_products'] = [
        {'id': row[0], 'name': row[1], 'size': row[2], 'price': row[3], 'subcategory_id': row[4]}
        for row in cursor.fetchall()
    ]
    
    conn.close()
    return result

if __name__ == '__main__':
    print(json.dumps(check_products(), indent=2))

