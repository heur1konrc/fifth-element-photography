#!/usr/bin/env python3
"""
Direct Fix for Canvas Sub-Options
Simple approach: Update existing Canvas products to have proper sub_option_1_id values
"""

from flask import jsonify
import sqlite3

def fix_canvas_sub_options_route():
    """Direct fix for Canvas products sub-option assignments"""
    try:
        conn = sqlite3.connect('lumaprints_pricing.db')
        cursor = conn.cursor()
        
        # First, check current state
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(sub_option_1_id) as has_sub_1
            FROM products 
            WHERE product_type_id = 1 AND active = 1
        """)
        
        before_stats = cursor.fetchone()
        
        # Update all Canvas Prints (product_type_id = 1) to have sub_option_1_id = 1 (0.75" mounting)
        cursor.execute("""
            UPDATE products 
            SET sub_option_1_id = 1 
            WHERE product_type_id = 1 AND active = 1
        """)
        
        canvas_updated = cursor.rowcount
        
        # Update all Fine Art Paper Prints (product_type_id = 3) to have sub_option_1_id = 49 (Paper Type)
        cursor.execute("""
            UPDATE products 
            SET sub_option_1_id = 49 
            WHERE product_type_id = 3 AND active = 1
        """)
        
        fine_art_updated = cursor.rowcount
        
        # Update all Foam-Mounted Fine Art Paper Prints (product_type_id = 5) to have sub_option_1_id = 49
        cursor.execute("""
            UPDATE products 
            SET sub_option_1_id = 49 
            WHERE product_type_id = 5 AND active = 1
        """)
        
        foam_updated = cursor.rowcount
        
        # Update all Framed Canvas Prints (product_type_id = 2) to have both sub-options
        cursor.execute("""
            UPDATE products 
            SET sub_option_1_id = 32, sub_option_2_id = 14 
            WHERE product_type_id = 2 AND active = 1
        """)
        
        framed_canvas_updated = cursor.rowcount
        
        # Update all Framed Fine Art Paper Prints (product_type_id = 4) to have both sub-options
        cursor.execute("""
            UPDATE products 
            SET sub_option_1_id = 32, sub_option_2_id = 42 
            WHERE product_type_id = 4 AND active = 1
        """)
        
        framed_fine_art_updated = cursor.rowcount
        
        conn.commit()
        
        # Check final state
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
        
        final_stats = []
        for row in cursor.fetchall():
            final_stats.append({
                'product_type': row[0],
                'total': row[1],
                'has_sub_1': row[2],
                'has_sub_2': row[3]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Direct sub-option fix completed',
            'before_stats': {
                'canvas_total': before_stats[0],
                'canvas_had_sub_1': before_stats[1]
            },
            'updates': {
                'canvas_updated': canvas_updated,
                'fine_art_updated': fine_art_updated,
                'foam_updated': foam_updated,
                'framed_canvas_updated': framed_canvas_updated,
                'framed_fine_art_updated': framed_fine_art_updated
            },
            'final_stats': final_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
