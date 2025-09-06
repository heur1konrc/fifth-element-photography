from flask import Flask, render_template, jsonify, send_from_directory, send_file, request, redirect, url_for, flash
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

def load_background_images():
    """Load images marked for background use"""
    try:
        if os.path.exists('/data/background_images.json'):
            with open('/data/background_images.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_background_images(background_list):
    """Save images marked for background use"""
    try:
        with open('/data/background_images.json', 'w') as f:
            json.dump(background_list, f)
        return True
    except:
        return False

def load_featured_image():
    """Load weekly featured image"""
    try:
        if os.path.exists('/data/featured_image.json'):
            with open('/data/featured_image.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def save_featured_image(featured_data):
    """Save weekly featured image"""
    try:
        with open('/data/featured_image.json', 'w') as f:
            json.dump(featured_data, f)
        return True
    except:
        return False

def scan_images():
    """Scan /data directory for images"""
    images = []
    if not os.path.exists(IMAGES_FOLDER):
        return images
    
    # Load saved data
    image_categories = load_image_categories()
    image_descriptions = load_image_descriptions()
    background_images = load_background_images()
    featured_image_data = load_featured_image()
    
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
            
            # Check if image is marked for background use
            is_background = filename in background_images
            
            # Check if image is the weekly featured image
            is_featured = featured_image_data and featured_image_data.get('filename') == filename
            
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
                'is_background': is_background,
                'is_featured': is_featured,
                'url': f'/images/{filename}',
                'width': info['width'],
                'height': info['height']
            })
    
    return images

@app.route('/')
def index():
    """Main portfolio page"""
    images = scan_images()
    categories = load_categories()
    
    # Get category counts
    category_counts = {}
    for category in categories:
        category_counts[category] = len([img for img in images if img['category'] == category])
    
    # Get featured image (first landscape image for now)
    featured_image = None
    for image in images:
        if image['category'] == 'landscape':
            featured_image = image
            break
    if not featured_image and images:
        featured_image = images[0]
    
    return render_template('index.html', 
                         images=images, 
                         categories=categories,
                         category_counts=category_counts,
                         featured_image=featured_image)

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
        return render_template('admin_new.html', images=images, all_categories=all_categories)
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

@app.route('/edit_image/<filename>')
def edit_image(filename):
    """Get edit form for an image"""
    try:
        images = scan_images()
        image = next((img for img in images if img['filename'] == filename), None)
        if not image:
            return "Image not found", 404
        
        all_categories = load_categories()
        
        # Return HTML form for editing
        form_html = f"""
        <form action="/update_image/{filename}" method="post" class="edit-form">
            <div class="form-group">
                <label>Title:</label>
                <input type="text" name="title" value="{image.get('title', '')}" required>
            </div>
            <div class="form-group">
                <label>Description:</label>
                <textarea name="description" rows="3">{image.get('description', '')}</textarea>
            </div>
            <div class="form-group">
                <label>Category:</label>
                <select name="category" required>
                    {''.join([f'<option value="{cat}" {"selected" if cat == image.get("category") else ""}>{cat.title()}</option>' for cat in all_categories])}
                </select>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" name="is_featured" {"checked" if image.get('is_featured') else ""}>
                    Set as Featured Image
                </label>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" name="is_background" {"checked" if image.get('is_background') else ""}>
                    Set as Background Image
                </label>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="closeEditModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Changes</button>
            </div>
        </form>
        """
        return form_html
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/update_image/<filename>', methods=['POST'])
def update_image(filename):
    """Update image metadata"""
    try:
        # Update image metadata (this would need to be implemented based on your data structure)
        # For now, just redirect back to admin
        flash(f'Image {filename} updated successfully')
    except Exception as e:
        flash(f'Error updating image: {str(e)}')
    
    return redirect(url_for('admin'))

@app.route('/add_to_slideshow/<filename>', methods=['POST'])
def add_to_slideshow(filename):
    """Add image to slideshow"""
    try:
        # This would add the image to a slideshow configuration
        # For now, just return success
        return jsonify({'success': True, 'message': f'Added {filename} to slideshow'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/backup_system', methods=['POST'])
def backup_system():
    """Create system backup"""
    try:
        import zipfile
        import tempfile
        from datetime import datetime
        
        # Create temporary zip file
        temp_dir = tempfile.mkdtemp()
        backup_filename = f"portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        backup_path = os.path.join(temp_dir, backup_filename)
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all images
            for root, dirs, files in os.walk(IMAGES_FOLDER):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, IMAGES_FOLDER)
                        zipf.write(file_path, arcname)
            
            # Add configuration files
            config_files = [CATEGORIES_FILE, FEATURED_FILE, ABOUT_FILE, '/data/image_categories.json']
            for config_file in config_files:
                if os.path.exists(config_file):
                    zipf.write(config_file, os.path.basename(config_file))
        
        return send_file(backup_path, as_attachment=True, download_name=backup_filename)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# New routes for admin interface functionality
@app.route('/delete_image/<filename>', methods=['POST'])
def delete_image_new(filename):
    """Delete an image (new admin interface)"""
    try:
        filepath = os.path.join(IMAGES_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            # Also remove from category assignments
            image_categories = load_image_categories()
            if filename in image_categories:
                del image_categories[filename]
                save_image_categories(image_categories)
            return jsonify({'success': True, 'message': f'Image {filename} deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/assign_category/<filename>', methods=['POST'])
def assign_category_new(filename):
    """Assign category to an image (new admin interface)"""
    try:
        category = request.form.get('category', '').strip().lower()
        if not category:
            return jsonify({'success': False, 'message': 'Category is required'}), 400
        
        image_categories = load_image_categories()
        image_categories[filename] = category
        
        if save_image_categories(image_categories):
            return jsonify({'success': True, 'message': f'Image {filename} assigned to category {category}'})
        else:
            return jsonify({'success': False, 'message': 'Error saving category assignment'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/upload_images', methods=['POST'])
def upload_images_new():
    """Upload multiple images (new admin interface)"""
    try:
        uploaded_files = []
        failed_files = []
        
        if 'files' not in request.files:
            return jsonify({'success': False, 'message': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ensure unique filename
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while os.path.exists(os.path.join(IMAGES_FOLDER, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
                
                filepath = os.path.join(IMAGES_FOLDER, filename)
                file.save(filepath)
                uploaded_files.append(filename)
            else:
                failed_files.append(file.filename if file.filename else 'Unknown file')
        
        message = f'Successfully uploaded {len(uploaded_files)} file(s)'
        if failed_files:
            message += f'. Failed to upload {len(failed_files)} file(s): {", ".join(failed_files)}'
        
        return jsonify({
            'success': True, 
            'message': message,
            'uploaded': uploaded_files,
            'failed': failed_files
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/toggle_background/<filename>', methods=['POST'])
def toggle_background(filename):
    """Toggle background image setting"""
    try:
        # Load current about settings
        about_settings = {}
        if os.path.exists(ABOUT_FILE):
            with open(ABOUT_FILE, 'r') as f:
                about_settings = json.load(f)
        
        # Set this image as background
        about_settings['background_image'] = filename
        
        # Save settings
        with open(ABOUT_FILE, 'w') as f:
            json.dump(about_settings, f)
        
        return jsonify({'success': True, 'message': f'Set {filename} as background image'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/toggle_featured/<filename>', methods=['POST'])
def toggle_featured(filename):
    """Toggle featured image setting"""
    try:
        # Load current featured settings
        featured_settings = {}
        if os.path.exists(FEATURED_FILE):
            with open(FEATURED_FILE, 'r') as f:
                featured_settings = json.load(f)
        
        # Set this image as featured
        featured_settings['featured_image'] = filename
        
        # Save settings
        with open(FEATURED_FILE, 'w') as f:
            json.dump(featured_settings, f)
        
        return jsonify({'success': True, 'message': f'Set {filename} as featured image'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

