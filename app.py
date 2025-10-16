from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, send_from_directory, session
import os
import json
from datetime import datetime
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
import uuid
import hashlib
import secrets

# Lumaprints integration imports
from lumaprints_api import get_lumaprints_client, get_pricing_calculator

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Admin system - Multi-user support (up to 4 users)
ADMIN_USERS_FILE = "data/admin_users.json"
ADMIN_CONFIG_FILE = "admin_config.json"
RESET_TOKENS_FILE = "data/reset_tokens.json"

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash_value):
    """Verify a password against its hash"""
    return hash_password(password) == hash_value

def generate_reset_token():
    """Generate a secure reset token"""
    return secrets.token_urlsafe(32)

def load_admin_users():
    """Load admin users from file"""
    try:
        if os.path.exists(ADMIN_USERS_FILE):
            with open(ADMIN_USERS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading admin users: {e}")
    
    # Return default admin user (backward compatibility)
    default_users = {
        "Heur1konrc": {
            "password_hash": "3afeed04eeca02f36260571b19deb0898adfabcf3d0283aacdc9cafb81e0b0e1",  # "SecurePass123"
            "email": "",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True
        }
    }
    save_admin_users(default_users)
    return default_users

def save_admin_users(users):
    """Save admin users to file"""
    try:
        os.makedirs('data', exist_ok=True)
        with open(ADMIN_USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving admin users: {e}")
        return False

def load_reset_tokens():
    """Load password reset tokens"""
    try:
        if os.path.exists(RESET_TOKENS_FILE):
            with open(RESET_TOKENS_FILE, 'r') as f:
                tokens = json.load(f)
                # Clean expired tokens (24 hour expiry)
                current_time = datetime.now()
                valid_tokens = {}
                for token, data in tokens.items():
                    token_time = datetime.fromisoformat(data['created_at'])
                    if (current_time - token_time).total_seconds() < 86400:  # 24 hours
                        valid_tokens[token] = data
                if len(valid_tokens) != len(tokens):
                    save_reset_tokens(valid_tokens)
                return valid_tokens
    except Exception as e:
        print(f"Error loading reset tokens: {e}")
    return {}

def save_reset_tokens(tokens):
    """Save password reset tokens"""
    try:
        os.makedirs('data', exist_ok=True)
        with open(RESET_TOKENS_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving reset tokens: {e}")
        return False

def authenticate_user(username, password):
    """Authenticate a user"""
    users = load_admin_users()
    if username in users:
        user = users[username]
        if user.get('is_active', True) and verify_password(password, user['password_hash']):
            # Update last login
            user['last_login'] = datetime.now().isoformat()
            users[username] = user
            save_admin_users(users)
            return True
    return False

def get_user_count():
    """Get current number of admin users"""
    users = load_admin_users()
    return len([u for u in users.values() if u.get('is_active', True)])

def can_add_user():
    """Check if we can add another user (max 4)"""
    return get_user_count() < 4

def load_admin_config():
    """Load admin configuration from file (backward compatibility)"""
    try:
        if os.path.exists(ADMIN_CONFIG_FILE):
            with open(ADMIN_CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading admin config: {e}")
    
    # Return default config
    return {
        "last_updated": datetime.now().isoformat()
    }

def save_admin_config(config):
    """Save admin configuration to file (backward compatibility)"""
    try:
        config['last_updated'] = datetime.now().isoformat()
        with open(ADMIN_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving admin config: {e}")
        return False

def require_admin_auth(f):
    """Decorator to require admin authentication"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

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
# pricing_calc = get_pricing_calculator(markup_percentage=100.0, sandbox=False)  # TEMPORARILY DISABLED TO FIX CRASH

# Import Lumaprints routes (must be after app creation)

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

def get_image_info(filepath, skip_network_fetch=False):
    """Get image dimensions and basic info with caching"""
    filename = os.path.basename(filepath)
    
    # Check cache first
    cache_file = '/data/image_dimensions_cache.json'
    cache = {}
    
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
    except:
        pass
    
    # Return cached dimensions if available
    if filename in cache:
        return cache[filename]
    
    # If skip_network_fetch is True (during startup), return default dimensions
    if skip_network_fetch:
        result = {'width': 400, 'height': 300, 'format': 'JPEG'}
        return result
    
    # If not cached, fetch from URL
    try:
        # Construct the URL for the image (use production where images actually exist)
        image_url = f"https://fifthelement.photos/images/{filename}"
        
        # Import required modules
        import requests
        from PIL import Image
        from io import BytesIO
        
        # Fetch the image from URL
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Open image from response content
        with Image.open(BytesIO(response.content)) as img:
            width, height = img.size
            result = {
                'width': width,
                'height': height,
                'format': img.format
            }
            
            # Cache the result
            cache[filename] = result
            try:
                os.makedirs('/data', exist_ok=True)
                with open(cache_file, 'w') as f:
                    json.dump(cache, f)
            except:
                pass
            
            return result
            
    except Exception as e:
        print(f"Error getting image info for {filepath}: {e}")
        # Cache the fallback result too
        result = {'width': 400, 'height': 300, 'format': 'JPEG'}
        cache[filename] = result
        try:
            os.makedirs('/data', exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(cache, f)
        except:
            pass
        return result

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

def load_hero_image():
    """Load hero image set in admin"""
    try:
        if os.path.exists('/data/hero_image.json'):
            with open('/data/hero_image.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return None

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
            
            # Get image info (skip network fetch during startup to prevent timeouts)
            info = get_image_info(filepath, skip_network_fetch=True)
            
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

    # Load hero image for admin template
    hero_image_data = load_hero_image()
    hero_image = None
    if hero_image_data and hero_image_data.get("filename"):
        # Find the hero image in the images list
        for image in images:
            if image["filename"] == hero_image_data["filename"]:
                hero_image = image
                break
    
    # Load hero image for mobile template
    hero_image_data = load_hero_image()
    hero_image = None
    if hero_image_data and hero_image_data.get('filename'):
        # Find the hero image in the images list
        for image in images:
            if image['filename'] == hero_image_data['filename']:
                hero_image = image
                break
    
    # Mobile detection - serve different template based on device
    if is_mobile_device():
        return render_template('mobile.html', 
                             images=images, 
                             categories=categories,
                             category_counts=category_counts,
                             featured_image=featured_image,
                             featured_exif=featured_exif,
                             about_data=about_data,
                             hero_image=hero_image)
    else:
        # Desktop users get the original template (unchanged)
        return render_template('index.html', 
                             images=images, 
                             categories=categories,
                             category_counts=category_counts,
                             featured_image=featured_image,
                             featured_exif=featured_exif,
                             about_data=about_data,
                             hero_image=hero_image)

@app.route('/mobile')
def mobile_gallery():

    """Mobile-optimized gallery page"""
    return render_template('mobile.html')

@app.route('/mobile-new')
def mobile_new():
    """New mobile layout for testing"""
    return render_template('mobile_new.html')

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

@app.route('/api/lumaprints/categories')
def api_lumaprints_categories():
    """Get all Lumaprints product categories"""
    try:
        client = get_lumaprints_client()
        categories = client.get_categories()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lumaprints/subcategories/<int:category_id>')
def api_lumaprints_subcategories(category_id):
    """Get subcategories for a specific category"""
    try:
        client = get_lumaprints_client()
        subcategories = client.get_subcategories(category_id)
        return jsonify(subcategories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lumaprints/options/<int:subcategory_id>')
def api_lumaprints_options(subcategory_id):
    """Get all options for a specific subcategory"""
    try:
        client = get_lumaprints_client()
        options = client.get_subcategory_options(subcategory_id)
        return jsonify(options)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/order-print/<image_id>')
def order_print(image_id):
    """Redirect old order print route to new PayPal-integrated form"""
    return redirect('/test_order_form')

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

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if authenticate_user(username, password):
            session['admin_authenticated'] = True
            session['admin_username'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def admin_forgot_password():
    """Forgot password page"""
    if request.method == 'POST':
        username = request.form.get('username')
        
        users = load_admin_users()
        if username in users and users[username].get('is_active', True):
            # Generate reset token
            reset_token = generate_reset_token()
            tokens = load_reset_tokens()
            tokens[reset_token] = {
                'username': username,
                'created_at': datetime.now().isoformat()
            }
            save_reset_tokens(tokens)
            
            # Create reset URL
            reset_url = f"{request.url_root}admin/reset-password/{reset_token}"
            
            flash(f'Password reset link generated! <a href="{reset_url}" target="_blank" style="color: #ff6b35; text-decoration: underline;">Click here to reset your password</a>', 'success')
            flash('This link will expire in 24 hours.', 'info')
        else:
            flash('Username not found or account is inactive.', 'error')
    
    return render_template('admin_forgot_password.html')

@app.route('/admin/reset-password/<token>', methods=['GET', 'POST'])
def admin_reset_password(token):
    """Reset password with token"""
    tokens = load_reset_tokens()
    
    if token not in tokens:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('admin_login'))
    
    token_data = tokens[token]
    username = token_data['username']
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        else:
            # Update password
            users = load_admin_users()
            if username in users:
                users[username]['password_hash'] = hash_password(password)
                save_admin_users(users)
                
                # Remove used token
                del tokens[token]
                save_reset_tokens(tokens)
                
                flash('Password updated successfully! You can now log in.', 'success')
                return redirect(url_for('admin_login'))
            else:
                flash('User not found.', 'error')
    
    return render_template('admin_reset_password.html', username=username)

@app.route('/admin/users')
@require_admin_auth
def admin_users():
    """User management page"""
    users = load_admin_users()
    user_count = get_user_count()
    can_add = can_add_user()
    
    return render_template('admin_users.html', 
                         users=users, 
                         user_count=user_count, 
                         can_add_user=can_add)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@require_admin_auth
def admin_add_user():
    """Add new user"""
    if not can_add_user():
        flash('Maximum number of users (4) reached.', 'error')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username:
            flash('Username is required.', 'error')
        elif not username.replace('_', '').isalnum():
            flash('Username can only contain letters, numbers, and underscores.', 'error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        else:
            users = load_admin_users()
            if username in users:
                flash('Username already exists.', 'error')
            else:
                # Create new user
                users[username] = {
                    'password_hash': hash_password(password),
                    'email': email,
                    'created_at': datetime.now().isoformat(),
                    'last_login': None,
                    'is_active': True
                }
                
                if save_admin_users(users):
                    flash(f'User "{username}" created successfully!', 'success')
                    return redirect(url_for('admin_users'))
                else:
                    flash('Error creating user. Please try again.', 'error')
    
    user_count = get_user_count()
    return render_template('admin_add_user.html', user_count=user_count)

@app.route('/admin/users/edit/<username>', methods=['GET', 'POST'])
@require_admin_auth
def admin_edit_user(username):
    """Edit user"""
    users = load_admin_users()
    if username not in users:
        flash('User not found.', 'error')
        return redirect(url_for('admin_users'))
    
    user = users[username]
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Update email
        user['email'] = email
        
        # Update password if provided
        if new_password:
            if len(new_password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
            elif new_password != confirm_password:
                flash('Passwords do not match.', 'error')
            else:
                user['password_hash'] = hash_password(new_password)
                flash('Password updated successfully!', 'success')
        
        users[username] = user
        if save_admin_users(users):
            flash(f'User "{username}" updated successfully!', 'success')
            return redirect(url_for('admin_users'))
        else:
            flash('Error updating user. Please try again.', 'error')
    
    return render_template('admin_edit_user.html', username=username, user=user)

@app.route('/admin/users/deactivate/<username>')
@require_admin_auth
def admin_deactivate_user(username):
    """Deactivate user"""
    if username == session.get('admin_username'):
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin_users'))
    
    users = load_admin_users()
    if username in users:
        users[username]['is_active'] = False
        if save_admin_users(users):
            flash(f'User "{username}" deactivated successfully.', 'success')
        else:
            flash('Error deactivating user.', 'error')
    else:
        flash('User not found.', 'error')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/activate/<username>')
@require_admin_auth
def admin_activate_user(username):
    """Activate user"""
    users = load_admin_users()
    if username in users:
        users[username]['is_active'] = True
        if save_admin_users(users):
            flash(f'User "{username}" activated successfully.', 'success')
        else:
            flash('Error activating user.', 'error')
    else:
        flash('User not found.', 'error')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/change-password', methods=['GET', 'POST'])
@require_admin_auth
def admin_change_password():
    """Change admin password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        admin_config = load_admin_config()
        
        # Verify current password
        if not verify_password(current_password, admin_config['password_hash']):
            flash('Current password is incorrect', 'error')
            return render_template('admin_change_password.html')
        
        # Validate new password
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long', 'error')
            return render_template('admin_change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('admin_change_password.html')
        
        # Update password
        admin_config['password_hash'] = hash_password(new_password)
        if save_admin_config(admin_config):
            flash('Password changed successfully', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Error saving new password', 'error')
    
    return render_template('admin_change_password.html')

@app.route('/admin')
@require_admin_auth
def admin():
    """Admin panel for image management"""
    try:
        images = scan_images()
        all_categories = load_categories()
        about_data = load_about_data()

        # Load hero image for admin template
        hero_image_data = load_hero_image()
        hero_image = None
        if hero_image_data and hero_image_data.get("filename"):
            # Find the hero image in the images list
            for image in images:
                if image["filename"] == hero_image_data["filename"]:
                    hero_image = image
                    break
        return render_template('admin_new.html', images=images, all_categories=all_categories, about_data=about_data,
                             hero_image=hero_image)
    except Exception as e:
        return f"Admin Error: {str(e)}", 500

@app.route('/admin/upload', methods=['POST'])
@require_admin_auth
@require_admin_auth
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
@require_admin_auth
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
@require_admin_auth
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

# Lumaprints Thumbnail Management Routes
PRODUCT_THUMBNAILS_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'product-thumbnails')
THUMBNAIL_ASSIGNMENTS_FILE = os.path.join(os.path.dirname(__file__), 'thumbnail-assignments.json')

def ensure_product_thumbnails_folder():
    """Ensure product thumbnails folder exists"""
    if not os.path.exists(PRODUCT_THUMBNAILS_FOLDER):
        os.makedirs(PRODUCT_THUMBNAILS_FOLDER)

def load_thumbnail_assignments():
    """Load thumbnail assignments from JSON file"""
    try:
        if os.path.exists(THUMBNAIL_ASSIGNMENTS_FILE):
            with open(THUMBNAIL_ASSIGNMENTS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading thumbnail assignments: {e}")
        return {}

def save_thumbnail_assignments(assignments):
    """Save thumbnail assignments to JSON file"""
    try:
        with open(THUMBNAIL_ASSIGNMENTS_FILE, 'w') as f:
            json.dump(assignments, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving thumbnail assignments: {e}")
        return False

@app.route('/admin/thumbnails')
@require_admin_auth
def admin_thumbnails():
    """Admin page for managing product thumbnails"""
    return render_template('admin_thumbnails.html')

@app.route('/admin/upload-product-thumbnails', methods=['POST'])
@require_admin_auth
def upload_product_thumbnails():
    """Upload product thumbnails to the product-thumbnails directory"""
    try:
        ensure_product_thumbnails_folder()
        
        files = request.files.getlist('thumbnails')
        
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'No files selected'})
        
        uploaded_count = 0
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ensure unique filename
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while os.path.exists(os.path.join(PRODUCT_THUMBNAILS_FOLDER, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
                
                filepath = os.path.join(PRODUCT_THUMBNAILS_FOLDER, filename)
                file.save(filepath)
                uploaded_count += 1
        
        return jsonify({'success': True, 'uploaded': uploaded_count})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/product-thumbnails')
@require_admin_auth
def get_product_thumbnails():
    """Get all product thumbnails with their assignments"""
    try:
        ensure_product_thumbnails_folder()
        assignments = load_thumbnail_assignments()
        
        thumbnails = []
        for filename in os.listdir(PRODUCT_THUMBNAILS_FOLDER):
            if allowed_file(filename):
                thumbnail_id = filename
                assignment = assignments.get(thumbnail_id, '')
                
                # Get human-readable assignment name
                assignment_name = get_product_name(assignment) if assignment else ''
                
                thumbnails.append({
                    'id': thumbnail_id,
                    'name': filename,
                    'url': f"/product-thumbnails/{filename}",
                    'assignment': assignment_name
                })
        
        return jsonify(thumbnails)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/product-thumbnails/<filename>')
def serve_product_thumbnail(filename):
    """Serve product thumbnail files"""
    try:
        return send_from_directory(PRODUCT_THUMBNAILS_FOLDER, filename)
    except Exception as e:
        return "Thumbnail not found", 404

@app.route('/admin/assign-thumbnail', methods=['POST'])
@require_admin_auth
def assign_thumbnail():
    """Assign a thumbnail to a specific product"""
    try:
        data = request.get_json()
        thumbnail_id = data.get('thumbnail_id')
        product_id = data.get('product_id')
        
        if not thumbnail_id or not product_id:
            return jsonify({'success': False, 'error': 'Missing thumbnail_id or product_id'})
        
        # Load current assignments
        assignments = load_thumbnail_assignments()
        
        # Update assignment
        assignments[thumbnail_id] = product_id
        
        # Save assignments
        if save_thumbnail_assignments(assignments):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to save assignment'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/delete-product-thumbnail/<thumbnail_id>', methods=['DELETE'])
@require_admin_auth
def delete_product_thumbnail(thumbnail_id):
    """Delete a product thumbnail"""
    try:
        thumbnail_path = os.path.join(PRODUCT_THUMBNAILS_FOLDER, thumbnail_id)
        
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            
            # Also remove from assignments
            assignments = load_thumbnail_assignments()
            if thumbnail_id in assignments:
                del assignments[thumbnail_id]
                save_thumbnail_assignments(assignments)
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Thumbnail not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_product_name(product_id):
    """Convert product ID to human-readable name"""
    product_names = {
        'canvas-075-stretched': 'Canvas - 0.75" Stretched',
        'canvas-125-stretched': 'Canvas - 1.25" Stretched',
        'canvas-150-stretched': 'Canvas - 1.50" Stretched',
        'canvas-rolled': 'Canvas - Rolled',
        'framed-canvas-075-black': 'Framed Canvas - 0.75" Black',
        'framed-canvas-075-white': 'Framed Canvas - 0.75" White',
        'framed-canvas-075-silver': 'Framed Canvas - 0.75" Silver',
        'framed-canvas-075-gold': 'Framed Canvas - 0.75" Gold',
        'framed-canvas-075-espresso': 'Framed Canvas - 0.75" Espresso',
        'framed-canvas-125-black': 'Framed Canvas - 1.25" Black',
        'framed-canvas-125-white': 'Framed Canvas - 1.25" White',
        'framed-canvas-125-oak': 'Framed Canvas - 1.25" Oak',
        'framed-canvas-125-walnut': 'Framed Canvas - 1.25" Walnut',
        'framed-canvas-125-espresso': 'Framed Canvas - 1.25" Espresso',
        'framed-canvas-150-black': 'Framed Canvas - 1.50" Black',
        'framed-canvas-150-white': 'Framed Canvas - 1.50" White',
        'framed-canvas-150-silver': 'Framed Canvas - 1.50" Silver',
        'framed-canvas-150-gold': 'Framed Canvas - 1.50" Gold',
        'framed-canvas-150-oak': 'Framed Canvas - 1.50" Oak',
        'framed-canvas-150-espresso': 'Framed Canvas - 1.50" Espresso',
        'fine-art-archival-matte': 'Fine Art Paper - Archival Matte',
        'fine-art-hot-press': 'Fine Art Paper - Hot Press',
        'fine-art-cold-press': 'Fine Art Paper - Cold Press',
        'fine-art-semi-glossy': 'Fine Art Paper - Semi-Glossy',
        'fine-art-metallic': 'Fine Art Paper - Metallic',
        'fine-art-glossy': 'Fine Art Paper - Glossy',
        'fine-art-somerset-velvet': 'Fine Art Paper - Somerset Velvet',
        'framed-fine-art-0875-black': 'Framed Fine Art - 0.875" Black',
        'framed-fine-art-0875-white': 'Framed Fine Art - 0.875" White',
        'framed-fine-art-0875-oak': 'Framed Fine Art - 0.875" Oak',
        'framed-fine-art-0875-walnut': 'Framed Fine Art - 0.875" Walnut',
        'framed-fine-art-0875-espresso': 'Framed Fine Art - 0.875" Espresso',
        'framed-fine-art-125-black': 'Framed Fine Art - 1.25" Black',
        'framed-fine-art-125-white': 'Framed Fine Art - 1.25" White',
        'framed-fine-art-125-oak': 'Framed Fine Art - 1.25" Oak',
        'framed-fine-art-125-walnut': 'Framed Fine Art - 1.25" Walnut',
        'framed-fine-art-125-espresso': 'Framed Fine Art - 1.25" Espresso',
        'metal-glossy': 'Metal - Glossy',
        'metal-matte': 'Metal - Matte',
        'foam-mounted-archival-matte': 'Foam Mounted - Archival Matte',
        'foam-mounted-hot-press': 'Foam Mounted - Hot Press',
        'foam-mounted-cold-press': 'Foam Mounted - Cold Press',
        'foam-mounted-semi-glossy': 'Foam Mounted - Semi-Glossy',
        'foam-mounted-metallic': 'Foam Mounted - Metallic',
        'foam-mounted-glossy': 'Foam Mounted - Glossy',
        'peel-stick-vinyl': 'Peel and Stick - Vinyl',
        'peel-stick-fabric': 'Peel and Stick - Fabric'
    }
    return product_names.get(product_id, product_id)

@app.route('/admin/categories', methods=['GET', 'POST'])
@require_admin_auth
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
        
        return redirect(url_for('manage_categories'))
    
    # GET request - show categories management page
    categories = load_categories()
    return render_template('admin_categories.html', categories=categories)

@app.route('/admin/assign_category/<filename>', methods=['POST'])
@require_admin_auth
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
@require_admin_auth
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

    # Load hero image for admin template
    hero_image_data = load_hero_image()
    hero_image = None
    if hero_image_data and hero_image_data.get("filename"):
        # Find the hero image in the images list
        for image in images:
            if image["filename"] == hero_image_data["filename"]:
                hero_image = image
                break
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
@require_admin_auth
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
@app.route('/api/lumaprints/options/<int:subcategory_id>')
def get_lumaprints_options(subcategory_id):
    """Get frame options for a specific subcategory (3rd level for Framed Canvas)"""
    try:
        catalog = load_lumaprints_catalog()
        options = catalog.get('options', {}).get(str(subcategory_id), [])
        return jsonify({
            'success': True,
            'options': options
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
    """Redirect old order print form to new PayPal-integrated form"""
    return redirect('/test_order_form')

@app.route('/api/lumaprints/submit-order', methods=['POST'])
def submit_lumaprints_order():
    """Submit an order to Lumaprints and store locally"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer', 'shipping', 'items', 'payment']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Generate order ID
        order_id = str(uuid.uuid4())[:8].upper()
        
        # Calculate total price from items
        total_price = sum(item.get('totalPrice', 0) for item in data['items'])
        
        # Create order record
        order_record = {
            'orderId': order_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'payment_received',
            'customer': data['customer'],
            'items': data['items'],
            'pricing': {
                'total': total_price
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
            api = get_lumaprints_client(sandbox=False)
            
            # Prepare order items for Lumaprints
            order_items = []
            for i, item in enumerate(data['items']):
                # Convert local image URL to full URL
                image_url = item['imageUrl']
                if image_url.startswith('/static/'):
                    # Convert to full URL
                    image_url = f"https://fifth-element-photography-production.up.railway.app{image_url}"
                
                order_items.append({
                    "externalItemId": f"{order_id}-{i+1}",
                    "subcategoryId": item['subcategoryId'],
                    "quantity": item['quantity'],
                    "width": item['width'],
                    "height": item['height'],
                    "file": {
                        "imageUrl": image_url
                    },
                    "orderItemOptions": item.get('options', []),
                    "solidColorHexCode": None
                })
            
            # Prepare Lumaprints order payload
            lumaprints_payload = {
                "externalId": order_id,
                "storeId": "20027",  # Your store ID from catalog
                "shippingMethod": "default",
                "productionTime": "regular",
                "recipient": {
                    "firstName": data['shipping']['firstName'],
                    "lastName": data['shipping']['lastName'],
                    "addressLine1": data['shipping']['address1'],
                    "addressLine2": data['shipping'].get('address2', ''),
                    "city": data['shipping']['city'],
                    "state": data['shipping']['state'],
                    "zipCode": data['shipping']['postalCode'],
                    "country": data['shipping']['country'],
                    "phone": data['shipping'].get('phone', ''),
                    "company": ""
                },
                "orderItems": order_items
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
            'order': {
                'id': order_id,
                'status': order_record['status']
            },
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
@require_admin_auth
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

# Initialize dynamic pricing calculator with 150% markup using database
from dynamic_pricing_calculator import get_dynamic_pricing_calculator
pricing_calc = get_dynamic_pricing_calculator(markup_percentage=150.0)

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
        
        # Format response for frontend compatibility
        formatted_response = {
            'success': True,
            'pricing': {
                'formatted_price': f"${pricing_result['total_retail']:.2f}",
                'formatted_price_per_item': f"${pricing_result['price_per_item']:.2f}",
                'total_price': pricing_result['total_retail'],
                'price_per_item': pricing_result['price_per_item'],
                'wholesale_price': pricing_result['wholesale_price'],
                'quantity': pricing_result['quantity'],
                'markup_percentage': pricing_result['markup_percentage']
            },
            'product_info': {
                'subcategory_id': subcategory_id,
                'category': pricing_result.get('category', ''),
                'subcategory': pricing_result.get('subcategory', ''),
                'width': width,
                'height': height
            }
        }
        
        return jsonify(formatted_response)
        
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

@app.route('/api/lumaprints/sizes/<int:subcategory_id>')
def get_lumaprints_sizes(subcategory_id):
    """Get available sizes for a specific subcategory"""
    try:
        sizes = pricing_calc.get_available_sizes(subcategory_id)
        
        return jsonify({
            'success': True,
            'subcategory_id': subcategory_id,
            'sizes': sizes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/pricing-summary')
def get_pricing_summary():
    """Get pricing database summary information"""
    try:
        summary = pricing_calc.pricing_manager.get_pricing_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
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
@require_admin_auth
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

# ============================================================================
# ADMIN IMAGE DOWNLOAD ROUTE
# ============================================================================

@app.route('/admin/download-image/<filename>')
@require_admin_auth
def download_image(filename):
    """Download original image file for admin use (e.g., uploading to Lumaprints)"""
    try:
        # Security check - ensure filename is safe
        if not filename or '..' in filename or '/' in filename:
            return "Invalid filename", 400
        
        # Check if file exists
        file_path = os.path.join(IMAGES_FOLDER, filename)
        if not os.path.exists(file_path):
            return "File not found", 404
        
        # Send file with proper headers for download
        return send_from_directory(
            IMAGES_FOLDER, 
            filename, 
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/admin/download-highres/<filename>')
@require_admin_auth
def download_highres_image(filename):
    """Download high-resolution version of image for Lumaprints upload"""
    try:
        from image_storage_manager import ImageStorageManager
        storage_manager = ImageStorageManager()
        
        # Security check - ensure filename is safe
        if not filename or '..' in filename or '/' in filename:
            return "Invalid filename", 400
        
        # Get high-res path
        highres_path = storage_manager.get_highres_path(filename)
        
        if not highres_path:
            return "High-resolution version not found", 404
        
        # Send file with proper headers for download
        return send_from_directory(
            os.path.dirname(highres_path), 
            os.path.basename(highres_path), 
            as_attachment=True,
            download_name=f"highres_{filename}"
        )
        
    except Exception as e:
        return f"Error downloading high-res file: {str(e)}", 500

@app.route('/api/image-storage-info')
def get_image_storage_info():
    """Get storage information for all images"""
    try:
        from image_storage_manager import ImageStorageManager
        storage_manager = ImageStorageManager()
        
        all_info = storage_manager.get_all_images_info()
        
        return jsonify({
            'success': True,
            'images': all_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Product Thumbnail Management Routes
@app.route('/admin/products')
@require_admin_auth
def admin_products():
    """Product thumbnail management page"""
    return render_template('admin_products_new.html')

@app.route('/api/product-thumbnail-check/<product_key>')
def check_product_thumbnail(product_key):
    """Check if a product thumbnail exists"""
    try:
        thumbnails_dir = os.path.join('static', 'product-thumbnails')
        filename = f"{product_key}.jpg"
        thumbnail_path = os.path.join(thumbnails_dir, filename)
        
        if os.path.exists(thumbnail_path):
            return jsonify({
                'exists': True,
                'url': f'/static/product-thumbnails/{filename}',
                'filename': filename
            })
        else:
            return jsonify({'exists': False})
    except Exception as e:
        return jsonify({'exists': False, 'error': str(e)}), 500

@app.route('/api/upload-product-thumbnail-new', methods=['POST'])
def upload_product_thumbnail_new():
    """Upload a product thumbnail with new structure"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        product_key = request.form.get('productKey')
        product_type = request.form.get('productType')
        product_variant = request.form.get('productVariant')
        
        if not file or file.filename == '' or not product_key:
            return jsonify({'success': False, 'message': 'File and product information required'}), 400
        
        # Create thumbnails directory
        thumbnails_dir = os.path.join('static', 'product-thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # Process and save image
        from PIL import Image
        import io
        import pillow_heif
        
        # Register HEIF opener for AVIF support
        pillow_heif.register_heif_opener()
        
        # Read file content into memory
        file.stream.seek(0)  # Reset stream position
        file_content = file.stream.read()
        
        # Open and process image from bytes
        image = Image.open(io.BytesIO(file_content))
        
        # Convert to RGB if necessary (handles AVIF, PNG with transparency, etc.)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Keep original size (150x150) - no resizing needed
        filename = f"{product_key}.jpg"
        thumbnail_path = os.path.join(thumbnails_dir, filename)
        
        # Save as JPEG
        image.save(thumbnail_path, 'JPEG', quality=90, optimize=True)
        
        # Save metadata
        metadata_file = os.path.join(thumbnails_dir, 'metadata.json')
        metadata = {}
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        
        metadata[product_key] = {
            'productType': product_type,
            'productVariant': product_variant,
            'filename': filename,
            'uploadDate': datetime.now().isoformat()
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Thumbnail uploaded successfully',
            'url': f'/static/product-thumbnails/{filename}',
            'productKey': product_key
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error uploading thumbnail: {str(e)}'
        }), 500

@app.route('/api/delete-product-thumbnail-new/<product_key>', methods=['DELETE'])
def delete_product_thumbnail_new(product_key):
    """Delete a product thumbnail"""
    try:
        thumbnails_dir = os.path.join('static', 'product-thumbnails')
        filename = f"{product_key}.jpg"
        thumbnail_path = os.path.join(thumbnails_dir, filename)
        
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            
            # Remove from metadata
            metadata_file = os.path.join(thumbnails_dir, 'metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                if product_key in metadata:
                    del metadata[product_key]
                    
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
            
            return jsonify({'success': True, 'message': 'Thumbnail deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Thumbnail not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/product-thumbnails-new')
def get_product_thumbnails_new():
    """Get all product thumbnails with metadata"""
    try:
        thumbnails_dir = os.path.join('static', 'product-thumbnails')
        metadata_file = os.path.join(thumbnails_dir, 'metadata.json')
        
        thumbnails = []
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            for product_key, info in metadata.items():
                thumbnail_path = os.path.join(thumbnails_dir, info['filename'])
                if os.path.exists(thumbnail_path):
                    thumbnails.append({
                        'productKey': product_key,
                        'productType': info['productType'],
                        'productVariant': info['productVariant'],
                        'filename': info['filename'],
                        'url': f'/static/product-thumbnails/{info["filename"]}',
                        'displayName': info['productVariant'],
                        'uploadDate': info.get('uploadDate', '')
                    })
        
        return jsonify({'thumbnails': thumbnails})
        
    except Exception as e:
        return jsonify({'thumbnails': [], 'error': str(e)}), 500

@app.route('/api/product-thumbnails-stats')
def get_product_thumbnails_stats():
    """Get thumbnail upload statistics"""
    try:
        # Count total possible thumbnails from PRODUCT_VARIANTS
        total_variants = 0
        total_variants += 4  # Canvas
        total_variants += 32  # Framed Canvas (approximate)
        total_variants += 7   # Fine Art Paper
        total_variants += 9   # Foam-mounted Print
        total_variants += 25  # Framed Fine Art Paper (approximate)
        total_variants += 2   # Metal
        total_variants += 1   # Peel and Stick
        
        # Count uploaded thumbnails
        thumbnails_dir = os.path.join('static', 'product-thumbnails')
        metadata_file = os.path.join(thumbnails_dir, 'metadata.json')
        
        uploaded_count = 0
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                uploaded_count = len(metadata)
        
        percentage = round((uploaded_count / total_variants) * 100) if total_variants > 0 else 0
        
        return jsonify({
            'uploaded': uploaded_count,
            'total': total_variants,
            'percentage': percentage
        })
        
    except Exception as e:
        return jsonify({
            'uploaded': 0,
            'total': 80,
            'percentage': 0,
            'error': str(e)
        }), 500

@app.route('/api/product-thumbnail/<path:product_path>')
def get_product_thumbnail(product_path):
    """Check if a product thumbnail exists"""
    try:
        # Create thumbnails directory if it doesn't exist
        thumbnails_dir = os.path.join('static', 'product-thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # Convert path to filename
        filename = product_path.replace('/', '_') + '.jpg'
        thumbnail_path = os.path.join(thumbnails_dir, filename)
        
        if os.path.exists(thumbnail_path):
            return jsonify({
                'exists': True,
                'url': f'/static/product-thumbnails/{filename}',
                'path': product_path
            })
        else:
            return jsonify({
                'exists': False,
                'path': product_path
            })
    except Exception as e:
        return jsonify({
            'exists': False,
            'error': str(e)
        }), 500

@app.route('/api/upload-product-thumbnail', methods=['POST'])
def upload_product_thumbnail():
    """Upload a product thumbnail"""
    try:
        print(f"Upload request received. Files: {list(request.files.keys())}")
        print(f"Form data: {dict(request.form)}")
        
        if 'file' not in request.files:
            print("No file in request")
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        product_path = request.form.get('productPath')
        
        print(f"File: {file}, filename: {file.filename if file else 'None'}")
        print(f"Product path: {product_path}")
        
        if not file or file.filename == '' or not product_path:
            print("Invalid file or product path")
            return jsonify({'success': False, 'message': 'File and product path required'}), 400
        
        # Create thumbnails directory
        thumbnails_dir = os.path.join('static', 'product-thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # Convert path to filename
        filename = product_path.replace('/', '_') + '.jpg'
        
        # Process and save image
        from PIL import Image
        import io
        import pillow_heif
        
        # Register HEIF opener for AVIF support
        pillow_heif.register_heif_opener()
        
        # Open and process image
        image = Image.open(file.stream)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize to standard thumbnail size
        image.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        # Save as JPEG
        thumbnail_path = os.path.join(thumbnails_dir, filename)
        image.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
        
        return jsonify({
            'success': True,
            'message': 'Thumbnail uploaded successfully',
            'url': f'/static/product-thumbnails/{filename}',
            'path': product_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error uploading thumbnail: {str(e)}'
        }), 500

@app.route('/api/delete-product-thumbnail/<path:product_path>', methods=['DELETE'])
def delete_product_thumbnail_by_path(product_path):
    """Delete a product thumbnail"""
    try:
        # Convert path to filename
        filename = product_path.replace('/', '_') + '.jpg'
        thumbnail_path = os.path.join('static', 'product-thumbnails', filename)
        
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            return jsonify({
                'success': True,
                'message': 'Thumbnail deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Thumbnail not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting thumbnail: {str(e)}'
        }), 500

@app.route('/api/product-thumbnails')
def get_all_product_thumbnails():
    """Get all existing product thumbnails"""
    try:
        thumbnails_dir = os.path.join('static', 'product-thumbnails')
        thumbnails = []
        
        if os.path.exists(thumbnails_dir):
            for filename in os.listdir(thumbnails_dir):
                if filename.endswith('.jpg'):
                    # Convert filename back to path
                    product_path = filename[:-4].replace('_', '/')
                    
                    # Create display name
                    parts = product_path.split('/')
                    display_name = f"{parts[0].replace('-', ' ').title()} - {parts[1]} - {parts[2].replace('-', ' ').title()}"
                    
                    thumbnails.append({
                        'name': filename,
                        'path': product_path,
                        'displayName': display_name,
                        'url': f'/static/product-thumbnails/{filename}'
                    })
        
        # Sort by display name
        thumbnails.sort(key=lambda x: x['displayName'])
        
        return jsonify({
            'success': True,
            'thumbnails': thumbnails
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Route to serve correct canvas sizes data
@app.route('/correct_canvas_sizes.json')
def serve_correct_canvas_sizes():
    """Serve the correct canvas sizes data"""
    try:
        with open('correct_canvas_sizes.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Duplicate function removed - using the first implementation above


@app.route('/checkout')
def checkout():
    """Display the professional checkout form"""
    return render_template('checkout.html')


# ============================================================================
# PRICING MANAGEMENT ROUTES
# ============================================================================

def load_pricing_config():
    """Load pricing configuration from JSON file"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'pricing_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading pricing config: {e}")
    
    # Return default config if file doesn't exist or has errors
    return {
        "global_margin": 100,
        "products": {}
    }

def save_pricing_config(config):
    """Save pricing configuration to JSON file"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'pricing_config.json')
        config['last_updated'] = datetime.now().isoformat()
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving pricing config: {e}")
        return False

@app.route('/admin/pricing')
@require_admin_auth
def admin_pricing():
    """Pricing management admin page"""
    try:
        pricing_config = load_pricing_config()
        return render_template('admin_pricing.html', pricing_config=pricing_config)
    except Exception as e:
        return f"Pricing Admin Error: {str(e)}", 500

@app.route('/admin/pricing/update-margin', methods=['POST'])
@require_admin_auth
def update_global_margin():
    """Update global margin percentage"""
    try:
        data = request.get_json()
        margin = float(data.get('margin', 100))
        
        config = load_pricing_config()
        config['global_margin'] = margin
        
        if save_pricing_config(config):
            return jsonify({'success': True, 'message': 'Global margin updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error saving configuration'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/pricing/update-variant', methods=['POST'])
@require_admin_auth
def update_variant_price():
    """Update individual variant base cost"""
    try:
        data = request.get_json()
        product_type = data.get('product_type')
        variant_key = data.get('variant_key')
        base_cost = float(data.get('base_cost', 0))
        
        config = load_pricing_config()
        
        if product_type in config['products'] and variant_key in config['products'][product_type]['variants']:
            config['products'][product_type]['variants'][variant_key]['base_cost'] = base_cost
            
            if save_pricing_config(config):
                return jsonify({'success': True, 'message': 'Variant price updated successfully'})
            else:
                return jsonify({'success': False, 'message': 'Error saving configuration'}), 500
        else:
            return jsonify({'success': False, 'message': 'Product or variant not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/pricing/add-variant', methods=['POST'])
@require_admin_auth
def add_variant():
    """Add new variant to existing product"""
    try:
        data = request.get_json()
        product_type = data.get('product_type')
        variant_name = data.get('variant_name')
        base_cost = float(data.get('base_cost', 0))
        sku = data.get('sku', '')
        lumaprints_options = data.get('lumaprints_options', '')
        
        config = load_pricing_config()
        
        if product_type not in config['products']:
            return jsonify({'success': False, 'message': 'Product type not found'}), 404
        
        # Create variant key from name
        variant_key = variant_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('"', '')
        
        config['products'][product_type]['variants'][variant_key] = {
            'display_name': variant_name,
            'base_cost': base_cost,
            'sku': sku,
            'lumaprints_options': lumaprints_options
        }
        
        if save_pricing_config(config):
            return jsonify({'success': True, 'message': 'Variant added successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error saving configuration'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/pricing/delete-variant', methods=['POST'])
@require_admin_auth
def delete_variant():
    """Delete variant from product"""
    try:
        data = request.get_json()
        product_type = data.get('product_type')
        variant_key = data.get('variant_key')
        
        config = load_pricing_config()
        
        if product_type in config['products'] and variant_key in config['products'][product_type]['variants']:
            del config['products'][product_type]['variants'][variant_key]
            
            if save_pricing_config(config):
                return jsonify({'success': True, 'message': 'Variant deleted successfully'})
            else:
                return jsonify({'success': False, 'message': 'Error saving configuration'}), 500
        else:
            return jsonify({'success': False, 'message': 'Product or variant not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/pricing/add-product', methods=['POST'])
@require_admin_auth
def add_new_product():
    """Add new product type"""
    try:
        data = request.get_json()
        product_key = data.get('product_key', '').lower()
        display_name = data.get('display_name', '')
        
        if not product_key or not display_name:
            return jsonify({'success': False, 'message': 'Product key and display name are required'}), 400
        
        config = load_pricing_config()
        
        if product_key in config['products']:
            return jsonify({'success': False, 'message': 'Product already exists'}), 400
        
        config['products'][product_key] = {
            'display_name': display_name,
            'active': True,
            'variants': {}
        }
        
        if save_pricing_config(config):
            return jsonify({'success': True, 'message': 'Product added successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error saving configuration'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/pricing/toggle-product', methods=['POST'])
@require_admin_auth
def toggle_product():
    """Toggle product active/inactive status"""
    try:
        data = request.get_json()
        product_type = data.get('product_type')
        
        config = load_pricing_config()
        
        if product_type not in config['products']:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        config['products'][product_type]['active'] = not config['products'][product_type].get('active', True)
        
        if save_pricing_config(config):
            return jsonify({'success': True, 'message': 'Product status updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error saving configuration'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/pricing/delete-product', methods=['POST'])
@require_admin_auth
def delete_product():
    """Delete entire product and all variants"""
    try:
        data = request.get_json()
        product_type = data.get('product_type')
        
        config = load_pricing_config()
        
        if product_type not in config['products']:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        del config['products'][product_type]
        
        if save_pricing_config(config):
            return jsonify({'success': True, 'message': 'Product deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Error saving configuration'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/pricing/calculate', methods=['POST'])
def calculate_price():
    """Calculate final price for a product variant"""
    try:
        data = request.get_json()
        product_type = data.get('product_type')
        variant_key = data.get('variant_key')
        
        config = load_pricing_config()
        
        if product_type not in config['products'] or variant_key not in config['products'][product_type]['variants']:
            return jsonify({'success': False, 'message': 'Product or variant not found'}), 404
        
        variant = config['products'][product_type]['variants'][variant_key]
        base_cost = variant.get('base_cost', 0)
        margin = config.get('global_margin', 100)
        
        final_price = base_cost * (1 + margin / 100)
        
        return jsonify({
            'success': True,
            'base_cost': base_cost,
            'margin_percent': margin,
            'final_price': round(final_price, 2),
            'variant_info': variant
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================================================
# IMAGE ANALYZER ADMIN ROUTE
# ============================================================================



# ============================================================================
# ORDERDESK TEST INTEGRATION ROUTES
# ============================================================================

import requests

# OrderDesk API Configuration - UPDATE THESE WITH YOUR ACTUAL VALUES
ORDERDESK_API_URL = "https://app.orderdesk.me/api/v2/orders"
ORDERDESK_STORE_ID = "125137"
ORDERDESK_API_KEY = "pXmXDSnjdoRsjPYWD6uU2CBCcKPgZUur7SDDSMUa6NR2R4v6mQ"

# Product mapping for test - 12x12 Sparrow canvas
ORDERDESK_PRODUCT_MAPPING = {
    "101001": {"name": "Canvas Print 0.75in (12x12)", "price": 25.00, "lumaprints_options": "1,5"},
    "106001": {"name": "Metal Print", "price": 35.00, "lumaprints_options": "29,31"},
    "103001": {"name": "Fine Art Paper", "price": 20.00, "lumaprints_options": "36"}
}

@app.route('/test_order_form')
def test_order_form():
    """Display the test order form for OrderDesk integration"""
    # PayPal integration added - force staging redeploy
    return render_template('test_order_form.html')

@app.route('/test_order_submit', methods=['POST'])
def test_order_submit():
    """Submit test order to OrderDesk API with dynamic pricing"""
    try:
        # Get form data
        form_data = request.form
        product_sku = form_data.get('product_sku')  # Now comes from dynamic pricing
        lumaprints_options = form_data.get('lumaprints_options')  # From dynamic pricing
        product_price = float(form_data.get('product_price', 0))  # From dynamic pricing
        paypal_order_id = form_data.get('paypal_order_id')
        paypal_payer_id = form_data.get('paypal_payer_id')
        
        # Verify PayPal payment was completed
        if not paypal_order_id or not paypal_payer_id:
            return jsonify({
                "status": "error",
                "message": "Payment required before order submission"
            }), 400
        
        # Verify we have product information
        if not product_sku or not lumaprints_options or product_price <= 0:
            return jsonify({
                "status": "error", 
                "message": "Invalid product information"
            }), 400
        
        # Get product name from form data or create a generic one
        product_name = f"Print Order - SKU {product_sku}"
        if product_sku == "101001":
            product_name = "Canvas Print 0.75\" (12x12)"
        elif product_sku == "101002":
            product_name = "Canvas Print 1.25\" (12x12)"
        elif product_sku == "106001":
            product_name = "Metal Print (12x12)"
        elif product_sku == "103001":
            product_name = "Fine Art Paper (12x12)"
        
        # Prepare OrderDesk order data with dynamic pricing
        order_data = {
            "source_name": "Fifth Element Photography",
            "email": form_data.get('email'),
            "shipping": {
                "first_name": form_data.get('first_name'),
                "last_name": form_data.get('last_name'),
                "address1": form_data.get('address1'),
                "city": form_data.get('city'),
                "state": form_data.get('state'),
                "postal_code": form_data.get('postal_code'),
                "country": form_data.get('country'),
                "phone": form_data.get('phone', '')
            },
            "order_items": [
                {
                    "name": product_name + " - SPARROW 12x12 SQUARE CANVAS",
                    "price": product_price,  # Use dynamic pricing
                    "quantity": 1,
                    "weight": 1.0,
                    "code": product_sku,
                    "metadata": {
                        "print_sku": product_sku,
                        "print_url": "https://fifthelement.photos/images/12x12_Sparrow.jpg",
                        "print_width": "12",
                        "print_height": "12",
                        "lumaprints_options": lumaprints_options,  # Use dynamic options
                        "paypal_order_id": paypal_order_id,
                        "paypal_payer_id": paypal_payer_id,
                        "payment_status": "COMPLETED",
                        "dynamic_pricing": True  # Flag to indicate this uses new pricing system
                    }
                }
            ]
        }
        
        # Submit to OrderDesk API
        headers = {
            "ORDERDESK-STORE-ID": ORDERDESK_STORE_ID,
            "ORDERDESK-API-KEY": ORDERDESK_API_KEY,
            "Content-Type": "application/json"
        }
        
        print("=== ORDERDESK DEBUG INFO ===")
        print(f"Store ID: {ORDERDESK_STORE_ID}")
        print(f"API Key: {ORDERDESK_API_KEY[:10]}...")
        print(f"URL: {ORDERDESK_API_URL}")
        print("Headers:", headers)
        print("Order Data:", json.dumps(order_data, indent=2))
        
        # Test authentication first
        test_url = "https://app.orderdesk.me/api/v2/test"
        test_response = requests.get(test_url, headers=headers)
        print(f"Auth Test Status: {test_response.status_code}")
        print(f"Auth Test Response: {test_response.text}")
        
        if test_response.status_code != 200:
            print("❌ Authentication test failed!")
            return jsonify({
                "status": "error",
                "message": "OrderDesk authentication failed",
                "auth_test_status": test_response.status_code,
                "auth_test_response": test_response.text
            }), 401
        
        response = requests.post(ORDERDESK_API_URL, headers=headers, json=order_data)
        
        print("OrderDesk Response Status:", response.status_code)
        print("OrderDesk Response:", response.text)
        
        if response.status_code == 201:
            # Success
            order_response = response.json()
            # flash(f'Order submitted successfully! OrderDesk Order ID: {order_response.get("id")}', 'success')  # Removed to clean up admin
            return jsonify({
                "status": "success",
                "message": "Order submitted to OrderDesk successfully",
                "orderdesk_order_id": order_response.get("id"),
                "response": order_response
            })
        else:
            # Error
            # flash(f'Error submitting order: {response.text}', 'error')  # Removed to clean up admin
            return jsonify({
                "status": "error",
                "message": f"OrderDesk API error: {response.status_code}",
                "response": response.text
            }), 400
            
    except Exception as e:
        print("Exception:", str(e))
        # flash(f'Error: {str(e)}', 'error')  # Removed to clean up admin
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
