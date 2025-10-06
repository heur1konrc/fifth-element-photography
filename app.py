from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, send_file
import os
import json
from datetime import datetime
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
import uuid

# Lumaprints integration imports
from lumaprints_api import get_lumaprints_client, get_pricing_calculator

app = Flask(__name__)

def is_mobile_device():
    """Detect if the request is from a mobile device"""
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_keywords = [
        'mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 
        'windows phone', 'opera mini', 'iemobile', 'webos', 'palm'
    ]
    return any(keyword in user_agent for keyword in mobile_keywords)

# Template filter for exposure time conversion
@app.template_filter('exposure_fraction')
def exposure_fraction(value):
    """Convert decimal exposure time to fraction format"""
    try:
        if isinstance(value, str):
            val = float(value)
        else:
            val = float(value)
        
        if val >= 1:
            return f"{val:.1f}s"
        else:
            # Convert to fraction
            fraction = int(round(1 / val))
            return f"1/{fraction}s"
    except:
        return str(value)

# Force deployment - About upload button added - JS fixes applied
app.secret_key = 'fifth-element-admin-key-2024'

# Configuration
IMAGES_FOLDER = '/data'
STATIC_FOLDER = 'static'
CATEGORIES_FILE = '/data/categories.json'
FEATURED_FILE = '/data/featured.json'
ABOUT_FILE = '/data/about.json'

# Lumaprints configuration
ORDERS_FILE = '/data/lumaprints_orders.json'
LUMAPRINTS_CATALOG_FILE = os.path.join(os.path.dirname(__file__), 'lumaprints_catalog.json')

# Initialize Lumaprints pricing calculator with 100% markup
# pricing_calc = get_pricing_calculator(markup_percentage=100.0, sandbox=True)  # TEMPORARILY DISABLED TO FIX CRASH

# SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'rick@fifthelement.photos'
SMTP_PASSWORD = 'ahrc paio vwsm scro'
CONTACT_EMAIL = 'info@fifthelement.photos'

def load_about_data():
    """Load about page data"""
    try:
        if os.path.exists('/data/about_data.json'):
            with open('/data/about_data.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

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

def load_image_titles():
    """Load image titles"""
    try:
        if os.path.exists('/data/image_titles.json'):
            with open('/data/image_titles.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_image_titles(titles):
    """Save image titles"""
    try:
        with open('/data/image_titles.json', 'w') as f:
            json.dump(titles, f)
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
    image_titles = load_image_titles()
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
            
            # Get title (use saved title or generate from filename)
            if filename in image_titles:
                title = image_titles[filename]
            else:
                # Create clean title from filename
                title = filename.replace('-', ' ').replace('_', ' ')
                title = os.path.splitext(title)[0]
                title = ' '.join(word.capitalize() for word in title.split())
            
            # Check if image is marked for background use
            is_background = filename in background_images
            
            # Check if image is the weekly featured image
            is_featured = featured_image_data and featured_image_data.get('filename') == filename
            
            # SINGLE SOURCE: Use description as the story (no separate featured_story)
            # Description and story are now the same field
            featured_story = description
            
            # Get image info
            info = get_image_info(filepath)
            
            # Load display order from metadata if available
            display_order = None
            metadata_file = os.path.join(IMAGES_FOLDER, f"{filename}.json")
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        display_order = metadata.get('display_order')
                except:
                    pass
            
            images.append({
                'filename': filename,
                'title': title,
                'category': category,
                'description': description,
                'is_background': is_background,
                'is_featured': is_featured,
                'story': featured_story,
                'url': f'/images/{filename}',
                'width': info['width'],
                'height': info['height'],
                'display_order': display_order
            })
    
    # Sort images by display_order if available, otherwise by filename
    def sort_key(img):
        if img['display_order'] is not None:
            return (0, img['display_order'])  # Randomized images first
        else:
            return (1, img['filename'])  # Non-randomized images second, sorted by filename
    
    images.sort(key=sort_key)
    
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
    
    # Get featured image from featured_image.json
    featured_image = None
    featured_image_data = load_featured_image()
    if featured_image_data and featured_image_data.get('filename'):
        # Find the featured image in the images list
        for image in images:
            if image['filename'] == featured_image_data['filename']:
                featured_image = image
                break
    
    # If no featured image is set, fallback to first landscape image or first image
    if not featured_image:
        for image in images:
            if image['category'] == 'landscape':
                featured_image = image
                break
        if not featured_image and images:
            featured_image = images[0]
    
    # Extract EXIF data for featured image - SINGLE SOURCE APPROACH
    featured_exif = None
    if featured_image:
        image_path = os.path.join(IMAGES_FOLDER, featured_image['filename'])
        featured_exif = extract_exif_data(image_path)
        
        # SINGLE SOURCE: Story is always the same as description
        featured_image['story'] = featured_image.get('description', '')
    
    about_data = load_about_data()
    
    # Mobile detection - serve different template based on device
    if is_mobile_device():
        return render_template('index_mobile.html', 
                             images=images, 
                             categories=categories,
                             category_counts=category_counts,
                             featured_image=featured_image,
                             featured_exif=featured_exif,
                             about_data=about_data)
    else:
        # Desktop users get the original template (unchanged)
        return render_template('index.html', 
                             images=images, 
                             categories=categories,
                             category_counts=category_counts,
                             featured_image=featured_image,
                             featured_exif=featured_exif,
                             about_data=about_data)

@app.route('/featured')
def featured():
    """Featured Image of the Week page"""
    images = scan_images()
    
    # Find the featured image
    featured_image = None
    for image in images:
        if image['is_featured']:
            featured_image = image
            break
    
    if not featured_image:
        # If no featured image is set, return to index
        return redirect(url_for('index'))
    
    # Extract EXIF data from the actual featured image
    exif_data = None
    if featured_image:
        image_path = os.path.join(IMAGES_FOLDER, featured_image['filename'])
        exif_data = extract_exif_data(image_path)
    
    return render_template('featured.html', 
                         featured_image=featured_image,
                         exif_data=exif_data)

@app.route('/api/images')
def api_images():
    """API endpoint for images"""
    images = scan_images()
    return jsonify(images)

@app.route('/images/<filename>')
def serve_image(filename):
    """Serve images from /data directory"""
    return send_from_directory(IMAGES_FOLDER, filename)

@app.route('/thumbnail/<filename>')
def get_thumbnail(filename):
    """Generate and serve thumbnail for admin grid performance"""
    try:
        from PIL import Image
        import io
        
        # Check if thumbnail already exists
        thumbnail_path = os.path.join('/data/thumbnails', filename)
        if os.path.exists(thumbnail_path):
            return send_file(thumbnail_path)
        
        # Create thumbnails directory if it doesn't exist
        os.makedirs('/data/thumbnails', exist_ok=True)
        
        # Open original image
        original_path = os.path.join(IMAGES_FOLDER, filename)
        if not os.path.exists(original_path):
            return jsonify({'error': 'Image not found'}), 404
        
        with Image.open(original_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail (max 400x300 for admin grid)
            img.thumbnail((400, 300), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
            
            return send_file(thumbnail_path)
            
    except Exception as e:
        # Fallback to original image if thumbnail generation fails
        original_path = os.path.join(IMAGES_FOLDER, filename)
        if os.path.exists(original_path):
            return send_file(original_path)
        return jsonify({'error': str(e)}), 500

@app.route('/admin')
def admin():
    """Admin panel for image management"""
    try:
        images = scan_images()
        all_categories = load_categories()
        about_data = load_about_data()
        return render_template('admin_new.html', images=images, all_categories=all_categories, about_data=about_data)
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
        
        # Generate category options HTML
        category_options = ""
        current_category = image.get('category', 'other')
        for category in sorted(all_categories):
            selected = 'selected' if category == current_category else ''
            category_options += f'<option value="{category}" {selected}>{category.title()}</option>'
        
        # Return HTML form for editing that matches modal styling
        form_html = f"""
        <div class="edit-form">
            <form onsubmit="saveImageChanges(event, '{filename}')">
                <div class="form-group">
                    <label for="title">Title:</label>
                    <input type="text" id="title" name="title" value="{image.get('title', '')}" required>
                </div>
                <div class="form-group">
                    <label for="description">Description:</label>
                    <textarea id="description" name="description" rows="3">{image.get('description', '')}</textarea>
                </div>
                <div class="form-group">
                    <label for="category">Category:</label>
                    <select id="category" name="category">
                        {category_options}
                    </select>
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
        </div>
        """
        return form_html
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/update_image/<filename>', methods=['POST'])
def update_image(filename):
    """Update image metadata and sync description with featured story"""
    try:
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip().lower()
        is_featured = request.form.get('is_featured') == 'on'
        is_background = request.form.get('is_background') == 'on'
        
        # Update category assignment
        if category:
            image_categories = load_image_categories()
            image_categories[filename] = category
            save_image_categories(image_categories)
        
        # Update image descriptions
        image_descriptions = load_image_descriptions()
        image_descriptions[filename] = description
        save_image_descriptions(image_descriptions)
        
        # SYNC: Also update featured story if this image is featured
        try:
            featured_stories = {}
            if os.path.exists('/data/featured_stories.json'):
                with open('/data/featured_stories.json', 'r') as f:
                    featured_stories = json.load(f)
            
            # Update the story to match the description
            featured_stories[filename] = description
            
            # Save updated featured stories
            with open('/data/featured_stories.json', 'w') as f:
                json.dump(featured_stories, f)
        except Exception as sync_error:
            print(f"Warning: Could not sync featured story: {sync_error}")
        
        # Update image titles
        image_titles = load_image_titles()
        image_titles[filename] = title
        save_image_titles(image_titles)
        
        # Handle featured image
        if is_featured:
            featured_settings = {'featured_image': filename}
            with open(FEATURED_FILE, 'w') as f:
                json.dump(featured_settings, f)
        
        # Handle background image
        if is_background:
            about_settings = {'background_image': filename}
            with open(ABOUT_FILE, 'w') as f:
                json.dump(about_settings, f)
        
        return jsonify({'success': True, 'message': f'Image {filename} updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
            # Add all images from /data directory
            if os.path.exists('/data'):
                for root, dirs, files in os.walk('/data'):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, '/data')
                        zipf.write(file_path, f"data/{arcname}")
            
            # Add configuration files
            config_files = [CATEGORIES_FILE, FEATURED_FILE, ABOUT_FILE]
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
        # Save featured image data in the format expected by scan_images
        featured_data = {
            'filename': filename,
            'set_date': datetime.now().isoformat()
        }
        
        # Save to the file that scan_images reads from
        with open('/data/featured_image.json', 'w') as f:
            json.dump(featured_data, f)
        
        return jsonify({'success': True, 'message': f'Set {filename} as featured image'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/save_featured_story/<filename>', methods=['POST'])
def save_featured_story(filename):
    """Save story for featured image and sync with image description - SINGLE SOURCE OF TRUTH"""
    try:
        data = request.get_json()
        story = data.get('story', '')
        
        # SINGLE SOURCE: Update image description (primary storage)
        image_descriptions = load_image_descriptions()
        image_descriptions[filename] = story
        save_image_descriptions(image_descriptions)
        
        # SYNC: Also update featured stories for backwards compatibility
        featured_stories = {}
        if os.path.exists('/data/featured_stories.json'):
            with open('/data/featured_stories.json', 'r') as f:
                featured_stories = json.load(f)
        
        featured_stories[filename] = story
        
        with open('/data/featured_stories.json', 'w') as f:
            json.dump(featured_stories, f)
        
        return jsonify({'success': True, 'message': 'Story and description synchronized successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/upload_about_image', methods=['POST'])
def upload_about_image():
    """Upload about page image with bio"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        bio = request.form.get('bio', '')
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Create about images directory
            about_dir = '/data/about'
            if not os.path.exists(about_dir):
                os.makedirs(about_dir)
            
            # Remove any existing about image
            for existing_file in os.listdir(about_dir):
                if existing_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    os.remove(os.path.join(about_dir, existing_file))
            
            # Save new about image
            filename = secure_filename(file.filename)
            filepath = os.path.join(about_dir, filename)
            file.save(filepath)
            
            # Save bio
            bio_data = {
                'filename': filename,
                'bio': bio,
                'upload_date': datetime.now().isoformat()
            }
            
            with open('/data/about_data.json', 'w') as f:
                json.dump(bio_data, f)
            
            return jsonify({
                'success': True, 
                'message': 'About image uploaded successfully',
                'filename': filename
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/save_about_bio/<filename>', methods=['POST'])
def save_about_bio(filename):
    """Save bio for about image"""
    try:
        data = request.get_json()
        bio = data.get('bio', '')
        
        # Load current about data
        about_data = {}
        if os.path.exists('/data/about_data.json'):
            with open('/data/about_data.json', 'r') as f:
                about_data = json.load(f)
        
        # Update bio
        about_data['bio'] = bio
        about_data['filename'] = filename
        
        # Save to file
        with open('/data/about_data.json', 'w') as f:
            json.dump(about_data, f)
        
        return jsonify({'success': True, 'message': 'About bio saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/remove_about_image/<filename>', methods=['POST'])
def remove_about_image(filename):
    """Remove about image"""
    try:
        about_dir = '/data/about'
        filepath = os.path.join(about_dir, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Remove about data
        if os.path.exists('/data/about_data.json'):
            os.remove('/data/about_data.json')
        
        return jsonify({'success': True, 'message': 'About image removed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/debug_about')
def debug_about():
    """Debug about data"""
    about_data = load_about_data()
    return jsonify({
        'about_data': about_data,
        'about_data_exists': bool(about_data),
        'about_file_exists': os.path.exists('/data/about_data.json'),
        'about_dir_exists': os.path.exists('/data/about')
    })

@app.route('/about/<filename>')
def serve_about_image(filename):
    """Serve about images - Using send_from_directory"""
    return send_from_directory('/data/about', filename)


@app.route('/version')
def version():
    """Version endpoint - JS fixes applied"""
    return jsonify({'version': '1.2', 'status': 'JS fixes applied'})

@app.route('/backup')
def create_backup():
    """Simple working backup system"""
    try:
        import tarfile
        import tempfile
        from datetime import datetime
        
        # Create backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"portfolio_backup_{timestamp}.tar.gz"
        
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.tar.gz')
        os.close(temp_fd)
        
        # Get current directory (where app.py is)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create tar file
        with tarfile.open(temp_path, 'w:gz') as tar:
            # Add main files
            main_files = ['app.py', 'requirements.txt', 'Procfile', 'app_backup.py', 'backup.py', '.gitignore']
            for filename in main_files:
                filepath = os.path.join(current_dir, filename)
                if os.path.exists(filepath):
                    tar.add(filepath, arcname=filename)
            
            # Add directories
            directories = ['templates', 'static', 'data']
            for dirname in directories:
                dirpath = os.path.join(current_dir, dirname)
                if os.path.exists(dirpath):
                    tar.add(dirpath, arcname=dirname)
        
        # Send file
        return send_file(temp_path, as_attachment=True, download_name=backup_filename)
        
    except Exception as e:
        return f"Backup error: {str(e)}", 500


def extract_exif_data(image_path):
    """Extract EXIF data from image file"""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        print(f"Extracting EXIF from: {image_path}")
        
        # Open image and get EXIF data
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            
        if not exif_data:
            print("No EXIF data found in image")
            return get_default_exif()
            
        # Convert EXIF data to readable format
        exif = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            exif[tag] = value
        
        print(f"Found EXIF data: {exif}")
        
        # Convert exposure time to fraction format
        if 'ExposureTime' in exif:
            exposure_time = exif['ExposureTime']
            print(f"Original ExposureTime: {exposure_time}, type: {type(exposure_time)}")
            try:
                # Handle different data types
                if isinstance(exposure_time, str):
                    exposure_time = float(exposure_time)
                
                if isinstance(exposure_time, tuple) and len(exposure_time) == 2:
                    if exposure_time[0] == 1:
                        exif['ExposureTime'] = f"1/{exposure_time[1]}s"
                    else:
                        exif['ExposureTime'] = f"{exposure_time[0]}/{exposure_time[1]}s"
                elif isinstance(exposure_time, (float, int)):
                    if exposure_time >= 1:
                        exif['ExposureTime'] = f"{exposure_time:.1f}s"
                    else:
                        # Convert decimal to fraction (e.g., 0.00133 -> 1/750)
                        fraction = int(round(1 / exposure_time))
                        exif['ExposureTime'] = f"1/{fraction}s"
                        print(f"Converted ExposureTime to: {exif['ExposureTime']}")
            except Exception as e:
                print(f"Error converting ExposureTime: {e}")
                # Fallback: try simple conversion
                try:
                    if isinstance(exposure_time, (str, float, int)):
                        val = float(exposure_time)
                        if val < 1:
                            fraction = int(round(1 / val))
                            exif['ExposureTime'] = f"1/{fraction}s"
                except:
                    pass
        
        # Format FNumber with f/ prefix
        if 'FNumber' in exif:
            try:
                f_number = exif['FNumber']
                if isinstance(f_number, tuple) and len(f_number) == 2:
                    aperture = f_number[0] / f_number[1]
                    exif['FNumber'] = f"f/{aperture:.1f}"
                else:
                    aperture = float(f_number)
                    exif['FNumber'] = f"f/{aperture:.1f}"
            except:
                pass
        
        # Format FocalLength with mm and remove decimals
        if 'FocalLength' in exif:
            try:
                focal_length = exif['FocalLength']
                if isinstance(focal_length, tuple) and len(focal_length) == 2:
                    focal = focal_length[0] / focal_length[1]
                    exif['FocalLength'] = f"{int(focal)}mm"
                else:
                    focal = float(focal_length)
                    exif['FocalLength'] = f"{int(focal)}mm"
            except:
                pass
        
        # Return the raw EXIF data with the actual field names
        return exif
        
    except Exception as e:
        print(f"Error extracting EXIF from {image_path}: {str(e)}")
        return get_default_exif()
def get_camera_info(exif):
    """Extract camera information from EXIF"""
    make = exif.get('Make', '').strip()
    model = exif.get('Model', '').strip()
    
    if make and model:
        # Remove make from model if it's already included
        if make.lower() in model.lower():
            return model
        else:
            return f"{make} {model}"
    elif model:
        return model
    elif make:
        return make
    else:
        return 'Unavailable'

def get_lens_info(exif):
    """Extract lens information from EXIF"""
    # Try different lens fields
    lens_fields = ['LensModel', 'Lens', 'LensInfo', 'LensMake']
    
    for field in lens_fields:
        lens = exif.get(field)
        if lens:
            if isinstance(lens, str):
                return lens.strip()
            elif isinstance(lens, bytes):
                try:
                    return lens.decode('utf-8').strip()
                except:
                    continue
    
    return 'Unavailable'

def get_aperture_info(exif):
    """Extract aperture information from EXIF"""
    # Try FNumber first, then ApertureValue
    f_number = exif.get('FNumber')
    if f_number:
        try:
            if isinstance(f_number, tuple) and len(f_number) == 2:
                aperture = f_number[0] / f_number[1]
                return f"f/{aperture:.1f}"
            else:
                # Handle direct float/string values
                aperture = float(f_number)
                return f"f/{aperture:.1f}"
        except:
            pass
    
    # Try ApertureValue as backup
    aperture_value = exif.get('ApertureValue')
    if aperture_value:
        try:
            aperture = float(aperture_value)
            return f"f/{aperture:.1f}"
        except:
            pass
    
    return 'Unavailable'

def get_shutter_speed_info(exif):
    """Extract shutter speed information from EXIF"""
    exposure_time = exif.get('ExposureTime')
    if exposure_time:
        if isinstance(exposure_time, tuple) and len(exposure_time) == 2:
            if exposure_time[0] == 1:
                return f"1/{exposure_time[1]}s"
            else:
                speed = exposure_time[0] / exposure_time[1]
                if speed >= 1:
                    return f"{speed:.1f}s"
                else:
                    return f"1/{int(1/speed)}s"
        elif hasattr(exposure_time, '__float__'):  # Handle IFDRational and other numeric types
            speed = float(exposure_time)
            if speed >= 1:
                return f"{speed:.1f}s"
            else:
                return f"1/{int(1/speed)}s"
        elif isinstance(exposure_time, (int, float)):
            if exposure_time >= 1:
                return f"{exposure_time:.1f}s"
            else:
                return f"1/{int(1/exposure_time)}s"
    
    return 'Unavailable'

def get_iso_info(exif):
    """Extract ISO information from EXIF"""
    iso_fields = ['ISOSpeedRatings', 'ISO', 'PhotographicSensitivity']
    
    for field in iso_fields:
        iso = exif.get(field)
        if iso:
            if isinstance(iso, (list, tuple)) and len(iso) > 0:
                return f"ISO {iso[0]}"
            elif isinstance(iso, (int, float)):
                return f"ISO {int(iso)}"
    
    return 'Unavailable'

def get_focal_length_info(exif):
    """Extract focal length information from EXIF"""
    focal_length = exif.get('FocalLength')
    if focal_length:
        if isinstance(focal_length, tuple) and len(focal_length) == 2:
            fl = focal_length[0] / focal_length[1]
            return f"{fl:.0f}mm"
        elif hasattr(focal_length, '__float__'):  # Handle IFDRational and other numeric types
            return f"{float(focal_length):.0f}mm"
        elif isinstance(focal_length, (int, float)):
            return f"{focal_length:.0f}mm"
    
    return 'Unavailable'

def get_default_exif():
    """Return default EXIF data when extraction fails"""
    return {
        'camera': 'Unavailable',
        'lens': 'Unavailable',
        'aperture': 'Unavailable',
        'shutter_speed': 'Unavailable',
        'iso': 'Unavailable',
        'focal_length': 'Unavailable'
    }

@app.route('/debug_exif')
def debug_exif():
    """Debug route to show all EXIF data from featured image"""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        # Get featured image from the actual featured_image.json file
        featured_image = None
        if os.path.exists('/data/featured_image.json'):
            with open('/data/featured_image.json', 'r') as f:
                featured_data = json.load(f)
                featured_image = featured_data
        
        if not featured_image:
            return jsonify({'error': 'No featured image set'})
        
        # Get image path
        image_path = os.path.join(IMAGES_FOLDER, featured_image['filename'])
        
        # Extract ALL EXIF data
        with Image.open(image_path) as img:
            exif_data = img._getexif()
        
        if not exif_data:
            return jsonify({
                'filename': featured_image['filename'],
                'message': 'No EXIF data found in this image',
                'exif_data': {}
            })
        
        # Convert all EXIF data to readable format
        readable_exif = {}
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, f"Unknown_{tag_id}")
            
            # Convert value to string for JSON serialization
            if isinstance(value, bytes):
                try:
                    readable_exif[tag_name] = value.decode('utf-8', errors='ignore')
                except:
                    readable_exif[tag_name] = f"<bytes: {len(value)} bytes>"
            elif isinstance(value, tuple):
                readable_exif[tag_name] = f"{value[0]}/{value[1]}" if len(value) == 2 else str(value)
            else:
                readable_exif[tag_name] = str(value)
        
        return jsonify({
            'filename': featured_image['filename'],
            'total_exif_fields': len(readable_exif),
            'exif_data': readable_exif
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/set_hero_image', methods=['POST'])
def set_hero_image():
    """Set a specific image as the hero image"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        title = data.get('title')
        
        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'})
        
        # Save hero image selection
        hero_data = {
            'filename': filename,
            'title': title
        }
        
        hero_file_path = os.path.join('/data', 'hero_image.json')
        with open(hero_file_path, 'w') as f:
            json.dump(hero_data, f, indent=2)
        
        return jsonify({'success': True, 'message': f'Hero image set to "{title}"'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear_hero_image', methods=['POST'])
def clear_hero_image():
    """Clear the hero image selection (return to random)"""
    try:
        hero_data = {
            'filename': None,
            'title': None
        }
        
        hero_file_path = os.path.join('/data', 'hero_image.json')
        with open(hero_file_path, 'w') as f:
            json.dump(hero_data, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Hero image cleared - using random selection'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/hero_image')
def get_hero_image():
    """API endpoint to get current hero image selection"""
    try:
        hero_file_path = os.path.join('/data', 'hero_image.json')
        if os.path.exists(hero_file_path):
            with open(hero_file_path, 'r') as f:
                hero_data = json.load(f)
                return jsonify(hero_data)
        else:
            # Return default if file doesn't exist
            return jsonify({'filename': None, 'title': None})
    except Exception as e:
        return jsonify({'filename': None, 'title': None})


@app.route('/admin/randomize_portfolio', methods=['POST'])
def randomize_portfolio():
    """Randomize the order of portfolio images"""
    try:
        import random
        
        # Get all images
        images = []
        for filename in os.listdir(IMAGES_FOLDER):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                filepath = os.path.join(IMAGES_FOLDER, filename)
                if os.path.isfile(filepath):
                    # Get image metadata
                    image_data = {
                        'filename': filename,
                        'size': os.path.getsize(filepath),
                        'modified': os.path.getmtime(filepath)
                    }
                    
                    # Load existing metadata if available
                    metadata_file = os.path.join(IMAGES_FOLDER, f"{filename}.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                                image_data.update(metadata)
                        except:
                            pass
                    
                    images.append(image_data)
        
        # Randomize the order
        random.shuffle(images)
        
        # Save the new order by updating modification times
        # We'll use a simple approach: update the metadata with a new 'display_order' field
        for index, image in enumerate(images):
            metadata_file = os.path.join(IMAGES_FOLDER, f"{image['filename']}.json")
            
            # Load existing metadata or create new
            metadata = {}
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            # Add display order
            metadata['display_order'] = index
            metadata['randomized_at'] = datetime.now().isoformat()
            
            # Save metadata
            try:
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
            except Exception as e:
                print(f"Error saving metadata for {image['filename']}: {e}")
        
        return jsonify({
            'success': True, 
            'message': f'Successfully randomized {len(images)} images',
            'count': len(images)
        })
        
    except Exception as e:
        print(f"Error randomizing portfolio: {e}")
        return jsonify({'success': False, 'error': str(e)})

def send_contact_email(name, email, phone, shoot_type, budget, how_heard, message):
    """Send contact form email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = CONTACT_EMAIL
        msg['Subject'] = f'New Contact Form Submission from {name}'
        
        # Create email body
        body = f"""
New contact form submission from Fifth Element Photography website:

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Shoot Type: {shoot_type if shoot_type else 'Not specified'}
Budget: {budget if budget else 'Not specified'}
How they heard about us: {how_heard if how_heard else 'Not specified'}

Message:
{message}

---
This email was sent automatically from the Fifth Element Photography contact form.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, CONTACT_EMAIL, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/contact', methods=['POST'])
def contact():
    """Handle contact form submission"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        shoot_type = data.get('shoot_type', '').strip()
        budget = data.get('budget', '').strip()
        how_heard = data.get('how_heard', '').strip()
        message = data.get('message', '').strip()
        
        # Validate required fields
        if not name or not email or not message:
            return jsonify({'success': False, 'error': 'Name, email, and message are required'}), 400
        
        # Send email
        if send_contact_email(name, email, phone, shoot_type, budget, how_heard, message):
            return jsonify({'success': True, 'message': 'Thank you for your message! We will get back to you soon.'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send message. Please try again later.'}), 500
            
    except Exception as e:
        print(f"Error processing contact form: {e}")
        return jsonify({'success': False, 'error': 'An error occurred. Please try again later.'}), 500

# ============================================================================
# LUMAPRINTS PRINT ORDERING ROUTES
# ============================================================================

def load_lumaprints_catalog():
    """Load the Lumaprints product catalog"""
    try:
        with open(LUMAPRINTS_CATALOG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"categories": [], "subcategories": {}, "options": {}, "stores": []}

def load_orders():
    """Load orders from JSON file"""
    try:
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_orders(orders):
    """Save orders to JSON file"""
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)

@app.route('/api/lumaprints/catalog')
def get_lumaprints_catalog():
    """Get the complete Lumaprints product catalog"""
    try:
        catalog = load_lumaprints_catalog()
        return jsonify({
            'success': True,
            'catalog': catalog
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/subcategories/<int:category_id>')
def get_lumaprints_subcategories(category_id):
    """Get subcategories for a specific category"""
    try:
        catalog = load_lumaprints_catalog()
        subcategories = catalog.get('subcategories', {}).get(str(category_id), [])
        return jsonify({
            'success': True,
            'subcategories': subcategories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# 
@app.route('/api/lumaprints/pricing-detailed', methods=['POST'])
def get_lumaprints_pricing_detailed():
    """Calculate detailed pricing for a specific product configuration"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['subcategoryId', 'width', 'height']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        subcategory_id = data['subcategoryId']
        width = float(data['width'])
        height = float(data['height'])
        quantity = int(data.get('quantity', 1))
        options = data.get('options', [])
        
        # Calculate pricing
        pricing_result = pricing_calc.calculate_retail_price(
            subcategory_id=subcategory_id,
            width=width,
            height=height,
            quantity=quantity,
            options=options if options else None
        )
        
        if 'error' in pricing_result:
            return jsonify({
                'success': False,
                'error': pricing_result['error']
            }), 500
        
        # Format response
        response = {
            'success': True,
            'pricing': {
                'subcategoryId': subcategory_id,
                'width': width,
                'height': height,
                'quantity': quantity,
                'options': options,
                'wholesale_price': pricing_result['wholesale_price'],
                'markup_percentage': pricing_result['markup_percentage'],
                'markup_amount': pricing_result['markup_amount'],
                'retail_price': pricing_result['retail_price'],
                'price_per_item': pricing_result['price_per_item'],
                'formatted_price': f"${pricing_result['retail_price']:.2f}",
                'formatted_price_per_item': f"${pricing_result['price_per_item']:.2f}"
            }
        }
        
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid data format: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# 
@app.route('/order-print')
def order_print_form():
    """Display the order form for a specific product configuration"""
    try:
        # Get parameters from query string
        image_filename = request.args.get('image', '')
        image_title = request.args.get('title', 'Untitled')
        subcategory_id = int(request.args.get('subcategory_id', 0))
        width = float(request.args.get('width', 0))
        height = float(request.args.get('height', 0))
        quantity = int(request.args.get('quantity', 1))
        price = float(request.args.get('price', 0))
        options = request.args.get('options', '[]')
        
        # Parse options
        try:
            options = json.loads(options)
        except:
            options = []
        
        # Validate required parameters
        if not all([image_filename, subcategory_id, width, height, price]):
            return "Missing required parameters", 400
        
        # Load catalog to get product names
        catalog = load_lumaprints_catalog()
        
        # Find product and subcategory names
        product_name = "Unknown Product"
        size_name = "Custom Size"
        
        for category in catalog['categories']:
            subcategories = catalog['subcategories'].get(str(category['id']), [])
            for subcat in subcategories:
                if subcat['subcategoryId'] == subcategory_id:
                    product_name = category['name']
                    size_name = subcat['name']
                    break
        
        # Check if image is mapped to Lumaprints library
        from lumaprints_mapping import LumaprintsMapping
        mapping_manager = LumaprintsMapping()
        
        if not mapping_manager.is_mapped(image_filename):
            return f"Error: Image '{image_filename}' is not mapped to Lumaprints library. Please contact admin to add this image to the print catalog.", 400
        
        # Construct image URL for display
        image_url = f"/images/{image_filename}"
        
        # Render order form
        return render_template('lumaprints_order_form.html',
            image_url=image_url,
            image_title=image_title,
            product_name=product_name,
            size_name=size_name,
            width=width,
            height=height,
            quantity=quantity,
            formatted_price=f"${price:.2f}",
            subcategory_id=subcategory_id,
            options=options,
            price=price
        )
        
    except Exception as e:
        return f"Error loading order form: {str(e)}", 500
# 
@app.route('/api/lumaprints/submit-order', methods=['POST'])
def submit_lumaprints_order():
    """Submit an order to Lumaprints and store locally"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['subcategoryId', 'width', 'height', 'quantity', 'imageUrl', 'price', 'shipping', 'payment']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Generate order ID
        order_id = str(uuid.uuid4())[:8].upper()
        
        # Create order record
        order_record = {
            'orderId': order_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending',
            'product': {
                'subcategoryId': data['subcategoryId'],
                'width': data['width'],
                'height': data['height'],
                'quantity': data['quantity'],
                'options': data.get('options', [])
            },
            'image': {
                'url': data['imageUrl'],
                'filename': os.path.basename(data['imageUrl'])
            },
            'pricing': {
                'total': data['price']
            },
            'shipping': data['shipping'],
            'payment': data['payment'],
            'lumaprints': {
                'orderId': None,
                'status': None,
                'submitted': False
            }
        }
        
        # Store order locally
        orders = load_orders()
        orders[order_id] = order_record
        save_orders(orders)
        
        # Submit to Lumaprints API
        try:
            api = get_lumaprints_client(sandbox=True)
            
            # Convert local image URL to full URL
            image_url = data['imageUrl']
            if image_url.startswith('/static/'):
                # Convert to full URL
                image_url = f"https://fifth-element-photography-production.up.railway.app{image_url}"
            
            # Prepare Lumaprints order payload
            lumaprints_payload = {
                "externalId": order_id,
                "storeId": "20027",  # Your store ID from catalog
                "shippingMethod": "default",
                "productionTime": "regular",
                "recipient": {
                    "firstName": data['shipping']['firstName'],
                    "lastName": data['shipping']['lastName'],
                    "addressLine1": data['shipping']['addressLine1'],
                    "addressLine2": data['shipping'].get('addressLine2', ''),
                    "city": data['shipping']['city'],
                    "state": data['shipping']['state'],
                    "zipCode": data['shipping']['zipCode'],
                    "country": data['shipping']['country'],
                    "phone": data['shipping'].get('phone', ''),
                    "company": ""
                },
                "orderItems": [{
                    "externalItemId": f"{order_id}-1",
                    "subcategoryId": data['subcategoryId'],
                    "quantity": data['quantity'],
                    "width": data['width'],
                    "height": data['height'],
                    "file": {
                        "imageUrl": image_url
                    },
                    "orderItemOptions": data.get('options', []),
                    "solidColorHexCode": None
                }]
            }
            
            # Submit order to Lumaprints
            lumaprints_response = api.submit_order(lumaprints_payload)
            
            # Update order record with Lumaprints response
            order_record['lumaprints'] = {
                'orderId': lumaprints_response.get('orderId'),
                'status': lumaprints_response.get('status'),
                'submitted': True,
                'response': lumaprints_response
            }
            order_record['status'] = 'submitted'
            
            # Save updated order
            orders[order_id] = order_record
            save_orders(orders)
            
        except Exception as lumaprints_error:
            # Log the error but don't fail the order
            print(f"Lumaprints submission error: {lumaprints_error}")
            order_record['lumaprints']['error'] = str(lumaprints_error)
            order_record['status'] = 'payment_received'
            
            # Save order with error
            orders[order_id] = order_record
            save_orders(orders)
        
        return jsonify({
            'success': True,
            'orderId': order_id,
            'message': 'Order submitted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# 
@app.route('/order-confirmation/<order_id>')
def order_confirmation(order_id):
    """Display order confirmation page"""
    try:
        orders = load_orders()
        order = orders.get(order_id)
        
        if not order:
            return "Order not found", 404
        
        return render_template('order_confirmation.html', order=order)
        
    except Exception as e:
        return f"Error loading order confirmation: {str(e)}", 500

@app.route('/admin/orders')
def admin_orders():
    """Admin page to view all orders"""
    try:
        orders = load_orders()
        
        # Sort orders by timestamp (newest first)
        sorted_orders = sorted(orders.items(), 
                             key=lambda x: x[1]['timestamp'], 
                             reverse=True)
        
        return render_template('admin_orders.html', orders=sorted_orders)
        
    except Exception as e:
        return f"Error loading orders: {str(e)}", 500
# ============================================================================
# LUMAPRINTS ROUTES (ACTIVE)
# ============================================================================

# Load product catalog
def load_catalog():
    """Load the Lumaprints product catalog"""
    catalog_path = os.path.join(os.path.dirname(__file__), 'lumaprints_catalog.json')
    try:
        with open(catalog_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"categories": [], "subcategories": {}, "options": {}, "stores": []}

# Initialize pricing calculator with 100% markup (double wholesale price)
pricing_calc = get_pricing_calculator(markup_percentage=100.0, sandbox=True)

@app.route('/api/lumaprints/categories')
def get_lumaprints_categories():
    """Get available product categories"""
    try:
        catalog = load_catalog()
        return jsonify({
            'success': True,
            'categories': catalog.get('categories', [])
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/pricing', methods=['POST'])
def get_lumaprints_pricing():
    """Calculate pricing for a specific product configuration"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['subcategoryId', 'width', 'height']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        subcategory_id = data['subcategoryId']
        width = float(data['width'])
        height = float(data['height'])
        quantity = int(data.get('quantity', 1))
        options = data.get('options', [])
        
        # Calculate pricing
        pricing_result = pricing_calc.calculate_retail_price(
            subcategory_id=subcategory_id,
            width=width,
            height=height,
            quantity=quantity,
            options=options if options else None
        )
        
        if 'error' in pricing_result:
            return jsonify({
                'success': False,
                'error': pricing_result['error']
            }), 500
        
        # Format response
        response = {
            'success': True,
            'pricing': {
                'subcategoryId': subcategory_id,
                'width': width,
                'height': height,
                'quantity': quantity,
                'wholesale_price': pricing_result['wholesale_price'],
                'markup_percentage': pricing_result['markup_percentage'],
                'retail_price': pricing_result['retail_price'],
                'formatted_price': f"${pricing_result['retail_price']:.2f}"
            }
        }
        
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid data format: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# END LUMAPRINTS ROUTES
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
# 

# ============================================================================
# LUMAPRINTS LIBRARY MAPPING ROUTES
# ============================================================================

@app.route('/admin/lumaprints-mapping')
def admin_lumaprints_mapping():
    """Admin interface for managing Lumaprints library mapping"""
    try:
        from lumaprints_mapping import LumaprintsMapping
        mapping_manager = LumaprintsMapping()
        
        gallery_images = mapping_manager.get_gallery_images()
        mapping_status = mapping_manager.get_mapping_status_for_all_images()
        
        return render_template('admin_lumaprints_mapping.html',
                             gallery_images=gallery_images,
                             mapping_status=mapping_status)
    except Exception as e:
        return f"Error loading Lumaprints mapping page: {str(e)}", 500

@app.route('/api/lumaprints/add-mapping', methods=['POST'])
def add_lumaprints_mapping():
    """Add mapping between gallery image and Lumaprints library ID"""
    try:
        from lumaprints_mapping import LumaprintsMapping
        mapping_manager = LumaprintsMapping()
        
        data = request.get_json()
        filename = data.get('filename')
        library_id = data.get('library_id')
        library_name = data.get('library_name')
        
        if not filename or not library_id:
            return jsonify({'success': False, 'error': 'Filename and Library ID required'}), 400
        
        # Validate the mapping
        valid, message = mapping_manager.validate_mapping(filename, library_id)
        if not valid:
            return jsonify({'success': False, 'error': message}), 400
        
        success, result = mapping_manager.add_mapping(filename, library_id, library_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/remove-mapping', methods=['POST'])
def remove_lumaprints_mapping():
    """Remove mapping for a gallery image"""
    try:
        from lumaprints_mapping import LumaprintsMapping
        mapping_manager = LumaprintsMapping()
        
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': 'Filename required'}), 400
        
        success, result = mapping_manager.remove_mapping(filename)
        
        if success:
            return jsonify({
                'success': True,
                'message': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/mapping-status')
def get_lumaprints_mapping_status():
    """Get mapping status for all gallery images"""
    try:
        from lumaprints_mapping import LumaprintsMapping
        mapping_manager = LumaprintsMapping()
        
        mapping_status = mapping_manager.get_mapping_status_for_all_images()
        stats = mapping_manager.get_mapping_stats()
        
        return jsonify({
            'success': True,
            'mapping_status': mapping_status,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/export-mapping')
def export_lumaprints_mapping():
    """Export mapping data as JSON file"""
    try:
        from lumaprints_mapping import LumaprintsMapping
        mapping_manager = LumaprintsMapping()
        
        export_data = mapping_manager.export_mapping_data()
        
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = 'attachment; filename=lumaprints_mapping.json'
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
