from flask import Blueprint, jsonify
import sqlite3
import os

add_metal_bp = Blueprint('add_metal', __name__)

@add_metal_bp.route('/api/admin/add-metal-prints', methods=['POST'])
def add_metal_prints():
    """Migration endpoint to add Metal prints to the database"""
    
    # Get database path
    if os.path.exists('/data'):
        db_path = '/data/print_ordering.db'
    else:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'print_ordering.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add Metal category
        cursor.execute("""
            INSERT OR IGNORE INTO product_categories (category_name, display_order) 
            VALUES ('Metal', 5)
        """)
        
        # Add Glossy White Metal subcategory
        cursor.execute("""
            INSERT OR IGNORE INTO product_subcategories (category_id, subcategory_name, display_name, display_order)
            SELECT category_id, 'glossy_white_metal', 'Glossy White Metal', 1
            FROM product_categories WHERE category_name = 'Metal'
        """)
        
        # Add Glossy Silver Metal subcategory
        cursor.execute("""
            INSERT OR IGNORE INTO product_subcategories (category_id, subcategory_name, display_name, display_order)
            SELECT category_id, 'glossy_silver_metal', 'Glossy Silver Metal', 2
            FROM product_categories WHERE category_name = 'Metal'
        """)
        
        # 3:2 sizes and prices
        standard_sizes = [
            ('8×12"', 33.95),
            ('12×18"', 59.77),
            ('16×24"', 95.21),
            ('24×36"', 188.32),
            ('32×48"', 316.76),
            ('40×60"', 480.27)
        ]
        
        # 1:1 sizes and prices
        square_sizes = [
            ('12×12"', 43.94),
            ('20×20"', 98.15),
            ('24×24"', 132.45),
            ('30×30"', 194.93),
            ('36×36"', 270.62)
        ]
        
        # Add pricing for Glossy White Metal
        for subcategory_name in ['glossy_white_metal', 'glossy_silver_metal']:
            # Add 3:2 sizes
            for size_name, cost in standard_sizes:
                cursor.execute("""
                    INSERT OR IGNORE INTO base_pricing (subcategory_id, size_id, cost_price, is_available)
                    SELECT 
                        ps.subcategory_id,
                        pz.size_id,
                        ?,
                        TRUE
                    FROM product_subcategories ps
                    JOIN product_categories pc ON ps.category_id = pc.category_id
                    JOIN print_sizes pz ON pz.aspect_ratio_id = (SELECT aspect_ratio_id FROM aspect_ratios WHERE display_name = 'Standard')
                    WHERE pc.category_name = 'Metal' 
                    AND ps.subcategory_name = ?
                    AND pz.size_name = ?
                """, (cost, subcategory_name, size_name))
            
            # Add 1:1 sizes
            for size_name, cost in square_sizes:
                cursor.execute("""
                    INSERT OR IGNORE INTO base_pricing (subcategory_id, size_id, cost_price, is_available)
                    SELECT 
                        ps.subcategory_id,
                        pz.size_id,
                        ?,
                        TRUE
                    FROM product_subcategories ps
                    JOIN product_categories pc ON ps.category_id = pc.category_id
                    JOIN print_sizes pz ON pz.aspect_ratio_id = (SELECT aspect_ratio_id FROM aspect_ratios WHERE display_name = 'Square')
                    WHERE pc.category_name = 'Metal' 
                    AND ps.subcategory_name = ?
                    AND pz.size_name = ?
                """, (cost, subcategory_name, size_name))
        
        conn.commit()
        
        # Verify what was added
        cursor.execute("""
            SELECT ps.display_name, COUNT(bp.pricing_id) as price_count
            FROM product_subcategories ps
            JOIN product_categories pc ON ps.category_id = pc.category_id
            LEFT JOIN base_pricing bp ON ps.subcategory_id = bp.subcategory_id
            WHERE pc.category_name = 'Metal'
            GROUP BY ps.subcategory_id
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Metal prints added successfully',
            'subcategories': [{'name': row[0], 'price_count': row[1]} for row in results]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
