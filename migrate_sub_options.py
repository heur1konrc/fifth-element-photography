#!/usr/bin/env python3
"""
Database Migration Route - Apply Sub-Option Fix
This creates a web route that can be called to apply the sub-option assignments fix
on the live Railway server.
"""

from flask import jsonify
import sqlite3
import traceback

def migrate_sub_options_route():
    """
    Web route to apply sub-option assignments fix to the live database
    Call this route after deployment to fix the size selection issue
    """
    try:
        print("Starting sub-option migration...")
        
        conn = sqlite3.connect('lumaprints_pricing.db')
        cursor = conn.cursor()
        
        # Check if migration is needed
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(sub_option_1_id) as has_sub_1,
                   COUNT(sub_option_2_id) as has_sub_2
            FROM products WHERE active = 1
        """)
        
        stats = cursor.fetchone()
        total, has_sub_1, has_sub_2 = stats
        
        # If most products already have sub-options, skip migration
        if has_sub_1 > (total * 0.8):  # 80% already have sub-options
            return jsonify({
                'success': True,
                'message': 'Migration not needed - sub-options already assigned',
                'stats': {
                    'total_products': total,
                    'has_sub_option_1': has_sub_1,
                    'has_sub_option_2': has_sub_2
                }
            })
        
        print(f"Migration needed: {total} products, {has_sub_1} have sub_option_1, {has_sub_2} have sub_option_2")
        
        # Get product type mappings
        cursor.execute("SELECT id, name FROM product_types ORDER BY name")
        product_types = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Get sub-option mappings
        cursor.execute("SELECT id, name, level FROM sub_options ORDER BY level, name")
        sub_options = {}
        for row in cursor.fetchall():
            option_id, name, level = row
            if level not in sub_options:
                sub_options[level] = {}
            sub_options[level][name] = option_id
        
        print(f"Found product types: {list(product_types.keys())}")
        print(f"Found sub-options: {sub_options}")
        
        # Store original products before clearing
        cursor.execute("""
            SELECT id, category_id, name, size, cost_price, description, product_type_id,
                   lumaprints_subcategory_id, lumaprints_options, lumaprints_frame_option
            FROM products 
            WHERE active = 1
        """)
        base_products = cursor.fetchall()
        
        # Clear existing products
        cursor.execute("DELETE FROM products")
        
        # Assignment rules based on Lumaprints structure
        assignments = []
        
        # 1 Option Products - Canvas Prints (mounting depth)
        if 'Canvas Prints' in product_types:
            product_type_id = product_types['Canvas Prints']
            mounting_options = [1, 2, 3]  # Mounting Size options
            
            for mounting_id in mounting_options:
                assignments.append((product_type_id, mounting_id, None, 'Canvas Prints'))
        
        # 1 Option Products - Fine Art Paper Prints (paper type)
        if 'Fine Art Paper Prints' in product_types:
            product_type_id = product_types['Fine Art Paper Prints']
            # Use first Paper Type option
            paper_type_id = sub_options.get(1, {}).get('Paper Type', 49)
            assignments.append((product_type_id, paper_type_id, None, 'Fine Art Paper Prints'))
        
        # 1 Option Products - Foam-Mounted Fine Art Paper Prints
        if 'Foam-Mounted Fine Art Paper Prints' in product_types:
            product_type_id = product_types['Foam-Mounted Fine Art Paper Prints']
            paper_type_id = sub_options.get(1, {}).get('Paper Type', 49)
            assignments.append((product_type_id, paper_type_id, None, 'Foam-Mounted Fine Art Paper Prints'))
        
        # 1 Option Products - Peel and Stick Prints
        if 'Peel and Stick Prints' in product_types:
            product_type_id = product_types['Peel and Stick Prints']
            paper_type_id = sub_options.get(1, {}).get('Paper Type', 49)
            assignments.append((product_type_id, paper_type_id, None, 'Peel and Stick Prints'))
        
        # 2 Option Products - Framed Canvas Prints (frame size + color)
        if 'Framed Canvas Prints' in product_types:
            product_type_id = product_types['Framed Canvas Prints']
            frame_size_id = sub_options.get(1, {}).get('Frame Size', 32)
            frame_color_id = sub_options.get(2, {}).get('Frame Color', 14)
            assignments.append((product_type_id, frame_size_id, frame_color_id, 'Framed Canvas Prints'))
        
        # 2 Option Products - Framed Fine Art Paper Prints (frame + mat)
        if 'Framed Fine Art Paper Prints' in product_types:
            product_type_id = product_types['Framed Fine Art Paper Prints']
            frame_size_id = sub_options.get(1, {}).get('Frame Size', 32)
            mat_size_id = sub_options.get(2, {}).get('Mat Size', 42)
            assignments.append((product_type_id, frame_size_id, mat_size_id, 'Framed Fine Art Paper Prints'))
        
        print(f"Created {len(assignments)} assignment rules")
        
        # Create products with sub-option assignments
        product_id = 1
        created_count = 0
        
        for assignment in assignments:
            product_type_id, sub_option_1_id, sub_option_2_id, type_name = assignment
            
            # Find base products for this product type
            matching_products = [p for p in base_products if p[6] == product_type_id]
            
            for base_product in matching_products:
                cursor.execute("""
                    INSERT INTO products (
                        id, category_id, name, size, cost_price, description, active,
                        product_type_id, sub_option_1_id, sub_option_2_id,
                        lumaprints_subcategory_id, lumaprints_options, lumaprints_frame_option
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id,
                    base_product[1],  # category_id
                    base_product[2],  # name
                    base_product[3],  # size
                    base_product[4],  # cost_price
                    base_product[5],  # description
                    product_type_id,
                    sub_option_1_id,
                    sub_option_2_id,
                    base_product[7],  # lumaprints_subcategory_id
                    base_product[8],  # lumaprints_options
                    base_product[9]   # lumaprints_frame_option
                ))
                
                product_id += 1
                created_count += 1
        
        # Handle 0-option products (Metal Prints, Rolled Canvas)
        zero_option_types = ['Metal Prints', 'Rolled Canvas Prints']
        zero_option_product_types = [product_types[name] for name in zero_option_types if name in product_types]
        
        for product_type_id in zero_option_product_types:
            matching_products = [p for p in base_products if p[6] == product_type_id]
            
            for base_product in matching_products:
                cursor.execute("""
                    INSERT INTO products (
                        id, category_id, name, size, cost_price, description, active,
                        product_type_id, sub_option_1_id, sub_option_2_id,
                        lumaprints_subcategory_id, lumaprints_options, lumaprints_frame_option
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, NULL, NULL, ?, ?, ?)
                """, (
                    product_id,
                    base_product[1],  # category_id
                    base_product[2],  # name
                    base_product[3],  # size
                    base_product[4],  # cost_price
                    base_product[5],  # description
                    product_type_id,
                    base_product[7],  # lumaprints_subcategory_id
                    base_product[8],  # lumaprints_options
                    base_product[9]   # lumaprints_frame_option
                ))
                
                product_id += 1
                created_count += 1
        
        conn.commit()
        
        # Get final stats
        cursor.execute("""
            SELECT 
                pt.name as product_type,
                COUNT(*) as total_products,
                COUNT(p.sub_option_1_id) as has_sub_option_1,
                COUNT(p.sub_option_2_id) as has_sub_option_2
            FROM products p
            JOIN product_types pt ON p.product_type_id = pt.id
            WHERE p.active = 1
            GROUP BY pt.name
            ORDER BY pt.name
        """)
        
        results = cursor.fetchall()
        results_dict = {}
        for row in results:
            results_dict[row[0]] = {
                'total': row[1],
                'sub_option_1': row[2],
                'sub_option_2': row[3]
            }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Sub-option migration completed successfully! Created {created_count} products.',
            'results': results_dict,
            'total_created': created_count
        })
        
    except Exception as e:
        error_msg = f"Migration failed: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'traceback': traceback.format_exc()
        }), 500
