#!/usr/bin/env python3
"""
Debug Sub-Options - Check actual database state
"""

from flask import jsonify
import sqlite3

def debug_sub_options_route():
    """Debug route to check actual sub-option assignments in database"""
    try:
        conn = sqlite3.connect('lumaprints_pricing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get sample products for each product type with their sub-option assignments
        cursor.execute("""
            SELECT 
                pt.id as product_type_id,
                pt.name as product_type_name,
                p.id as product_id,
                p.name as product_name,
                p.sub_option_1_id,
                p.sub_option_2_id,
                so1.name as sub_option_1_name,
                so2.name as sub_option_2_name
            FROM products p
            JOIN product_types pt ON p.product_type_id = pt.id
            LEFT JOIN sub_options so1 ON p.sub_option_1_id = so1.id
            LEFT JOIN sub_options so2 ON p.sub_option_2_id = so2.id
            WHERE p.active = 1
            ORDER BY pt.name, p.id
            LIMIT 50
        """)
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'product_type_id': row['product_type_id'],
                'product_type_name': row['product_type_name'],
                'product_id': row['product_id'],
                'product_name': row['product_name'],
                'sub_option_1_id': row['sub_option_1_id'],
                'sub_option_2_id': row['sub_option_2_id'],
                'sub_option_1_name': row['sub_option_1_name'],
                'sub_option_2_name': row['sub_option_2_name']
            })
        
        # Get counts by product type
        cursor.execute("""
            SELECT 
                pt.name as product_type_name,
                COUNT(*) as total_products,
                COUNT(p.sub_option_1_id) as has_sub_option_1,
                COUNT(p.sub_option_2_id) as has_sub_option_2
            FROM products p
            JOIN product_types pt ON p.product_type_id = pt.id
            WHERE p.active = 1
            GROUP BY pt.name
            ORDER BY pt.name
        """)
        
        counts = []
        for row in cursor.fetchall():
            counts.append({
                'product_type': row['product_type_name'],
                'total': row['total_products'],
                'has_sub_1': row['has_sub_option_1'],
                'has_sub_2': row['has_sub_option_2']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'sample_products': products,
            'counts_by_type': counts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
