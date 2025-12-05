import os
import subprocess

def generate_thumbnail_for_image(filename, images_folder='/data', thumbnails_folder=None, thumb_width=600, thumb_quality=95):
    """
    Generate a thumbnail for a given image file
    
    Args:
        filename: Name of the image file
        images_folder: Path to the images directory (default: /data)
        thumbnails_folder: Path to thumbnails directory (default: static/thumbnails relative to script)
        thumb_width: Width of thumbnail in pixels (default: 600)
        thumb_quality: JPEG quality 0-100 (default: 95)
    
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
    
    # Check if thumbnail already exists
    if os.path.exists(output_path):
        print(f"Thumbnail already exists: {thumb_filename}")
        return output_path
    
    try:
        # Generate thumbnail using ImageMagick
        cmd = [
            'convert',
            input_path,
            '-resize', f'{thumb_width}x',
            '-quality', str(thumb_quality),
            output_path
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Generated thumbnail: {thumb_filename}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating thumbnail for {filename}: {e.stderr}")
        return None
    except Exception as e:
        print(f"Unexpected error generating thumbnail for {filename}: {e}")
        return None
