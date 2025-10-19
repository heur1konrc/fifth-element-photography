"""
Initialize the live database with all required tables and data
This script can be run on the live server to set up the pricing system
"""
import sqlite3
import os

def initialize_database():
    """Initialize the complete database with all tables and sample data"""
    
    # Use the database path that should exist on the server
    db_path = 'lumaprints_pricing.db'
    
    print(f"Initializing database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Create global_settings table
        print("Creating global_settings table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_settings (
                id INTEGER PRIMARY KEY,
                markup_percentage DECIMAL(5,2) DEFAULT 123.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default global settings
        cursor.execute('SELECT COUNT(*) FROM global_settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO global_settings (markup_percentage) VALUES (123.0)')
            print("Inserted default global settings (123% markup)")
        
        # 2. Create categories table
        print("Creating categories table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. Create products table
        print("Creating products table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name VARCHAR(200) NOT NULL,
                size VARCHAR(50) NOT NULL,
                cost_price DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # 4. Create product_variants table
        print("Creating product_variants table...")
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
        
        # 5. Insert essential categories if they don't exist
        essential_categories = [
            ('Canvas - 0.75" Stretched', 'Canvas prints with 0.75 inch stretching'),
            ('Canvas - 1.25" Stretched', 'Canvas prints with 1.25 inch stretching'),
            ('Canvas - 1.5" Stretched', 'Canvas prints with 1.5 inch stretching'),
            ('Framed Canvas - 0.75"', 'Framed canvas with 0.75 inch frame'),
            ('Framed Canvas - 1.25"', 'Framed canvas with 1.25 inch frame'),
            ('Framed Canvas - 1.5"', 'Framed canvas with 1.5 inch frame')
        ]
        
        for cat_name, cat_desc in essential_categories:
            cursor.execute('SELECT id FROM categories WHERE name = ?', (cat_name,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)', (cat_name, cat_desc))
                print(f"Created category: {cat_name}")
        
        # 6. Insert sample products if none exist
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            print("Adding sample products...")
            
            # Get category IDs
            categories_map = {}
            for cat_name, _ in essential_categories:
                cursor.execute('SELECT id FROM categories WHERE name = ?', (cat_name,))
                result = cursor.fetchone()
                if result:
                    categories_map[cat_name] = result[0]
            
            # Sample products with realistic pricing
            sample_products = [
                # Stretched Canvas 0.75"
                (categories_map.get('Canvas - 0.75" Stretched'), 'Canvas 0.75"', '8×10"', 15.39),
                (categories_map.get('Canvas - 0.75" Stretched'), 'Canvas 0.75"', '11×14"', 18.76),
                (categories_map.get('Canvas - 0.75" Stretched'), 'Canvas 0.75"', '16×20"', 24.13),
                
                # Stretched Canvas 1.25"
                (categories_map.get('Canvas - 1.25" Stretched'), 'Canvas 1.25"', '8×10"', 16.23),
                (categories_map.get('Canvas - 1.25" Stretched'), 'Canvas 1.25"', '11×14"', 19.80),
                (categories_map.get('Canvas - 1.25" Stretched'), 'Canvas 1.25"', '16×20"', 25.50),
                
                # Stretched Canvas 1.5"
                (categories_map.get('Canvas - 1.5" Stretched'), 'Canvas 1.5"', '8×10"', 18.76),
                (categories_map.get('Canvas - 1.5" Stretched'), 'Canvas 1.5"', '11×14"', 22.89),
                (categories_map.get('Canvas - 1.5" Stretched'), 'Canvas 1.5"', '16×20"', 29.45),
                
                # Framed Canvas 1.5" (these will get variants)
                (categories_map.get('Framed Canvas - 1.5"'), 'Framed Canvas 1.5"', '8×10"', 31.25),
                (categories_map.get('Framed Canvas - 1.5"'), 'Framed Canvas 1.5"', '11×14"', 38.50),
                (categories_map.get('Framed Canvas - 1.5"'), 'Framed Canvas 1.5"', '16×20"', 49.75),
            ]
            
            for category_id, name, size, cost in sample_products:
                if category_id:
                    cursor.execute('''
                        INSERT INTO products (category_id, name, size, cost_price)
                        VALUES (?, ?, ?, ?)
                    ''', (category_id, name, size, cost))
            
            print(f"Added {len(sample_products)} sample products")
        
        # 7. Add variants for Framed Canvas 1.5" products
        framed_15_category_id = categories_map.get('Framed Canvas - 1.5"')
        if framed_15_category_id:
            # Get Framed Canvas 1.5" products
            framed_products = cursor.execute('''
                SELECT id FROM products WHERE category_id = ?
            ''', (framed_15_category_id,)).fetchall()
            
            # Frame variants
            frame_variants = [
                ("Maple Wood", "Maple Wood Floating Frame", True),
                ("Espresso", "Espresso Floating Frame", False),
                ("Natural Wood", "Natural Wood Floating Frame", False),
                ("Oak", "Oak Floating Frame", False),
                ("Gold", "Gold Floating Frame", False),
                ("Silver", "Silver Floating Frame", False),
                ("White", "White Floating Frame", False),
                ("Black", "Black Floating Frame", False)
            ]
            
            for product_row in framed_products:
                product_id = product_row[0]
                
                # Check if variants already exist
                cursor.execute('SELECT COUNT(*) FROM product_variants WHERE product_id = ?', (product_id,))
                if cursor.fetchone()[0] == 0:
                    # Add variants
                    for variant_name, variant_desc, is_default in frame_variants:
                        cursor.execute('''
                            INSERT INTO product_variants (product_id, variant_name, variant_description, price_modifier, is_default)
                            VALUES (?, ?, ?, 0.00, ?)
                        ''', (product_id, variant_name, variant_desc, is_default))
            
            print("Added frame variants for Framed Canvas 1.5\" products")
        
        conn.commit()
        
        # 8. Verify the setup
        print("\n=== Database Setup Complete ===")
        
        # Count records
        cursor.execute('SELECT COUNT(*) FROM categories')
        cat_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM products')
        prod_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM product_variants')
        var_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT markup_percentage FROM global_settings LIMIT 1')
        markup = cursor.fetchone()[0]
        
        print(f"Categories: {cat_count}")
        print(f"Products: {prod_count}")
        print(f"Variants: {var_count}")
        print(f"Global Markup: {markup}%")
        
        print("\nDatabase initialization successful!")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = initialize_database()
    if success:
        print("✅ Database ready for use!")
    else:
        print("❌ Database initialization failed!")
