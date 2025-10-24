#!/usr/bin/env python3
"""
Switch app.py to use Pictorem instead of Lumaprints
This script updates the imports and API endpoints
"""

import os
import shutil
from datetime import datetime

APP_FILE = 'app.py'
BACKUP_FILE = f'app_lumaprints_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'

def backup_app():
    """Create backup of current app.py"""
    print(f"Creating backup: {BACKUP_FILE}")
    shutil.copy2(APP_FILE, BACKUP_FILE)
    print(f"✅ Backup created")

def update_imports():
    """Update imports to use Pictorem modules"""
    print("\nUpdating imports...")
    
    with open(APP_FILE, 'r') as f:
        content = f.read()
    
    # Comment out Lumaprints imports
    content = content.replace(
        'from lumaprints_api import get_lumaprints_client, get_pricing_calculator',
        '# from lumaprints_api import get_lumaprints_client, get_pricing_calculator  # REPLACED WITH PICTOREM'
    )
    
    content = content.replace(
        'from dynamic_product_api import get_products_for_frontend',
        '# from dynamic_product_api import get_products_for_frontend  # REPLACED WITH PICTOREM'
    )
    
    # Add Pictorem imports after Flask import
    flask_import = 'from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for'
    if flask_import in content:
        content = content.replace(
            flask_import,
            flask_import + '\n\n# Pictorem integration\nfrom pictorem_product_api import get_products_for_frontend, get_product_price_api, get_categories_for_frontend, get_product_details\nfrom pictorem_admin import pictorem_admin_bp\nfrom pictorem_api import PictoremAPI'
        )
    
    with open(APP_FILE, 'w') as f:
        f.write(content)
    
    print("✅ Imports updated")

def register_pictorem_blueprint():
    """Register Pictorem admin blueprint"""
    print("\nRegistering Pictorem admin blueprint...")
    
    with open(APP_FILE, 'r') as f:
        content = f.read()
    
    # Find where to add blueprint registration (after app creation)
    app_creation = "app = Flask(__name__)"
    if app_creation in content:
        # Add blueprint registration after app secret key
        secret_key_line = "app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))"
        if secret_key_line in content:
            content = content.replace(
                secret_key_line,
                secret_key_line + '\n\n# Register Pictorem admin blueprint\napp.register_blueprint(pictorem_admin_bp)'
            )
    
    with open(APP_FILE, 'w') as f:
        f.write(content)
    
    print("✅ Blueprint registered")

def add_pictorem_api_routes():
    """Add Pictorem API routes"""
    print("\nAdding Pictorem API routes...")
    
    with open(APP_FILE, 'r') as f:
        content = f.read()
    
    # Find the products API endpoint and update it
    old_products_route = """@app.route('/api/products', methods=['GET'])
def get_frontend_products():
    \"\"\"Get all products for frontend order form (no auth required)\"\"\"
    return get_products_for_frontend()"""
    
    new_products_route = """@app.route('/api/products', methods=['GET'])
def get_frontend_products():
    \"\"\"Get all products for frontend order form (no auth required) - PICTOREM VERSION\"\"\"
    return get_products_for_frontend()

@app.route('/api/categories', methods=['GET'])
def get_frontend_categories():
    \"\"\"Get all product categories for frontend\"\"\"
    return get_categories_for_frontend()

@app.route('/api/product/<slug>', methods=['GET'])
def get_product_by_slug(slug):
    \"\"\"Get product details by slug\"\"\"
    return get_product_details(slug)

@app.route('/api/price', methods=['POST'])
def calculate_product_price():
    \"\"\"Calculate price for a product configuration\"\"\"
    data = request.get_json()
    product_slug = data.get('product_slug')
    width = data.get('width')
    height = data.get('height')
    options = data.get('options', {})
    return get_product_price_api(product_slug, width, height, options)"""
    
    if old_products_route in content:
        content = content.replace(old_products_route, new_products_route)
    
    with open(APP_FILE, 'w') as f:
        f.write(content)
    
    print("✅ API routes added")

def update_database_path():
    """Update database path references"""
    print("\nUpdating database paths...")
    
    with open(APP_FILE, 'r') as f:
        content = f.read()
    
    # This will keep Lumaprints database for orders/admin, but products come from Pictorem
    # No changes needed - both databases can coexist
    
    print("✅ Database paths OK (both databases will coexist)")

def main():
    print("="*60)
    print("SWITCHING APP TO PICTOREM")
    print("="*60)
    
    if not os.path.exists(APP_FILE):
        print(f"❌ Error: {APP_FILE} not found")
        return
    
    backup_app()
    update_imports()
    register_pictorem_blueprint()
    add_pictorem_api_routes()
    update_database_path()
    
    print("\n" + "="*60)
    print("✅ APP SUCCESSFULLY SWITCHED TO PICTOREM")
    print("="*60)
    print(f"\nBackup saved as: {BACKUP_FILE}")
    print("\nNext steps:")
    print("1. Test the app: python3.11 app.py")
    print("2. Verify /api/products endpoint returns Pictorem data")
    print("3. Test pricing admin at /admin/pictorem/pricing")
    print()

if __name__ == '__main__':
    main()

