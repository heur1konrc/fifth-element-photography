"""
Category management routes for pricing admin
"""
import sqlite3
from flask import request, jsonify, render_template_string

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('lumaprints_pricing.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_category_route():
    """Add new category"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Category name is required'})
        
        conn = get_db_connection()
        
        # Check if category already exists
        existing = conn.execute('SELECT id FROM categories WHERE name = ?', (name,)).fetchone()
        if existing:
            conn.close()
            return jsonify({'success': False, 'message': 'Category already exists'})
        
        # Add new category
        cursor = conn.execute(
            'INSERT INTO categories (name, description) VALUES (?, ?)',
            (name, description)
        )
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Category "{name}" added successfully',
            'category': {
                'id': category_id,
                'name': name,
                'description': description
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding category: {str(e)}'})

def delete_category_route():
    """Delete category (only if it has no products)"""
    try:
        data = request.get_json()
        category_id = data.get('category_id')
        
        if not category_id:
            return jsonify({'success': False, 'message': 'Category ID is required'})
        
        conn = get_db_connection()
        
        # Check if category has products
        product_count = conn.execute(
            'SELECT COUNT(*) as count FROM products WHERE category_id = ?', 
            (category_id,)
        ).fetchone()['count']
        
        if product_count > 0:
            conn.close()
            return jsonify({
                'success': False, 
                'message': f'Cannot delete category with {product_count} products. Remove products first.'
            })
        
        # Get category name for confirmation message
        category = conn.execute(
            'SELECT name FROM categories WHERE id = ?', 
            (category_id,)
        ).fetchone()
        
        if not category:
            conn.close()
            return jsonify({'success': False, 'message': 'Category not found'})
        
        # Delete category
        conn.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Category "{category["name"]}" deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting category: {str(e)}'})

def get_categories_route():
    """Get all categories for dropdown refresh"""
    try:
        conn = get_db_connection()
        categories = conn.execute('''
            SELECT c.id, c.name, c.description, COUNT(p.id) as product_count
            FROM categories c
            LEFT JOIN products p ON c.id = p.category_id
            GROUP BY c.id, c.name, c.description
            ORDER BY c.name
        ''').fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'categories': [dict(cat) for cat in categories]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching categories: {str(e)}'})
