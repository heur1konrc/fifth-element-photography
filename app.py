from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, send_file
import os
import json
from datetime import datetime
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)

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
            
            # Get featured story if this is the featured image
            featured_story = ''
            if is_featured:
                try:
                    if os.path.exists('/data/featured_stories.json'):
                        with open('/data/featured_stories.json', 'r') as f:
                            featured_stories = json.load(f)
                            featured_story = featured_stories.get(filename, '')
                except:
                    pass
            
            # Get image info
            info = get_image_info(filepath)
            
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
    
    # Extract EXIF data for featured image
    featured_exif = None
    if featured_image:
        image_path = os.path.join(IMAGES_FOLDER, featured_image['filename'])
        featured_exif = extract_exif_data(image_path)
    
    about_data = load_about_data()
    
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
        
        # Return HTML form for editing
        form_html = f"""
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
        """
        return form_html
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/update_image/<filename>', methods=['POST'])
def update_image(filename):
    """Update image metadata"""
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
    """Save story for featured image"""
    try:
        data = request.get_json()
        story = data.get('story', '')
        
        # Load current featured stories
        featured_stories = {}
        if os.path.exists('/data/featured_stories.json'):
            with open('/data/featured_stories.json', 'r') as f:
                featured_stories = json.load(f)
        
        # Save story for this image
        featured_stories[filename] = story
        
        # Save to file
        with open('/data/featured_stories.json', 'w') as f:
            json.dump(featured_stories, f)
        
        return jsonify({'success': True, 'message': 'Featured story saved successfully'})
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
    """Create comprehensive backup via URL - ADDED FOR BACKUP ONLY"""
    try:
        import tarfile
        import tempfile
        
        # Create temporary directory for backup
        temp_dir = tempfile.mkdtemp()
        backup_filename = f"portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        backup_path = os.path.join(temp_dir, backup_filename)
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        with tarfile.open(backup_path, 'w:gz') as tar:
            # Add all source code files
            source_files = ['app.py', 'requirements.txt', 'README.md', 'backup.py', 'Procfile']
            for file in source_files:
                file_path = os.path.join(project_root, file)
                if os.path.exists(file_path):
                    tar.add(file_path, arcname=file)
            
            # Add templates directory
            templates_dir = os.path.join(project_root, 'templates')
            if os.path.exists(templates_dir):
                tar.add(templates_dir, arcname='templates')
            
            # Add static directory (CSS, JS, images)
            static_dir = os.path.join(project_root, 'static')
            if os.path.exists(static_dir):
                tar.add(static_dir, arcname='static')
            
            # Add data directory (all data files and uploaded images)
            if os.path.exists('/data'):
                tar.add('/data', arcname='data')
        
        return send_file(backup_path, as_attachment=True, download_name=backup_filename, mimetype='application/gzip')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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

