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
    # Original is in /data/filename
    # Gallery version is in /data/gallery-images/filename
    
    images_folder = current_app.config.get('IMAGES_FOLDER', '/data')
    gallery_folder = '/data/gallery-images'
    
    # Ensure gallery folder exists
    os.makedirs(gallery_folder, exist_ok=True)
    
    original_path = os.path.join(images_folder, filename)
    gallery_path = os.path.join(gallery_folder, filename)
    
    # Verify original exists
    if not os.path.exists(original_path):
        return jsonify({'success': False, 'error': f'Original image not found at {original_path}'}), 404
        
    try:
        # Step 1: Create fresh gallery copy from ORIGINAL
        from PIL import Image
        with Image.open(original_path) as img:
            # Resize logic (match existing gallery logic)
            # Max dimension 1200
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
                
            orig_width, orig_height = img.size
            max_dimension = 1200
            
            if orig_width > orig_height:
                new_width = max_dimension
                new_height = int((max_dimension / orig_width) * orig_height)
            else:
                new_height = max_dimension
                new_width = int((max_dimension / orig_height) * orig_width)
                
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to gallery path (clean slate)
            img.save(gallery_path, 'JPEG', quality=90, optimize=True)
                
        # Step 2: Apply Watermark to the NEW gallery image
        success = apply_watermark(
            gallery_path, 
            gallery_path, 
            position=position, 
            size=size, 
            color_mode=color
        )
        
        if success:
            # Step 3: Regenerate Thumbnail so Admin UI updates
            try:
                from thumbnail_helper import generate_thumbnail_for_image
                # Force regeneration of thumbnail from the NEW watermarked gallery image
                # Note: thumbnail_helper might default to reading from /data/filename (original)
                # We need to ensure it reads from gallery_path if we want the watermark to show
                
                # Actually, let's just manually generate the thumbnail here to be safe
                # Or rely on the helper if it's smart enough. 
                # Let's call the helper but pass the gallery path if possible?
                # The helper usually takes just filename.
                
                generate_thumbnail_for_image(filename, force=True)
                print(f"DEBUG: Regenerated thumbnail for {filename}")
            except Exception as e:
                print(f"DEBUG: Failed to regenerate thumbnail: {e}")
                
            return jsonify({'success': True, 'message': 'Watermark applied successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to apply watermark'}), 500
            
    except Exception as e:
        print(f"Error in watermark route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@watermark_bp.route('/api/watermark/remove', methods=['POST'])
def remove_watermark_route():
    """Remove watermark (by regenerating from original)"""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'success': False, 'error': 'Filename required'}), 400
        
    images_folder = current_app.config.get('IMAGES_FOLDER', '/data')
    gallery_folder = '/data/gallery-images'
    
    original_path = os.path.join(images_folder, filename)
    gallery_path = os.path.join(gallery_folder, filename)
    
    if not os.path.exists(original_path):
        return jsonify({'success': False, 'error': 'Original image not found. Cannot restore.'}), 404
        
    try:
        # Restore from ORIGINAL (just like apply, but skip the watermark step)
        from PIL import Image
        with Image.open(original_path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
                
            orig_width, orig_height = img.size
            max_dimension = 1200
            
            if orig_width > orig_height:
                new_width = max_dimension
                new_height = int((max_dimension / orig_width) * orig_height)
            else:
                new_height = max_dimension
                new_width = int((max_dimension / orig_height) * orig_width)
                
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save clean version to gallery path
            img.save(gallery_path, 'JPEG', quality=90, optimize=True)
        
        # Regenerate thumbnail (clean)
        try:
            from thumbnail_helper import generate_thumbnail_for_image
            generate_thumbnail_for_image(filename, force=True)
        except Exception as e:
            print(f"DEBUG: Failed to regenerate thumbnail: {e}")
                
        return jsonify({'success': True, 'message': 'Watermark removed (image reset)'})
        
    except Exception as e:
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
    
    # Recursive list of /data (max depth 2 to avoid huge output)
    data_structure = {}
    try:
        for root, dirs, files in os.walk('/data'):
            # limit depth
            depth = root[len('/data'):].count(os.sep)
            if depth < 2:
                data_structure[root] = files[:20] # Limit to 20 files per dir
    except Exception as e:
        data_structure = str(e)

    debug_info = {
        'images_folder': images_folder,
        'images_folder_exists': os.path.exists(images_folder),
        'wm_dir_prod': wm_dir_prod,
        'wm_dir_prod_exists': os.path.exists(wm_dir_prod),
        'wm_dir_local': wm_dir_local,
        'wm_dir_local_exists': os.path.exists(wm_dir_local),
        'wm_files_prod': os.listdir(wm_dir_prod) if os.path.exists(wm_dir_prod) else [],
        'wm_files_local': os.listdir(wm_dir_local) if os.path.exists(wm_dir_local) else [],
        'DATA_STRUCTURE': data_structure
    }
    
    return jsonify(debug_info)
