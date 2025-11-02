"""
Test script for the download images functionality
"""
import os
import zipfile
from io import BytesIO

def test_download_images(data_dir='/home/ubuntu/test_data'):
    """Test the image download logic"""
    
    print(f"Scanning directory: {data_dir}")
    print(f"Directory exists: {os.path.exists(data_dir)}")
    print()
    
    # Create an in-memory bytes buffer for the zip file
    memory_file = BytesIO()
    
    images_found = []
    
    # Walk through all directories and files
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            # Get the full file path
            file_path = os.path.join(root, file)
            
            # Check if it's an image file
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg')):
                arcname = os.path.relpath(file_path, data_dir)
                file_size = os.path.getsize(file_path)
                images_found.append({
                    'path': arcname,
                    'size': file_size
                })
                print(f"Found image: {arcname} ({file_size} bytes)")
    
    print(f"\nTotal images found: {len(images_found)}")
    
    if len(images_found) == 0:
        print("No images found!")
        return
    
    # Create the zip file
    print("\nCreating ZIP file...")
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg')):
                    arcname = os.path.relpath(file_path, data_dir)
                    
                    try:
                        zipf.write(file_path, arcname)
                        print(f"  Added to zip: {arcname}")
                    except Exception as e:
                        print(f"  Error adding {file_path}: {str(e)}")
    
    # Check zip file size
    zip_size = memory_file.tell()
    print(f"\nZIP file created successfully!")
    print(f"ZIP file size: {zip_size} bytes")
    
    # Save to disk for verification
    output_path = '/home/ubuntu/test_images.zip'
    memory_file.seek(0)
    with open(output_path, 'wb') as f:
        f.write(memory_file.read())
    
    print(f"Test ZIP saved to: {output_path}")
    
    return True

if __name__ == '__main__':
    test_download_images()

