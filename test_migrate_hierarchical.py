import sqlite3

def test_migrate_products():
    """Test migration with only a few products from each category"""
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    # Category mapping to product types and sub-options
    category_mappings = {
        # Canvas Prints (Product Type 1)
        'Canvas - 0.75" Stretched': {'product_type_id': 1, 'sub_option_1_id': 1},  # 0.75" Stretched
        'Canvas - 1.25" Stretched': {'product_type_id': 1, 'sub_option_1_id': 2},  # 1.25" Stretched
        'Canvas - 1.5" Stretched': {'product_type_id': 1, 'sub_option_1_id': 3},   # 1.50" Stretched
        
        # Framed Canvas Prints (Product Type 2) - Using Maple Wood frame
        'Framed Canvas - 1.5"': {'product_type_id': 2, 'sub_option_1_id': 6, 'sub_option_2_id': 8},    # 1.50" Frame + Maple Wood
        
        # Fine Art Paper Prints (Product Type 3)
        'Fine Art Paper - Archival Matte': {'product_type_id': 3, 'sub_option_1_id': 17},      # Archival Matte
        'Fine Art Paper - Hot Press': {'product_type_id': 3, 'sub_option_1_id': 18},           # Hot Press
        
        # Metal Prints (Product Type 6) - No sub-options
        'Metal Prints': {'product_type_id': 6},
        
        # Peel and Stick Prints (Product Type 7) - No sub-options
        'Peel & Stick': {'product_type_id': 7}
    }
    
    print("Starting TEST migration with limited products...")
    
    migration_stats = {
        'total_products': 0,
        'migrated_products': 0,
        'categories_tested': 0
    }
    
    for category_name, mapping in category_mappings.items():
        print(f"\nTesting category: {category_name}")
        
        # Get category ID
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        category_result = cursor.fetchone()
        
        if not category_result:
            print(f"  WARNING: Category '{category_name}' not found")
            continue
        
        category_id = category_result[0]
        
        # Get first 3 products from this category for testing
        cursor.execute("""
            SELECT id, name, size 
            FROM products 
            WHERE category_id = ? AND active = 1 
            ORDER BY id 
            LIMIT 3
        """, (category_id,))
        products = cursor.fetchall()
        
        print(f"  Found {len(products)} products (testing with 3 max)")
        migration_stats['total_products'] += len(products)
        migration_stats['categories_tested'] += 1
        
        # Update each test product with hierarchical mapping
        for product_id, product_name, product_size in products:
            update_query = "UPDATE products SET product_type_id = ?"
            update_params = [mapping['product_type_id']]
            
            if mapping.get('sub_option_1_id'):
                update_query += ", sub_option_1_id = ?"
                update_params.append(mapping['sub_option_1_id'])
            
            if mapping.get('sub_option_2_id'):
                update_query += ", sub_option_2_id = ?"
                update_params.append(mapping['sub_option_2_id'])
            
            update_query += " WHERE id = ?"
            update_params.append(product_id)
            
            cursor.execute(update_query, update_params)
            migration_stats['migrated_products'] += 1
            
            print(f"    ✓ {product_name} ({product_size})")
    
    conn.commit()
    
    print(f"\n=== TEST MIGRATION COMPLETE ===")
    print(f"Categories tested: {migration_stats['categories_tested']}")
    print(f"Total products migrated: {migration_stats['migrated_products']}")
    
    # Verification
    print(f"\n=== VERIFICATION ===")
    cursor.execute("""
        SELECT pt.name, COUNT(p.id) as product_count
        FROM product_types pt
        LEFT JOIN products p ON pt.id = p.product_type_id AND p.active = 1
        GROUP BY pt.id, pt.name
        ORDER BY pt.display_order
    """)
    
    for product_type, count in cursor.fetchall():
        print(f"{product_type}: {count} products")
    
    # Show sample migrated products
    print(f"\n=== SAMPLE MIGRATED PRODUCTS ===")
    cursor.execute("""
        SELECT p.name, p.size, pt.name as product_type, 
               so1.value as sub_option_1, so2.value as sub_option_2
        FROM products p
        JOIN product_types pt ON p.product_type_id = pt.id
        LEFT JOIN sub_options so1 ON p.sub_option_1_id = so1.id
        LEFT JOIN sub_options so2 ON p.sub_option_2_id = so2.id
        WHERE p.product_type_id IS NOT NULL
        ORDER BY pt.display_order, p.name
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        product_name, size, product_type, sub1, sub2 = row
        options = []
        if sub1: options.append(sub1)
        if sub2: options.append(sub2)
        options_str = " • ".join(options) if options else "No options"
        print(f"  {product_name} ({size}) → {product_type} → {options_str}")
    
    conn.close()
    print("\nTest migration completed successfully!")
    print("\nYou can now test the hierarchical system at:")
    print("https://fifthelement.photos/hierarchical_order_form?image=https://fifthelement.photos/images/MG_0010.jpg")

if __name__ == "__main__":
    test_migrate_products()
