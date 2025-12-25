"""
API endpoint to force regenerate a single gallery image
This is useful when the REPLACE tool doesn't properly regenerate the gallery image
"""
from flask import jsonify
import os
from PIL import Image

def register_regenerate_gallery_image_route(app, require_admin_auth, IMAGES_FOLDER):
    """Register the force regenerate gallery image route"""
    
    @app.route('/api/regenerate-gallery-image/<filename>', methods=['POST'])
    @require_admin_auth
    def regenerate_gallery_image(filename):
        """Force regenerate a single gallery-optimized image"""
        try:
            print(f"[REGENERATE] Force regenerating gallery image for: {filename}")
            
            # Validate filename
            if not filename or '..' in filename or '/' in filename:
                return jsonify({'success': False, 'error': 'Invalid filename'}), 400
            
            # Check if original image exists
            original_path = os.path.join(IMAGES_FOLDER, filename)
            if not os.path.exists(original_path):
                return jsonify({'success': False, 'error': 'Original image not found'}), 404
            
            # Create gallery-images directory if it doesn't exist
            os.makedirs('/data/gallery-images', exist_ok=True)
            gallery_path = os.path.join('/data/gallery-images', filename)
            
            print(f"[REGENERATE] Original path: {original_path}")
            print(f"[REGENERATE] Gallery path: {gallery_path}")
            
            # Delete existing gallery image if it exists
            if os.path.exists(gallery_path):
                os.remove(gallery_path)
                print(f"[REGENERATE] Deleted existing gallery image")
            
            # Open and process original image
            with Image.open(original_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Get original dimensions
                orig_width, orig_height = img.size
                print(f"[REGENERATE] Original dimensions: {orig_width}x{orig_height}")
                
                # Calculate new dimensions (max 1200px on longest side)
                max_dimension = 1200
                if orig_width > orig_height:
                    new_width = max_dimension
                    new_height = int((max_dimension / orig_width) * orig_height)
                else:
                    new_height = max_dimension
                    new_width = int((max_dimension / orig_height) * orig_width)
                
                print(f"[REGENERATE] New dimensions: {new_width}x{new_height}")
                
                # Resize image with high quality
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save gallery image with good quality
                img.save(gallery_path, 'JPEG', quality=90, optimize=True)
                print(f"[REGENERATE] ✓ Successfully saved gallery image")
            
            # Verify the file was created
            if os.path.exists(gallery_path):
                file_size = os.path.getsize(gallery_path)
                print(f"[REGENERATE] ✓ Gallery image verified: {file_size} bytes")
                
                # Also regenerate thumbnail
                try:
                    from thumbnail_helper import generate_thumbnail_for_image
                    print(f"[REGENERATE] Force regenerating thumbnail for {filename}")
                    generate_thumbnail_for_image(filename, images_folder=IMAGES_FOLDER, force=True)
                    print(f"[REGENERATE] ✓ Thumbnail regenerated successfully")
                except Exception as thumb_error:
                    print(f"[REGENERATE] ✗ Failed to regenerate thumbnail: {thumb_error}")
                
                return jsonify({
                    'success': True,
                    'message': f'Gallery image and thumbnail regenerated successfully for {filename}',
                    'gallery_path': gallery_path,
                    'file_size': file_size
                })
            else:
                print(f"[REGENERATE] ✗ Gallery image file not found after save!")
                return jsonify({'success': False, 'error': 'Gallery image file not created'}), 500
                
        except Exception as e:
            print(f"[REGENERATE] ✗ Error regenerating gallery image: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
