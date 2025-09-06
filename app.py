from flask import Flask, render_template, jsonify, send_from_directory
import os
import json
from PIL import Image
import random

app = Flask(__name__)

# Configuration
IMAGES_FOLDER = '/data'
STATIC_FOLDER = 'static'

def get_image_info(filepath):
    """Get image dimensions and basic info"""
    try:
        with Image.open(filepath) as img:
            width, height = img.size
            return {
                'width': width,
                'height': height,
                'format': img.format
            }
    except:
        return {'width': 400, 'height': 300, 'format': 'JPEG'}

def scan_images():
    """Scan /data directory for images"""
    images = []
    if not os.path.exists(IMAGES_FOLDER):
        return images
    
    # Categories mapping
    categories = {
        'portrait': ['portrait', 'headshot', 'person', 'people', 'face'],
        'landscape': ['mountain', 'lake', 'sunset', 'landscape', 'nature', 'scenic'],
        'wildlife': ['bird', 'animal', 'turkey', 'duck', 'rabbit', 'crane', 'sparrow', 'woodpecker'],
        'wedding': ['wedding', 'bride', 'groom', 'celebration', 'reception'],
        'commercial': ['logo', 'business', 'corporate', 'commercial'],
        'street': ['street', 'urban', 'city', 'skyline']
    }
    
    for filename in os.listdir(IMAGES_FOLDER):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            filepath = os.path.join(IMAGES_FOLDER, filename)
            
            # Determine category based on filename
            category = 'other'
            filename_lower = filename.lower()
            for cat, keywords in categories.items():
                if any(keyword in filename_lower for keyword in keywords):
                    category = cat
                    break
            
            # Get image info
            info = get_image_info(filepath)
            
            # Create clean title from filename
            title = filename.replace('-', ' ').replace('_', ' ')
            title = os.path.splitext(title)[0]
            title = ' '.join(word.capitalize() for word in title.split())
            
            images.append({
                'filename': filename,
                'title': title,
                'category': category,
                'url': f'/images/{filename}',
                'width': info['width'],
                'height': info['height']
            })
    
    return images

@app.route('/')
def index():
    """Main portfolio page"""
    return render_template('index.html')

@app.route('/api/images')
def api_images():
    """API endpoint for images"""
    images = scan_images()
    return jsonify(images)

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve images from /data directory"""
    return send_from_directory(IMAGES_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

