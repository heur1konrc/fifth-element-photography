#!/usr/bin/env python3
"""
Clean up naming convention in sub_options table
Remove "Stretched" suffix from Canvas mounting options
"""

import sqlite3

def cleanup_canvas_naming():
    """Remove 'Stretched' from Canvas mounting options"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("🧹 CLEANING UP CANVAS NAMING CONVENTION")
    print("=" * 50)
    
    # Get current Canvas mounting options (Type 1)
    cursor.execute('''
        SELECT id, name, value 
        FROM sub_options 
        WHERE product_type_id = 1 AND option_type = 'mounting'
        ORDER BY id
    ''')
    
    canvas_options = cursor.fetchall()
    
    print("📋 Current Canvas mounting options:")
    for opt_id, name, value in canvas_options:
        print(f"   {opt_id}: {name} = \"{value}\"")
    
    print("\n🔧 Updating naming convention...")
    
    # Update each option to remove "Stretched"
    updates = [
        (1, '0.75"'),      # "0.75" Stretched" → "0.75""
        (2, '1.25"'),      # "1.25" Stretched" → "1.25""
        (3, '1.5"'),       # "1.50" Stretched" → "1.5""
    ]
    
    for opt_id, new_value in updates:
        cursor.execute('''
            UPDATE sub_options 
            SET value = ? 
            WHERE id = ?
        ''', (new_value, opt_id))
        
        print(f"   ✅ Updated option {opt_id}: \"{new_value}\"")
    
    # Also update any products that reference these options
    print("\n🔄 Updating product names that reference old naming...")
    
    # Update product names that contain "Stretched"
    cursor.execute('''
        UPDATE products 
        SET name = REPLACE(name, ' Stretched', '')
        WHERE name LIKE '%Stretched%'
    ''')
    
    updated_products = cursor.rowcount
    print(f"   ✅ Updated {updated_products} product names")
    
    conn.commit()
    
    # Verify the changes
    print("\n✅ VERIFICATION - Updated Canvas mounting options:")
    cursor.execute('''
        SELECT id, name, value 
        FROM sub_options 
        WHERE product_type_id = 1 AND option_type = 'mounting'
        ORDER BY id
    ''')
    
    updated_options = cursor.fetchall()
    for opt_id, name, value in updated_options:
        print(f"   {opt_id}: {name} = \"{value}\"")
    
    # Show sample updated product names
    print("\n📋 Sample updated product names:")
    cursor.execute('''
        SELECT name 
        FROM products 
        WHERE product_type_id = 1 
        LIMIT 5
    ''')
    
    sample_products = cursor.fetchall()
    for (name,) in sample_products:
        print(f"   • {name}")
    
    conn.close()
    print("\n🎉 Naming convention cleanup completed!")

def verify_frame_naming():
    """Verify Frame naming is consistent"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("\n🔍 VERIFYING FRAME NAMING CONVENTION")
    print("=" * 40)
    
    # Check Framed Canvas options (Type 2)
    cursor.execute('''
        SELECT id, name, value, option_type
        FROM sub_options 
        WHERE product_type_id = 2
        ORDER BY option_type, id
    ''')
    
    frame_options = cursor.fetchall()
    
    current_type = None
    for opt_id, name, value, option_type in frame_options:
        if option_type != current_type:
            print(f"\n📁 {option_type.title()}:")
            current_type = option_type
        print(f"   {opt_id}: {name} = \"{value}\"")
    
    conn.close()

def main():
    """Main execution"""
    cleanup_canvas_naming()
    verify_frame_naming()
    
    print("\n🚀 NEXT STEPS:")
    print("1. Update Lumaprints mapping script to use clean naming")
    print("2. Re-run product mapping with correct sub_option values")
    print("3. Test hierarchical wizard with updated naming")

if __name__ == "__main__":
    main()
