#!/usr/bin/env python3
"""
Updated Lumaprints Mapping Script - Fixed for Clean Naming Convention
Maps all 684 products to proper Lumaprints subcategory IDs and option codes
"""

import sqlite3
import json
from lumaprints_complete_mapping import LUMAPRINTS_SUBCATEGORIES, LUMAPRINTS_OPTIONS, LUMAPRINTS_DEFAULTS

def map_all_products_to_lumaprints():
    """Map all existing products to Lumaprints subcategory IDs with clean naming"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("🗺️  MAPPING ALL PRODUCTS TO LUMAPRINTS CODES")
    print("=" * 50)
    
    # Get all products with their sub_options (using clean naming)
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
        ORDER BY pt.name, p.name
    ''')
    
    products = cursor.fetchall()
    
    print(f"📊 Processing {len(products)} products...")
    
    # Statistics
    mapped_count = 0
    unmapped_count = 0
    mapping_stats = {}
    
    for product in products:
        (prod_id, prod_name, type_id, sub1_id, sub2_id, 
         type_name, sub1_name, sub1_value, sub2_name, sub2_value) = product
        
        # Determine Lumaprints subcategory ID and options
        lumaprints_subcategory_id = None
        lumaprints_frame_option = None
        lumaprints_options = []
        
        # CANVAS PRINTS (Type 1)
        if type_name == 'Canvas Prints':
            if sub1_value == '0.75"':
                lumaprints_subcategory_id = 101001  # 0.75" Stretched Canvas
                lumaprints_options = [1, 4]  # Image Wrap, Sawtooth Hanger (defaults)
            elif sub1_value == '1.25"':
                lumaprints_subcategory_id = 101002  # 1.25" Stretched Canvas
                lumaprints_options = [1, 4]  # Image Wrap, Sawtooth Hanger (defaults)
            elif sub1_value == '1.5"':
                lumaprints_subcategory_id = 101003  # 1.5" Stretched Canvas
                lumaprints_options = [1, 4, 9]  # Image Wrap, Sawtooth Hanger, No Underlayer (defaults)
        
        # FRAMED CANVAS PRINTS (Type 2)
        elif type_name == 'Framed Canvas Prints':
            # Map based on frame size (sub_option_1) 
            if sub1_value == '0.75" Frame':
                lumaprints_subcategory_id = 102001  # 0.75" Framed Canvas
                lumaprints_options = [1, 16]  # Image Wrap, Hanging Wire (defaults)
                
                # Map frame color (sub_option_2) to Lumaprints frame option
                if sub2_value == 'White':
                    lumaprints_frame_option = 13  # 0.75" White Floating Frame
                    lumaprints_options.append(13)
                elif sub2_value == 'Black':
                    lumaprints_frame_option = 12  # 0.75" Black Floating Frame (default)
                    lumaprints_options.append(12)
                elif sub2_value == 'Silver':
                    lumaprints_frame_option = 14  # 0.75" Silver Floating Frame
                    lumaprints_options.append(14)
                elif sub2_value == 'Gold':
                    lumaprints_frame_option = 15  # 0.75" Gold Floating Frame
                    lumaprints_options.append(15)
                else:
                    # Default to Black frame if color not specified
                    lumaprints_frame_option = 12
                    lumaprints_options.append(12)
                    
            elif sub1_value == '1.25" Frame':
                lumaprints_subcategory_id = 102002  # 1.25" Framed Canvas
                lumaprints_options = [1, 28]  # Image Wrap, Hanging Wire (defaults)
                
                if sub2_value == 'Black':
                    lumaprints_frame_option = 27  # 1.25" Black Floating Frame (default)
                    lumaprints_options.append(27)
                elif sub2_value == 'Oak':
                    lumaprints_frame_option = 91  # 1.25" Oak Floating Frame
                    lumaprints_options.append(91)
                elif sub2_value == 'Natural Wood':  # Map to Oak
                    lumaprints_frame_option = 91  # 1.25" Oak Floating Frame
                    lumaprints_options.append(91)
                else:
                    # Default to Black frame
                    lumaprints_frame_option = 27
                    lumaprints_options.append(27)
                    
            elif sub1_value == '1.50" Frame':
                lumaprints_subcategory_id = 102003  # 1.5" Framed Canvas
                lumaprints_options = [1, 16, 9]  # Image Wrap, Hanging Wire, No Underlayer (defaults)
                
                if sub2_value == 'Black':
                    lumaprints_frame_option = 23  # 1.5" Black Floating Frame (default)
                    lumaprints_options.append(23)
                elif sub2_value == 'White':
                    lumaprints_frame_option = 24  # 1.5" White Floating Frame
                    lumaprints_options.append(24)
                elif sub2_value == 'Silver':
                    lumaprints_frame_option = 25  # 1.5" Silver Floating Frame
                    lumaprints_options.append(25)
                elif sub2_value == 'Gold':
                    lumaprints_frame_option = 26  # 1.5" Gold Floating Frame
                    lumaprints_options.append(26)
                elif sub2_value == 'Oak':
                    lumaprints_frame_option = 92  # 1.5" Oak Floating Frame
                    lumaprints_options.append(92)
                else:
                    # Default to Black frame
                    lumaprints_frame_option = 23
                    lumaprints_options.append(23)
        
        # FINE ART PAPER PRINTS (Type 3)
        elif type_name == 'Fine Art Paper Prints':
            # Map based on paper type
            if sub1_value == 'Archival Matte':
                lumaprints_subcategory_id = 103001  # Archival Matte Fine Art Paper
            elif sub1_value == 'Hot Press':
                lumaprints_subcategory_id = 103002  # Hot Press Fine Art Paper
            elif sub1_value == 'Cold Press':
                lumaprints_subcategory_id = 103003  # Cold Press Fine Art Paper
            elif sub1_value == 'Semi-Gloss':
                lumaprints_subcategory_id = 103005  # Semi-Glossy Fine Art Paper
            elif sub1_value == 'Metallic':
                lumaprints_subcategory_id = 103006  # Metallic Fine Art Paper
            elif sub1_value == 'Glossy':
                lumaprints_subcategory_id = 103007  # Glossy Fine Art Paper
            elif sub1_value == 'Somerset Velvet':
                lumaprints_subcategory_id = 103009  # Somerset Velvet Fine Art Paper
            else:
                lumaprints_subcategory_id = 103001  # Default to Archival Matte
            
            lumaprints_options = [36]  # 0.25" Bleed (default)
        
        # FRAMED FINE ART PAPER PRINTS (Type 4)
        elif type_name == 'Framed Fine Art Paper Prints':
            lumaprints_subcategory_id = 105001  # Default to 0.875" Black Frame
            # Note: This would need more complex mapping based on frame sizes and mat options
        
        # METAL PRINTS (Type 6)
        elif type_name == 'Metal Prints':
            lumaprints_subcategory_id = 106001  # Metal Print
            lumaprints_options = [29, 31]  # Glossy White, Inset Frame (defaults)
        
        # Update the product with Lumaprints codes
        if lumaprints_subcategory_id:
            options_json = json.dumps(lumaprints_options)
            
            cursor.execute('''
                UPDATE products 
                SET lumaprints_subcategory_id = ?, 
                    lumaprints_options = ?,
                    lumaprints_frame_option = ?
                WHERE id = ?
            ''', (lumaprints_subcategory_id, options_json, lumaprints_frame_option, prod_id))
            
            mapped_count += 1
            
            # Track mapping statistics
            if lumaprints_subcategory_id not in mapping_stats:
                mapping_stats[lumaprints_subcategory_id] = 0
            mapping_stats[lumaprints_subcategory_id] += 1
            
        else:
            unmapped_count += 1
            print(f"   ⚠️  Unmapped: {prod_name} (Type: {type_name}, Sub1: {sub1_value}, Sub2: {sub2_value})")
    
    conn.commit()
    conn.close()
    
    # Print results
    print(f"\n📊 MAPPING RESULTS:")
    print(f"   ✅ Mapped: {mapped_count} products")
    print(f"   ⚠️  Unmapped: {unmapped_count} products")
    print(f"   📈 Success rate: {mapped_count/(mapped_count+unmapped_count)*100:.1f}%")
    
    print(f"\n📋 LUMAPRINTS SUBCATEGORIES USED:")
    for subcategory_id, count in sorted(mapping_stats.items()):
        info = LUMAPRINTS_SUBCATEGORIES.get(subcategory_id, {'category': 'Unknown', 'subcategory': 'Unknown'})
        print(f"   {subcategory_id}: {count} products - {info['category']} - {info['subcategory']}")
    
    return mapped_count, unmapped_count

def verify_mapping():
    """Verify the mapping results"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print(f"\n🔍 VERIFICATION:")
    
    # Check how many products have Lumaprints codes
    cursor.execute('SELECT COUNT(*) FROM products WHERE lumaprints_subcategory_id IS NOT NULL')
    mapped_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE active = 1')
    total_products = cursor.fetchone()[0]
    
    print(f"   📊 {mapped_products}/{total_products} products have Lumaprints codes")
    
    # Show sample mapped products
    cursor.execute('''
        SELECT p.name, p.lumaprints_subcategory_id, p.lumaprints_options, p.lumaprints_frame_option
        FROM products p
        WHERE p.lumaprints_subcategory_id IS NOT NULL
        LIMIT 5
    ''')
    
    samples = cursor.fetchall()
    print(f"\n📋 Sample mapped products:")
    for name, subcategory_id, options, frame_option in samples:
        print(f"   • {name}")
        print(f"     Subcategory: {subcategory_id}, Options: {options}, Frame: {frame_option}")
    
    conn.close()

def main():
    """Main execution"""
    print("🚀 LUMAPRINTS PRODUCT MAPPING - FIXED VERSION")
    print("=" * 60)
    
    mapped, unmapped = map_all_products_to_lumaprints()
    verify_mapping()
    
    print(f"\n🎉 Mapping completed!")
    print(f"Next steps:")
    print(f"1. Update hierarchical wizard to use lumaprints_subcategory_id")
    print(f"2. Update OrderDesk integration to pass Lumaprints codes")
    print(f"3. Test complete order flow with real Lumaprints products")

if __name__ == "__main__":
    main()
