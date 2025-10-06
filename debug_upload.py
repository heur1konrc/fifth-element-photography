#!/usr/bin/env python3
"""
Debug script to test the upload functionality
"""

import os
import requests
from PIL import Image
import io

def create_test_image():
    """Create a test image in memory"""
    img = Image.new('RGB', (300, 300), color='#FF5722')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_upload():
    """Test the upload endpoint"""
    
    # Create test image
    test_image = create_test_image()
    
    # Prepare the request
    files = {'file': ('test.jpg', test_image, 'image/jpeg')}
    data = {'productPath': 'canvas/8x10/standard-canvas'}
    
    try:
        # Test locally first
        print("Testing upload functionality...")
        
        # Check if we can create the directory
        thumbnails_dir = os.path.join('static', 'product-thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        print(f"Directory created/exists: {thumbnails_dir}")
        
        # Test image processing
        test_image.seek(0)
        image = Image.open(test_image)
        print(f"Image opened successfully: {image.size}, {image.mode}")
        
        # Test filename generation
        product_path = 'canvas/8x10/standard-canvas'
        filename = product_path.replace('/', '_') + '.jpg'
        print(f"Generated filename: {filename}")
        
        # Test save path
        thumbnail_path = os.path.join(thumbnails_dir, filename)
        print(f"Save path: {thumbnail_path}")
        
        # Test image processing
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        image.thumbnail((300, 300), Image.Resampling.LANCZOS)
        image.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
        
        print(f"Test image saved successfully to: {thumbnail_path}")
        print(f"File exists: {os.path.exists(thumbnail_path)}")
        
        if os.path.exists(thumbnail_path):
            file_size = os.path.getsize(thumbnail_path)
            print(f"File size: {file_size} bytes")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_upload()
