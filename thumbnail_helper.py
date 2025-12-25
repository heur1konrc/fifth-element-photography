import os
from PIL import Image

def generate_thumbnail_for_image(filename, images_folder='/data', thumbnails_folder=None, thumb_width=600, thumb_quality=95, force=False):
    """
    Generate a thumbnail for a given image file using PIL/Pillow
    
    Args:
        filename: Name of the image file
        images_folder: Path to the images directory (default: /data)
        thumbnails_folder: Path to thumbnails directory (default: static/thumbnails relative to script)
        thumb_width: Width of thumbnail in pixels (default: 600)
        thumb_quality: JPEG quality 0-100 (default: 95)
        force: If True, regenerate even if thumbnail already exists (default: False)
    
    Returns:
        Path to generated thumbnail or None if failed
    """
    if thumbnails_folder is None:
        # Default to static/thumbnails relative to this script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        thumbnails_folder = os.path.join(script_dir, 'static', 'thumbnails')
    
    # Ensure thumbnails directory exists
    os.makedirs(thumbnails_folder, exist_ok=True)
    
    # Paths
    input_path = os.path.join(images_folder, filename)
    thumb_filename = f"thumb_{filename}"
    output_path = os.path.join(thumbnails_folder, thumb_filename)
    
    # Check if input exists
    if not os.path.exists(input_path):
        print(f"Error: Input image not found: {input_path}")
        return None
    
    # Check if thumbnail already exists (skip if force=True)
    if os.path.exists(output_path) and not force:
        print(f"Thumbnail already exists: {thumb_filename}")
        return output_path
    
    # Delete existing thumbnail if force regeneration
    if force and os.path.exists(output_path):
        os.remove(output_path)
        print(f"Deleted existing thumbnail for force regeneration: {thumb_filename}")
    
    try:
        # Open and process image with PIL
        with Image.open(input_path) as img:
            # Convert RGBA/P to RGB for JPEG compatibility
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Get original dimensions
            orig_width, orig_height = img.size
            
            # Calculate new height maintaining aspect ratio
            new_width = thumb_width
            new_height = int((thumb_width / orig_width) * orig_height)
            
            # Resize with high quality LANCZOS resampling
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            img_resized.save(output_path, 'JPEG', quality=thumb_quality, optimize=True)
            
        print(f"Generated thumbnail: {thumb_filename} ({new_width}x{new_height})")
        return output_path
        
    except Exception as e:
        print(f"Error generating thumbnail for {filename}: {e}")
        import traceback
        traceback.print_exc()
        return None
