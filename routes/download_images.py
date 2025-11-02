"""
Route for downloading all images from /data directory as a zip file
"""
from flask import Blueprint, send_file, current_app
import os
import zipfile
from io import BytesIO
from datetime import datetime

download_bp = Blueprint('download', __name__)

@download_bp.route('/admin/download-images')
def download_images():
    """
    Create a zip file containing all images from /data directory and subdirectories
    Returns the zip file for download
    """
    # Define the data directory
    data_dir = '/data'
    
    # Create an in-memory bytes buffer for the zip file
    memory_file = BytesIO()
    
    # Create the zip file
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through all directories and files in /data
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                # Get the full file path
                file_path = os.path.join(root, file)
                
                # Check if it's an image file (common image extensions)
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg')):
                    # Calculate the archive name (relative path from data_dir)
                    arcname = os.path.relpath(file_path, data_dir)
                    
                    try:
                        # Add file to zip
                        zipf.write(file_path, arcname)
                        print(f"Added to zip: {arcname}")
                    except Exception as e:
                        print(f"Error adding {file_path}: {str(e)}")
                        continue
    
    # Seek to the beginning of the BytesIO buffer
    memory_file.seek(0)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'fifth_element_images_{timestamp}.zip'
    
    # Send the file
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )

@download_bp.route('/admin/list-images')
def list_images():
    """
    List all images found in /data directory (for debugging)
    """
    data_dir = '/data'
    images = []
    
    # Walk through all directories and files in /data
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            # Check if it's an image file
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg')):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                rel_path = os.path.relpath(file_path, data_dir)
                
                images.append({
                    'path': rel_path,
                    'size': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2)
                })
    
    # Create HTML response
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image List - Fifth Element Photography</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            .stats {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .download-btn {{ background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-bottom: 20px; }}
            .download-btn:hover {{ background: #45a049; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .size {{ text-align: right; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📷 Fifth Element Photography - Image Files</h1>
            
            <div class="stats">
                <strong>Total Images Found:</strong> {len(images)}<br>
                <strong>Total Size:</strong> {sum(img['size_mb'] for img in images):.2f} MB
            </div>
            
            <a href="/admin/download-images" class="download-btn">⬇️ Download All Images as ZIP</a>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>File Path</th>
                        <th class="size">Size (MB)</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for idx, img in enumerate(images, 1):
        html += f"""
                    <tr>
                        <td>{idx}</td>
                        <td>{img['path']}</td>
                        <td class="size">{img['size_mb']}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    return html

