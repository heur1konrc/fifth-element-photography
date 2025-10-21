#!/usr/bin/env python3
"""
Assign Product Types Script
Assigns correct product_type_id to all 654 products based on their names
"""

import sqlite3
import re

def assign_product_types():
    """Assign product_type_id to products based on their names"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    print("🏷️  ASSIGNING PRODUCT TYPES TO ALL PRODUCTS")
    print("=" * 45)
    
    # Get products without product_type_id
    cursor.execute('''
        SELECT id, name 
        FROM products 
        WHERE product_type_id IS NULL
        ORDER BY name
    ''')
    
    products_without_type = cursor.fetchall()
    print(f"📊 Found {len(products_without_type)} products without product_type_id")
    
    # Product type mapping rules based on name patterns
    type_assignments = {
        1: [],  # Canvas Prints
        2: [],  # Framed Canvas Prints  
        3: [],  # Fine Art Paper Prints
        4: [],  # Framed Fine Art Paper Prints
        5: [],  # Foam-Mounted Fine Art Paper Prints
        6: [],  # Metal Prints
        7: [],  # Peel and Stick Prints
    }
    
    unassigned = []
    
    for prod_id, prod_name in products_without_type:
        assigned_type = None
        
        # CANVAS PRINTS (Type 1)
        if re.match(r'^Canvas \d+\.?\d*"', prod_name):
            assigned_type = 1
        
        # FRAMED CANVAS PRINTS (Type 2) 
        elif 'Framed Canvas' in prod_name:
            assigned_type = 2
        
        # FINE ART PAPER PRINTS (Type 3)
        elif prod_name.startswith('Fine Art ') and 'Framed' not in prod_name:
            assigned_type = 3
        
        # FRAMED FINE ART PAPER PRINTS (Type 4)
        elif 'Framed Fine Art' in prod_name:
            assigned_type = 4
        
        # FOAM-MOUNTED FINE ART PAPER PRINTS (Type 5)
        elif 'Foam Mounted' in prod_name or 'Foam-Mounted' in prod_name:
            assigned_type = 5
        
        # METAL PRINTS (Type 6)
        elif 'Metal Print' in prod_name or prod_name.startswith('Metal '):
            assigned_type = 6
        
        # PEEL AND STICK PRINTS (Type 7)
        elif 'Peel & Stick' in prod_name or 'Peel and Stick' in prod_name:
            assigned_type = 7
        
        if assigned_type:
            type_assignments[assigned_type].append((prod_id, prod_name))
        else:
            unassigned.append((prod_id, prod_name))
    
    # Show assignment summary
    print(f"\n📋 ASSIGNMENT SUMMARY:")
    type_names = {
        1: 'Canvas Prints',
        2: 'Framed Canvas Prints', 
        3: 'Fine Art Paper Prints',
        4: 'Framed Fine Art Paper Prints',
        5: 'Foam-Mounted Fine Art Paper Prints',
        6: 'Metal Prints',
        7: 'Peel and Stick Prints'
    }
    
    total_assigned = 0
    for type_id, products in type_assignments.items():
        count = len(products)
        total_assigned += count
        if count > 0:
            print(f"   Type {type_id} ({type_names[type_id]}): {count} products")
            # Show first 3 examples
            for i, (_, name) in enumerate(products[:3]):
                print(f"     • {name}")
            if count > 3:
                print(f"     ... and {count-3} more")
    
    print(f"\n   ✅ Total assigned: {total_assigned}")
    print(f"   ⚠️  Unassigned: {len(unassigned)}")
    
    if unassigned:
        print(f"\n❓ UNASSIGNED PRODUCTS:")
        for prod_id, name in unassigned[:10]:
            print(f"   • {name}")
        if len(unassigned) > 10:
            print(f"   ... and {len(unassigned)-10} more")
    
    # Apply the assignments
    print(f"\n🔄 APPLYING ASSIGNMENTS TO DATABASE...")
    
    for type_id, products in type_assignments.items():
        if products:
            product_ids = [str(prod_id) for prod_id, _ in products]
            cursor.execute(f'''
                UPDATE products 
                SET product_type_id = {type_id}
                WHERE id IN ({','.join(product_ids)})
            ''')
            print(f"   ✅ Updated {len(products)} products to type {type_id}")
    
    conn.commit()
    
    # Verify the results
    print(f"\n🔍 VERIFICATION:")
    cursor.execute('SELECT COUNT(*) FROM products WHERE product_type_id IS NULL')
    remaining_null = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE product_type_id IS NOT NULL')
    assigned_count = cursor.fetchone()[0]
    
    print(f"   📊 Products with assigned types: {assigned_count}")
    print(f"   📊 Products still unassigned: {remaining_null}")
    
    # Show final type distribution
    cursor.execute('''
        SELECT pt.name, COUNT(p.id) as count
        FROM products p
        JOIN product_types pt ON p.product_type_id = pt.id
        GROUP BY pt.name
        ORDER BY count DESC
    ''')
    
    print(f"\n📊 FINAL TYPE DISTRIBUTION:")
    for type_name, count in cursor.fetchall():
        print(f"   {type_name}: {count} products")
    
    conn.close()
    
    return total_assigned, len(unassigned)

def main():
    """Main execution"""
    print("🚀 PRODUCT TYPE ASSIGNMENT")
    print("=" * 30)
    
    assigned, unassigned = assign_product_types()
    
    print(f"\n🎉 Product type assignment completed!")
    print(f"   ✅ Assigned: {assigned} products")
    print(f"   ⚠️  Unassigned: {unassigned} products")
    print(f"\nReady to map all products to Lumaprints codes!")

if __name__ == "__main__":
    main()
