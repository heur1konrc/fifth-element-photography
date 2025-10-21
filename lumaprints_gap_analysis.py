#!/usr/bin/env python3
"""
Gap Analysis: Current vs Complete Lumaprints Product Mapping
"""

# Current mapping from dynamic_pricing_calculator.py
CURRENT_MAPPING = {
    101001: {'category': 'Canvas', 'subcategory': '0.75" Stretched Canvas'},
    101002: {'category': 'Canvas', 'subcategory': '1.25" Stretched Canvas'},
    101003: {'category': 'Canvas', 'subcategory': '1.5" Stretched Canvas'},
    101004: {'category': 'Canvas', 'subcategory': 'Rolled Canvas'},  # WRONG ID!
    102001: {'category': 'Framed Canvas', 'subcategory': '0.75" Framed Canvas'},
    102002: {'category': 'Framed Canvas', 'subcategory': '1.25" Framed Canvas'},
    102003: {'category': 'Framed Canvas', 'subcategory': '1.5" Framed Canvas'},
    103001: {'category': 'Fine Art Paper', 'subcategory': 'Standard'},
    104001: {'category': 'Framed Fine Art Paper', 'subcategory': 'Standard Frame'},  # WRONG ID!
    105001: {'category': 'Foam-mounted Fine Art Paper', 'subcategory': 'Standard Mount'},  # WRONG CATEGORY!
    106001: {'category': 'Metal', 'subcategory': 'Standard'},
    107001: {'category': 'Peel and Stick', 'subcategory': 'Standard'},  # NOT IN LUMAPRINTS API!
}

# Complete mapping from Lumaprints API
from lumaprints_complete_mapping import LUMAPRINTS_SUBCATEGORIES

def analyze_gaps():
    print("=== LUMAPRINTS PRODUCT MAPPING GAP ANALYSIS ===\n")
    
    print("🔍 CURRENT MAPPING ISSUES:")
    print("❌ 101004 (Rolled Canvas) - Should be 101005")
    print("❌ 104001 (Framed Fine Art Paper) - Should be 105001-105007 (6 different frames)")
    print("❌ 105001 (Foam-mounted) - This ID is actually 'Framed Fine Art Paper - 0.875\" Black Frame'")
    print("❌ 107001 (Peel and Stick) - Not found in Lumaprints API documentation")
    print()
    
    print("📊 COVERAGE ANALYSIS:")
    current_ids = set(CURRENT_MAPPING.keys())
    complete_ids = set(LUMAPRINTS_SUBCATEGORIES.keys())
    
    print(f"Current mapping: {len(current_ids)} subcategories")
    print(f"Complete Lumaprints: {len(complete_ids)} subcategories")
    print(f"Coverage: {len(current_ids & complete_ids)}/{len(complete_ids)} ({len(current_ids & complete_ids)/len(complete_ids)*100:.1f}%)")
    print()
    
    print("✅ CORRECTLY MAPPED:")
    correct_ids = current_ids & complete_ids
    for subcat_id in sorted(correct_ids):
        info = LUMAPRINTS_SUBCATEGORIES[subcat_id]
        print(f"  {subcat_id}: {info['category']} - {info['subcategory']}")
    print()
    
    print("❌ MISSING FROM CURRENT MAPPING:")
    missing_ids = complete_ids - current_ids
    for subcat_id in sorted(missing_ids):
        info = LUMAPRINTS_SUBCATEGORIES[subcat_id]
        print(f"  {subcat_id}: {info['category']} - {info['subcategory']}")
    print()
    
    print("⚠️  INCORRECT IN CURRENT MAPPING:")
    incorrect_ids = current_ids - complete_ids
    for subcat_id in sorted(incorrect_ids):
        info = CURRENT_MAPPING[subcat_id]
        print(f"  {subcat_id}: {info['category']} - {info['subcategory']} (NOT IN LUMAPRINTS API)")
    print()
    
    print("🎯 PRODUCTS TO ADD:")
    categories = {}
    for subcat_id in sorted(missing_ids):
        info = LUMAPRINTS_SUBCATEGORIES[subcat_id]
        category = info['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(f"{subcat_id}: {info['subcategory']}")
    
    for category, products in categories.items():
        print(f"\n  📁 {category}:")
        for product in products:
            print(f"    {product}")
    
    return missing_ids, incorrect_ids

if __name__ == "__main__":
    missing, incorrect = analyze_gaps()
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"1. Fix {len(incorrect)} incorrect mappings")
    print(f"2. Add {len(missing)} missing products to database")
    print(f"3. Update hierarchical wizard to use all {len(LUMAPRINTS_SUBCATEGORIES)} subcategories")
    print(f"4. Add option codes for frame colors, hanging hardware, etc.")
