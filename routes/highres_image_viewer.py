from flask import Blueprint, send_from_directory
import os

highres_viewer_bp = Blueprint('highres_viewer', __name__)

@highres_viewer_bp.route('/admin/view-highres/<filename>')
def view_highres_image(filename):
    """Serve high-resolution image for viewing/analysis (not download)"""
    try:
        from image_storage_manager import ImageStorageManager
        storage_manager = ImageStorageManager()
        
        # Security check - ensure filename is safe
        if not filename or '..' in filename or '/' in filename:
            return "Invalid filename", 400
        
        # Check /data first (current production location)
        data_path = os.path.join('/data', filename)
        if os.path.exists(data_path):
            highres_path = data_path
        else:
            # Try /data/originals
            highres_path = storage_manager.get_highres_path(filename)
            
            if not highres_path:
                # Fall back to web version for legacy images
                web_path = storage_manager.get_web_path(filename)
                if not web_path:
                    return "Image file not found", 404
                highres_path = web_path
        
        # Send file for viewing (not as attachment)
        return send_from_directory(
            os.path.dirname(highres_path), 
            os.path.basename(highres_path)
        )
        
    except Exception as e:
        return f"Error loading high-res file: {str(e)}", 500
