from flask import Blueprint, render_template, jsonify
from functools import wraps
from flask import session, redirect, url_for
import os
import sqlite3

setup_pricing_bp = Blueprint('setup_pricing', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
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

