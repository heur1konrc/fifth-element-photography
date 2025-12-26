from flask import Blueprint, request, jsonify, current_app
import os
import shutil
from watermark_helper import apply_watermark

watermark_bp = Blueprint('watermark_bp', __name__)

@watermark_bp.route('/api/watermark/apply', methods=['POST'])
def apply_watermark_route():
    """Apply watermark to a specific image"""
    data = request.json
    filename = data.get('filename')
    position = data.get('position', 'bottom-right')
    size = data.get('size', 'medium')
    color = data.get('color', 'auto')
    
    if not filename:
        return jsonify({'success': False, 'error': 'Filename required'}), 400
        
    # Paths
    images_folder = current_app.config.get('IMAGES_FOLDER', '/data')
    
    # We operate on the GALLERY version (usually just filename)
    # But we should regenerate from ORIGINAL (highres_) to ensure clean slate
    # Logic: 
    # 1. Find highres original
    # 2. Resize to gallery size (1200px) -> overwriting current gallery image
    # 3. Apply watermark
    
    gallery_path = os.path.join(images_folder, filename)
    highres_path = os.path.join(images_folder, f"highres_{filename}")
    
    if not os.path.exists(highres_path):
        # Fallback: if no highres, try to use existing gallery image (not ideal but works)
        if not os.path.exists(gallery_path):
             return jsonify({'success': False, 'error': 'Image not found'}), 404
        source_path = gallery_path
    else:
        source_path = highres_path
        
    try:
        # Step 1: Create fresh gallery copy from source
        from PIL import Image
        with Image.open(source_path) as img:
            # Resize logic (match existing gallery logic)
            # Max dimension 1200
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            # Save to gallery path (clean slate)
            if gallery_path.lower().endswith(('.jpg', '.jpeg')):
                img = img.convert('RGB')
                img.save(gallery_path, quality=85)
            else:
                img.save(gallery_path)
                
        # Step 2: Apply Watermark
        success = apply_watermark(
            gallery_path, 
            gallery_path, 
            position=position, 
            size=size, 
            color_mode=color
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Watermark applied successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to apply watermark'}), 500
            
    except Exception as e:
        print(f"Error in watermark route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@watermark_bp.route('/api/watermark/debug', methods=['GET'])
def debug_watermark_route():
    """Debug endpoint to check paths"""
    import os
    from flask import current_app
    
    images_folder = current_app.config.get('IMAGES_FOLDER', '/data')
    
    # Check watermarks
    wm_dir_prod = '/data/watermarks'
    wm_dir_local = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'watermarks')
    
    debug_info = {
        'images_folder': images_folder,
        'images_folder_exists': os.path.exists(images_folder),
        'wm_dir_prod': wm_dir_prod,
        'wm_dir_prod_exists': os.path.exists(wm_dir_prod),
        'wm_dir_local': wm_dir_local,
        'wm_dir_local_exists': os.path.exists(wm_dir_local),
        'wm_files_prod': os.listdir(wm_dir_prod) if os.path.exists(wm_dir_prod) else [],
        'wm_files_local': os.listdir(wm_dir_local) if os.path.exists(wm_dir_local) else []
    }
    
    return jsonify(debug_info)

@watermark_bp.route('/api/watermark/remove', methods=['POST'])
def remove_watermark_route():
    """Remove watermark (by regenerating from original)"""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'success': False, 'error': 'Filename required'}), 400
        
    images_folder = current_app.config.get('IMAGES_FOLDER', '/data')
    gallery_path = os.path.join(images_folder, filename)
    highres_path = os.path.join(images_folder, f"highres_{filename}")
    
    if not os.path.exists(highres_path):
        return jsonify({'success': False, 'error': 'Original high-res image not found. Cannot restore.'}), 404
        
    try:
        # Restore from highres
        from PIL import Image
        with Image.open(highres_path) as img:
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            if gallery_path.lower().endswith(('.jpg', '.jpeg')):
                img = img.convert('RGB')
                img.save(gallery_path, quality=85)
            else:
                img.save(gallery_path)
                
        return jsonify({'success': True, 'message': 'Watermark removed (image reset)'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
