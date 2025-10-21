import sqlite3
import re

def migrate_products_to_hierarchical():
    """Migrate existing products to the new hierarchical structure"""
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    # Category mapping to product types and sub-options
    category_mappings = {
        # Canvas Prints (Product Type 1)
        'Canvas - 0.75" Stretched': {'product_type_id': 1, 'sub_option_1_id': 1},  # 0.75" Stretched
        'Canvas - 1.25" Stretched': {'product_type_id': 1, 'sub_option_1_id': 2},  # 1.25" Stretched
        'Canvas - 1.5" Stretched': {'product_type_id': 1, 'sub_option_1_id': 3},   # 1.50" Stretched
        'Canvas - Rolled': {'product_type_id': 1, 'sub_option_1_id': None},        # Rolled (needs new sub-option)
        
        # Framed Canvas Prints (Product Type 2) - Currently only has Maple Wood frame
        'Framed Canvas - 0.75"': {'product_type_id': 2, 'sub_option_1_id': 4, 'sub_option_2_id': 8},   # 0.75" Frame + Maple Wood
        'Framed Canvas - 1.25"': {'product_type_id': 2, 'sub_option_1_id': 5, 'sub_option_2_id': 8},   # 1.25" Frame + Maple Wood
        'Framed Canvas - 1.5"': {'product_type_id': 2, 'sub_option_1_id': 6, 'sub_option_2_id': 8},    # 1.50" Frame + Maple Wood
        
        # Fine Art Paper Prints (Product Type 3)
        'Fine Art Paper - Archival Matte': {'product_type_id': 3, 'sub_option_1_id': 17},      # Archival Matte
        'Fine Art Paper - Hot Press': {'product_type_id': 3, 'sub_option_1_id': 18},           # Hot Press
        'Fine Art Paper - Cold Press': {'product_type_id': 3, 'sub_option_1_id': 19},          # Cold Press
        'Fine Art Paper - Semi-Gloss': {'product_type_id': 3, 'sub_option_1_id': 20},          # Semi-Gloss
        'Fine Art Paper - Metallic': {'product_type_id': 3, 'sub_option_1_id': 21},            # Metallic
        'Fine Art Paper - Glossy': {'product_type_id': 3, 'sub_option_1_id': 22},              # Glossy
        'Fine Art Paper - Somerset Velvet': {'product_type_id': 3, 'sub_option_1_id': 23},     # Somerset Velvet
        
        # Framed Fine Art Paper Prints (Product Type 4) - Default to first frame size and no mat
        'Framed Fine Art - 0.875" Frame': {'product_type_id': 4, 'sub_option_1_id': 24, 'sub_option_2_id': 35},  # 0.875" × 0.875" + No Mat
        'Framed Fine Art - 1.25" Frame': {'product_type_id': 4, 'sub_option_1_id': 25, 'sub_option_2_id': 35},   # Complex frame + No Mat
        
        # Foam-Mounted Fine Art Paper Prints (Product Type 5)
        'Foam Mounted - Archival Matte': {'product_type_id': 5, 'sub_option_1_id': 46},        # Archival Matte
        'Foam Mounted - Hot Press': {'product_type_id': 5, 'sub_option_1_id': 47},             # Hot Press
        'Foam Mounted - Cold Press': {'product_type_id': 5, 'sub_option_1_id': 48},            # Cold Press
        'Foam Mounted - Semi-Gloss': {'product_type_id': 5, 'sub_option_1_id': 49},            # Semi-Gloss
        'Foam Mounted - Metallic': {'product_type_id': 5, 'sub_option_1_id': 50},              # Metallic
        'Foam Mounted - Glossy': {'product_type_id': 5, 'sub_option_1_id': 51},                # Glossy
        'Foam Mounted - Somerset Velvet': {'product_type_id': 5, 'sub_option_1_id': 52},       # Somerset Velvet
        
        # Metal Prints (Product Type 6) - No sub-options
        'Metal Prints': {'product_type_id': 6},
        
        # Peel and Stick Prints (Product Type 7) - No sub-options
        'Peel & Stick': {'product_type_id': 7}
    }
    
    print("Starting product migration to hierarchical structure...")
    
    # Get all categories
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()
    
    migration_stats = {
        'total_products': 0,
        'migrated_products': 0,
        'unmapped_categories': []
    }
    
    for category_id, category_name in categories:
        print(f"\nProcessing category: {category_name}")
        
        if category_name not in category_mappings:
            print(f"  WARNING: No mapping found for category '{category_name}'")
            migration_stats['unmapped_categories'].append(category_name)
            continue
        
        mapping = category_mappings[category_name]
        
        # Get all products in this category
        cursor.execute("SELECT id, name FROM products WHERE category_id = ? AND active = 1", (category_id,))
        products = cursor.fetchall()
        
        print(f"  Found {len(products)} products")
        migration_stats['total_products'] += len(products)
        
        # Update each product with hierarchical mapping
        for product_id, product_name in products:
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
        
        print(f"  Migrated {len(products)} products")
    
    # Add missing "Rolled" sub-option for Canvas Prints
    print("\nAdding missing 'Rolled' sub-option for Canvas Prints...")
    cursor.execute("""
        INSERT INTO sub_options (product_type_id, level, option_type, name, value, display_order)
        VALUES (1, 1, 'mounting', 'Mounting Size', 'Rolled', 4)
    """)
    rolled_sub_option_id = cursor.lastrowid
    
    # Update Canvas - Rolled products with the new sub-option
    cursor.execute("SELECT id FROM categories WHERE name = 'Canvas - Rolled'")
    rolled_category = cursor.fetchone()
    if rolled_category:
        cursor.execute("""
            UPDATE products 
            SET sub_option_1_id = ? 
            WHERE category_id = ? AND product_type_id = 1
        """, (rolled_sub_option_id, rolled_category[0]))
        print(f"  Updated Canvas - Rolled products with sub_option_1_id = {rolled_sub_option_id}")
    
    conn.commit()
    
    print(f"\n=== MIGRATION COMPLETE ===")
    print(f"Total products processed: {migration_stats['total_products']}")
    print(f"Successfully migrated: {migration_stats['migrated_products']}")
    print(f"Unmapped categories: {len(migration_stats['unmapped_categories'])}")
    
    if migration_stats['unmapped_categories']:
        print("Unmapped categories:")
        for cat in migration_stats['unmapped_categories']:
            print(f"  - {cat}")
    
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
    
    conn.close()
    print("\nMigration completed successfully!")

if __name__ == "__main__":
    migrate_products_to_hierarchical()
