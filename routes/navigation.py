"""
Navigation API Routes
Handles CRUD operations for navigation management
"""

from flask import Blueprint, request, jsonify
from navigation_db import (
    get_all_nav_items, get_nav_tree, add_nav_item, 
    update_nav_item, delete_nav_item, reorder_nav_items,
    get_visible_nav_tree
)
from gallery_db import get_all_galleries

navigation_bp = Blueprint('navigation', __name__)

@navigation_bp.route('/api/navigation/items', methods=['GET'])
def get_nav_items():
    """Get all navigation items as a tree"""
    try:
        tree = get_nav_tree()
        return jsonify({'success': True, 'items': tree})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@navigation_bp.route('/api/navigation/items/visible', methods=['GET'])
def get_visible_items():
    """Get only visible navigation items"""
    try:
        tree = get_visible_nav_tree()
        return jsonify({'success': True, 'items': tree})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@navigation_bp.route('/api/navigation/items', methods=['POST'])
def create_nav_item():
    """Create a new navigation item"""
    try:
        data = request.json
        name = data.get('name')
        item_type = data.get('type', 'category')  # 'category', 'gallery', 'link'
        parent_id = data.get('parent_id')
        gallery_id = data.get('gallery_id')
        url = data.get('url')
        order_index = data.get('order_index', 0)
        
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        item_id = add_nav_item(name, item_type, parent_id, gallery_id, url, order_index)
        return jsonify({'success': True, 'id': item_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@navigation_bp.route('/api/navigation/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update a navigation item"""
    try:
        data = request.json
        name = data.get('name')
        parent_id = data.get('parent_id')
        order_index = data.get('order_index')
        visible = data.get('visible')
        url = data.get('url')
        
        update_nav_item(item_id, name, parent_id, order_index, visible, url)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@navigation_bp.route('/api/navigation/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete a navigation item"""
    try:
        delete_nav_item(item_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@navigation_bp.route('/api/navigation/reorder', methods=['POST'])
def reorder_items():
    """Reorder navigation items"""
    try:
        data = request.json
        item_orders = data.get('items', [])
        
        reorder_nav_items(item_orders)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@navigation_bp.route('/api/navigation/galleries', methods=['GET'])
def get_available_galleries():
    """Get all galleries for assignment to navigation"""
    try:
        galleries = get_all_galleries()
        return jsonify({'success': True, 'galleries': galleries})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
