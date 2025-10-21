#!/usr/bin/env python3
"""
Database Update Script: Add Lumaprints Subcategory IDs and Option Codes
This script adds the missing Lumaprints integration fields to the existing database
"""

import sqlite3
import json
from lumaprints_complete_mapping import LUMAPRINTS_SUBCATEGORIES, LUMAPRINTS_OPTIONS, LUMAPRINTS_DEFAULTS

def add_lumaprints_fields():
    """Add Lumaprints fields to products table"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("🔧 Adding Lumaprints integration fields to products table...")
    
    # Add new columns for Lumaprints integration
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN lumaprints_subcategory_id INTEGER')
        print("✅ Added lumaprints_subcategory_id column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  lumaprints_subcategory_id column already exists")
        else:
            raise e
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN lumaprints_options TEXT')  # JSON string of option IDs
        print("✅ Added lumaprints_options column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  lumaprints_options column already exists")
        else:
            raise e
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN lumaprints_frame_option INTEGER')
        print("✅ Added lumaprints_frame_option column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  lumaprints_frame_option column already exists")
        else:
            raise e
    
    conn.commit()
    conn.close()
    print("✅ Database schema updated successfully!")

def map_product_types_to_lumaprints():
    """Map existing product types to Lumaprints subcategory IDs"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("\n🗺️  Mapping product types to Lumaprints subcategory IDs...")
    
    # Get current product types
    cursor.execute('SELECT id, name FROM product_types WHERE active = 1')
    product_types = cursor.fetchall()
    
    # Mapping from our product type names to Lumaprints subcategory IDs
    TYPE_TO_LUMAPRINTS = {
        'Canvas Prints': {
            # Will need to differentiate by sub_options (0.75", 1.25", 1.5", Rolled)
            'default': 101002  # 1.25" as default
        },
        'Framed Canvas Prints': {
            # Will need to differentiate by sub_options (0.75", 1.25", 1.5")
            'default': 102001  # 0.75" as default
        },
        'Fine Art Paper Prints': {
            'default': 103001  # Archival Matte as default
        },
        'Metal Prints': {
            'default': 106001  # Metal Print
        },
        'Framed Fine Art Paper Prints': {
            'default': 105001  # 0.875" Black Frame as default
        }
    }
    
    for type_id, type_name in product_types:
        print(f"📋 Product Type: {type_name} (ID: {type_id})")
        
        if type_name in TYPE_TO_LUMAPRINTS:
            default_subcategory = TYPE_TO_LUMAPRINTS[type_name]['default']
            print(f"   → Default Lumaprints subcategory: {default_subcategory}")
        else:
            print(f"   ⚠️  No mapping found for '{type_name}'")
    
    conn.close()

def update_existing_products():
    """Update existing products with Lumaprints subcategory IDs based on their options"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("\n🔄 Updating existing products with Lumaprints codes...")
    
    # Get products with their sub_options
    cursor.execute('''
        SELECT p.id, p.name, p.product_type_id, p.sub_option_1_id, p.sub_option_2_id,
               pt.name as product_type_name,
               so1.name as sub_option_1_name, so1.value as sub_option_1_value,
               so2.name as sub_option_2_name, so2.value as sub_option_2_value
        FROM products p
        JOIN product_types pt ON p.product_type_id = pt.id
        LEFT JOIN sub_options so1 ON p.sub_option_1_id = so1.id
        LEFT JOIN sub_options so2 ON p.sub_option_2_id = so2.id
        WHERE p.active = 1
        LIMIT 10
    ''')
    
    products = cursor.fetchall()
    
    print(f"📊 Found {len(products)} products to analyze...")
    
    for product in products:
        (prod_id, prod_name, type_id, sub1_id, sub2_id, 
         type_name, sub1_name, sub1_value, sub2_name, sub2_value) = product
        
        print(f"\n🔍 Product: {prod_name}")
        print(f"   Type: {type_name}")
        print(f"   Sub1: {sub1_name} = {sub1_value}" if sub1_name else "   Sub1: None")
        print(f"   Sub2: {sub2_name} = {sub2_value}" if sub2_name else "   Sub2: None")
        
        # Determine Lumaprints subcategory ID based on product type and options
        lumaprints_subcategory_id = None
        lumaprints_frame_option = None
        
        if type_name == 'Framed Canvas Prints':
            # Map based on frame size (sub_option_1) 
            if sub1_value == '0.75"':
                lumaprints_subcategory_id = 102001  # 0.75" Framed Canvas
                # Map frame color (sub_option_2) to Lumaprints frame option
                if sub2_value == 'White':
                    lumaprints_frame_option = 13  # 0.75" White Floating Frame
                elif sub2_value == 'Black':
                    lumaprints_frame_option = 12  # 0.75" Black Floating Frame (default)
                elif sub2_value == 'Silver':
                    lumaprints_frame_option = 14  # 0.75" Silver Floating Frame
                elif sub2_value == 'Gold':
                    lumaprints_frame_option = 15  # 0.75" Gold Floating Frame
            elif sub1_value == '1.25"':
                lumaprints_subcategory_id = 102002  # 1.25" Framed Canvas
                if sub2_value == 'Black':
                    lumaprints_frame_option = 27  # 1.25" Black Floating Frame (default)
                elif sub2_value == 'Oak':
                    lumaprints_frame_option = 91  # 1.25" Oak Floating Frame
                elif sub2_value == 'Walnut':
                    lumaprints_frame_option = 120  # 1.25" Walnut Floating Frame
            elif sub1_value == '1.5"':
                lumaprints_subcategory_id = 102003  # 1.5" Framed Canvas
                if sub2_value == 'Black':
                    lumaprints_frame_option = 23  # 1.5" Black Floating Frame (default)
                elif sub2_value == 'White':
                    lumaprints_frame_option = 24  # 1.5" White Floating Frame
                elif sub2_value == 'Silver':
                    lumaprints_frame_option = 25  # 1.5" Silver Floating Frame
                elif sub2_value == 'Gold':
                    lumaprints_frame_option = 26  # 1.5" Gold Floating Frame
                elif sub2_value == 'Oak':
                    lumaprints_frame_option = 92  # 1.5" Oak Floating Frame
        
        elif type_name == 'Canvas Prints':
            # Map based on canvas depth
            if sub1_value == '0.75"':
                lumaprints_subcategory_id = 101001  # 0.75" Stretched Canvas
            elif sub1_value == '1.25"':
                lumaprints_subcategory_id = 101002  # 1.25" Stretched Canvas
            elif sub1_value == '1.5"':
                lumaprints_subcategory_id = 101003  # 1.5" Stretched Canvas
            elif sub1_value == 'Rolled':
                lumaprints_subcategory_id = 101005  # Rolled Canvas
        
        elif type_name == 'Fine Art Paper Prints':
            lumaprints_subcategory_id = 103001  # Default to Archival Matte
        
        elif type_name == 'Metal Prints':
            lumaprints_subcategory_id = 106001  # Metal Print
        
        # Update the product with Lumaprints codes
        if lumaprints_subcategory_id:
            # Create options JSON
            options = LUMAPRINTS_DEFAULTS.get(lumaprints_subcategory_id, [])
            if lumaprints_frame_option and lumaprints_frame_option not in options:
                options.append(lumaprints_frame_option)
            
            options_json = json.dumps(options)
            
            cursor.execute('''
                UPDATE products 
                SET lumaprints_subcategory_id = ?, 
                    lumaprints_options = ?,
                    lumaprints_frame_option = ?
                WHERE id = ?
            ''', (lumaprints_subcategory_id, options_json, lumaprints_frame_option, prod_id))
            
            print(f"   ✅ Updated: subcategory_id={lumaprints_subcategory_id}, frame_option={lumaprints_frame_option}")
        else:
            print(f"   ⚠️  Could not determine Lumaprints mapping")
    
    conn.commit()
    conn.close()
    print("\n✅ Product updates completed!")

def add_missing_products():
    """Add missing Lumaprints products that aren't in our current catalog"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("\n➕ Adding missing Lumaprints products...")
    
    # Get existing subcategory IDs
    cursor.execute('SELECT DISTINCT lumaprints_subcategory_id FROM products WHERE lumaprints_subcategory_id IS NOT NULL')
    existing_subcategories = set(row[0] for row in cursor.fetchall())
    
    print(f"📊 Currently have products for {len(existing_subcategories)} Lumaprints subcategories")
    
    missing_subcategories = set(LUMAPRINTS_SUBCATEGORIES.keys()) - existing_subcategories
    print(f"📊 Missing {len(missing_subcategories)} Lumaprints subcategories")
    
    for subcategory_id in sorted(missing_subcategories):
        info = LUMAPRINTS_SUBCATEGORIES[subcategory_id]
        print(f"   ➕ Need to add: {subcategory_id} - {info['category']} - {info['subcategory']}")
    
    # For now, just report what's missing - actual product creation would need size/pricing data
    conn.close()

def main():
    """Main execution function"""
    print("🚀 LUMAPRINTS DATABASE INTEGRATION UPDATE")
    print("=" * 50)
    
    # Step 1: Add new database fields
    add_lumaprints_fields()
    
    # Step 2: Map existing product types
    map_product_types_to_lumaprints()
    
    # Step 3: Update existing products
    update_existing_products()
    
    # Step 4: Identify missing products
    add_missing_products()
    
    print("\n🎉 Database update completed!")
    print("Next steps:")
    print("1. Test hierarchical wizard with Lumaprints codes")
    print("2. Update OrderDesk integration to use subcategory_id and options")
    print("3. Add missing product types to complete catalog")

if __name__ == "__main__":
    main()
