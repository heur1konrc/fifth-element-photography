#!/usr/bin/env python3
"""
Test script to create a sample thumbnail for testing the product management system
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_thumbnail():
    # Create a 300x300 test image
    img = Image.new('RGB', (300, 300), color='#4CAF50')
    draw = ImageDraw.Draw(img)
    
    # Add some text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    # Draw some shapes and text
    draw.rectangle([50, 50, 250, 250], outline='white', width=3)
    draw.text((150, 120), "TEST", fill='white', anchor='mm', font=font)
    draw.text((150, 150), "THUMBNAIL", fill='white', anchor='mm', font=font)
    draw.text((150, 180), "300x300", fill='white', anchor='mm', font=font)
    
    # Save the test image
    test_path = 'static/product-thumbnails/test_canvas_8x10_standard-canvas.jpg'
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    img.save(test_path, 'JPEG', quality=85)
    
    print(f"Test thumbnail created: {test_path}")
    return test_path

if __name__ == "__main__":
    create_test_thumbnail()
