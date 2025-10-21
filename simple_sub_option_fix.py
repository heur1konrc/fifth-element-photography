#!/usr/bin/env python3
"""
Simple Sub-Option Fix - Add to existing route
"""

from flask import jsonify
import sqlite3

def apply_simple_sub_option_fix():
    """Apply simple sub-option fix via existing route"""
    try:
        conn = sqlite3.connect('lumaprints_pricing.db')
        cursor = conn.cursor()
        
        # Simple direct updates
        updates = []
        
        # Canvas Prints (product_type_id = 1) -> sub_option_1_id = 1
        cursor.execute("UPDATE products SET sub_option_1_id = 1 WHERE product_type_id = 1 AND active = 1")
        updates.append(f"Canvas Prints: {cursor.rowcount} products updated")
        
        # Fine Art Paper Prints (product_type_id = 3) -> sub_option_1_id = 49
        cursor.execute("UPDATE products SET sub_option_1_id = 49 WHERE product_type_id = 3 AND active = 1")
        updates.append(f"Fine Art Paper: {cursor.rowcount} products updated")
        
        # Foam-Mounted Fine Art Paper Prints (product_type_id = 5) -> sub_option_1_id = 49
        cursor.execute("UPDATE products SET sub_option_1_id = 49 WHERE product_type_id = 5 AND active = 1")
        updates.append(f"Foam-Mounted: {cursor.rowcount} products updated")
        
        # Framed Canvas Prints (product_type_id = 2) -> both sub-options
        cursor.execute("UPDATE products SET sub_option_1_id = 32, sub_option_2_id = 14 WHERE product_type_id = 2 AND active = 1")
        updates.append(f"Framed Canvas: {cursor.rowcount} products updated")
        
        # Framed Fine Art Paper Prints (product_type_id = 4) -> both sub-options
        cursor.execute("UPDATE products SET sub_option_1_id = 32, sub_option_2_id = 42 WHERE product_type_id = 4 AND active = 1")
        updates.append(f"Framed Fine Art: {cursor.rowcount} products updated")
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Sub-option fix applied successfully',
            'updates': updates
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
