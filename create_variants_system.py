"""
Create product variants system for handling frame options
"""
import sqlite3

def create_variants_system():
    """Create the variants table and add frame options for 1.5" Framed Canvas"""
    
    conn = sqlite3.connect('lumaprints_pricing.db')
    cursor = conn.cursor()
    
    # Create product_variants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            variant_name VARCHAR(100) NOT NULL,
            variant_description TEXT,
            price_modifier DECIMAL(10,2) DEFAULT 0.00,
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')
    
    # Get all 1.5" Framed Canvas products
    framed_canvas_products = cursor.execute('''
        SELECT p.id, p.name, p.size 
        FROM products p 
        JOIN categories c ON p.category_id = c.id 
        WHERE c.name = 'Framed Canvas - 1.5"'
    ''').fetchall()
    
    print(f"Found {len(framed_canvas_products)} Framed Canvas - 1.5\" products")
    
    # Frame variants for 1.5" Framed Canvas (from the image)
    frame_variants = [
        ("Maple Wood", "Maple Wood Floating Frame", True),  # Default
        ("Espresso", "Espresso Floating Frame", False),
        ("Natural Wood", "Natural Wood Floating Frame", False),
        ("Oak", "Oak Floating Frame", False),
        ("Gold", "Gold Floating Frame", False),
        ("Silver", "Silver Floating Frame", False),
        ("White", "White Floating Frame", False),
        ("Black", "Black Floating Frame", False)
    ]
    
    # Add variants for each 1.5" Framed Canvas product
    for product_id, product_name, size in framed_canvas_products:
        print(f"Adding variants for: {product_name} ({size})")
        
        for variant_name, variant_description, is_default in frame_variants:
            cursor.execute('''
                INSERT INTO product_variants (product_id, variant_name, variant_description, price_modifier, is_default)
                VALUES (?, ?, ?, 0.00, ?)
            ''', (product_id, variant_name, variant_description, is_default))
    
    conn.commit()
    
    # Verify the variants were created
    variant_count = cursor.execute('SELECT COUNT(*) FROM product_variants').fetchone()[0]
    print(f"Created {variant_count} product variants")
    
    # Show sample variants
    sample_variants = cursor.execute('''
        SELECT p.name, p.size, pv.variant_name, pv.variant_description, pv.is_default
        FROM product_variants pv
        JOIN products p ON pv.product_id = p.id
        LIMIT 10
    ''').fetchall()
    
    print("\nSample variants created:")
    for name, size, variant_name, variant_desc, is_default in sample_variants:
        default_marker = " (DEFAULT)" if is_default else ""
        print(f"  {name} {size} - {variant_name}{default_marker}")
    
    conn.close()
    print("\nVariants system created successfully!")

if __name__ == "__main__":
    create_variants_system()
