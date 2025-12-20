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
        
        # Step 1: Add Metal category
        cursor.execute("""
            INSERT INTO product_categories (category_name, display_order) 
            VALUES ('Metal', 5)
        """)
        metal_category_id = cursor.lastrowid
        
        # Step 2: Add Glossy White Metal subcategory
        cursor.execute("""
            INSERT INTO product_subcategories (category_id, subcategory_name, display_name, display_order)
            VALUES (?, 'glossy_white_metal', 'Glossy White Metal', 1)
        """, (metal_category_id,))
        white_subcategory_id = cursor.lastrowid
        
        # Step 3: Add Glossy Silver Metal subcategory
        cursor.execute("""
            INSERT INTO product_subcategories (category_id, subcategory_name, display_name, display_order)
            VALUES (?, 'glossy_silver_metal', 'Glossy Silver Metal', 2)
        """, (metal_category_id,))
        silver_subcategory_id = cursor.lastrowid
        
        # Get aspect ratio IDs
        cursor.execute("SELECT aspect_ratio_id FROM aspect_ratios WHERE display_name = '3:2'")
        aspect_32_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT aspect_ratio_id FROM aspect_ratios WHERE display_name = '1:1'")
        aspect_11_id = cursor.fetchone()[0]
        
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
        
        # Add pricing for both subcategories
        for subcategory_id in [white_subcategory_id, silver_subcategory_id]:
            # Add 3:2 sizes
            for size_name, cost in standard_sizes:
                cursor.execute("""
                    SELECT size_id FROM print_sizes 
                    WHERE aspect_ratio_id = ? AND size_name = ?
                """, (aspect_32_id, size_name))
                size_result = cursor.fetchone()
                if size_result:
                    size_id = size_result[0]
                    cursor.execute("""
                        INSERT INTO base_pricing (subcategory_id, size_id, cost_price, is_available)
                        VALUES (?, ?, ?, TRUE)
                    """, (subcategory_id, size_id, cost))
            
            # Add 1:1 sizes
            for size_name, cost in square_sizes:
                cursor.execute("""
                    SELECT size_id FROM print_sizes 
                    WHERE aspect_ratio_id = ? AND size_name = ?
                """, (aspect_11_id, size_name))
                size_result = cursor.fetchone()
                if size_result:
                    size_id = size_result[0]
                    cursor.execute("""
                        INSERT INTO base_pricing (subcategory_id, size_id, cost_price, is_available)
                        VALUES (?, ?, ?, TRUE)
                    """, (subcategory_id, size_id, cost))
        
        conn.commit()
        
        # Verify what was added
        cursor.execute("""
            SELECT ps.display_name, COUNT(bp.pricing_id) as price_count
            FROM product_subcategories ps
            LEFT JOIN base_pricing bp ON ps.subcategory_id = bp.subcategory_id
            WHERE ps.subcategory_id IN (?, ?)
            GROUP BY ps.subcategory_id
        """, (white_subcategory_id, silver_subcategory_id))
        
        results = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Metal prints added successfully',
            'metal_category_id': metal_category_id,
            'subcategories': [{'name': row[0], 'price_count': row[1]} for row in results]
        })
    
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
