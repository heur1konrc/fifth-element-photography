"""
Admin route for cleaning image descriptions
"""
from flask import Blueprint, render_template, jsonify, session, redirect, url_for
import os
import sys

# Add parent directory to path to import clean_descriptions module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clean_descriptions import clean_descriptions_file

clean_descriptions_admin_bp = Blueprint('clean_descriptions_admin', __name__)

@clean_descriptions_admin_bp.route('/admin/clean-descriptions')
def clean_descriptions_page():
    """Display page for cleaning descriptions"""
    return render_template('admin/clean_descriptions.html')

@clean_descriptions_admin_bp.route('/admin/api/clean-descriptions', methods=['POST'])
def clean_descriptions_api():
    """API endpoint to trigger description cleaning"""
    
    try:
        # Determine file path based on environment
        file_path = '/data/image_descriptions.json' if os.path.exists('/data') else 'image_descriptions.json'
        
        # Run cleaning with backup
        stats = clean_descriptions_file(file_path, backup=True)
        
        if 'error' in stats:
            return jsonify({'success': False, 'error': stats['error']}), 400
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': f"Cleaned {stats['cleaned']} descriptions successfully!"
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
