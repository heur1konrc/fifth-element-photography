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
CATEGORIES_FILE = '/data/categories.json'
FEATURED_FILE = '/data/featured.json'
ABOUT_FILE = '/data/about.json'

def load_categories():
    """Load categories from JSON file"""
    try:
        if os.path.exists(CATEGORIES_FILE):
            with open(CATEGORIES_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return ['portrait', 'landscape', 'wildlife', 'wedding', 'commercial', 'street', 'other']

def save_categories(categories):
    """Save categories to JSON file"""
    try:
        with open(CATEGORIES_FILE, 'w') as f:
            json.dump(categories, f)
        return True
    except:
        return False

def load_image_categories():
    """Load image category assignments"""
    try:
        if os.path.exists('/data/image_categories.json'):
            with open('/data/image_categories.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_image_categories(assignments):
    """Save image category assignments"""
    try:
        with open('/data/image_categories.json', 'w') as f:
            json.dump(assignments, f)
        return True
    except:
        return False

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

def load_image_descriptions():
    """Load image descriptions"""
    try:
        if os.path.exists('/data/image_descriptions.json'):
            with open('/data/image_descriptions.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_image_descriptions(descriptions):
    """Save image descriptions"""
    try:
        with open('/data/image_descriptions.json', 'w') as f:
            json.dump(descriptions, f)
        return True
    except:
        return False

def scan_images():
    """Scan /data directory for images"""
    images = []
    if not os.path.exists(IMAGES_FOLDER):
        return images
    
    # Load saved category assignments and descriptions
    image_categories = load_image_categories()
    image_descriptions = load_image_descriptions()
    
    # Default categories mapping for auto-detection
    default_categories = {
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
            
            # Use saved category assignment or auto-detect
            if filename in image_categories:
                category = image_categories[filename]
            else:
                # Auto-detect category based on filename
                category = 'other'
                filename_lower = filename.lower()
                for cat, keywords in default_categories.items():
                    if any(keyword in filename_lower for keyword in keywords):
                        category = cat
                        break
            
            # Get description
            description = image_descriptions.get(filename, '')
            
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
                'description': description,
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
        all_categories = load_categories()
        return render_template('admin.html', images=images, all_categories=all_categories)
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

@app.route('/admin/categories', methods=['GET', 'POST'])
def manage_categories():
    """Manage categories - add/delete"""
    if request.method == 'POST':
        action = request.form.get('action')
        categories = load_categories()
        
        if action == 'add':
            new_category = request.form.get('category_name', '').strip().lower()
            if new_category and new_category not in categories:
                categories.append(new_category)
                if save_categories(categories):
                    flash(f'Category "{new_category}" added successfully!')
                else:
                    flash('Error saving category')
            elif new_category in categories:
                flash('Category already exists')
            else:
                flash('Please enter a category name')
        
        elif action == 'delete':
            category_to_delete = request.form.get('category_to_delete')
            if category_to_delete and category_to_delete in categories:
                # Remove from categories list
                categories.remove(category_to_delete)
                save_categories(categories)
                
                # Move images from deleted category to 'other'
                image_categories = load_image_categories()
                updated_count = 0
                for filename, category in image_categories.items():
                    if category == category_to_delete:
                        image_categories[filename] = 'other'
                        updated_count += 1
                
                save_image_categories(image_categories)
                flash(f'Category "{category_to_delete}" deleted. {updated_count} images moved to "other" category.')
            else:
                flash('Please select a valid category to delete')
    
    return redirect(url_for('admin'))

@app.route('/admin/assign_category/<filename>', methods=['POST'])
def assign_category(filename):
    """Assign category to an image"""
    new_category = request.form.get('category', '').strip().lower()
    if new_category:
        image_categories = load_image_categories()
        image_categories[filename] = new_category
        if save_image_categories(image_categories):
            flash(f'Image "{filename}" assigned to category "{new_category}"')
        else:
            flash('Error saving category assignment')
    else:
        flash('Please select a category')
    
    return redirect(url_for('admin'))

@app.route('/admin/update_description/<filename>', methods=['POST'])
def update_description(filename):
    """Update image description"""
    new_description = request.form.get('description', '').strip()
    image_descriptions = load_image_descriptions()
    image_descriptions[filename] = new_description
    if save_image_descriptions(image_descriptions):
        flash(f'Description updated for "{filename}"')
    else:
        flash('Error saving description')
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

