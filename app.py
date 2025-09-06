from flask import Flask, render_template, jsonify, send_from_directory, request, redirect, url_for, flash
import os
import json
from PIL import Image
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'fifth-element-admin-key-2024'

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

@app.route('/admin')
def admin():
    """Admin panel for image management"""
    try:
        images = scan_images()
        return render_template('admin.html', images=images)
    except Exception as e:
        return f"Admin Error: {str(e)}", 500

@app.route('/admin/upload', methods=['POST'])
def upload_image():
    """Upload new image"""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('admin'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('admin'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure unique filename
        counter = 1
        base_name, ext = os.path.splitext(filename)
        while os.path.exists(os.path.join(IMAGES_FOLDER, filename)):
            filename = f"{base_name}_{counter}{ext}"
            counter += 1
        
        filepath = os.path.join(IMAGES_FOLDER, filename)
        file.save(filepath)
        flash(f'Image "{filename}" uploaded successfully!')
    else:
        flash('Invalid file type. Please upload JPG, PNG, or GIF files.')
    
    return redirect(url_for('admin'))

@app.route('/admin/delete/<filename>', methods=['POST'])
def delete_image(filename):
    """Delete an image"""
    filepath = os.path.join(IMAGES_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'Image "{filename}" deleted successfully!')
    else:
        flash('Image not found')
    return redirect(url_for('admin'))

@app.route('/admin/rename/<filename>', methods=['POST'])
def rename_image(filename):
    """Rename an image"""
    new_name = request.form.get('new_name')
    if not new_name:
        flash('Please provide a new name')
        return redirect(url_for('admin'))
    
    # Ensure proper extension
    old_ext = os.path.splitext(filename)[1]
    if not new_name.endswith(old_ext):
        new_name += old_ext
    
    new_name = secure_filename(new_name)
    old_path = os.path.join(IMAGES_FOLDER, filename)
    new_path = os.path.join(IMAGES_FOLDER, new_name)
    
    if os.path.exists(old_path):
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            flash(f'Image renamed from "{filename}" to "{new_name}"')
        else:
            flash('A file with that name already exists')
    else:
        flash('Original image not found')
    
    return redirect(url_for('admin'))

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

