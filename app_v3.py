"""
Flask Application V3 - Fifth Element Photography
Version: 3.0.0-alpha

Clean, well-documented Flask application for Admin V3.
All routes are organized and documented.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for, send_file, Response
from werkzeug.utils import secure_filename
from data_manager_v3 import DataManagerV3
import os
import json
import tarfile
import tempfile
import logging
from datetime import datetime
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize data manager
data_manager = DataManagerV3(data_dir=os.environ.get('DATA_DIR', '/data'))

# Configuration
# Images are stored directly in /data/, not in /data/images/
UPLOAD_FOLDER = '/data'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Admin credentials (in production, use environment variables)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password')


# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Decorator to require login for admin routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login_v3'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/login_v3', methods=['GET', 'POST'])
def login_v3():
    """Admin login page for V3."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_v3'))
        else:
            return render_template('login_v3.html', error='Invalid credentials')
    
    return render_template('login_v3.html')


@app.route('/logout_v3')
def logout_v3():
    """Logout from admin V3."""
    session.pop('logged_in', None)
    return redirect(url_for('login_v3'))


# ==================== ADMIN DASHBOARD ====================

@app.route('/admin_v3')
@login_required
def admin_v3():
    """Main admin dashboard for V3."""
    return render_template('admin_v3.html')


# ==================== IMAGE API ROUTES ====================

@app.route('/api/v3/images', methods=['GET'])
def get_images_v3():
    """
    Get all images with metadata and categories.
    
    Query Parameters:
        category (optional): Filter by category name
        sort (optional): Sort order (newest, oldest, name_asc, name_desc)
    
    Returns:
        JSON array of image objects
    """
    images = data_manager.get_all_images()
    
    # Filter by category if specified
    category_filter = request.args.get('category')
    if category_filter and category_filter != 'all':
        images = [img for img in images if category_filter in img['categories']]
    
    # Sort images
    sort_order = request.args.get('sort', 'newest')
    if sort_order == 'newest':
        images.sort(key=lambda x: x['upload_date'], reverse=True)
    elif sort_order == 'oldest':
        images.sort(key=lambda x: x['upload_date'])
    elif sort_order == 'name_asc':
        images.sort(key=lambda x: x['title'].lower())
    elif sort_order == 'name_desc':
        images.sort(key=lambda x: x['title'].lower(), reverse=True)
    
    return jsonify(images)


@app.route('/api/v3/images/<filename>', methods=['GET'])
@login_required
def get_image_v3(filename):
    """
    Get a single image's data.
    
    Args:
        filename: Image filename
    
    Returns:
        JSON object with image data or 404 if not found
    """
    image = data_manager.get_image(filename)
    if image is None:
        return jsonify({'error': 'Image not found'}), 404
    return jsonify(image)


@app.route('/api/v3/images/<filename>', methods=['PUT'])
@login_required
def update_image_v3(filename):
    """
    Update an image's metadata and/or categories.
    
    Args:
        filename: Image filename
    
    Request Body:
        {
            "title": "New Title" (optional),
            "description": "New Description" (optional),
            "categories": ["Category1", "Category2"] (optional)
        }
    
    Returns:
        JSON success message or error
    """
    data = request.get_json()
    
    # Update metadata if provided
    if 'title' in data or 'description' in data:
        data_manager.update_image_metadata(
            filename,
            title=data.get('title'),
            description=data.get('description')
        )
    
    # Update categories if provided
    if 'categories' in data:
        data_manager.update_image_categories(filename, data['categories'])
    
    return jsonify({'success': True, 'message': 'Image updated successfully'})


@app.route('/api/v3/images/<filename>', methods=['DELETE'])
@login_required
def delete_image_v3(filename):
    """
    Delete an image and all its associated data.
    
    Args:
        filename: Image filename
    
    Returns:
        JSON success message or error
    """
    success = data_manager.delete_image(filename)
    if success:
        return jsonify({'success': True, 'message': 'Image deleted successfully'})
    else:
        return jsonify({'error': 'Image not found'}), 404


@app.route('/api/v3/upload', methods=['POST'])
@login_required
def upload_images_v3():
    """
    Upload one or more images.
    
    Request:
        multipart/form-data with 'files[]' field
    
    Returns:
        JSON with list of uploaded filenames and any errors
    """
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files[]')
    uploaded = []
    errors = []
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                errors.append(f'{filename}: File already exists')
                continue
            
            try:
                file.save(filepath)
                # Generate thumbnail immediately after upload
                data_manager.generate_thumbnail(filename)
                uploaded.append(filename)
            except Exception as e:
                errors.append(f'{filename}: {str(e)}')
        else:
            errors.append(f'{file.filename}: Invalid file type')
    
    return jsonify({
        'success': len(uploaded) > 0,
        'uploaded': uploaded,
        'errors': errors
    })


# ==================== CATEGORY API ROUTES ====================

@app.route('/api/v3/categories', methods=['GET'])
@login_required
def get_categories_v3():
    """
    Get all categories with image counts.
    
    Returns:
        JSON array of category objects
    """
    categories = data_manager.get_all_categories()
    return jsonify(categories)


@app.route('/api/v3/categories', methods=['POST'])
@login_required
def create_category_v3():
    """
    Create a new category.
    
    Request Body:
        {
            "name": "Category Name"
        }
    
    Returns:
        JSON success message or error
    """
    data = request.get_json()
    category_name = data.get('name', '').strip()
    
    if not category_name:
        return jsonify({'error': 'Category name is required'}), 400
    
    success = data_manager.create_category(category_name)
    if success:
        return jsonify({'success': True, 'message': 'Category created successfully'})
    else:
        return jsonify({'error': 'Category already exists'}), 400


@app.route('/api/v3/categories/<category_name>', methods=['DELETE'])
@login_required
def delete_category_v3(category_name):
    """
    Delete a category and remove it from all images.
    
    Args:
        category_name: Name of the category to delete
    
    Returns:
        JSON success message or error
    """
    success = data_manager.delete_category(category_name)
    if success:
        return jsonify({'success': True, 'message': 'Category deleted successfully'})
    else:
        return jsonify({'error': 'Category not found'}), 404


# ==================== BACKUP ROUTES ====================

@app.route('/api/v3/backup/list')
@login_required
def list_backups_v3():
    """
    List all existing backups with metadata.
    
    Returns:
        JSON with list of backups (filename, size, date)
    """
    try:
        backups_dir = '/data/backups'
        backups = []
        total_size = 0
        
        if os.path.exists(backups_dir):
            for filename in os.listdir(backups_dir):
                if filename.endswith('.tar.gz'):
                    filepath = os.path.join(backups_dir, filename)
                    stat = os.stat(filepath)
                    size_bytes = stat.st_size
                    size_mb = size_bytes / (1024 * 1024)
                    total_size += size_bytes
                    
                    # Check if there's a corresponding .s3url file
                    s3url_file = os.path.join(backups_dir, f'{filename}.s3url')
                    s3_url = None
                    if os.path.exists(s3url_file):
                        try:
                            with open(s3url_file, 'r') as f:
                                s3_url = f.read().strip()
                        except:
                            pass
                    
                    backups.append({
                        'filename': filename,
                        'size_bytes': size_bytes,
                        'size_mb': round(size_mb, 2),
                        'created': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'download_url': s3_url if s3_url else f'/data/backups/{filename}',
                        's3_url': s3_url,
                        'local_url': f'/data/backups/{filename}'
                    })
            
            # Sort by creation time, newest first
            backups.sort(key=lambda x: x['created'], reverse=True)
        
        total_size_mb = total_size / (1024 * 1024)
        
        return jsonify({
            'success': True,
            'backups': backups,
            'total_count': len(backups),
            'total_size_mb': round(total_size_mb, 2)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to list backups: {str(e)}'}), 500


@app.route('/api/v3/backup/delete/<filename>', methods=['DELETE'])
@login_required
def delete_backup_v3(filename):
    """
    Delete a specific backup file.
    
    Args:
        filename: Name of the backup file to delete
    
    Returns:
        JSON success message
    """
    try:
        # Security: only allow deleting .tar.gz files
        if not filename.endswith('.tar.gz'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        backups_dir = '/data/backups'
        filepath = os.path.join(backups_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Backup file not found'}), 404
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Backup {filename} deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete backup: {str(e)}'}), 500


@app.route('/api/v3/backup/create')
@login_required
def create_backup_v3():
    """
    Create a backup of all V3 data and save to /data/backups/.
    Returns JSON with download URL.
    
    Returns:
        JSON with backup filename and download URL
    """
    try:
        # Create backups directory if it doesn't exist
        backups_dir = '/data/backups'
        os.makedirs(backups_dir, exist_ok=True)
        
        # Create backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'fifth_element_backup_v3_{timestamp}.tar.gz'
        backup_path = os.path.join(backups_dir, backup_filename)
        
        # Create tar.gz archive directly in /data/backups/
        with tarfile.open(backup_path, 'w:gz') as tar:
            # Add V3 metadata files
            metadata_files = [
                '/data/image_metadata_v3.json',
                '/data/image_categories_v3.json',
                '/data/categories_v3.json'
            ]
            
            for filepath in metadata_files:
                if os.path.exists(filepath):
                    arcname = os.path.join('metadata', os.path.basename(filepath))
                    tar.add(filepath, arcname=arcname)
            
            # Add all image files from /data/
            images_dir = '/data'
            if os.path.exists(images_dir):
                for filename in os.listdir(images_dir):
                    filepath = os.path.join(images_dir, filename)
                    if os.path.isfile(filepath) and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        arcname = os.path.join('images', filename)
                        tar.add(filepath, arcname=arcname)
            
            # Add all thumbnails from /data/thumbnails/
            thumbnails_dir = '/data/thumbnails'
            if os.path.exists(thumbnails_dir):
                for filename in os.listdir(thumbnails_dir):
                    filepath = os.path.join(thumbnails_dir, filename)
                    if os.path.isfile(filepath):
                        arcname = os.path.join('thumbnails', filename)
                        tar.add(filepath, arcname=arcname)
        
        # Get file size
        file_size = os.path.getsize(backup_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # Upload to S3 for reliable large file downloads
        import subprocess
        try:
            result = subprocess.run(
                ['manus-upload-file', backup_path],
                capture_output=True,
                text=True,
                check=True
            )
            s3_url = result.stdout.strip()
            logging.info(f"Backup uploaded to S3: {s3_url}")
            
            # Save S3 URL to a file for future reference
            s3url_file = f'{backup_path}.s3url'
            with open(s3url_file, 'w') as f:
                f.write(s3_url)
        except Exception as e:
            logging.error(f"S3 upload failed: {str(e)}")
            s3_url = None
        
        # Return JSON with both local and S3 URLs
        return jsonify({
            'success': True,
            'filename': backup_filename,
            'download_url': s3_url if s3_url else f'/data/backups/{backup_filename}',
            's3_url': s3_url,
            'local_url': f'/data/backups/{backup_filename}',
            'size_bytes': file_size,
            'size_mb': round(file_size_mb, 2)
        })
        
    except Exception as e:
        return jsonify({'error': f'Backup failed: {str(e)}'}), 500


# ==================== BULK OPERATIONS ROUTES ====================

@app.route('/api/v3/images/bulk/assign-categories', methods=['POST'])
@login_required
def bulk_assign_categories_v3():
    """
    Assign categories to multiple images at once.
    
    Request Body:
        {
            "filenames": ["image1.jpg", "image2.jpg", ...],
            "categories": ["category1", "category2", ...]
        }
    
    Returns:
        JSON success message with count of updated images
    """
    data = request.get_json()
    filenames = data.get('filenames', [])
    categories = data.get('categories', [])
    
    if not filenames:
        return jsonify({'error': 'No images selected'}), 400
    
    if not categories:
        return jsonify({'error': 'No categories selected'}), 400
    
    # Assign categories to all images at once
    success_count = data_manager.assign_categories(filenames, categories)
    
    return jsonify({
        'success': True,
        'message': f'Assigned categories to {success_count} image(s)',
        'count': success_count
    })


# ==================== STATIC FILE SERVING ====================

@app.route('/data/<filename>')
def serve_image(filename):
    """Serve images from the data directory."""
    # Images are stored directly in /data/, not in /data/images/
    return send_from_directory('/data', filename)


@app.route('/data/thumbnails/<filename>')
def serve_thumbnail(filename):
    """
    Serve thumbnail images, generating on-demand if needed.
    
    This route automatically generates thumbnails for existing images
    that don't have thumbnails yet, ensuring all images (old and new)
    have optimized thumbnails for fast gallery loading.
    """
    # Get thumbnail path, generating if it doesn't exist
    thumbnail_path = data_manager.get_thumbnail_path(filename)
    
    # Serve the thumbnail
    return send_from_directory('/data/thumbnails', filename)


@app.route('/data/backups/<filename>')
def serve_backup(filename):
    """Serve backup files from /data/backups/ directory."""
    return send_from_directory('/data/backups', filename)


# ==================== DIAGNOSTIC ROUTES (TEMPORARY) ====================

@app.route('/api/v3/debug/list-images')
@login_required
def debug_list_images():
    """Diagnostic endpoint to list all files in /data/images/ directory."""
    import os
    images_dir = '/data/images'
    
    try:
        files = []
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath):
                    files.append({
                        'filename': filename,
                        'size': os.path.getsize(filepath),
                        'is_image': filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
                    })
        
        return jsonify({
            'directory': images_dir,
            'exists': os.path.exists(images_dir),
            'total_files': len(files),
            'files': files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v3/debug/categories-data')
@login_required
def debug_categories_data():
    """Diagnostic endpoint to view raw category data file."""
    try:
        categories_file = '/data/image_categories_v3.json'
        if os.path.exists(categories_file):
            with open(categories_file, 'r') as f:
                data = json.load(f)
            return jsonify({
                'file': categories_file,
                'exists': True,
                'total_entries': len(data),
                'data': data
            })
        else:
            return jsonify({
                'file': categories_file,
                'exists': False
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v3/debug/cleanup-categories', methods=['POST'])
@login_required
def debug_cleanup_categories():
    """Cleanup corrupted category data - remove invalid entries."""
    try:
        categories_file = '/data/image_categories_v3.json'
        if not os.path.exists(categories_file):
            return jsonify({'error': 'Categories file not found'}), 404
        
        # Read current data
        with open(categories_file, 'r') as f:
            data = json.load(f)
        
        # Get list of actual image files
        images_dir = '/data'
        valid_filenames = set()
        for filename in os.listdir(images_dir):
            filepath = os.path.join(images_dir, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                valid_filenames.add(filename)
        
        # Filter out invalid entries
        cleaned_data = {}
        removed_count = 0
        for key, value in data.items():
            if key in valid_filenames:
                cleaned_data[key] = value
            else:
                removed_count += 1
        
        # Write cleaned data back
        with open(categories_file, 'w') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up category data',
            'removed_entries': removed_count,
            'remaining_entries': len(cleaned_data),
            'valid_images': len(valid_filenames)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v3/debug/list-data')
@login_required
def debug_list_data():
    """Diagnostic endpoint to list entire /data/ directory structure."""
    import os
    data_dir = '/data'
    
    try:
        structure = {}
        if os.path.exists(data_dir):
            for item in os.listdir(data_dir):
                item_path = os.path.join(data_dir, item)
                if os.path.isdir(item_path):
                    # List files in subdirectory
                    subfiles = []
                    for subitem in os.listdir(item_path):
                        subitem_path = os.path.join(item_path, subitem)
                        if os.path.isfile(subitem_path):
                            subfiles.append(subitem)
                    structure[item] = {'type': 'directory', 'files': subfiles, 'count': len(subfiles)}
                elif os.path.isfile(item_path):
                    structure[item] = {'type': 'file', 'size': os.path.getsize(item_path)}
        
        return jsonify({
            'directory': data_dir,
            'exists': os.path.exists(data_dir),
            'structure': structure
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== FRONT-END ROUTES ====================

@app.route('/')
def index_v3():
    """Simple test front-end for V3."""
    return render_template('index_v3.html')


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

