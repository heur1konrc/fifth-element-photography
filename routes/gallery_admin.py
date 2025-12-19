"""Gallery Admin Routes"""
from flask import Blueprint, render_template, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gallery_db import *

gallery_admin_bp = Blueprint('gallery_admin', __name__)

@gallery_admin_bp.route('/admin/galleries')
def gallery_admin_page():
    """Gallery management page"""
    from app import require_admin_auth
    require_admin_auth()
    return render_template('gallery_admin.html')

@gallery_admin_bp.route('/api/galleries', methods=['GET'])
def api_get_galleries():
    """Get all galleries"""
    galleries = get_all_galleries()
    
    # Add image count to each gallery
    for gallery in galleries:
        gallery['image_count'] = len(get_gallery_images(gallery['id']))
    
    return jsonify({'success': True, 'galleries': galleries})

@gallery_admin_bp.route('/api/galleries', methods=['POST'])
def api_create_gallery():
    """Create new gallery"""
    data = request.json
    name = data.get('name')
    slug = data.get('slug', name.lower().replace(' ', '-'))
    hero_image = data.get('hero_image')
    description = data.get('description', '')
    display_order = data.get('display_order', 0)
    
    if not name:
        return jsonify({'success': False, 'error': 'Name required'}), 400
    
    gallery_id = create_gallery(name, slug, hero_image, description, display_order)
    
    if gallery_id:
        return jsonify({'success': True, 'gallery_id': gallery_id})
    else:
        return jsonify({'success': False, 'error': 'Gallery already exists'}), 400

@gallery_admin_bp.route('/api/galleries/<int:gallery_id>', methods=['PUT'])
def api_update_gallery(gallery_id):
    """Update gallery"""
    data = request.json
    update_gallery(gallery_id, **data)
    return jsonify({'success': True})

@gallery_admin_bp.route('/api/galleries/<int:gallery_id>', methods=['DELETE'])
def api_delete_gallery(gallery_id):
    """Delete gallery"""
    delete_gallery(gallery_id)
    return jsonify({'success': True})

@gallery_admin_bp.route('/api/galleries/<int:gallery_id>/images', methods=['GET'])
def api_get_gallery_images(gallery_id):
    """Get images in gallery"""
    images = get_gallery_images(gallery_id)
    return jsonify({'success': True, 'images': images})

@gallery_admin_bp.route('/api/galleries/<int:gallery_id>/images', methods=['POST'])
def api_add_gallery_image(gallery_id):
    """Add image to gallery"""
    data = request.json
    image_filename = data.get('image_filename')
    
    if not image_filename:
        return jsonify({'success': False, 'error': 'Image filename required'}), 400
    
    success = add_image_to_gallery(gallery_id, image_filename)
    return jsonify({'success': success})

@gallery_admin_bp.route('/api/galleries/<int:gallery_id>/images/<image_filename>', methods=['DELETE'])
def api_remove_gallery_image(gallery_id, image_filename):
    """Remove image from gallery"""
    remove_image_from_gallery(gallery_id, image_filename)
    return jsonify({'success': True})
