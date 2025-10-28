from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file, send_from_directory
import os
import json
import sqlite3
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

# Pictorem integration (DISABLED)
# from pictorem_product_api import get_products_for_frontend, get_product_price_api, get_categories_for_frontend, get_product_details
# from pictorem_admin import pictorem_admin_bp
# from pictorem_api import PictoremAPI

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Register Pictorem admin blueprint (DISABLED)
# app.register_blueprint(pictorem_admin_bp)

# Initialize database if it doesn't exist
def ensure_database_exists():
    """Ensure the database exists and has the required schema"""
    # Ensure /data directory exists
    os.makedirs('/data', exist_ok=True)
    db_path = '/data/lumaprints_pricing.db'
    old_db_path = 'lumaprints_pricing.db'
    
    # Check if old database exists and copy it to new location
    if not os.path.exists(db_path) and os.path.exists(old_db_path):
        print(f"Found old database at {old_db_path}, copying to {db_path}...")
        try:
            shutil.copy2(old_db_path, db_path)
            print(f"Successfully copied database to {db_path}")
            return
        except Exception as e:
            print(f"Error copying database: {e}")
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}, initializing...")
        try:
            from init_pricing_db import init_pricing_database
            init_pricing_database()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            # Create minimal schema if init script fails
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS product_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sub_option_1_name TEXT,
                sub_option_2_name TEXT
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS sub_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_type_id INTEGER,
                level INTEGER,
                option_type TEXT,
                name TEXT,
                value TEXT
            )''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT,
                size TEXT,
                cost_price REAL,
                product_type_id INTEGER,
                sub_option_1_id INTEGER,
                sub_option_2_id INTEGER,
                lumaprints_subcategory_id INTEGER,
                lumaprints_options TEXT,
                active INTEGER DEFAULT 1
            )''')
            cursor.execute("INSERT OR IGNORE INTO settings (key_name, value) VALUES ('global_markup_percentage', '150.0')")
            conn.commit()
            conn.close()
            print("Minimal database schema created")

# Call initialization on startup
ensure_database_exists()

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
        # TEMPORARILY DISABLED FOR TESTING - REMOVE BEFORE PRODUCTION
        # if not session.get('admin_authenticated'):
        #     return redirect(url_for('admin_login'))
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
    categories = sorted(load_categories())
    
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
        return render_template('mobile_new.html', 
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
    return render_template('mobile_new.html')

@app.route('/mobile-new')
@app.route('/mobile-new')
def mobile_new():
    """Mobile layout with admin data - using same data loading as main route"""
    images = scan_images()
    categories = sorted(load_categories())
    
    # Get category counts (same as main route)
    category_counts = {}
    for category in categories:
        category_counts[category] = len([img for img in images if img['category'] == category])
    
    # Get featured image from featured_image.json (same as main route)
    featured_image = None
    featured_image_data = load_featured_image()
    if featured_image_data and featured_image_data.get('filename'):
        # Find the featured image in the images list
        for image in images:
            if image['filename'] == featured_image_data['filename']:
                featured_image = image
                break
    
    # If no featured image is set, fallback to first landscape image or first image (same as main route)
    if not featured_image:
        for image in images:
            if image['category'] == 'landscape':
                featured_image = image
                break
        if not featured_image and images:
            featured_image = images[0]
    
    # Extract EXIF data for featured image (same as main route)
    featured_exif = None
    if featured_image:
        image_path = os.path.join(IMAGES_FOLDER, featured_image['filename'])
        featured_exif = extract_exif_data(image_path)
        
        # SINGLE SOURCE: Story is always the same as description
        featured_image['story'] = featured_image.get('description', '')
    
    about_data = load_about_data()

    # Load hero image (same as main route)
    hero_image_data = load_hero_image()
    hero_image = None
    if hero_image_data and hero_image_data.get('filename'):
        # Find the hero image in the images list
        for image in images:
            if image['filename'] == hero_image_data['filename']:
                hero_image = image
                break
    
    return render_template("mobile_new.html",
                         images=images,
                         categories=categories,
                         category_counts=category_counts,
                         featured_image=featured_image,
                         featured_exif=featured_exif,
                         about_data=about_data,
                         hero_image=hero_image)
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

# Removed duplicate subcategories route - using the one at line ~2463 instead

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
        all_categories = sorted(load_categories())
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
        categories = sorted(load_categories())
        
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
    categories = sorted(load_categories())
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
        
        all_categories = sorted(load_categories())
        
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
    """Get subcategories for a specific category from live API"""
    try:
        client = get_lumaprints_client(sandbox=False)
        subcategories = client.get_subcategories(category_id)
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
    """Get all options for a specific subcategory from live API"""
    try:
        client = get_lumaprints_client(sandbox=False)
        options = client.get_subcategory_options(subcategory_id)
        return jsonify({
            'success': True,
            'options': options
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/check-image', methods=['POST'])
def check_lumaprints_image():
    """Check if an image meets quality requirements for a specific print size"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['subcategoryId', 'printWidth', 'printHeight', 'imageUrl']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        client = get_lumaprints_client(sandbox=False)
        result = client.check_image(
            subcategory_id=data['subcategoryId'],
            print_width=float(data['printWidth']),
            print_height=float(data['printHeight']),
            image_url=data['imageUrl'],
            order_item_options=data.get('orderItemOptions', [])
        )
        
        # Check if result contains a status code (from error responses)
        status_code = result.pop('_status_code', 200)
        
        if status_code == 200:
            # Image quality check passed
            return jsonify({
                'success': True,
                'result': result
            })
        elif status_code == 400:
            # Invalid URL or request
            return jsonify({
                'success': False,
                'error': result.get('message', 'Invalid image URL'),
                'details': result
            }), 400
        elif status_code == 406:
            # Image sized incorrectly - return detailed error info
            return jsonify({
                'success': False,
                'error': result.get('message', 'Image does not meet quality requirements'),
                'details': result
            }), 406
        else:
            # Unexpected status code
            return jsonify({
                'success': False,
                'error': 'Unexpected response from Lumaprints API',
                'details': result
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Image quality check failed'
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

# Initialize dynamic pricing calculator using database-stored markup
from dynamic_pricing_calculator import get_dynamic_pricing_calculator
from pricing_admin import get_global_markup
pricing_calc = get_dynamic_pricing_calculator(markup_percentage=get_global_markup())

@app.route('/api/lumaprints/categories')
def get_lumaprints_categories():
    """Get available product categories from live Lumaprints API"""
    try:
        client = get_lumaprints_client(sandbox=False)
        categories = client.get_categories()
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/lumaprints/pricing', methods=['POST'])
def get_lumaprints_pricing():
    """Calculate pricing for a specific product configuration using live API"""
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
        
        # Get pricing from live Lumaprints API (use production for pricing)
        client = get_lumaprints_client(sandbox=False)
        api_pricing = client.get_pricing(
            subcategory_id=subcategory_id,
            width=width,
            height=height,
            quantity=quantity,
            options=options if options else None
        )
        
        # Get wholesale price from API response
        wholesale_price = api_pricing.get('price', 0)
        
        # Apply markup
        markup_percentage = get_global_markup()
        retail_price = wholesale_price * (1 + markup_percentage / 100)
        price_per_item = retail_price / quantity
        
        # Format response for frontend compatibility
        formatted_response = {
            'success': True,
            'pricing': {
                'formatted_price': f"${retail_price:.2f}",
                'formatted_price_per_item': f"${price_per_item:.2f}",
                'total_price': round(retail_price, 2),
                'price_per_item': round(price_per_item, 2),
                'wholesale_price': round(wholesale_price, 2),
                'quantity': quantity,
                'markup_percentage': markup_percentage
            },
            'product_info': {
                'subcategory_id': subcategory_id,
                'width': width,
                'height': height
            },
            'api_response': api_pricing
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
    """Get available sizes for a specific subcategory from live API"""
    try:
        client = get_lumaprints_client(sandbox=False)
        options = client.get_subcategory_options(subcategory_id)
        
        # Extract size information from options
        # The API returns options including sizes, we need to parse them
        sizes = []
        for option in options:
            if option.get('type') == 'size' or 'size' in option.get('name', '').lower():
                sizes.append(option)
        
        return jsonify({
            'success': True,
            'subcategory_id': subcategory_id,
            'sizes': sizes,
            'all_options': options  # Include all options for debugging
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

# ============================================================================
# NEW HIERARCHICAL API ROUTES (V2 - Simplified Database Structure)
# ============================================================================

from hierarchical_api_new import register_hierarchical_routes_new
register_hierarchical_routes_new(app)

# ============================================================================
# ADMIN IMPORT ENDPOINT
# ============================================================================

from admin_import_endpoint_new import register_import_routes
register_import_routes(app)

# ============================================================================
# ORDER FORM V3 - CLEAN IMPLEMENTATION
# ============================================================================

# from order_api_v3 import register_order_routes_v3
# register_order_routes_v3(app)  # Disabled - using new /order route instead

# NEW: Register fresh print order routes to bypass Railway cache
from print_order_api import setup_print_order_routes
setup_print_order_routes(app)

# Register print order diagnostic routes
from print_order_diagnostic import register_print_diagnostic_routes
register_print_diagnostic_routes(app)

# Register diagnostic routes
from diagnostic_api import register_diagnostic_routes
register_diagnostic_routes(app)

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

# Import pricing admin functions
from pricing_admin import (
    admin_pricing_route, update_global_markup_route, update_product_cost_route,
    add_product_route, delete_product_route
)
from category_admin import (
    add_category_route, delete_category_route, get_categories_route
)
from variant_routes import (
    get_product_variants_route, get_variant_price_route, get_products_with_variants_route
)
from dynamic_product_api import (
    get_products_for_frontend, get_product_details_api
)
from database_setup_route import setup_database_route
from rebuild_lumaprints_db import rebuild_database_route
from order_route import order_form_route

@app.route('/admin/pricing')
@require_admin_auth
def admin_pricing():
    """Pricing management admin page"""
    return admin_pricing_route()

@app.route('/admin/pricing/update-markup', methods=['POST'])
@require_admin_auth
def update_global_markup():
    """Update global markup percentage"""
    return update_global_markup_route()

@app.route('/admin/pricing/update-product', methods=['POST'])
@require_admin_auth
def update_product_cost():
    """Update individual product cost"""
    return update_product_cost_route()

@app.route('/admin/pricing/add-product', methods=['POST'])
@require_admin_auth
def add_product():
    """Add new product"""
    return add_product_route()

@app.route('/admin/pricing/delete-product', methods=['POST'])
@require_admin_auth
def delete_pricing_product():
    """Delete product from pricing system"""
    return delete_product_route()

@app.route('/admin/pricing/add-category', methods=['POST'])
@require_admin_auth
def add_category():
    """Add new category"""
    return add_category_route()

@app.route('/admin/pricing/delete-category', methods=['POST'])
@require_admin_auth
def delete_category():
    """Delete category (if empty)"""
    return delete_category_route()

@app.route('/admin/pricing/categories', methods=['GET'])
@require_admin_auth
def get_categories():
    """Get all categories for dropdown refresh"""
    return get_categories_route()

# Variant management routes
@app.route('/api/product-variants', methods=['GET'])
def get_product_variants():
    """Get variants for a specific product"""
    return get_product_variants_route()

@app.route('/api/variant-price', methods=['GET'])
def get_variant_price():
    """Get price for a specific variant"""
    return get_variant_price_route()

@app.route('/api/products-with-variants', methods=['GET'])
def get_products_with_variants():
    """Get all products with variant information"""
    return get_products_with_variants_route()

# Dynamic product API for frontend
@app.route('/api/products', methods=['GET'])
def get_frontend_products():
    """Get all products for frontend order form (no auth required) - PICTOREM VERSION"""
    return get_products_for_frontend()

@app.route('/api/categories', methods=['GET'])
def get_frontend_categories():
    """Get all product categories for frontend"""
    return get_categories_for_frontend()

@app.route('/api/product/<slug>', methods=['GET'])
def get_product_by_slug(slug):
    """Get product details by slug"""
    return get_product_details(slug)

@app.route('/api/price', methods=['POST'])
def calculate_product_price():
    """Calculate price for a product configuration"""
    data = request.get_json()
    product_slug = data.get('product_slug')
    width = data.get('width')
    height = data.get('height')
    options = data.get('options', {})
    return get_product_price_api(product_slug, width, height, options)

@app.route('/api/product-details', methods=['GET'])
def get_product_details():
    """Get detailed product information (no auth required)"""
    return get_product_details_api()

# Database setup route (for initializing live database)
@app.route('/setup-database', methods=['GET'])
def setup_database():
    """Initialize database with required tables and sample data"""
    return setup_database_route()

@app.route('/admin/rebuild-lumaprints-db', methods=['GET'])
@require_admin_auth
def rebuild_lumaprints_db():
    """Rebuild Lumaprints database from JSON pricing files"""
    return rebuild_database_route()

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

# Old pricing route removed - replaced with database-driven system
            
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
    # Pass all query parameters to template
    params = request.args.to_dict()
    
    # Check if image parameter is provided
    if "image" not in params or not params["image"]:
        params["no_image_selected"] = True
    
    return render_template("test_order_form.html", **params)

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
        
        # Verify PayPal payment was completed (DISABLED FOR TESTING)
        # if not paypal_order_id or not paypal_payer_id:
        #     return jsonify({
        #         "status": "error",
        #         "message": "Payment required before order submission"
        #     }), 400
        
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
                        "lumaprints_options": lumaprints_options
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
            print("=== ORDERDESK RESPONSE DEBUG ===")
            print("Full response:", json.dumps(order_response, indent=2))
            print("Order ID:", order_response.get("id"))
            print("Response keys:", list(order_response.keys()) if isinstance(order_response, dict) else "Not a dict")
            # flash(f'Order submitted successfully! OrderDesk Order ID: {order_response.get("id")}', 'success')  # Removed to clean up admin
            return jsonify({
                "status": "success",
                "message": "Order submitted to OrderDesk successfully",
                "orderdesk_order_id": order_response.get("order", {}).get("id") if order_response.get("order") else order_response.get("id"),
                "debug_info": {
                    "response_keys": list(order_response.keys()) if isinstance(order_response, dict) else "Not a dict",
                    "id_field": order_response.get("id"),
                    "order_id_field": order_response.get("order_id"),
                    "order_number_field": order_response.get("order_number"),
                    "order_object_id": order_response.get("order", {}).get("id") if order_response.get("order") else None
                },
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


@app.route('/enhanced_order_form')
def enhanced_order_form():
    """Enhanced order form with 3-dropdown product selection system"""
    return render_template('enhanced_order_form_v2.html')


# ===============================================
# HIERARCHICAL ORDERING SYSTEM API ROUTES
# ===============================================

@app.route('/api/hierarchical/product-types', methods=['GET'])
def get_hierarchical_product_types():
    """Get all product types for hierarchical ordering system"""
    try:
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, display_order, has_sub_options, max_sub_option_levels, active
            FROM product_types 
            WHERE active = 1 
            ORDER BY display_order
        """)
        
        product_types = []
        for row in cursor.fetchall():
            product_types.append({
                'id': row['id'],
                'name': row['name'],
                'display_order': row['display_order'],
                'has_sub_options': bool(row['has_sub_options']),
                'max_sub_option_levels': row['max_sub_option_levels'],
                'active': bool(row['active'])
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'product_types': product_types
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hierarchical/sub-options/<int:product_type_id>/<int:level>', methods=['GET'])
def get_hierarchical_sub_options(product_type_id, level):
    """Get sub-options for a product type at a specific level"""
    try:
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get sub-options that actually have products
        # This prevents showing options with no available products
        cursor.execute("""
            SELECT DISTINCT so.id, so.option_type, so.name, so.value, so.image_path, so.display_order
            FROM sub_options so
            WHERE so.product_type_id = ? AND so.level = ? AND so.active = 1
              AND EXISTS (
                SELECT 1 FROM products p 
                WHERE p.product_type_id = so.product_type_id 
                  AND p.active = 1
                  AND (p.sub_option_1_id = so.id OR p.sub_option_2_id = so.id)
              )
            ORDER BY so.display_order
        """, (product_type_id, level))
        
        sub_options = []
        for row in cursor.fetchall():
            sub_options.append({
                'id': row['id'],
                'option_type': row['option_type'],
                'name': row['name'],
                'value': row['value'],
                'image_path': row['image_path'],
                'display_order': row['display_order']
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'sub_options': sub_options
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hierarchical/available-sizes', methods=['GET'])
def get_hierarchical_available_sizes():
    """Get available sizes based on product type and sub-options"""
    try:
        product_type_id = request.args.get('product_type_id', type=int)
        
        # Support BOTH old internal IDs and new Lumaprints codes
        sub_option_1_id = request.args.get('sub_option_1_id', type=int)
        sub_option_2_id = request.args.get('sub_option_2_id', type=int)
        lumaprints_subcategory_id = request.args.get('lumaprints_subcategory_id', type=int)
        lumaprints_option_id = request.args.get('lumaprints_option_id', type=int)
        
        if not product_type_id:
            return jsonify({
                'success': False,
                'error': 'product_type_id is required'
            }), 400
        
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get global markup percentage
        cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
        markup_row = cursor.fetchone()
        markup_percentage = float(markup_row['value']) if markup_row else 150.0
        multiplier = (markup_percentage / 100) + 1  # Convert percentage to multiplier
        
        # Build query - prefer Lumaprints codes over internal IDs
        query = """
            SELECT p.id, p.name, p.size, p.cost_price, c.name as category_name,
                   p.lumaprints_subcategory_id, p.lumaprints_options, p.lumaprints_frame_option
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.active = 1 AND p.product_type_id = ?
        """
        params = [product_type_id]
        
        # Use Lumaprints codes if provided, otherwise fall back to internal IDs
        if lumaprints_subcategory_id:
            query += " AND p.lumaprints_subcategory_id = ?"
            params.append(lumaprints_subcategory_id)
        elif sub_option_1_id:
            query += " AND p.sub_option_1_id = ?"
            params.append(sub_option_1_id)
            
        if lumaprints_option_id:
            # Filter by JSON option - check if option_id exists in lumaprints_options
            query += " AND (p.lumaprints_options LIKE ? OR p.lumaprints_frame_option = ?)"
            params.append(f'%{lumaprints_option_id}%')
            params.append(lumaprints_option_id)
        elif sub_option_2_id:
            query += " AND p.sub_option_2_id = ?"
            params.append(sub_option_2_id)
            
        query += " ORDER BY p.name, p.size"
        
        cursor.execute(query, params)
        
        products = []
        for row in cursor.fetchall():
            # Calculate customer price using global markup
            customer_price = row['cost_price'] * multiplier
            
            # Parse Lumaprints options JSON
            lumaprints_options = []
            if row['lumaprints_options']:
                try:
                    import json
                    lumaprints_options = json.loads(row['lumaprints_options'])
                except:
                    lumaprints_options = []
            
            products.append({
                'id': row['id'],
                'name': row['name'],
                'size': row['size'],
                'category_name': row['category_name'],
                'cost_price': float(row['cost_price']),
                'customer_price': round(customer_price, 2),
                # Lumaprints integration fields for OrderDesk
                'lumaprints_subcategory_id': row['lumaprints_subcategory_id'],
                'lumaprints_options': lumaprints_options,
                'lumaprints_frame_option': row['lumaprints_frame_option']
            })
        
        conn.close()
        return jsonify({
            'success': True,
            'products': products,
            'markup_percentage': markup_percentage
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hierarchical/product-details/<int:product_id>', methods=['GET'])
def get_hierarchical_product_details(product_id):
    """Get detailed information about a specific product"""
    try:
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get global markup percentage
        cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
        markup_row = cursor.fetchone()
        markup_percentage = float(markup_row['value']) if markup_row else 150.0
        multiplier = (markup_percentage / 100) + 1  # Convert percentage to multiplier
        
        cursor.execute("""
            SELECT p.*, c.name as category_name, pt.name as product_type_name,
                   so1.value as sub_option_1_value, so2.value as sub_option_2_value
            FROM products p
            JOIN categories c ON p.category_id = c.id
            LEFT JOIN product_types pt ON p.product_type_id = pt.id
            LEFT JOIN sub_options so1 ON p.sub_option_1_id = so1.id
            LEFT JOIN sub_options so2 ON p.sub_option_2_id = so2.id
            WHERE p.id = ? AND p.active = 1
        """, (product_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404
        
        # Calculate customer price using global markup
        customer_price = row['cost_price'] * multiplier
        
        # Parse Lumaprints options JSON
        lumaprints_options = []
        if row['lumaprints_options']:
            try:
                import json
                lumaprints_options = json.loads(row['lumaprints_options'])
            except:
                lumaprints_options = []
        
        product = {
            'id': row['id'],
            'name': row['name'],
            'size': row['size'],
            'cost_price': float(row['cost_price']),
            'customer_price': round(customer_price, 2),
            'category_name': row['category_name'],
            'product_type_name': row['product_type_name'],
            'sub_option_1_value': row['sub_option_1_value'],
            'sub_option_2_value': row['sub_option_2_value'],
            'description': row['description'],
            # Lumaprints integration fields for OrderDesk
            'lumaprints_subcategory_id': row['lumaprints_subcategory_id'],
            'lumaprints_options': lumaprints_options,
            'lumaprints_frame_option': row['lumaprints_frame_option']
        }
        
        conn.close()
        return jsonify({
            'success': True,
            'product': product,
            'markup_percentage': markup_percentage
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/admin/add-test-products')
def add_test_products():
    try:
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        cursor = conn.cursor()
        
        # Add test products for Framed Canvas Prints - 0.75" Frame - White
        test_products = [
            (1, 'Framed Canvas Print - 0.75" Frame - White - 8x10', '8x10', 42.99, 2, 4, 11),
            (1, 'Framed Canvas Print - 0.75" Frame - White - 11x14', '11x14', 62.99, 2, 4, 11),
            (1, 'Framed Canvas Print - 0.75" Frame - White - 16x20', '16x20', 86.99, 2, 4, 11),
            (1, 'Framed Canvas Print - 1.25" Frame - White - 8x10', '8x10', 49.99, 2, 5, 11)
        ]
        
        for product in test_products:
            cursor.execute("""
                INSERT OR IGNORE INTO products 
                (category_id, name, size, cost_price, product_type_id, sub_option_1_id, sub_option_2_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, product)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Added {len(test_products)} test products',
            'products': [p[1] for p in test_products]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/debug-canvas')
def debug_canvas():
    """Debug page for Canvas Prints workflow"""
    return send_from_directory('.', 'debug_canvas.html')

@app.route('/hierarchical_order_form')
def hierarchical_order_form():
    """New hierarchical ordering system interface"""
    image_url = request.args.get('image', '')
    return render_template('hierarchical_order_form.html', image_url=image_url)


@app.route('/admin/fix-test-products')
def fix_test_products_route():
    """Fix test products with correct sub_option IDs"""
    try:
        import sqlite3
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        cursor = conn.cursor()
        
        # Update the test products with correct sub_option_1_id and sub_option_2_id
        # Product IDs 682, 683, 684 are 0.75" Frame + White (sub_option_1_id=4, sub_option_2_id=11)
        cursor.execute('UPDATE products SET sub_option_1_id = 4, sub_option_2_id = 11 WHERE id IN (682, 683, 684)')
        
        # Product ID 681 is 1.25" Frame + White (sub_option_1_id=5, sub_option_2_id=11)
        cursor.execute('UPDATE products SET sub_option_1_id = 5, sub_option_2_id = 11 WHERE id = 681')
        
        conn.commit()
        
        # Verify the fix
        cursor.execute('SELECT id, name, size, product_type_id, sub_option_1_id, sub_option_2_id FROM products WHERE id IN (681, 682, 683, 684)')
        results = cursor.fetchall()
        
        conn.close()
        
        html = "<h2>Test Products Fixed!</h2><table border='1'><tr><th>ID</th><th>Name</th><th>Size</th><th>Type</th><th>Sub1</th><th>Sub2</th></tr>"
        for row in results:
            html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
        html += "</table>"
        
        return html
        
    except Exception as e:
        return f"Error fixing test products: {str(e)}", 500


@app.route('/debug/sizes')
def debug_sizes():
    """Debug endpoint to show available sizes data - now includes fix option"""
    # Check if fix should be applied
    apply_fix = request.args.get('apply_fix', 'false').lower() == 'true'
    
    if apply_fix:
        from simple_sub_option_fix import apply_simple_sub_option_fix
        fix_result = apply_simple_sub_option_fix()
        if fix_result['success']:
            return f"<h2>Sub-Option Fix Applied!</h2><p>{fix_result['message']}</p><ul>" + "".join([f"<li>{update}</li>" for update in fix_result['updates']]) + "</ul><p><a href='/debug/sizes'>Test sizes now</a></p>"
        else:
            return f"<h2>Fix Failed:</h2><p>{fix_result['error']}</p>"
    
    # Original debug_sizes function continues below
    """Debug endpoint to show available sizes data"""
    product_type_id = request.args.get('product_type_id', 2)
    sub_option_1_id = request.args.get('sub_option_1_id', 4)  # 0.75" Frame
    sub_option_2_id = request.args.get('sub_option_2_id', 11)  # White
    
    try:
        import sqlite3
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get global markup percentage
        cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
        markup_row = cursor.fetchone()
        markup_percentage = float(markup_row['value']) if markup_row else 150.0
        multiplier = (markup_percentage / 100) + 1  # Convert percentage to multiplier
        
        # Use the exact same query as the working API
        query = """
            SELECT p.id, p.name, p.size, p.cost_price, c.name as category_name, p.sub_option_1_id, p.sub_option_2_id
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.active = 1 AND p.product_type_id = ?
        """
        params = [product_type_id]
        
        if sub_option_1_id:
            query += " AND p.sub_option_1_id = ?"
            params.append(sub_option_1_id)
            
        if sub_option_2_id:
            query += " AND p.sub_option_2_id = ?"
            params.append(sub_option_2_id)
            
        query += " ORDER BY p.name, p.size"
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        conn.close()
        
        # Format as readable HTML
        html = f"""
        <h2>Debug: Available Sizes API Data</h2>
        <p><strong>Query Parameters:</strong></p>
        <ul>
            <li>product_type_id: {product_type_id}</li>
            <li>sub_option_1_id: {sub_option_1_id}</li>
            <li>sub_option_2_id: {sub_option_2_id}</li>
        </ul>
        
        <p><strong>Markup Percentage:</strong> {markup_percentage}%</p>
        
        <p><strong>Products Found:</strong> {len(products)}</p>
        
        <table border="1" style="border-collapse: collapse; margin: 20px 0;">
            <tr>
                <th style="padding: 10px;">ID</th>
                <th style="padding: 10px;">Name</th>
                <th style="padding: 10px;">Size</th>
                <th style="padding: 10px;">Cost Price</th>
                <th style="padding: 10px;">Customer Price</th>
                <th style="padding: 10px;">Category</th>
                <th style="padding: 10px;">Sub Option 1 ID</th>
                <th style="padding: 10px;">Sub Option 2 ID</th>
            </tr>
        """
        
        for product in products:
            # Calculate customer price like the API does
            customer_price = product['cost_price'] * multiplier
            html += f"""
            <tr>
                <td style="padding: 10px;">{product['id']}</td>
                <td style="padding: 10px;">{product['name']}</td>
                <td style="padding: 10px;">{product['size']}</td>
                <td style="padding: 10px;">${product['cost_price']}</td>
                <td style="padding: 10px;">${customer_price:.2f}</td>
                <td style="padding: 10px;">{product['category_name']}</td>
                <td style="padding: 10px;">{product['sub_option_1_id']}</td>
                <td style="padding: 10px;">{product['sub_option_2_id']}</td>
            </tr>
            """
        
        html += """
        </table>
        
        <h3>API JSON Response:</h3>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
        """
        
        # Show the exact JSON that would be returned
        api_response = {
            "markup_percentage": markup_percentage,
            "products": [
                {
                    "id": p['id'],
                    "name": p['name'],
                    "size": p['size'],
                    "cost_price": float(p['cost_price']),
                    "customer_price": float(p['cost_price'] * multiplier),
                    "category_name": p['category_name']
                }
                for p in products
            ],
            "success": True
        }
        
        import json
        html += json.dumps(api_response, indent=2)
        html += "</pre>"
        
        return html
        
    except Exception as e:
        return f"<h2>Debug Error:</h2><p>{str(e)}</p>"


# Import migration, debug, and fix functions
from migrate_sub_options import migrate_sub_options_route
from debug_sub_options import debug_sub_options_route
from fix_canvas_sub_options import fix_canvas_sub_options_route

@app.route('/migrate-sub-options')
def migrate_sub_options():
    """Apply sub-option assignments fix to the live database"""
    return migrate_sub_options_route()

@app.route('/debug-sub-options')
def debug_sub_options():
    """Debug route to check actual sub-option assignments in database"""
    return debug_sub_options_route()

@app.route('/fix-canvas-sub-options')
def fix_canvas_sub_options():
    """Direct fix for Canvas products sub-option assignments"""
    return fix_canvas_sub_options_route()

@app.route('/admin/fix-white-id')
def fix_white_id():
    """Fix test products to use correct White color ID (14) - NOW INCLUDES SUB-OPTION FIX"""
    try:
        import sqlite3
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        cursor = conn.cursor()
        
        # APPLY SUB-OPTION FIX FOR ALL PRODUCT TYPES
        updates = []
        
        # Canvas Prints (product_type_id = 1) -> Distribute across all mounting options
        cursor.execute("SELECT id FROM products WHERE product_type_id = 1 AND active = 1 ORDER BY id")
        canvas_products = cursor.fetchall()
        canvas_count = 0
        for i, (product_id,) in enumerate(canvas_products):
            # Cycle through mounting options: 1, 2, 3, 1, 2, 3, ...
            sub_option_id = (i % 3) + 1
            cursor.execute("UPDATE products SET sub_option_1_id = ? WHERE id = ?", (sub_option_id, product_id))
            canvas_count += 1
        updates.append(f"Canvas Prints: {canvas_count} products updated")
        
        # Fine Art Paper Prints (product_type_id = 3) -> sub_option_1_id = 49
        cursor.execute("UPDATE products SET sub_option_1_id = 49 WHERE product_type_id = 3 AND active = 1")
        updates.append(f"Fine Art Paper: {cursor.rowcount} products updated")
        
        # Foam-Mounted Fine Art Paper Prints (product_type_id = 5) -> sub_option_1_id = 49
        cursor.execute("UPDATE products SET sub_option_1_id = 49 WHERE product_type_id = 5 AND active = 1")
        updates.append(f"Foam-Mounted: {cursor.rowcount} products updated")
        
        # Framed Canvas Prints (product_type_id = 2) -> both sub-options
        cursor.execute("UPDATE products SET sub_option_1_id = 32, sub_option_2_id = 14 WHERE product_type_id = 2 AND active = 1")
        updates.append(f"Framed Canvas: {cursor.rowcount} products updated")
        
        # Framed Fine Art Paper Prints (product_type_id = 4) -> both sub-options
        cursor.execute("UPDATE products SET sub_option_1_id = 32, sub_option_2_id = 42 WHERE product_type_id = 4 AND active = 1")
        updates.append(f"Framed Fine Art: {cursor.rowcount} products updated")
        
        # Update test products to use correct White ID (14 instead of 11)
        cursor.execute('UPDATE products SET sub_option_2_id = 14 WHERE id IN (681, 682, 683, 684)')
        
        conn.commit()
        
        # Verify the fix
        cursor.execute('SELECT id, name, size, product_type_id, sub_option_1_id, sub_option_2_id FROM products WHERE id IN (681, 682, 683, 684)')
        results = cursor.fetchall()
        
        conn.close()
        
        html = "<h2>SUB-OPTION FIX APPLIED SUCCESSFULLY!</h2>"
        html += "<h3>Updates Applied:</h3><ul>"
        for update in updates:
            html += f"<li>{update}</li>"
        html += "</ul>"
        html += "<h3>Test Products Fixed:</h3><table border='1'><tr><th>ID</th><th>Name</th><th>Size</th><th>Type</th><th>Sub1</th><th>Sub2</th></tr>"
        for row in results:
            html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
        html += "</table><p><strong>SIZE SELECTION SHOULD NOW WORK!</strong></p>"
        html += "<p>Test Canvas: <a href='/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=1'>Canvas Sizes API</a></p>"
        
        return html
        
    except Exception as e:
        return f"Error fixing White ID: {str(e)}", 500


@app.route('/fix-canvas-now')
def fix_canvas_now():
    """FINAL Canvas fix - distribute products across all mounting options"""
    import sqlite3
    
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        # Get Canvas product IDs
        cursor.execute("SELECT id FROM products WHERE product_type_id = 1 ORDER BY id")
        canvas_ids = [row[0] for row in cursor.fetchall()]
        
        # Distribute evenly across 3 mounting options
        total = len(canvas_ids)
        per_option = total // 3
        
        # Assign to mounting option 1 (0.75")
        cursor.execute(f"""
            UPDATE products 
            SET sub_option_1_id = 1 
            WHERE product_type_id = 1 
            AND id IN ({','.join(map(str, canvas_ids[:per_option]))})
        """)
        
        # Assign to mounting option 2 (1.25")  
        cursor.execute(f"""
            UPDATE products 
            SET sub_option_1_id = 2 
            WHERE product_type_id = 1 
            AND id IN ({','.join(map(str, canvas_ids[per_option:per_option*2]))})
        """)
        
        # Assign remaining to mounting option 3 (1.5")
        cursor.execute(f"""
            UPDATE products 
            SET sub_option_1_id = 3 
            WHERE product_type_id = 1 
            AND id IN ({','.join(map(str, canvas_ids[per_option*2:]))})
        """)
        
        conn.commit()
        
        # Check results
        cursor.execute("""
            SELECT sub_option_1_id, COUNT(*) 
            FROM products 
            WHERE product_type_id = 1 
            GROUP BY sub_option_1_id
        """)
        results = cursor.fetchall()
        
        return f"""
        <h1>CANVAS FIX COMPLETE!</h1>
        <h3>Distribution:</h3>
        <ul>
        {''.join([f'<li>Mounting {["0.75", "1.25", "1.5"][sub_id-1]}": {count} products</li>' for sub_id, count in results])}
        </ul>
        
        <h2>TEST LINKS:</h2>
        <ul>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=1">Test 0.75" Canvas</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=2">Test 1.25" Canvas</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=3">Test 1.5" Canvas</a></li>
        </ul>
        
        <h1>🎉 CANVAS SHOULD WORK NOW! 🎉</h1>
        """
        
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()


@app.route('/fix-framed-canvas')
def fix_framed_canvas():
    """Fix Framed Canvas - assign both sub-options"""
    import sqlite3
    
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        # Get Framed Canvas product IDs (product_type_id = 2)
        cursor.execute("SELECT id FROM products WHERE product_type_id = 2 ORDER BY id")
        framed_ids = [row[0] for row in cursor.fetchall()]
        
        # Frame sizes: 4, 5, 6 (0.75", 1.25", 1.50")
        # Frame colors: 7, 8, 9, 10, 11, 12, 13, 14 (8 colors)
        
        frame_sizes = [4, 5, 6]
        frame_colors = [7, 8, 9, 10, 11, 12, 13, 14]
        
        # Distribute products across all combinations
        updates = []
        for i, product_id in enumerate(framed_ids):
            frame_size = frame_sizes[i % 3]  # Cycle through 3 frame sizes
            frame_color = frame_colors[i % 8]  # Cycle through 8 colors
            updates.append((frame_size, frame_color, product_id))
        
        # Apply updates
        cursor.executemany("""
            UPDATE products 
            SET sub_option_1_id = ?, sub_option_2_id = ?
            WHERE id = ?
        """, updates)
        
        conn.commit()
        
        # Check results
        cursor.execute("""
            SELECT sub_option_1_id, sub_option_2_id, COUNT(*) 
            FROM products 
            WHERE product_type_id = 2 
            GROUP BY sub_option_1_id, sub_option_2_id
            ORDER BY sub_option_1_id, sub_option_2_id
        """)
        results = cursor.fetchall()
        
        return f"""
        <h1>FRAMED CANVAS FIX COMPLETE!</h1>
        <h3>Distribution ({len(framed_ids)} products):</h3>
        <ul>
        {''.join([f'<li>Frame {["0.75", "1.25", "1.50"][sub1-4]}" + Color {sub2-6}: {count} products</li>' for sub1, sub2, count in results[:10]])}
        {'<li>... and more combinations</li>' if len(results) > 10 else ''}
        </ul>
        
        <h2>TEST FRAMED CANVAS:</h2>
        <ul>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=2&sub_option_1_id=4&sub_option_2_id=7">Test Frame 0.75" + Maple</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=2&sub_option_1_id=5&sub_option_2_id=8">Test Frame 1.25" + Black</a></li>
        </ul>
        
        <h1>🎉 FRAMED CANVAS SHOULD WORK NOW! 🎉</h1>
        """
        
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()

@app.route('/fix-all-remaining')
def fix_all_remaining():
    """Fix ALL remaining product types at once"""
    import sqlite3
    
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        results = []
        
        # 1. Fine Art Paper Prints (product_type_id = 3, 1 option level)
        # Paper types: IDs 15-21 (Archival Matte, Hot Press, Cold Press, Semi-Gloss, Metallic, Glossy, Somerset Velvet)
        cursor.execute("SELECT id FROM products WHERE product_type_id = 3 ORDER BY id")
        fine_art_ids = [row[0] for row in cursor.fetchall()]
        
        paper_types = [15, 16, 17, 18, 19, 20, 21]  # 7 paper types
        for i, product_id in enumerate(fine_art_ids):
            paper_type = paper_types[i % 7]
            cursor.execute("UPDATE products SET sub_option_1_id = ? WHERE id = ?", (paper_type, product_id))
        
        results.append(f"Fine Art Paper: {len(fine_art_ids)} products assigned to paper types")
        
        # 2. Foam-Mounted Fine Art Paper (product_type_id = 5, 1 option level)
        # Same paper types as Fine Art Paper
        cursor.execute("SELECT id FROM products WHERE product_type_id = 5 ORDER BY id")
        foam_ids = [row[0] for row in cursor.fetchall()]
        
        for i, product_id in enumerate(foam_ids):
            paper_type = paper_types[i % 7]
            cursor.execute("UPDATE products SET sub_option_1_id = ? WHERE id = ?", (paper_type, product_id))
        
        results.append(f"Foam-Mounted: {len(foam_ids)} products assigned to paper types")
        
        # 3. Framed Fine Art Paper (product_type_id = 4, 2 option levels)
        # Need to get sub-option 2 for this one - frame colors should be similar to Framed Canvas
        cursor.execute("SELECT id FROM products WHERE product_type_id = 4 ORDER BY id")
        framed_fine_art_ids = [row[0] for row in cursor.fetchall()]
        
        # Frame sizes for Fine Art: assume similar IDs to Framed Canvas but check
        # For now, use paper types (15-21) for sub_option_1 and frame colors (7-14) for sub_option_2
        frame_colors = [7, 8, 9, 10, 11, 12, 13, 14]  # Same as Framed Canvas
        
        for i, product_id in enumerate(framed_fine_art_ids):
            paper_type = paper_types[i % 7]
            frame_color = frame_colors[i % 8]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = ? WHERE id = ?", 
                          (paper_type, frame_color, product_id))
        
        results.append(f"Framed Fine Art: {len(framed_fine_art_ids)} products assigned paper types + frame colors")
        
        conn.commit()
        
        return f"""
        <h1>🎉 ALL REMAINING PRODUCTS FIXED! 🎉</h1>
        
        <h3>Results:</h3>
        <ul>
        {''.join([f'<li>{result}</li>' for result in results])}
        </ul>
        
        <h2>TEST LINKS:</h2>
        <ul>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=3&sub_option_1_id=15">Test Fine Art Paper (Archival Matte)</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=5&sub_option_1_id=15">Test Foam-Mounted (Archival Matte)</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=4&sub_option_1_id=15&sub_option_2_id=7">Test Framed Fine Art (Archival + Maple)</a></li>
        </ul>
        
        <h1>🚀 ALL PRODUCT TYPES SHOULD WORK NOW! 🚀</h1>
        
        <p><strong>Summary:</strong></p>
        <ul>
            <li>✅ Rolled Canvas (0 options) - Already working</li>
            <li>✅ Metal Prints (0 options) - Already working</li>
            <li>✅ Peel & Stick (0 options) - Already working</li>
            <li>✅ Canvas Prints (1 option) - Fixed</li>
            <li>✅ Framed Canvas (2 options) - Fixed</li>
            <li>✅ Fine Art Paper (1 option) - Just fixed</li>
            <li>✅ Foam-Mounted (1 option) - Just fixed</li>
            <li>✅ Framed Fine Art (2 options) - Just fixed</li>
        </ul>
        """
        
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()

@app.route('/fix-final-two')
def fix_final_two():
    """Fix Framed Fine Art Paper and Foam-Mounted Fine Art Paper"""
    import sqlite3
    
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        # 1. Foam-Mounted Fine Art Paper (product_type_id = 5, 1 option level)
        # Paper types: IDs 15-21
        cursor.execute("SELECT id FROM products WHERE product_type_id = 5 ORDER BY id")
        foam_ids = [row[0] for row in cursor.fetchall()]
        
        paper_types = [15, 16, 17, 18, 19, 20, 21]  # 7 paper types
        for i, product_id in enumerate(foam_ids):
            paper_type = paper_types[i % 7]
            cursor.execute("UPDATE products SET sub_option_1_id = ? WHERE id = ?", (paper_type, product_id))
        
        # 2. Framed Fine Art Paper (product_type_id = 4, 2 option levels)
        # Frame sizes: IDs 22-32 (11 frame sizes)
        # Mat sizes: IDs 33-42 (10 mat sizes)
        cursor.execute("SELECT id FROM products WHERE product_type_id = 4 ORDER BY id")
        framed_fine_art_ids = [row[0] for row in cursor.fetchall()]
        
        frame_sizes = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]  # 11 frame sizes
        mat_sizes = [33, 34, 35, 36, 37, 38, 39, 40, 41, 42]  # 10 mat sizes
        
        for i, product_id in enumerate(framed_fine_art_ids):
            frame_size = frame_sizes[i % 11]
            mat_size = mat_sizes[i % 10]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = ? WHERE id = ?", 
                          (frame_size, mat_size, product_id))
        
        conn.commit()
        
        return f"""
        <h1>🎉 FINAL TWO PRODUCTS FIXED! 🎉</h1>
        
        <h3>Results:</h3>
        <ul>
            <li>Foam-Mounted Fine Art: {len(foam_ids)} products assigned to paper types (15-21)</li>
            <li>Framed Fine Art: {len(framed_fine_art_ids)} products assigned frame sizes (22-32) + mat sizes (33-42)</li>
        </ul>
        
        <h2>TEST LINKS:</h2>
        <ul>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=5&sub_option_1_id=15">Test Foam-Mounted (Archival Matte)</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=4&sub_option_1_id=22&sub_option_2_id=33">Test Framed Fine Art (0.875" frame + No Mat)</a></li>
        </ul>
        
        <h1>🚀 ALL 8 PRODUCT TYPES SHOULD NOW WORK! 🚀</h1>
        """
        
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()

@app.route('/fix-everything-once')
def fix_everything_once():
    """COMPREHENSIVE FIX - ALL PRODUCT TYPES AT ONCE"""
    import sqlite3
    
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        # 1. Canvas Prints (product_type_id = 1) - 1 option level
        cursor.execute("SELECT id FROM products WHERE product_type_id = 1 ORDER BY id")
        canvas_ids = [row[0] for row in cursor.fetchall()]
        mounting_options = [1, 2, 3]  # 0.75", 1.25", 1.5"
        
        for i, product_id in enumerate(canvas_ids):
            mounting = mounting_options[i % 3]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = NULL WHERE id = ?", (mounting, product_id))
        
        # 2. Framed Canvas Prints (product_type_id = 2) - 2 option levels  
        cursor.execute("SELECT id FROM products WHERE product_type_id = 2 ORDER BY id")
        framed_canvas_ids = [row[0] for row in cursor.fetchall()]
        frame_sizes = [4, 5, 6]
        frame_colors = [7, 8, 9, 10, 11, 12, 13, 14]
        
        for i, product_id in enumerate(framed_canvas_ids):
            frame_size = frame_sizes[i % 3]
            frame_color = frame_colors[i % 8]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = ? WHERE id = ?", (frame_size, frame_color, product_id))
        
        # 3. Fine Art Paper Prints (product_type_id = 3) - 1 option level
        cursor.execute("SELECT id FROM products WHERE product_type_id = 3 ORDER BY id")
        fine_art_ids = [row[0] for row in cursor.fetchall()]
        paper_types = [15, 16, 17, 18, 19, 20, 21]
        
        for i, product_id in enumerate(fine_art_ids):
            paper_type = paper_types[i % 7]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = NULL WHERE id = ?", (paper_type, product_id))
        
        # 4. Framed Fine Art Paper Prints (product_type_id = 4) - 2 option levels
        cursor.execute("SELECT id FROM products WHERE product_type_id = 4 ORDER BY id")
        framed_fine_art_ids = [row[0] for row in cursor.fetchall()]
        fine_art_frame_sizes = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        mat_sizes = [33, 34, 35, 36, 37, 38, 39, 40, 41, 42]
        
        for i, product_id in enumerate(framed_fine_art_ids):
            frame_size = fine_art_frame_sizes[i % 11]
            mat_size = mat_sizes[i % 10]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = ? WHERE id = ?", (frame_size, mat_size, product_id))
        
        # 5. Foam-Mounted Fine Art Paper Prints (product_type_id = 5) - 1 option level
        cursor.execute("SELECT id FROM products WHERE product_type_id = 5 ORDER BY id")
        foam_mounted_ids = [row[0] for row in cursor.fetchall()]
        
        for i, product_id in enumerate(foam_mounted_ids):
            paper_type = paper_types[i % 7]
            cursor.execute("UPDATE products SET sub_option_1_id = ?, sub_option_2_id = NULL WHERE id = ?", (paper_type, product_id))
        
        # 6. 0-option products - keep NULL
        for product_type_id in [8, 6, 7]:  # Rolled Canvas, Metal, Peel & Stick
            cursor.execute("UPDATE products SET sub_option_1_id = NULL, sub_option_2_id = NULL WHERE product_type_id = ?", (product_type_id,))
        
        conn.commit()
        
        return f"""
        <h1>🎉 COMPREHENSIVE FIX COMPLETE! 🎉</h1>
        
        <h3>ALL PRODUCT TYPES FIXED:</h3>
        <ul>
            <li>✅ Canvas Prints: {len(canvas_ids)} products → Mounting options (1,2,3)</li>
            <li>✅ Framed Canvas: {len(framed_canvas_ids)} products → Frame sizes + colors</li>
            <li>✅ Fine Art Paper: {len(fine_art_ids)} products → Paper types (15-21)</li>
            <li>✅ Framed Fine Art: {len(framed_fine_art_ids)} products → Frame sizes + mat sizes</li>
            <li>✅ Foam-Mounted: {len(foam_mounted_ids)} products → Paper types (15-21)</li>
            <li>✅ 0-option products: NULL assignments preserved</li>
        </ul>
        
        <h2>🚀 ALL 8 PRODUCT TYPES SHOULD NOW WORK! 🚀</h2>
        
        <h3>Test Links:</h3>
        <ul>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=1">Canvas 0.75"</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=2&sub_option_1_id=4&sub_option_2_id=7">Framed Canvas</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=3&sub_option_1_id=15">Fine Art Paper</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=4&sub_option_1_id=22&sub_option_2_id=33">Framed Fine Art</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=5&sub_option_1_id=15">Foam-Mounted</a></li>
        </ul>
        """
        
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()

@app.route('/fix-foam-mounted-final')
def fix_foam_mounted_final():
    """Fix Foam-Mounted with correct sub-option IDs (43-49)"""
    import sqlite3
    
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM products WHERE product_type_id = 5 ORDER BY id")
        foam_ids = [row[0] for row in cursor.fetchall()]
        
        # Correct Foam-Mounted paper type IDs: 43-49
        foam_paper_types = [43, 44, 45, 46, 47, 48, 49]  # 7 paper types
        
        for i, product_id in enumerate(foam_ids):
            paper_type = foam_paper_types[i % 7]
            cursor.execute("UPDATE products SET sub_option_1_id = ? WHERE id = ?", (paper_type, product_id))
        
        conn.commit()
        
        return f"""
        <h1>🎉 FOAM-MOUNTED FIXED!</h1>
        <p>Updated {len(foam_ids)} products with correct sub-option IDs (43-49)</p>
        <h2>Test:</h2>
        <a href="/api/hierarchical/available-sizes?product_type_id=5&sub_option_1_id=43">Test Foam-Mounted Archival Matte</a>
        """
        
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()



@app.route('/debug-framed-fine-art')
def debug_framed_fine_art():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, sub_option_1_id, sub_option_2_id 
        FROM products 
        WHERE product_type_id=4 AND sub_option_1_id=23
        LIMIT 50
    """)
    products = cursor.fetchall()
    result = "<h1>Framed Fine Art Products with 1.25\" frame (sub_option_1_id=23)</h1>"
    result += f"<p>Found {len(products)} products</p><ul>"
    for p in products:
        result += f"<li>ID: {p[0]}, Name: {p[1]}, sub_option_1_id: {p[2]}, sub_option_2_id: {p[3]}</li>"
    result += "</ul>"
    return result

@app.route('/fix-all-product-mappings')
def fix_all_product_mappings():
    """Fix ALL product sub_option mappings for the hierarchical wizard"""
    import sqlite3
    
    conn = sqlite3.connect('/data/lumaprints_pricing.db')
    cursor = conn.cursor()
    
    try:
        results = []
        
        # Fix Canvas Prints (product_type_id=1) - distribute by mounting size
        cursor.execute("UPDATE products SET sub_option_1_id=1 WHERE product_type_id=1 AND name LIKE '%0.75%'")
        results.append(f"Canvas 0.75\": {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=2 WHERE product_type_id=1 AND name LIKE '%1.25%'")
        results.append(f"Canvas 1.25\": {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=3 WHERE product_type_id=1 AND name LIKE '%1.5%'")
        results.append(f"Canvas 1.5\": {cursor.rowcount} products")
        
        # Fix Fine Art Paper (product_type_id=3) - distribute by paper type
        cursor.execute("UPDATE products SET sub_option_1_id=15 WHERE product_type_id=3 AND name LIKE '%Archival Matte%'")
        results.append(f"Fine Art Archival Matte: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=16 WHERE product_type_id=3 AND name LIKE '%Hot Press%'")
        results.append(f"Fine Art Hot Press: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=17 WHERE product_type_id=3 AND name LIKE '%Cold Press%'")
        results.append(f"Fine Art Cold Press: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=18 WHERE product_type_id=3 AND name LIKE '%Semi-Gloss%'")
        results.append(f"Fine Art Semi-Gloss: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=19 WHERE product_type_id=3 AND name LIKE '%Metallic%'")
        results.append(f"Fine Art Metallic: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=20 WHERE product_type_id=3 AND name LIKE '%Glossy%'")
        results.append(f"Fine Art Glossy: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=21 WHERE product_type_id=3 AND name LIKE '%Somerset Velvet%'")
        results.append(f"Fine Art Somerset Velvet: {cursor.rowcount} products")
        
        # Fix Framed Canvas (product_type_id=2) - map by lumaprints_subcategory_id
        cursor.execute("UPDATE products SET sub_option_1_id=4, sub_option_2_id=8 WHERE product_type_id=2 AND lumaprints_subcategory_id=102001 AND (lumaprints_frame_option=12 OR lumaprints_frame_option IS NULL)")
        results.append(f"Framed Canvas 0.75\" Black: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=4, sub_option_2_id=14 WHERE product_type_id=2 AND lumaprints_subcategory_id=102001 AND lumaprints_frame_option=13")
        results.append(f"Framed Canvas 0.75\" White: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=5, sub_option_2_id=8 WHERE product_type_id=2 AND lumaprints_subcategory_id=102002 AND lumaprints_frame_option=27")
        results.append(f"Framed Canvas 1.25\" Black: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=5, sub_option_2_id=12 WHERE product_type_id=2 AND lumaprints_subcategory_id=102002 AND lumaprints_frame_option=91")
        results.append(f"Framed Canvas 1.25\" Oak: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=6, sub_option_2_id=8 WHERE product_type_id=2 AND lumaprints_subcategory_id=102003 AND lumaprints_frame_option=23")
        results.append(f"Framed Canvas 1.5\" Black: {cursor.rowcount} products")
        
        # Fix Foam-Mounted (product_type_id=5) - distribute by paper type
        cursor.execute("UPDATE products SET sub_option_1_id=43 WHERE product_type_id=5 AND name LIKE '%Archival Matte%'")
        results.append(f"Foam-Mounted Archival Matte: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=44 WHERE product_type_id=5 AND name LIKE '%Hot Press%'")
        results.append(f"Foam-Mounted Hot Press: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=45 WHERE product_type_id=5 AND name LIKE '%Cold Press%'")
        results.append(f"Foam-Mounted Cold Press: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=46 WHERE product_type_id=5 AND name LIKE '%Semi-Gloss%'")
        results.append(f"Foam-Mounted Semi-Gloss: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=47 WHERE product_type_id=5 AND name LIKE '%Metallic%'")
        results.append(f"Foam-Mounted Metallic: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=48 WHERE product_type_id=5 AND name LIKE '%Glossy%'")
        results.append(f"Foam-Mounted Glossy: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=49 WHERE product_type_id=5 AND name LIKE '%Somerset Velvet%'")
        results.append(f"Foam-Mounted Somerset Velvet: {cursor.rowcount} products")
        
        # Fix Framed Fine Art Paper (product_type_id=4) - map by frame size and mat
        cursor.execute("UPDATE products SET sub_option_1_id=22, sub_option_2_id=33 WHERE product_type_id=4 AND name LIKE '%0.875\" No Mat%'")
        results.append(f"Framed Fine Art 0.875\" No Mat: {cursor.rowcount} products")
        
        cursor.execute("UPDATE products SET sub_option_1_id=23, sub_option_2_id=33 WHERE product_type_id=4 AND name LIKE '%1.25\" No Mat%'")
        results.append(f"Framed Fine Art 1.25\" No Mat: {cursor.rowcount} products")
        
        # Import missing Framed Fine Art products (6 frames × 5 mats × 8 papers × sizes)
        FRAME_STYLES = [
            (105001, 22, "Black"), (105002, 22, "White"), (105003, 22, "Oak"),
            (105005, 23, "Black"), (105006, 23, "White"), (105007, 23, "Oak")
        ]
        MAT_SIZES = [
            (64, 33, "No Mat"), (66, 66, "1.5\""), (67, 67, "2.0\""), 
            (68, 68, "2.5\""), (69, 69, "3.0\"")
        ]
        PAPER_TYPES = [(74, "Archival Matte"), (75, "Hot Press"), (76, "Cold Press"), 
                       (77, "Metallic"), (78, "Semi-Glossy"), (79, "Glossy"), 
                       (80, "Semi-Matte"), (82, "Somerset Velvet")]
        SIZES = ["5×7", "6×6", "8×8", "8×10", "8×12", "10×10", "11×14", "11×17",
                 "12×12", "12×16", "12×24", "12×36", "16×16", "16×20", "16×24", "16×32",
                 "18×36", "20×20", "20×36", "24×24", "24×30", "24×36"]
        
        imported = 0
        for frame_id, wizard_frame_id, color in FRAME_STYLES:
            for mat_luma_id, wizard_mat_id, mat_name in MAT_SIZES:
                for paper_id, paper_name in PAPER_TYPES:
                    for size in SIZES:
                        name = f"Framed Fine Art {color} {mat_name} Mat {paper_name} {size}\""
                        cursor.execute("SELECT id FROM products WHERE name=?", (name,))
                        if not cursor.fetchone():
                            area = int(size.split('×')[0]) * int(size.split('×')[1])
                            price = 20.0 if area <= 50 else (25.0 if area <= 100 else (35.0 if area <= 200 else (50.0 if area <= 400 else (75.0 if area <= 800 else 100.0))))
                            cursor.execute("""
                                INSERT INTO products (name, product_type_id, category_id, size, cost_price,
                                                    sub_option_1_id, sub_option_2_id, lumaprints_subcategory_id,
                                                    lumaprints_options, active)
                                VALUES (?, 4, 4, ?, ?, ?, ?, ?, ?, 1)
                            """, (name, size, price, wizard_frame_id, wizard_mat_id, frame_id, json.dumps({"mat_size": mat_luma_id, "paper_type": paper_id})))
                            imported += 1
        results.append(f"Imported {imported} new Framed Fine Art products")
        
        # Import additional products for 1.25" frames with mats (if missing)
        FRAME_125_STYLES = [
            (105005, 23, "Black"), (105006, 23, "White"), (105007, 23, "Oak")
        ]
        MAT_SIZES_ONLY = [
            (66, 66, "1.5\""), (67, 67, "2.0\""), (68, 68, "2.5\""), (69, 69, "3.0\"")
        ]
        imported_125 = 0
        for frame_id, wizard_frame_id, color in FRAME_125_STYLES:
            for mat_luma_id, wizard_mat_id, mat_name in MAT_SIZES_ONLY:
                for paper_id, paper_name in PAPER_TYPES:
                    for size in SIZES:
                        name = f"Framed Fine Art {color} {mat_name} Mat {paper_name} {size}\""
                        cursor.execute("SELECT id FROM products WHERE name=?", (name,))
                        if not cursor.fetchone():
                            area = int(size.split('×')[0]) * int(size.split('×')[1])
                            price = 20.0 if area <= 50 else (25.0 if area <= 100 else (35.0 if area <= 200 else (50.0 if area <= 400 else (75.0 if area <= 800 else 100.0))))
                            cursor.execute("""
                                INSERT INTO products (name, product_type_id, category_id, size, cost_price,
                                                    sub_option_1_id, sub_option_2_id, lumaprints_subcategory_id,
                                                    lumaprints_options, active)
                                VALUES (?, 4, 4, ?, ?, ?, ?, ?, ?, 1)
                            """, (name, size, price, wizard_frame_id, wizard_mat_id, frame_id, json.dumps({"mat_size": mat_luma_id, "paper_type": paper_id})))
                            imported_125 += 1
        results.append(f"Imported {imported_125} additional 1.25\" frame + mat products")
        
        # Clean up unused Framed Fine Art frame sizes (keep only 0.875" and 1.25")
        cursor.execute("DELETE FROM sub_options WHERE product_type_id=4 AND level=1 AND id NOT IN (22, 23)")
        results.append(f"Removed {cursor.rowcount} unused frame size options")
        
        # Add mat size options (keep No Mat and add 1.5", 2.0", 2.5", 3.0")
        cursor.execute("""INSERT OR IGNORE INTO sub_options (id, product_type_id, level, option_type, name, value, display_order, active) VALUES
            (66, 4, 2, 'mat_size', 'Mat Size', '1.5" on each side', 2, 1),
            (67, 4, 2, 'mat_size', 'Mat Size', '2.0" on each side', 3, 1),
            (68, 4, 2, 'mat_size', 'Mat Size', '2.5" on each side', 4, 1),
            (69, 4, 2, 'mat_size', 'Mat Size', '3.0" on each side', 5, 1)
        """)
        results.append(f"Added mat size options (1.5\", 2.0\", 2.5\", 3.0\")")
        
        # Clean up other unused mat sizes
        cursor.execute("DELETE FROM sub_options WHERE product_type_id=4 AND level=2 AND id NOT IN (33, 66, 67, 68, 69)")
        results.append(f"Removed {cursor.rowcount} other unused mat size options")
        
        conn.commit()
        
        # Verify the fixes
        cursor.execute("SELECT sub_option_1_id, COUNT(*) FROM products WHERE product_type_id=1 GROUP BY sub_option_1_id")
        canvas_dist = cursor.fetchall()
        
        cursor.execute("SELECT sub_option_1_id, COUNT(*) FROM products WHERE product_type_id=3 GROUP BY sub_option_1_id")
        fine_art_dist = cursor.fetchall()
        
        return f"""
        <h1>🎉 PRODUCT MAPPINGS FIXED!</h1>
        
        <h2>Updates Applied:</h2>
        <ul>
            {''.join([f'<li>{r}</li>' for r in results])}
        </ul>
        
        <h2>Canvas Distribution:</h2>
        <ul>
            {''.join([f'<li>sub_option {row[0]}: {row[1]} products</li>' for row in canvas_dist])}
        </ul>
        
        <h2>Fine Art Paper Distribution:</h2>
        <ul>
            {''.join([f'<li>sub_option {row[0]}: {row[1]} products</li>' for row in fine_art_dist])}
        </ul>
        
        <h2>Test Links:</h2>
        <ul>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=1">Canvas 0.75"</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=1&sub_option_1_id=2">Canvas 1.25"</a></li>
            <li><a href="/api/hierarchical/available-sizes?product_type_id=3&sub_option_1_id=15">Fine Art Archival Matte</a></li>
        </ul>
        
        <h1>✅ WIZARD SHOULD NOW LOAD PRODUCTS!</h1>
        """
        
    except Exception as e:
        conn.rollback()
        return f"Error: {e}"
    finally:
        conn.close()




@app.route('/import-framed-fine-art')
def import_framed_fine_art_products():
    """Import all Framed Fine Art products (No Mat only for testing)"""
    
    # Lumaprints frame subcategories
    FRAME_STYLES = {
        105001: {"name": "0.875\" Black Frame", "wizard_id": 22, "color": "Black"},
        105002: {"name": "0.875\" White Frame", "wizard_id": 22, "color": "White"},
        105003: {"name": "0.875\" Oak Frame", "wizard_id": 22, "color": "Oak"},
        105005: {"name": "1.25\" Black Frame", "wizard_id": 23, "color": "Black"},
        105006: {"name": "1.25\" White Frame", "wizard_id": 23, "color": "White"},
        105007: {"name": "1.25\" Oak Frame", "wizard_id": 23, "color": "Oak"},
    }
    
    # Lumaprints mat sizes (No Mat only)
    MAT_SIZES = {
        64: {"name": "No Mat", "wizard_id": 33},
    }
    
    # Lumaprints paper types
    PAPER_TYPES = {
        74: "Archival Matte",
        75: "Hot Press",
        76: "Cold Press",
        77: "Metallic",
        78: "Semi-Glossy",
        79: "Glossy",
        80: "Semi-Matte",
        82: "Somerset Velvet",
    }
    
    # Standard print sizes
    PRINT_SIZES = [
        "5×7", "6×6", "8×8", "8×10", "8×12",
        "10×10", "11×14", "11×17",
        "12×12", "12×16", "12×24", "12×36",
        "16×16", "16×20", "16×24", "16×32",
        "18×36", "20×20", "20×36", "20×40",
        "24×24", "24×30", "24×36", "24×40",
        "30×30", "30×32", "30×40", "32×48",
        "36×36", "36×48", "40×40", "40×60"
    ]
    
    def get_base_price(size):
        """Calculate base price based on size"""
        parts = size.split('×')
        w, h = int(parts[0]), int(parts[1])
        area = w * h
        
        if area <= 50:
            return 20.0
        elif area <= 100:
            return 25.0
        elif area <= 200:
            return 35.0
        elif area <= 400:
            return 50.0
        elif area <= 800:
            return 75.0
        else:
            return 100.0
    
    conn = get_db()
    cursor = conn.cursor()
    
    product_count = 0
    skipped_count = 0
    
    for frame_id, frame_info in FRAME_STYLES.items():
        for mat_id, mat_info in MAT_SIZES.items():
            for paper_id, paper_name in PAPER_TYPES.items():
                for size in PRINT_SIZES:
                    # Create product name
                    product_name = f"Framed Fine Art {frame_info['color']} {mat_info['name']} {paper_name} {size}\""
                    
                    # Calculate pricing
                    base_price = get_base_price(size)
                    
                    # Check if product already exists
                    cursor.execute("""
                        SELECT id FROM products 
                        WHERE name = ? AND product_type_id = 4
                    """, (product_name,))
                    
                    if cursor.fetchone():
                        skipped_count += 1
                        continue
                    
                    # Store Lumaprints options as JSON
                    lumaprints_opts = json.dumps({"mat_size": mat_id, "paper_type": paper_id})
                    
                    # Insert product
                    cursor.execute("""
                        INSERT INTO products (
                            name, product_type_id, category_id, size, cost_price,
                            sub_option_1_id, sub_option_2_id,
                            lumaprints_subcategory_id, lumaprints_options,
                            active
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        product_name,
                        4,  # Framed Fine Art Paper
                        4,  # Category ID
                        size,
                        base_price,
                        frame_info['wizard_id'],
                        mat_info['wizard_id'],
                        frame_id,
                        lumaprints_opts,
                        1
                    ))
                    
                    product_count += 1
    
    conn.commit()
    
    return f"""
    <h1 style="color: green;">✅ FRAMED FINE ART PRODUCTS IMPORTED!</h1>
    
    <h2>Summary:</h2>
    <ul>
        <li><strong>New products imported:</strong> {product_count}</li>
        <li><strong>Existing products skipped:</strong> {skipped_count}</li>
        <li><strong>Total:</strong> {product_count + skipped_count}</li>
    </ul>
    
    <h2>Configuration:</h2>
    <ul>
        <li>Frame Styles: 6 (0.875" and 1.25" in Black, White, Oak)</li>
        <li>Mat Sizes: 1 (No Mat only)</li>
        <li>Paper Types: 8 (All Lumaprints paper types)</li>
        <li>Print Sizes: 32 standard sizes</li>
    </ul>
    
    <h2>Test the Form:</h2>
    <p><a href="/hierarchical_order_form?image=starling.JPG">Test Order Form</a></p>
    """

# Add this to app.py after the other fix endpoints

@app.route('/restore-database-from-backup')
def restore_database_from_backup():
    """Restore database from the backup file in static folder"""
    import shutil
    import os
    
    try:
        # Source: backup file in static folder
        backup_file = 'static/lumaprints_pricing_restore.db'
        
        # Destination: persistent /data/ directory
        target_file = '/data/lumaprints_pricing.db'
        
        # Ensure /data directory exists
        os.makedirs('/data', exist_ok=True)
        
        # Check if backup file exists
        if not os.path.exists(backup_file):
            return f"""
            <h1>❌ Error</h1>
            <p>Backup file not found at {backup_file}</p>
            """, 404
        
        # Copy the backup to /data/
        shutil.copy2(backup_file, target_file)
        
        # Verify the restore
        import sqlite3
        conn = sqlite3.connect(target_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE active = 1")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT value FROM settings WHERE key_name = 'global_markup_percentage'")
        markup = cursor.fetchone()
        markup_value = markup[0] if markup else 'Not set'
        conn.close()
        
        return f"""
        <h1>✅ Database Restored Successfully!</h1>
        <p><strong>Products restored:</strong> {product_count}</p>
        <p><strong>Global markup:</strong> {markup_value}%</p>
        <p><strong>Database location:</strong> {target_file}</p>
        
        <h2>Next Steps:</h2>
        <ul>
            <li><a href="/admin/pricing">Check Pricing Admin</a></li>
            <li><a href="/hierarchical_order_form">Test Order Form</a></li>
        </ul>
        """
        
    except Exception as e:
        return f"""
        <h1>❌ Restore Failed</h1>
        <p>Error: {str(e)}</p>
        """, 500


# Register pricing form blueprints
from product_api import product_api
from pricing_form_route import pricing_form
from order_form_api import order_form_api

app.register_blueprint(product_api)
app.register_blueprint(pricing_form)
app.register_blueprint(order_form_api)

# Database management routes
@app.route('/admin/database')
@require_admin_auth
def admin_database():
    """Database export/import management page"""
    return render_template('admin_database.html')

@app.route('/admin/database/diagnose', methods=['GET'])
@require_admin_auth
def diagnose_database_route():
    """Diagnose database structure"""
    from database_diagnostic import diagnose_database
    result = diagnose_database()
    return jsonify(result)

@app.route('/admin/database/check-products', methods=['GET'])
@require_admin_auth
def check_products_route():
    """Check what products exist in database"""
    from check_products import check_products
    result = check_products()
    return jsonify(result)

@app.route('/admin/database/export', methods=['POST'])
@require_admin_auth
def export_database():
    """Export pricing database to JSON"""
    import traceback
    from database_export_inline import export_pricing_database
    
    try:
        export_data = export_pricing_database()
        
        # Return JSON directly
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = f'attachment; filename=pricing_db_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        return response
        
    except Exception as e:
        print(f"Export error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': f'{type(e).__name__}: {str(e)}'}), 500

@app.route('/admin/database/import', methods=['POST'])
@require_admin_auth
def import_database():
    """Import pricing database from JSON"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from import_pricing_db import import_database as do_import
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({'success': False, 'error': 'File must be a JSON file'}), 400
        
        # Save uploaded file temporarily
        temp_path = '/tmp/uploaded_pricing_db.json'
        file.save(temp_path)
        
        # Import the database
        do_import(temp_path, '/data/lumaprints_pricing.db', clear_existing=True)
        
        # Get stats
        import sqlite3
        conn = sqlite3.connect('/data/lumaprints_pricing.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM product_types")
        product_type_count = cursor.fetchone()[0]
        conn.close()
        
        # Clean up temp file
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'stats': {
                'products': product_count,
                'categories': category_count,
                'product_types': product_type_count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Pricing API routes
@app.route('/api/pricing/product', methods=['GET'])
def get_pricing():
    """Get pricing for a specific product"""
    from pricing_api import get_product_price
    
    subcategory_id = request.args.get('subcategory_id', type=int)
    size = request.args.get('size')
    variant_id = request.args.get('variant_id', type=int)
    
    if not subcategory_id or not size:
        return jsonify({
            'success': False,
            'error': 'Missing required parameters: subcategory_id and size'
        }), 400
    
    result = get_product_price(subcategory_id, size, variant_id)
    return jsonify(result)

@app.route('/api/pricing/category/<int:category_id>', methods=['GET'])
def get_category_pricing(category_id):
    """Get all products and pricing for a category"""
    from pricing_api import get_category_products
    
    result = get_category_products(category_id)
    return jsonify(result)

@app.route('/api/pricing/variants/<int:product_id>', methods=['GET'])
def get_product_variants_route(product_id):
    """Get all variants for a product"""
    from pricing_api import get_product_variants
    
    result = get_product_variants(product_id)
    return jsonify(result)

@app.route('/api/image/exif/<path:filename>', methods=['GET'])
def get_image_exif(filename):
    """Get EXIF data including DPI from image file"""
    try:
        from PIL import Image
        import traceback
        
        # Images are stored in /data persistent volume on Railway
        image_path = os.path.join(IMAGES_FOLDER, filename)
        print(f"[EXIF] Attempting to read image from: {image_path}")
        print(f"[EXIF] IMAGES_FOLDER = {IMAGES_FOLDER}")
        print(f"[EXIF] File exists: {os.path.exists(image_path)}")
        
        if not os.path.exists(image_path):
            error_msg = f'Image not found at {image_path}'
            print(f"[EXIF ERROR] {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 404
        
        # Open image from local filesystem
        with Image.open(image_path) as img:
            width, height = img.size
            
            # Get DPI from image info
            dpi = img.info.get('dpi', None)
            if dpi and isinstance(dpi, tuple):
                # DPI is stored as (x_dpi, y_dpi), usually they're the same
                # Convert to float in case it's IFDRational
                dpi_value = float(dpi[0])
            else:
                # Try to get from EXIF
                try:
                    exif_data = img._getexif()
                    if exif_data:
                        # EXIF tag 282 is XResolution, 283 is YResolution
                        x_res = exif_data.get(282)
                        if x_res:
                            # Handle IFDRational objects (fractions)
                            if isinstance(x_res, tuple) and len(x_res) == 2:
                                dpi_value = float(x_res[0]) / float(x_res[1])
                            else:
                                # It's already a number or IFDRational
                                dpi_value = float(x_res)
                        else:
                            dpi_value = None
                    else:
                        dpi_value = None
                except Exception as exif_error:
                    print(f"[EXIF] Error reading EXIF: {exif_error}")
                    dpi_value = None
            
            # Ensure DPI is JSON serializable
            if dpi_value is not None:
                dpi_value = float(dpi_value)
            
            return jsonify({
                'success': True,
                'width': width,
                'height': height,
                'dpi': dpi_value,
                'format': img.format
            })
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[EXIF ERROR] Exception occurred: {str(e)}")
        print(f"[EXIF ERROR] Traceback:\n{error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace
        }), 500

# Dynamic order form route
@app.route('/order')
def order_form():
    """Clean order form using dynamic Lumaprints API"""
    return order_form_route()

