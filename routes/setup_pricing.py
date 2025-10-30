"""
Setup route for initializing print ordering database on Railway
Visit /admin/setup-pricing to populate the database
"""

from flask import Blueprint, render_template, jsonify, session, redirect, url_for
import sqlite3
import os
import openpyxl
from functools import wraps

setup_pricing_bp = Blueprint('setup_pricing', __name__)

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@setup_pricing_bp.route('/admin/setup-pricing')
@admin_required
def setup_pricing_page():
    """Display setup page"""
    return render_template('admin_setup_pricing.html')

@setup_pricing_bp.route('/admin/setup-pricing/run', methods=['POST'])
@admin_required
def run_pricing_setup():
    """Execute database setup - copy pre-populated database"""
    try:
        # Determine paths
        if os.path.exists('/data'):
            db_path = '/data/print_ordering.db'
            data_dir = '/data'
        else:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'print_ordering.db')
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
        
        os.makedirs(data_dir, exist_ok=True)
        
        # Use pre-populated database template
        template_db = os.path.join(os.path.dirname(__file__), '..', 'database_templates', 'print_ordering_initial.db')
        
        if not os.path.exists(template_db):
            return jsonify({
                'success': False,
                'error': 'Pre-populated database template not found',
                'path': template_db
            })
        
        # Copy template to target location
        import shutil
        shutil.copy2(template_db, db_path)
        
        # Verify the copy worked
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM base_pricing')
        total_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Database initialized successfully from template',
            'total': total_count,
            'db_path': db_path
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

# OLD IMPORT CODE BELOW - KEEPING FOR REFERENCE
'''
        # Step 1: Create schema
        schema_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'print_ordering_schema.sql')
        
        if not os.path.exists(schema_file):
            return jsonify({
                'success': False,
                'error': 'Schema file not found',
                'path': schema_file
            })
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        with open(schema_file, 'r') as f:
            conn.executescript(f.read())
        
        # Step 2: Import pricing data from Excel
        excel_file = os.path.join(os.path.dirname(__file__), '..', 'LumaprintsCatalogandSizingw_aspectratios.xlsx')
        
        if not os.path.exists(excel_file):
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Excel catalog file not found',
                'path': excel_file
            })
        
        wb = openpyxl.load_workbook(excel_file)
        ws = wb.active
        
        # Product mapping
        product_mapping = {
            'Canvas': {
                'category_id': 1,
                'subcategories': {
                    '0.75"': 101001,
                    '1.25"': 101002,
                    '1.50"': 101003,
                    'Rolled': 101005
                }
            },
            'Framed Canvas': {
                'category_id': 2,
                'subcategories': {
                    '0.75"': 102001,
                    '1.25"': 102002,
                    '1.50"': 102003
                }
            },
            'Fine Art Paper': {
                'category_id': 3,
                'subcategories': {
                    'Hot Press': 103002,
                    'Cold Press': 103003,
                    'Semi-Glossy': 103005,
                    'Glossy': 103007
                }
            },
            'Foam-mounted Print': {
                'category_id': 4,
                'subcategories': {
                    'Hot Press': 104002,
                    'Cold Press': 104003,
                    'Semi-Glossy': 104005,
                    'Glossy': 104007
                }
            }
        }
        
        imported_count = 0
        current_category = None
        current_aspect_ratio = None
        header_row = None
        
        for row_idx, row in enumerate(ws.iter_rows(min_row=1, values_only=True), start=1):
            if not row or not any(row):
                continue
            
            first_cell = str(row[0]).strip() if row[0] else ''
            
            # Detect category
            for cat_name in product_mapping.keys():
                if cat_name in first_cell:
                    current_category = cat_name
                    break
            
            # Detect aspect ratio
            if 'aspect ratio' in first_cell.lower():
                if '1:1' in first_cell:
                    current_aspect_ratio = '1:1'
                elif '3:2' in first_cell:
                    current_aspect_ratio = '3:2'
                continue
            
            # Detect header row
            if first_cell.lower() == 'size':
                header_row = row
                continue
            
            # Process data rows
            if current_category and current_aspect_ratio and header_row:
                size = first_cell
                if not size or size == 'SIZE':
                    continue
                
                # Import prices for each subcategory
                for col_idx, header in enumerate(header_row[1:], start=1):
                    if not header:
                        continue
                    
                    header_str = str(header).strip()
                    price_value = row[col_idx]
                    
                    if price_value and str(price_value).strip().lower() != 'n/a':
                        try:
                            cost_price = float(price_value)
                            
                            # Find matching subcategory
                            for subcat_name, subcat_id in product_mapping[current_category]['subcategories'].items():
                                if subcat_name in header_str:
                                    cursor.execute('''
                                        INSERT INTO base_pricing 
                                        (category_id, subcategory_id, size, aspect_ratio, cost_price, is_available)
                                        VALUES (?, ?, ?, ?, ?, TRUE)
                                    ''', (
                                        product_mapping[current_category]['category_id'],
                                        subcat_id,
                                        size,
                                        current_aspect_ratio,
                                        cost_price
                                    ))
                                    imported_count += 1
                                    break
                        except (ValueError, TypeError):
                            pass
        
        conn.commit()
        
        # Get final count
        cursor.execute('SELECT COUNT(*) FROM base_pricing')
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Database initialized successfully',
            'imported': imported_count,
            'total': total_count,
            'db_path': db_path
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@setup_pricing_bp.route('/admin/setup-pricing/status')
@admin_required
def check_setup_status():
    """Check if database is set up"""
    try:
        if os.path.exists('/data'):
            db_path = '/data/print_ordering.db'
        else:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'print_ordering.db')
        
        if not os.path.exists(db_path):
            return jsonify({
                'setup': False,
                'message': 'Database not found',
                'path': db_path
            })
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM base_pricing')
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'setup': True,
            'products': count,
            'path': db_path
        })
        
    except Exception as e:
        return jsonify({
            'setup': False,
            'error': str(e)
        })

